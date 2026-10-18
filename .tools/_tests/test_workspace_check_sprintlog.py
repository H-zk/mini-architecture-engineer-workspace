#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_workspace_check_sprintlog.py — sprint-log 尾段一致性校验回归测试

背景（掉落改标机检补齐回归）：WORKFLOW §2.7 掉落改标约定的
sprint-log 机检校验——掉落任务才写 sprint-log、两段起；尾段必须等于该任务
frontmatter sprint-version。验证：
无字段不查 / 合法两段与三段过 / 尾段不一致报 / 格式非法（单段、无空格箭头）报。
用临时 fixture 写 CURRENT，不写真实工作区文件（states 真源只读真实 skill
frontmatter，monkey-patch 见 setUp）。
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


def _current(sprint_log=None, sprint_version="20261015"):
    """构造最小合法 CURRENT.md（两态均在 skill states 集内）。"""
    lines = [
        "---",
        "status: 进行中",
        "next: 推进中事项",
        "blocker: 无",
        "updated-at: 2026-10-18",
        f"sprint-version: {sprint_version}",
    ]
    if sprint_log is not None:
        lines.append(f"sprint-log: {sprint_log}")
    lines += ["---", "", "# 当前进度", "", "- x", ""]
    return "\n".join(lines)


class SprintLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        # fixture 根下无 skill，monkey-patch load_states 返回状态集
        self._orig_load = wc.load_states
        wc.load_states = lambda t: {
            "workspace-optimize": ["进行中", "已完成"],
        }.get(t) or self._orig_load(t)
        self.task = self.root / "workspace-optimize" / "task-x"
        self.task.mkdir(parents=True)
        self.cur = self.task / "CURRENT.md"

    def tearDown(self):
        wc.ROOT = self._orig_root
        wc.load_states = self._orig_load
        self.tmp.cleanup()

    def _check(self):
        errors, warnings = [], []
        wc.check_task_current(self.task, "workspace-optimize/task-x", errors, warnings)
        return errors

    def test_no_sprint_log_not_checked(self):
        """非掉落任务不写 sprint-log：不查、零 error。"""
        self.cur.write_text(_current(), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_valid_two_segments_pass(self):
        self.cur.write_text(_current("20260917 → 20261015"), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_valid_three_segments_pass(self):
        """多次掉落 append 后三段轨迹合法（尾段仍等于当前 sprint-version）。"""
        self.cur.write_text(_current("20260827 → 20260917 → 20261015"), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_tail_mismatch_errors(self):
        """掉落改标只改一处（漏 append 或改标未同步）：尾段 ≠ sprint-version 报 error。"""
        self.cur.write_text(_current("20260917 → 20260917", "20261015"), encoding="utf-8")
        errs = self._check()
        self.assertEqual(len(errs), 1)
        self.assertIn("尾段", errs[0])
        self.assertIn("sprint-version", errs[0])

    def test_single_segment_format_error(self):
        """单段（两段起红线）：格式非法报 error。"""
        self.cur.write_text(_current("20261015"), encoding="utf-8")
        errs = self._check()
        self.assertEqual(len(errs), 1)
        self.assertIn("格式非法", errs[0])

    def test_arrow_without_spaces_format_error(self):
        """箭头无空格（'→' 两侧空格是格式本体）：格式非法报 error。"""
        self.cur.write_text(_current("20260917→20261015"), encoding="utf-8")
        errs = self._check()
        self.assertEqual(len(errs), 1)
        self.assertIn("格式非法", errs[0])


if __name__ == "__main__":
    unittest.main()
