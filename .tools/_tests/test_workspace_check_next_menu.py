#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_workspace_check_next_menu.py — feat next 受控菜单 token 级校验（NEXT_MENU）回归测试

背景：feat 各态 next 取值
按 feat-plan-research SKILL「next/blocker 约定」菜单枚举校验——越界取值/裸冒号视同
next 未明确报 error。验证：合法无参与带参 token 过 / 越界与裸冒号报 / 带参 token
错配报 / 已完成与非 story 类型不查。用临时 fixture 写 CURRENT，不写真实工作区文件
（states 真源只读真实 skill frontmatter）。
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


def _current(status, next_val):
    """构造最小合法 CURRENT.md（feat 五态均在 skill states 集内）。"""
    return (
        "---\n"
        f"status: {status}\n"
        f"next: {next_val}\n"
        "blocker: 无\n"
        "updated-at: 2026-08-29\n"
        "sprint-version: 20260827\n"
        "---\n\n# 当前进度\n\n- x\n"
    )


class NextMenuTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self._orig_root = wc.ROOT
        wc.ROOT = self.root
        # states 真源下放：--task 校验链从真实 skill frontmatter 读 feat states——
        # fixture 根下无 skill，monkey-patch load_states 返回 feat 状态集
        self._orig_load = wc.load_states
        wc.load_states = lambda t: {
            "story": ["进行中", "编码中", "审核中", "验证中", "已完成"],
            "workspace-optimize": ["进行中", "已完成"],
        }.get(t) or self._orig_load(t)
        self.task = self.root / "story" / "feat-x"
        self.task.mkdir(parents=True)
        self.cur = self.task / "CURRENT.md"

    def tearDown(self):
        wc.ROOT = self._orig_root
        wc.load_states = self._orig_load
        self.tmp.cleanup()

    def _check(self):
        errors, warnings = [], []
        wc.check_task_current(self.task, "story/feat-x", errors, warnings)
        return errors

    def test_fixed_token_passes(self):
        """无参 token（本态菜单内）→ 过（首态与末态各取一个代表，两段断言防覆盖）。"""
        self.cur.write_text(_current("进行中", "待开工"), encoding="utf-8")
        self.assertEqual(self._check(), [])
        self.cur.write_text(_current("审核中", "待人类审核"), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_param_token_passes(self):
        """带参 token + 非空参数 → 过（跨态同名 token 实施中/验证中）。"""
        self.cur.write_text(_current("编码中", "实施中:登录模块开发"), encoding="utf-8")
        self.assertEqual(self._check(), [])
        self.cur.write_text(_current("验证中", "验证中:导出功能"), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_fullwidth_colon_accepted(self):
        """全角冒号（中文输入习惯）→ 宽容按半角统一判。"""
        self.cur.write_text(_current("编码中", "实施中：登录模块开发"), encoding="utf-8")
        self.assertEqual(self._check(), [])

    def test_out_of_menu_reported(self):
        """越界取值（他态 token / 自由文本）→ error 视同 next 未明确。"""
        self.cur.write_text(_current("进行中", "待人类审核"), encoding="utf-8")  # 他态 token
        errs = self._check()
        self.assertEqual(len(errs), 1)
        self.assertIn("next 越界", errs[0])
        self.assertIn("待人类审核", errs[0])
        self.cur.write_text(_current("编码中", "继续开发"), encoding="utf-8")  # 自由文本
        self.assertIn("next 越界", self._check()[0])

    def test_bare_colon_reported(self):
        """带参 token 裸冒号（参数空）→ error（SKILL：裸冒号 = next 未明确）。"""
        self.cur.write_text(_current("编码中", "实施中:"), encoding="utf-8")
        errs = self._check()
        self.assertEqual(len(errs), 1)
        self.assertIn("next 越界", errs[0])
        self.cur.write_text(_current("编码中", "实施中:   "), encoding="utf-8")  # 空白参数同拒
        self.assertIn("next 越界", self._check()[0])

    def test_param_token_mismatch_reported(self):
        """无参 token 挂参数（待开工:x）→ error（带参仅限 param 集）。"""
        self.cur.write_text(_current("进行中", "待开工:调研"), encoding="utf-8")
        self.assertIn("next 越界", self._check()[0])

    def test_done_not_checked(self):
        """已完成态不入 NEXT_MENU（next 必无由 per-status 规则覆盖，不重复查）。"""
        self.cur.write_text(
            "---\nstatus: 已完成\nnext: 无\nblocker: 无\nupdated-at: 2026-08-29\nsprint-version: 20260827\n---\n\n# 当前进度\n\n- x\n",
            encoding="utf-8",
        )
        errs = [e for e in self._check() if "next 越界" in e]
        self.assertEqual(errs, [])

    def test_non_story_not_checked(self):
        """非 story 类型（workspace-optimize）next 自由文本 → 不做菜单校验。"""
        wo = self.root / "workspace-optimize" / "task-x"
        wo.mkdir(parents=True)
        (wo / "CURRENT.md").write_text(_current("进行中", "自由格式下一步"), encoding="utf-8")
        errors, warnings = [], []
        wc.check_task_current(wo, "workspace-optimize/task-x", errors, warnings)
        self.assertEqual([e for e in errors if "next 越界" in e], [])


if __name__ == "__main__":
    unittest.main()
