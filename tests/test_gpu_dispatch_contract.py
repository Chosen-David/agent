"""gpu-experiment-dispatch 危险进程操作与源身份硬规则的文本契约。

来源：2026-10-11 用户指令 + E125 停车双重事故（pkill -f 跨臂误伤 +
ssh 会话自杀）。这些断言只锁「可 grep 的硬规则与事故要素」确实在
SKILL/作战手册/工作流/rubric 里存在，不运行 GPU、不验证行为。
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / 'plugins/research-assistant/skills/gpu-experiment-dispatch'


def read(path):
    return path.read_text(encoding='utf-8')


class GpuDispatchHardRuleTests(unittest.TestCase):
    def test_skill_declares_process_and_identity_rules(self):
        text = read(SKILL_DIR / 'SKILL.md')
        # 危险进程操作：模糊模式禁令 + 精确 PID 三步 + 三验证。
        for token in (
            'NEVER 用 `pkill -f`/`pgrep -f` 模糊模式杀并行作业',
            'NEVER 让远程 ssh 命令字符串包含 pkill 模式',
            'MUST 精确 PID 三步',
            '先 kill 父 shell（防接力下一任务）→ 再 kill python',
            'kill 后 MUST 三验证（显存释放、残留进程清点、partial 输出盘点）',
            'pkill -9 -f \'tail -2\'',
        ):
            self.assertIn(token, text, f'SKILL.md 缺危险进程操作硬规则: {token}')
        # 源身份：git commit SHA 首选 + 派单前核对 + stash/pull 纪律。
        for token in (
            '源身份 = git commit SHA（首选）',
            'git fetch && git log -1',
            'git stash -u && git pull --rebase && git stash pop',
        ):
            self.assertIn(token, text, f'SKILL.md 缺源身份口径: {token}')
        # 共享契约段落不得被本次升级破坏。
        for token in ('references/result_reuse_workflow.md', 'agent_doc/results/',
                      'verify_experiment_result', 'usable-with-scope'):
            self.assertIn(token, text, f'SKILL.md 共享契约段被破坏: {token}')

    def test_playbook_records_e125_incident_and_rules(self):
        text = read(SKILL_DIR / 'references/dispatch_playbook.md')
        # 事故完整叙述要素：模糊模式误伤、自杀陷阱、恢复、正确做法。
        for token in (
            "pkill -9 -f 'tail -2'",
            'SIGPIPE', 'BrokenPipeError',
            'ssh host "pkill -9 -f \'tail -2\'"',
            'exit 255', '误以为节点失联',
            '先 kill 父 shell（防其捕获 rc≠0 后接力',
        ):
            self.assertIn(token, text, f'作战手册缺事故要素: {token}')
        # 硬规则（MUST/NEVER 可 grep）。
        for token in (
            'NEVER 用 `pkill -f` / `pgrep -f` 模糊模式杀并行作业',
            'NEVER 让远程 ssh 命令字符串包含将传给 pkill 的模式',
            'MUST 停车三步精确 PID',
            'MUST kill 后三验证',
            'MUST 多臂并行停车前先 ps 全量核对各 PID 归属',
        ):
            self.assertIn(token, text, f'作战手册缺硬规则: {token}')
        # 与既有协议衔接：隔离惯例 + SKIP 幂等重派 + 任务文档记录。
        for token in ('quarantine', 'SKIP 幂等重派', 'Progress 段'):
            self.assertIn(token, text, f'作战手册缺协议衔接: {token}')
        # 源身份 git 通道：SHA 首选 + 派单前核对 + 兼容路径不混标。
        for token in (
            'git commit SHA（首选）',
            'git fetch && git log -1',
            'rsync + md5 保留为兼容路径',
            '两种口径不混标',
        ):
            self.assertIn(token, text, f'作战手册缺源身份口径: {token}')

    def test_workflow_and_execution_wire_the_new_disciplines(self):
        workflow = read(ROOT / 'workflows/gpu_dispatch_workflow.md')
        for token in ('git commit SHA（首选）', 'git fetch && git log -1',
                      '严禁 `pkill -f`', '先 kill 父 shell 防接力、再 kill python',
                      'SKIP 幂等重派补跑'):
            self.assertIn(token, workflow, f'workflow 缺新纪律接线: {token}')
        execution = read(SKILL_DIR / 'references/execution.md')
        for token in ('commit SHA', '精确\n   PID 三步', '严禁 pkill -f 模糊'):
            self.assertIn(token, execution, f'execution.md 缺新纪律接线: {token}')

    def test_rubric_covers_process_ops_and_git_identity(self):
        rubric = json.loads((ROOT / 'evals/rubric.json').read_text())['criteria']
        criteria = rubric['gpu-experiment-dispatch']
        joined = '\n'.join(criteria)
        for token in ('精确 PID 三步', 'pkill -f/pgrep -f 模糊模式', '会话自杀陷阱',
                      '三验证', 'SKIP 幂等重派补跑', 'git commit SHA',
                      'rsync+md5 作为兼容路径'):
            self.assertIn(token, joined, f'rubric 缺新评判标准: {token}')
        # 既有关键标准不被替换。
        for token in ('best-file 口径', '点火验证含进程数、显存、log tail'):
            self.assertIn(token, joined, f'rubric 既有标准被破坏: {token}')


if __name__ == '__main__':
    unittest.main()
