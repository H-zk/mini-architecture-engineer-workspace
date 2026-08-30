#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_workspace_check_mdlint_scope.py — MDLINT scope 扩围口径回归测试（B6）。

`.agents/skills/**` 扩入 MDLINT_SCOPES 后，--staged 的 _in_mdlint_scope 从
首段目录名改为前缀判定——验证 skills 子树入范围、.agents/commands 不误入、
vendor skill 与 archive 冻结豁免。走只读的真实 skills-lock.json 判 vendor，
用临时 fixture 不写真实工作区文件。
（登记对分区测试已随分区实现外置至 test_registration_check.py——构建管线侧文件，不在本仓；元工序配套。）
"""
import importlib.util
import sys
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


class MdlintScopeTests(unittest.TestCase):
    """_in_mdlint_scope 的 B6 扩围口径（--staged 与全量 MDLINT_SCOPES 一致性）。"""

    def test_root_level_md_in_scope(self):
        self.assertTrue(wc._in_mdlint_scope("README.md"))

    def test_skills_tree_in_scope(self):
        self.assertTrue(wc._in_mdlint_scope(".agents/skills/case-troubleshoot/SKILL.md"))
        self.assertTrue(wc._in_mdlint_scope(".agents/skills/knowledge-base/command/x.md"))

    def test_agents_commands_out_of_scope(self):
        """多级 scope 只匹配 skills 子树：.agents/commands 不误入（首段目录名判定的回归防线）。"""
        self.assertFalse(wc._in_mdlint_scope(".agents/commands/anything.md"))
        self.assertFalse(wc._in_mdlint_scope(".agents/other.md"))

    def test_nested_dirs_in_scope(self):
        self.assertTrue(wc._in_mdlint_scope("notes/domain/deep/x.md"))

    def test_non_md_out_of_scope(self):
        self.assertFalse(wc._in_mdlint_scope(".agents/skills/x/SKILL.py"))

    def test_task_archive_frozen_out(self):
        self.assertFalse(wc._in_mdlint_scope("story/archive/feat-x/README.md"))

    def test_active_task_in_scope(self):
        self.assertTrue(wc._in_mdlint_scope("workspace-optimize/task-x/README.md"))

    def test_vendor_skill_exempt(self):
        """vendor skill 随源不检：豁免口径与全量 !{dir}/** 负 glob 一致。"""
        with mock.patch.object(wc, "_vendor_skill_dirs", return_value={".agents/skills/grilling"}):
            self.assertFalse(wc._in_mdlint_scope(".agents/skills/grilling/SKILL.md"))
            self.assertTrue(wc._in_mdlint_scope(".agents/skills/workspace-ops/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
