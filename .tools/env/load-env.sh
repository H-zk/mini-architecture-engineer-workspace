#!/usr/bin/env bash
# load-env.sh — 把 .env / .env.local 的变量 export 到当前 bash 会话。
#
# 用法：source .tools/env/load-env.sh   （或 . .tools/env/load-env.sh）
# 之后即可在命令里用 $KEY 展开，明文仅在展开瞬间于内存，不回显。
#
# 安全：逐行解析 KEY=value（不 source 执行文件内容），只 export 变量，不打印 value；
#       值含 ) ` $ 等特殊字符也不报错——比 `set -a; . file` 更健壮、更安全。
# 优先级：先 .env（占位符/默认），后 .env.local（真实，覆盖）；空值跳过不覆盖。
_env_load_file() {
    [ -f "$1" ] || return 0
    while IFS= read -r _line || [ -n "$_line" ]; do
        _line="${_line#"${_line%%[![:space:]]*}"}"   # 去前导空白
        [ -z "$_line" ] && continue
        [[ "$_line" == \#* ]] && continue
        [[ "$_line" != *=* ]] && continue
        _k="${_line%%=*}"
        _k="${_k#export }"            # 兼容 bash 风格 export KEY=value
        _v="${_line#*=}"
        _v="${_v#\"}"; _v="${_v%\"}"   # 去首尾双引号
        _v="${_v#\'}"; _v="${_v%\'}"   # 去首尾单引号
        [ -n "$_k" ] && [ -n "$_v" ] && export "$_k=$_v"
    done < "$1"
}
_env_load_file .env
_env_load_file .env.local
unset -f _env_load_file
unset _line _k _v 2>/dev/null
