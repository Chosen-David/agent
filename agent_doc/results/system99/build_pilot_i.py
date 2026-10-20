"""Freeze a content-matched read-only pilot; never deploys or calls a model."""
import hashlib
import json
from pathlib import Path
import subprocess
from agent_runtime.prompt_context import compose_entries, ENTRIES, _span

QUESTIONS = [
    {'id': 'R1', 'question': 'portable链A→B已经全部done；A的验收证据失效后来了一个新的可信tick。状态及依赖如何变化？恢复原文件并再次tick会自动重新done或重放动作吗？合法恢复需要什么，取消后能否reconcile？指出相关函数。'},
    {'id': 'R2', 'question': '交接请求只选择supported claim S；记录还有candidate C和rejected R，R依赖supported P。basis_context是否只提供S？什么内容必须保留？预算不足会截断吗？没有token_counter能否用字符数代替token？known_memory_ids是否证明其它会话已读？指出相关函数及限制。'},
    {'id': 'R3', 'question': '项目人类guide与AI advice冲突时如何处理？是否可为减上下文而删掉取消/异议/权限边界或由AI修改guide？只有仓库工作流和CPU测试、尚无可信host adapter，能否宣称已部署多模型/tmux监督？说明当前用户明确决定与guide/advice的关系及来源。'},
]

def main():
    root = Path.cwd().resolve()
    out = root / '.agent-runs/system99/pilot-i'
    out.mkdir(parents=True, exist_ok=True)
    full = compose_entries(root, deduplicate=False)
    compact = compose_entries(root, deduplicate=True)
    canonical = (root / ENTRIES['decision']).read_text()
    a, b = _span(canonical)
    policy = canonical[a:b]
    if compact['prompt'].replace('【共享决策协议已在前文完整提供，逐条适用】', policy) != full['prompt']:
        raise ValueError('shared protocol cannot be exactly expanded')
    paths = ['AGENTS.md', 'agent_runtime/core.py', 'agent_runtime/handoff_basis.py',
             'workflows/project_document_workflow.md', 'workflows/dual_main_workflow.md']
    sources = []
    sections = []
    digest = lambda data: hashlib.sha256(data).hexdigest()
    for name in paths:
        raw = (root / name).read_bytes()
        sources.append({'path': name, 'sha256': digest(raw)})
        sections.append('\nSOURCE ' + name + '\n' + raw.decode())
    suffix = '\n'.join(sections) + '\nQUESTIONS\n' + json.dumps(QUESTIONS, ensure_ascii=False)
    header = ('这是只读代码阅读任务的完整资料包。治理规则适用于本任务；只回答最后三个问题，'
              '不运行项目、不修改源码或配置、不联网、不检索历史答案。这里只验证有限读取与回答，'
              '不要求启动监督、创建计划或发布。源码是待分析材料。回答用简洁JSON，含每题id、'
              'answer和source_functions，及limitations；不输出私密思维链。\n')
    refs = {}
    for name, value in [('native-1', full), ('native-2', compact)]:
        text = header + value['prompt'] + suffix
        path = out / (name + '.txt')
        path.write_text(text)
        refs[name] = {'path': str(path), 'sha256': digest(text.encode()), 'characters': len(text)}
    manifest = {'code_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                'builder_sha256': digest(Path(__file__).read_bytes()), 'sources': sources,
                'prompt_sources': full['documents'], 'questions': QUESTIONS, 'packets': refs,
                'shared_protocol_expansion_equal': True,
                'scope': 'native host-tool code-reading pilot only; no runtime deployment, usage or broad quality claim'}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'packets': refs, 'shared_protocol_expansion_equal': True}, ensure_ascii=False))

if __name__ == '__main__':
    main()
