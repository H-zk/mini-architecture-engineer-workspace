#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_env_loader.py — .env / .env.local 零依赖共享加载器（脚本侧）。

单一真源：.env.local（gitignored，真实密钥）覆盖 .env（可提交，占位符/默认值）。
优先级：os.environ 已有非空值 > .env.local > .env。

定位：仅供 .tools 下脚本 import（脚本加载，agent 不参与，见 AGENTS.md 红线）。
安全：本模块不打印任何 value——只加载到 os.environ / 返回 dict，防泄密。
     （若上层把 value 打印出来，是调用方违规，不在此模块处理。）
解析约定：兼容 `export KEY=value`（剥离 export 前缀）；值首尾匹配的一对 ' 或 " 去一层；
     不处理行内注释（值里的 # 是值的一部分，无需引号包裹——与 python-dotenv 不同）。

依赖：仅 Python 标准库。
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 工作区根
_DEFAULT_FILES = (".env.local", ".env")
_cache = {}


def _strip_quotes(v):
    """去首尾匹配的一对引号（' 或 "）。仅当首尾是同一种引号时去一层（非 strip 全部），
    语义对齐 python-dotenv：`"'abc'"` → `'abc'`（值带单引号），`"abc"` → `abc`。"""
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def _parse_file(path):
    """解析单个 env 文件为 dict（去注释/空行/引号，剥离 export 前缀）。结果按路径缓存。"""
    key = str(path)
    if key in _cache:
        return _cache[key]
    d = {}
    if path.is_file():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k.startswith("export "):   # 兼容 bash 风格 `export KEY=value`
                k = k[7:].strip()
            d[k] = _strip_quotes(v.strip())
    _cache[key] = d
    return d


def _merged(files=_DEFAULT_FILES):
    """合并 files 为 dict，优先级与 get() 完全一致（os.environ 非空 > files 中首个非空）。

    空值不覆盖非空值——.env 的空占位不会顶掉 .env.local 的真值，与文档
    「.env.local 覆盖 .env」一致。load_into_environ/as_dict 经此获得正确优先级。
    """
    keys = set()
    for fname in files:
        keys |= _parse_file(ROOT / fname).keys()
    return {k: get(k, "", files) for k in keys}


def get(key, default=None, files=_DEFAULT_FILES):
    """读单个值。优先级：os.environ 非空 > files（默认 .env.local 覆盖 .env）。

    files=(".env.local",) 可限定只读 .env.local（如个人确认标志，避免 .env 污染）。
    """
    v = os.environ.get(key)
    if v:
        return v
    for fname in files:
        v = _parse_file(ROOT / fname).get(key)
        if v:
            return v
    return default


def require(key, files=_DEFAULT_FILES):
    """同 get，但读不到非空值时 sys.exit(1)（只提示缺哪个 key，不泄露任何 value）。"""
    v = get(key, None, files)
    if not v:
        src = " / ".join(files)
        print(f"ERR: 未在 os.environ 或 {src} 找到 {key}", file=sys.stderr)
        sys.exit(1)
    return v


def load_into_environ(override=False, files=_DEFAULT_FILES):
    """合并 files 到 os.environ。

    override=False（默认）：用 setdefault，不覆盖进程已有的环境变量。
    override=True：覆盖（重新加载刷新值）。
    """
    for k, v in _merged(files).items():
        if override:
            os.environ[k] = v
        else:
            os.environ.setdefault(k, v)


def as_dict(files=_DEFAULT_FILES):
    """返回合并后的 {KEY: value} dict（不含 os.environ）。"""
    return dict(_merged(files))
