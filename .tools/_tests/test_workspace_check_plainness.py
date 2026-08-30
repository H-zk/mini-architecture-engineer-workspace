#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_workspace_check_plainness.py — plainness 分区（文档平实度四指标）回归测试

背景（v1 吸收批次二直搬）：机制文档「生产者逻辑 ≠ 消费者逻辑」——单行/单段密度过大致
常规阅读失效。验证四类检出（单行/表格行/散文段/括号嵌套）+ 正常文件不误报 +
frontmatter/围栏跳过 + --staged files= 参数路径。用临时 fixture，不读真实工作区文件。
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# 强制 stdout UTF-8：Windows 中文控制台默认 GBK（工作区惯例，见 AGENTS 终端节）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOOLS = Path(__file__).resolve().parent.parent

# workspace-check.py 文件名含连字符，用 importlib 加载
_spec = importlib.util.spec_from_file_location("_wc_under_test", TOOLS / "workspace-check.py")
wc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wc)


class PlainnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        self.doc = self.root / "WORKFLOW.md"

    def tearDown(self):
        wc.ROOT = self._orig_root
        self.tmp.cleanup()

    def _warnings(self, files=None):
        warns = []
        wc.check_doc_plainness(warns, files=files)
        return warns

    def test_normal_doc_no_warning(self):
        """正常短行/短段/浅嵌套文档：零告警。"""
        self.doc.write_text(
            "# 标题\n\n短行正文。\n\n- 列表项\n\n表格行不超限（浅嵌套（一层））。\n",
            encoding="utf-8",
        )
        self.assertEqual(self._warnings(), [])

    def test_long_line_detected(self):
        """单行 >400 检出（同时构成超限散文段——两条聚合告警各指标一条）。"""
        self.doc.write_text("# 标题\n\n" + "长" * 401 + "\n", encoding="utf-8")
        warns = self._warnings()
        self.assertEqual(len(warns), 2)  # 行超限 + 散文段超限（纯文本行 401>400）
        self.assertTrue(all(":3" in w for w in warns))

    def test_table_line_higher_limit(self):
        """表格行阈值 600：正文行 500 字在表格内合法、裸行 500 报。"""
        (self.root / "t500.md").write_text("| " + "a" * 500 + " |\n", encoding="utf-8")
        (self.root / "t700.md").write_text("| " + "a" * 700 + " |\n", encoding="utf-8")
        self.assertEqual(self._warnings(files=["t500.md"]), [])
        warns = self._warnings(files=["t700.md"])
        self.assertTrue(any("行超限" in w for w in warns))

    def test_prose_paragraph_accumulates(self):
        """散文段合计 >400 检出（单行不超限但连续纯文本行累加）。"""
        para = "\n".join("正" * 90 for _ in range(5))  # 5 行 ×90 = 450，单行均 <400
        self.doc.write_text("# 标题\n\n" + para + "\n", encoding="utf-8")
        warns = self._warnings()
        self.assertTrue(any("散文段超" in w for w in warns))

    def test_structural_lines_break_paragraph(self):
        """列表/标题/表格行切断散文段累计（结构性行不计入段落）。"""
        body = "\n".join(
            ["正" * 90, "- 列表切断", "正" * 90]  # 90 + 90 = 180 < 400
        )
        self.doc.write_text("# 标题\n\n" + body + "\n", encoding="utf-8")
        self.assertEqual(self._warnings(), [])

    def test_nesting_depth_three_detected(self):
        """括号嵌套 ≥3 层检出（中英文括号合计）。"""
        self.doc.write_text("# 标题\n\n条款（一级（二级（三级）））。\n", encoding="utf-8")
        warns = self._warnings()
        self.assertTrue(any("括号嵌套" in w for w in warns))

    def test_frontmatter_and_fences_skipped(self):
        """frontmatter 单串与围栏内长行/深嵌套不计（非散文）。"""
        self.doc.write_text(
            "---\ndescription: " + "描" * 500 + "\n---\n\n# 标题\n\n```text\n"
            + "代码" * 250 + "\n```\n",
            encoding="utf-8",
        )
        self.assertEqual(self._warnings(), [])

    def test_files_param_scopes_check(self):
        """files=[相对路径] 只查给定文件，目标集外的违规不可见。"""
        (self.root / "a.md").write_text("长" * 401 + "\n", encoding="utf-8")
        (self.root / "b.md").write_text("正常短行。\n", encoding="utf-8")
        self.assertEqual(self._warnings(files=["b.md"]), [])
        self.assertTrue(self._warnings(files=["a.md"]))


class NestDepthUnitTests(unittest.TestCase):
    def test_unbalanced_close_clamped_to_zero(self):
        """闭括号多余只钳到 0，不产生负深度误判后续开括号。"""
        self.assertEqual(wc._nest_depth("))（（"), 2)

    def test_mixed_paren_kinds_counted(self):
        self.assertEqual(wc._nest_depth("（(（"), 3)
        self.assertEqual(wc._nest_depth("(a(b)c)"), 2)


class FrozenSnapshotTests(unittest.TestCase):
    def test_run_prefixes_frozen(self):
        self.assertTrue(wc._is_frozen_snapshot("run-2026.md"))
        self.assertTrue(wc._is_frozen_snapshot("evals-run-x.md"))
        self.assertFalse(wc._is_frozen_snapshot("learn-report.md"))


if __name__ == "__main__":
    unittest.main()
