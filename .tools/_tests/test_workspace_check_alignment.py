#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_workspace_check_alignment.py — INDEX 对齐 / README H1 / CURRENT 软上限回归测试

背景（v1 吸收批次二直搬）：活跃任务漏登 INDEX = 任务对「先查索引」的会话不可见；
README 全员同名，H1 不记目录名无法定位；CURRENT 被过程明细挤爆则活状态失效。
三项都是新机检分区，验证检出与豁免边界。用临时 fixture，不读真实工作区文件。
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

STATES = ["进行中", "已完成"]


class IndexAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        (self.root / "story").mkdir()
        (self.root / "story" / "feat-task").mkdir()
        self.index = self.root / "story" / "INDEX.md"

    def tearDown(self):
        wc.ROOT = self._orig_root
        self.tmp.cleanup()

    def _errors(self, task_rel=None):
        errors, warnings = [], []
        wc.check_index_alignment(errors, warnings, task_rel=task_rel)
        return errors

    def test_unregistered_task_reported(self):
        """活跃任务未在 INDEX 登记 → error。"""
        self.index.write_text("| 标题 | 摘要 | 关键词 | 文件 |\n| - | - | - | - |\n", encoding="utf-8")
        self.assertTrue(any("未登记" in e for e in self._errors(task_rel="story/feat-task")))
        self.assertTrue(any("未登记" in e for e in self._errors()))  # 全量口径同报

    def test_index_missing_reported(self):
        """根 INDEX.md 缺失 → error（比漏行更根本）。"""
        self.assertTrue(any("INDEX.md 缺失" in e for e in self._errors(task_rel="story/feat-task")))

    def test_exact_registration_passes(self):
        """表格行内精确 `<目录名>/README.md` 登记 → 通过。"""
        self.index.write_text(
            "| x | [t](./feat-task/README.md) |\n", encoding="utf-8",
        )
        self.assertEqual(self._errors(task_rel="story/feat-task"), [])

    def test_prefix_name_does_not_satisfy(self):
        """任务名前缀变体（feat-task-extra）不算登记——精确正则防误命中。"""
        self.index.write_text("| x | feat-task-extra/README.md |\n", encoding="utf-8")
        self.assertTrue(any("未登记" in e for e in self._errors(task_rel="story/feat-task")))

    def test_archive_task_rel_skipped(self):
        """archive 任务不查（历史行对齐另行治理）。"""
        self.assertEqual(self._errors(task_rel="archive/story/feat-old"), [])

    def test_legacy_archive_task_rel_skipped(self):
        """旧布局残留（<根>/archive/…）不查——归档已收拢根级 archive/<根>/。"""
        self.assertEqual(self._errors(task_rel="story/archive/feat-old"), [])


class ReadmeH1Tests(unittest.TestCase):
    """_check_products 内 H1 校验（未完成任务 README 首 H1 须含目录名）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        self.entry = self.root / "story" / "feat-2026-08-29-h1"
        self.entry.mkdir(parents=True)
        (self.entry / "CURRENT.md").write_text(
            "---\nstatus: 进行中\nnext: x\nblocker: 无\n---\n# 进度\n",
            encoding="utf-8",
        )
        # story 需要 plan.md 从编码中起、review.md 从审核中起；进行中只强制 README/CURRENT
        self._states_patch = mock.patch.object(wc, "load_states", return_value=list(STATES))
        self._states_patch.start()

    def tearDown(self):
        self._states_patch.stop()
        wc.ROOT = self._orig_root
        self.tmp.cleanup()

    def _errors(self, status="进行中"):
        (self.entry / "CURRENT.md").write_text(
            f"---\nstatus: {status}\nnext: x\nblocker: 无\n---\n# 进度\n", encoding="utf-8",
        )
        errors, warnings = [], []
        wc._check_products(self.entry, "story/feat-2026-08-29-h1", "story", status, errors)
        return errors

    def test_h1_with_dirname_passes(self):
        (self.entry / "README.md").write_text(
            "# feat-2026-08-29-h1：某需求\n\n正文\n", encoding="utf-8",
        )
        self.assertEqual(self._errors(), [])

    def test_h1_without_dirname_reported(self):
        (self.entry / "README.md").write_text("# 某需求开发\n\n正文\n", encoding="utf-8")
        self.assertTrue(any("H1 未含任务目录名" in e for e in self._errors()))

    def test_missing_h1_reported(self):
        (self.entry / "README.md").write_text("## 只有二级标题\n\n正文\n", encoding="utf-8")
        self.assertTrue(any("缺 H1 标题" in e for e in self._errors()))

    def test_completed_exempt(self):
        """已完成豁免（README 冻结，留作回顾基准）。"""
        (self.entry / "README.md").write_text("# 旧标题不回改\n", encoding="utf-8")
        self.assertEqual(self._errors(status="已完成"), [])

    def test_fenced_h1_example_not_counted(self):
        """围栏代码块内示例 H1 不算首个 H1。"""
        (self.entry / "README.md").write_text(
            "```markdown\n# 示例标题\n```\n\n正文无 H1\n", encoding="utf-8",
        )
        self.assertTrue(any("缺 H1 标题" in e for e in self._errors()))


class CurrentSoftLimitTests(unittest.TestCase):
    """CURRENT 正文非空行 >60 软上限（warning 档，digest 化约定 WORKFLOW §2.6）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        self.entry = self.root / "story" / "feat-digest"
        self.entry.mkdir(parents=True)
        self._states_patch = mock.patch.object(wc, "load_states", return_value=list(STATES))
        self._states_patch.start()

    def tearDown(self):
        self._states_patch.stop()
        wc.ROOT = self._orig_root
        self.tmp.cleanup()

    def _warnings(self, body_lines, rel="story/feat-digest"):
        body = "\n".join(body_lines)
        (self.entry / "CURRENT.md").write_text(
            f"---\nstatus: 进行中\nnext: x\nblocker: 无\n---\n{body}\n",
            encoding="utf-8",
        )
        errors, warnings = [], []
        wc.check_task_current(self.entry, rel, errors, warnings)
        return warnings

    def test_over_60_lines_warned(self):
        warns = self._warnings(["- 事件行"] * 61)
        self.assertTrue(any("非空行（>60" in w for w in warns))

    def test_at_60_lines_ok(self):
        self.assertEqual(self._warnings(["- 事件行"] * 60), [])

    def test_blank_lines_not_counted(self):
        """空行不计（61 行内容夹 40 空行 → 61 非空仍报）。"""
        lines = []
        for i in range(61):
            lines.append(f"- 事件 {i}")
            lines.append("")
        warns = self._warnings(lines)
        self.assertTrue(any("非空行（>60" in w for w in warns))

    def test_archive_exempt(self):
        """archive 历史任务保留原貌不告警。"""
        warns = self._warnings(["- 事件行"] * 100, rel="archive/story/feat-old")
        self.assertEqual(warns, [])


if __name__ == "__main__":
    unittest.main()
