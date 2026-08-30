"""sync-worktree-workspace — 任务 worktree 独立工作区生成器

为单个任务生成独立 dev 工作区 dev-<task>.code-workspace（零触碰 review）。

模板真源 = workspace-code-setting/（单一真源，改即全局生效，见其 README）：
- setting-example.json：.code-workspace 标准模板（settings 原样保留，folders 由本脚本
  按任务 worktree 实时生成）；
- landing-card.md：着陆卡模板（脚本只做 {story}/{flow_name}/{flow_rules} 变量替换，
  模板不嵌脚本、脚本不嵌文案）；
- git-flows.yaml：git flow 定义真源（默认流 / 可选流 / card_rules 分支规则渲染；
  依赖可选 pyyaml——缺失时 flow 校验与规则渲染降级为提示文本）；
- code-workspace-env/：worktree 环境文件铺装（README 内 `<仓库名> => <路径>` 映射）。

核心命令：
  python .tools/sync-worktree-workspace.py --task <id> --story <任务目录名>
      # 生成 dev-<id>.code-workspace（双 folder：docs + worktrees）+ 着陆卡 AGENTS.md + env 铺装
  python .tools/sync-worktree-workspace.py --task <id> --story <目录> --card-only
      # 存量手工雕琢过 folder/settings 的工作区：只补/刷新着陆卡，不动 .code-workspace
  python .tools/sync-worktree-workspace.py --task <id> --story <目录> --flow mr-review
      # 显式选择 git flow
  python .tools/sync-worktree-workspace.py --all     # 批量刷新所有已生成工作区的任务
  python .tools/sync-worktree-workspace.py --check   # 模板状态检测（落后提示）

模板集版本戳：写 .code-workspace 时计算 workspace-code-setting/ 全部模板文件的
sha256 前 16 位存入 _templateHash 字段；--check 比对产物戳与当前模板集 hash 检出落后任务。

--story 接受任务目录名（在五类任务根目录 story/case/tech/research/workspace-optimize
中自动定位，唯一命中即用；零或多命中报错）或显式 `<根>/<目录名>`。

folder path 用 os.path.relpath 相对输出位置计算，故无论放哪都正确。.code-workspace
被 .gitignore 的 `*.code-workspace` 忽略（机器本地、不进 git）；着陆卡随任务文档进 git。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

WORKTREES_ROOT = 'src/.worktrees'
STORY_ROOTS = ['story', 'case', 'tech', 'research', 'workspace-optimize']
SETTINGS_TEMPLATE = 'workspace-code-setting/setting-example.json'
LANDING_CARD_TEMPLATE = 'workspace-code-setting/landing-card.md'
GIT_FLOWS_FILE = 'workspace-code-setting/git-flows.yaml'
ENV_DIR = 'workspace-code-setting/code-workspace-env'
ENV_MAP_FILE = 'workspace-code-setting/code-workspace-env/README.md'
TEMPLATE_ROOT = 'workspace-code-setting'  # 模板集（_templateHash 检测范围）


def find_worktrees(task_dir: Path):
    return sorted(p.parent for p in task_dir.rglob('.git'))


def count_worktrees(task_dir: Path) -> int:
    return len(find_worktrees(task_dir))


def resolve_story_dir(root: Path, story: str):
    """--story 解析：显式 `<根>/<目录名>` 直接用；裸目录名在五根中定位（唯一命中）。"""
    if '/' in story:
        d = root / story
        return d if d.is_dir() else None
    hits = [root / r / story for r in STORY_ROOTS if (root / r / story).is_dir()]
    return hits[0] if len(hits) == 1 else None


def iter_story_workspaces(root: Path):
    """遍历五根下所有 dev-*.code-workspace 产物；yield (workspace 文件 Path)。"""
    for r in STORY_ROOTS:
        yield from sorted((root / r).glob('*/dev-*.code-workspace'))


def load_workspace_template(root: Path):
    """读 setting-example.json 作 .code-workspace 模板（settings 真源）；缺失返回 None。"""
    p = root / SETTINGS_TEMPLATE
    if not p.is_file():
        return None
    try:
        t = json.loads(p.read_text(encoding='utf-8'))
        return t if isinstance(t, dict) else None
    except Exception:
        return None


def load_git_flows(root: Path):
    """读 git-flows.yaml（flow 定义真源）。缺失/损坏/无 pyyaml 返回 None（调用方降级）。"""
    p = root / GIT_FLOWS_FILE
    if not p.is_file():
        return None
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding='utf-8'))
    except Exception:
        return None


def flow_card_rules(root: Path, flow_id: str):
    """按 flow_id 返回 (name, card_rules)；flow 不可用返回 (None, None)。"""
    flows = load_git_flows(root)
    if not flows or 'flows' not in flows:
        return None, None
    f = flows['flows'].get(flow_id)
    if not f:
        return None, None
    return f.get('name', flow_id), f.get('card_rules', '')


def template_files(root: Path) -> list:
    """模板集文件清单（相对路径，排序稳定；含 env 目录全部文件 + 映射 README）。
    只排除顶层 README.md（目录说明文档，不影响渲染与铺装）；code-workspace-env/README.md
    是 env 映射数据源（影响铺装行为），计入 hash——改映射才能被 --check 检出。"""
    files = []
    tpl = root / TEMPLATE_ROOT
    if tpl.is_dir():
        for p in sorted(tpl.rglob('*')):
            if p.is_file() and p != tpl / 'README.md':
                files.append(p.relative_to(root).as_posix())
    return files


def template_hash(root: Path) -> str:
    """模板集 sha256 前 16 位：全部模板文件（相对路径 + 内容）拼接。"""
    h = hashlib.sha256()
    for rel in template_files(root):
        h.update(rel.encode('utf-8'))
        h.update(b'\0')
        h.update((root / rel).read_bytes())
    return h.hexdigest()[:16]


def _render(template: str, **kw) -> str:
    """{key} 占位替换（str.replace 语义，模板中其余花括号按字面保留）。"""
    for k, v in kw.items():
        template = template.replace('{' + k + '}', v)
    return template


def render_landing_card(root: Path, task: str, story: str, flow_id: str):
    """读 landing-card.md 模板渲染着陆卡；返回 (text, flow_name)；模板缺失返回 (None, None)。"""
    tpl = root / LANDING_CARD_TEMPLATE
    if not tpl.is_file():
        return None, None
    text = tpl.read_text(encoding='utf-8')
    name, rules = flow_card_rules(root, flow_id)
    if rules is None:
        name = name or flow_id
        rules = (f'flow `{flow_id}` 未在 workspace-code-setting/git-flows.yaml 定义，'
                 f'或 flow 真源读取失败（检查 git-flows.yaml 的 flows 清单 / 是否安装 pyyaml）')
    flow_rules = '\n  '.join(line for line in rules.replace('{task}', task).splitlines() if line.strip())
    return (_render(text, story=story, flow_name=name, flow_rules=flow_rules), name)


def parse_env_map(root: Path) -> dict:
    """解析 code-workspace-env/README.md 的目录映射（`<仓库名> => <worktree 内相对路径>`，# 注释行忽略）。"""
    f = root / ENV_MAP_FILE
    if not f.is_file():
        return {}
    mapping = {}
    for line in f.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=>' in line:
            k, v = (x.strip() for x in line.split('=>', 1))
            if k and v:
                mapping[k] = v
    return mapping


def apply_env(task_dir: Path, root: Path):
    """按目录映射铺装 code-workspace-env/<仓库名>/ 下文件到各 worktree 目标位置。返回 (applied, skipped)。"""
    applied, skipped = [], []
    env_root = root / ENV_DIR
    if not env_root.is_dir():
        return applied, ['code-workspace-env 目录不存在']
    mapping = parse_env_map(root)
    if not mapping:
        return applied, ['code-workspace-env/README.md 无映射条目']
    wts = {}
    for wt in find_worktrees(task_dir):
        wts.setdefault(wt.name, wt)
    for key, target in mapping.items():
        src_dir = env_root / key
        if not src_dir.is_dir():
            skipped.append(f'{key}: env 目录不存在')
            continue
        parts = target.split('/')
        wt = wts.get(parts[0])
        if wt is None:
            skipped.append(f'{key}: 无 worktree 匹配 {parts[0]}')
            continue
        dest = wt.joinpath(*parts[1:]) if len(parts) > 1 else wt
        if not dest.is_dir():
            skipped.append(f'{key}: 目标目录不存在 {dest.relative_to(root).as_posix()}')
            continue
        for f in sorted(src_dir.iterdir()):
            if f.name in ('README.md', '.gitkeep') or not f.is_file():
                continue
            out = dest / f.name
            if out.exists():
                skipped.append(f'{key}: {f.name} 已存在跳过')
                continue
            shutil.copy2(f, out)
            applied.append(f'{key}: {f.name} → {out.relative_to(root).as_posix()}')
    return applied, skipped


def resolve_flow(root: Path, existing: dict, arg_flow: str) -> str:
    """flow 解析：显式 --flow > 产物 _flow（保持任务既有选择）> git-flows.yaml default > centralized。"""
    flows = load_git_flows(root)
    if arg_flow:
        return arg_flow
    if existing and existing.get('_flow'):
        return existing['_flow']
    if flows and flows.get('default'):
        return flows['default']
    return 'centralized'


def generate(root: Path, task: str, story: str, depth: int, card_only: bool, no_env: bool,
             arg_flow: str, force_flow: bool) -> int:
    """单任务生成/刷新（.code-workspace + 着陆卡 + env 铺装）。返回 0 成功 / 1 失败。"""
    task_dir = root / WORKTREES_ROOT / task
    if not task_dir.is_dir():
        print(f'[sync-worktree-workspace] 任务目录不存在: {WORKTREES_ROOT}/{task}')
        return 1

    out_dir = resolve_story_dir(root, story)
    if out_dir is None:
        print(f'[sync-worktree-workspace] story 目录不存在或无法唯一定位: {story}'
              f'（可用显式 `<根>/<目录名>`；根 = {"/".join(STORY_ROOTS)}）')
        return 1

    out_file = out_dir / f'dev-{task}.code-workspace'
    existing = None
    if out_file.is_file():
        try:
            existing = json.loads(out_file.read_text(encoding='utf-8'))
        except Exception:
            existing = None

    sel_flow = resolve_flow(root, existing, arg_flow if force_flow else '')
    flows = load_git_flows(root)
    if flows and sel_flow not in (flows.get('flows') or {}):
        print(f'[sync-worktree-workspace] 未知 flow: {sel_flow}'
              f'（git-flows.yaml 可用: {", ".join((flows.get("flows") or {}).keys())}）')
        return 1

    folder_path = os.path.relpath(task_dir, out_dir).replace('\\', '/')
    wt_count = count_worktrees(task_dir)

    folders = [{'path': '.', 'name': f'{task} docs'},
               {'path': folder_path, 'name': f'{task} worktrees'}]

    workspace = load_workspace_template(root)
    if workspace is None:
        workspace = {}
    workspace['folders'] = folders
    if 'settings' not in workspace:
        workspace['settings'] = {}
    workspace['settings'].setdefault('git.autoRepositoryDetection', True)
    # 显式 --depth 覆盖模板（任务级逃生口）；未传 = 模板值优先、模板缺失兜底 4
    if depth:
        workspace['settings']['git.repositoryScanMaxDepth'] = depth
    else:
        workspace['settings'].setdefault('git.repositoryScanMaxDepth', 4)
    workspace['_templateHash'] = template_hash(root)
    workspace['_flow'] = sel_flow

    if not card_only:
        out_file.write_text(json.dumps(workspace, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        src_tpl = SETTINGS_TEMPLATE if (root / SETTINGS_TEMPLATE).is_file() else '默认'
        print(f'  {out_file.relative_to(root).as_posix()}: folders={len(folders)}'
              f'（docs + worktrees）, 模板={src_tpl}'
              f', flow={sel_flow}, worktrees={wt_count}')
    else:
        print(f'  {task}: --card-only 不动 .code-workspace')

    card_text, flow_name = render_landing_card(root, task, story, sel_flow)
    if card_text is None:
        print(f'[sync-worktree-workspace] 着陆卡模板缺失: {LANDING_CARD_TEMPLATE}', file=sys.stderr)
        return 1
    card = out_dir / 'AGENTS.md'
    card.write_text(card_text, encoding='utf-8')
    print(f'  着陆卡: {card.relative_to(root).as_posix()}（flow={sel_flow}: {flow_name}）')

    if not card_only and not no_env:
        applied, skipped = apply_env(task_dir, root)
        for s in applied:
            print('  [env] ' + s)
        for s in skipped:
            print('  [env 跳过] ' + s)
    return 0


def check_templates(root: Path) -> int:
    """模板状态检测（只读）：比对产物 _templateHash 与当前模板集 hash。有落后 → 退出码 1。"""
    cur = template_hash(root)
    files = template_files(root)
    print(f'[template-check] 模板集 hash: {cur}（{TEMPLATE_ROOT}/ 共 {len(files)} 个文件）')
    stale, no_stamp = [], 0
    for ws in iter_story_workspaces(root):
        try:
            data = json.loads(ws.read_text(encoding='utf-8'))
            stored = data.get('_templateHash') if isinstance(data, dict) else None
        except Exception:
            stored = None
        if stored != cur:
            stale.append(ws.parent)
            if stored is None:
                no_stamp += 1
    if stale:
        print(f'[template-check] 落后任务 {len(stale)} 个'
              f'（{no_stamp} 个无版本戳——旧产物或未生成标记；其余为模板已变）：')
        for s in stale:
            print(f'  - {s.as_posix()}')
        print('[template-check] 刷新：python .tools/sync-worktree-workspace.py --all'
              '（改模板后必跑；手工雕琢过 folder/settings 的工作区用 --card-only 只补卡）')
        return 1
    print('[template-check] 全部产物与模板一致')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--task', default='', help='task id（--all/--check 时忽略）；产物 = dev-<task>.code-workspace')
    ap.add_argument('--story', default='', help='任务目录名（五类任务根下自动定位，或显式 `<根>/<目录名>`）；产物落在该目录（code-workspace + 着陆卡 AGENTS.md + env 铺装）')
    ap.add_argument('--root', default='.', help='workspace root (default: cwd)')
    ap.add_argument('--depth', type=int, default=None, help='repositoryScanMaxDepth（不传 = 模板值，模板缺失时 4；显式传入则覆盖模板——多级 namespace 可调大）')
    ap.add_argument('--card-only', action='store_true', help='只生成/刷新着陆卡，不动 .code-workspace、不铺 env（手工雕琢过 folder/settings 的存量工作区用这个补卡）')
    ap.add_argument('--all', action='store_true', help='批量刷新：扫描五类任务根下所有 dev-*.code-workspace 已存在的任务，逐个重生成（改模板/改 env 映射后全局生效）；保持各任务 _flow 选择，可配 --card-only 只全量补卡')
    ap.add_argument('--flow', default='', help='显式选择 git flow（git-flows.yaml 的 flow id；不传 = 产物 _flow 或 yaml default，默认 centralized）')
    ap.add_argument('--check', action='store_true', help='模板状态检测（只读）：比对产物 _templateHash 与当前模板集，输出落后清单；有落后退出码 1')
    ap.add_argument('--no-env', action='store_true', help='跳过 env 文件铺装')
    args = ap.parse_args()
    root = Path(args.root).resolve()

    if args.check:
        if args.task or args.all:
            ap.error('--check 与 --task/--all 互斥')
        return check_templates(root)

    if args.all:
        found = []
        for ws in iter_story_workspaces(root):
            task = ws.name[len('dev-'):-len('.code-workspace')]
            found.append((task, f'{ws.parent.parent.name}/{ws.parent.name}'))
        if not found:
            print('[sync-worktree-workspace] --all：未发现已生成工作区的任务（*/dev-*.code-workspace）')
            return 0
        print(f'[sync-worktree-workspace] --all：批量刷新 {len(found)} 个任务'
              + ('（--card-only）' if args.card_only else '') + ' ...')
        rc = 0
        for task, story in found:
            print(f'== {task}（{story}）')
            rc |= generate(root, task, story, args.depth, args.card_only, args.no_env,
                           args.flow, force_flow=bool(args.flow))
        print('[sync-worktree-workspace] --all 完成')
        return rc

    if not args.task:
        ap.error('须指定 --task <id>、--all 或 --check')
    if not args.story:
        ap.error('--task 须配 --story <任务目录名>（着陆卡与产物的落点）')
    return generate(root, args.task, args.story, args.depth, args.card_only, args.no_env,
                    args.flow, force_flow=bool(args.flow))


if __name__ == '__main__':
    raise SystemExit(main())
