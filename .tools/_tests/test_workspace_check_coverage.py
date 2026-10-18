#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_workspace_check_coverage.py — 登记完整性分区（coverage）回归测试。

防线背景（历史两实例靠操作者手动指出后机器化）：
机制实例落地后入口真源失同步——孤儿目录检测机器化，warning 档。
验证：顶层孤儿报 / 顶层已登记过 / position 孤儿报 / position 已登记过 / 豁免集不误报。
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
_spec = importlib.util.spec_from_file_location("_wc_cov_under_test", TOOLS / "workspace-check.py")
wc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wc)


class RegistryCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root

    def tearDown(self):
        wc.ROOT = self._orig_root
        self.tmp.cleanup()

    def _check(self):
        errors, warnings = [], []
        wc.check_registry_coverage(errors, warnings)
        return warnings

    def test_topdir_orphan_reported(self):
        """顶层目录未在 README/AGENTS 出现 → warning。"""
        (self.root / "workspace-grills").mkdir()
        warns = self._check()
        self.assertEqual(len(warns), 1)
        self.assertIn("workspace-grills", warns[0])
        self.assertIn("README.md", warns[0])

    def test_topdir_registered_passes(self):
        """顶层目录名出现在 README.md → 零 warning。"""
        (self.root / "workspace-grills").mkdir()
        (self.root / "README.md").write_text("目录表里有 workspace-grills 条目", encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_topdir_exempt_not_reported(self):
        """豁免集目录（.git/.agents/.tools 等）不报。"""
        for name in (".git", ".agents", ".tools", ".zcode"):
            (self.root / name).mkdir()
        self.assertEqual(self._check(), [])

    def test_position_orphan_reported(self):
        """position/ 子目录未在 position/README.md 出现 → warning（顶层先登记 position 消除顶层孤儿噪音）。"""
        (self.root / "README.md").write_text("目录表含 position", encoding="utf-8")
        pos = self.root / "position"
        pos.mkdir()
        (pos / "mystery").mkdir()
        (pos / "README.md").write_text("定位基准（无子目录提及）", encoding="utf-8")
        warns = self._check()
        self.assertEqual(len(warns), 1)
        self.assertIn("position/mystery", warns[0])

    def test_position_registered_passes(self):
        """position/ 子目录名出现在其 README → 零 warning。"""
        (self.root / "README.md").write_text("目录表含 position", encoding="utf-8")
        pos = self.root / "position"
        pos.mkdir()
        (pos / "snapshots").mkdir()
        (pos / "README.md").write_text("对比体系含 [snapshots/] 行", encoding="utf-8")
        self.assertEqual(self._check(), [])


if __name__ == "__main__":
    unittest.main()
