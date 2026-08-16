# load-env.ps1 — 把 .env / .env.local 的变量设到当前 PowerShell 会话。
#
# 用法：. .\.tools\env\load-env.ps1
# 之后即可在命令里用 $env:KEY 展开，明文仅在展开瞬间于内存，不回显。
#
# 安全：逐行解析 KEY=value（不执行文件内容），只设环境变量，不打印 value。
# 优先级：先 .env（占位符/默认），后 .env.local（真实，覆盖）；空值跳过不覆盖。
$dq = [char]34   # "
$sq = [char]39   # '
foreach ($f in @('.env', '.env.local')) {
    if (Test-Path -LiteralPath $f) {
        foreach ($raw in (Get-Content -LiteralPath $f)) {
            $line = "$raw".Trim()
            if (-not $line) { continue }
            if ($line.StartsWith('#')) { continue }
            if (-not $line.Contains('=')) { continue }
            $idx = $line.IndexOf('=')
            $k = $line.Substring(0, $idx).Trim()
            if ($k.StartsWith('export ')) { $k = $k.Substring(7).Trim() }
            $v = $line.Substring($idx + 1).Trim()
            if ($v.Length -ge 2 -and $v[0] -eq $v[-1] -and ($v[0] -eq $dq -or $v[0] -eq $sq)) {
                $v = $v.Substring(1, $v.Length - 2)
            }
            if ($k -and $v) { Set-Item -Path "Env:$k" -Value $v }
        }
    }
}
Remove-Variable -Name dq, sq, f, raw, line, idx, k, v -ErrorAction SilentlyContinue
