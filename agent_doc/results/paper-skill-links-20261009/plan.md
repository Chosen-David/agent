# [PAPER-LINK-20261009-01] 论文技能章节链接兼容修复

Task-ID: PAPER-LINK-20261009-01
Date: 2026-10-09

## Plan

修复4356730811a4fa603de4d610089b56946bdc9cbd加入的七处本地文件章节锚点：现有catalog契约直接Path.is_file，导致合法网页片段被当文件名。仅将七个SKILL.md链接改为真实文件路径，紧邻文本指明§9（evidence-to-contribution），保留全面取证/贡献导向及只加载对应节的触发语义。不改测试、runtime、guide、SGLang或知识候选。分支fix/paper-skill-section-links-20261009位于独立干净worktree，同步起点7c2449ed16f979ca9f59579651f8f9d022525c02。

验收DAG：实际入口/历史失败核查 → 独立计划审核 → 七处最小文档修改 → catalog、同步/check、角色路径/链接/镜像与两组完整unittest → 独立实际diff/代码/日志/语义审核 → 再fetch并整合复测 → 只暂存七技能文档和本任务证据，非force push main → 读回远端SHA/内容与CI。未提供真实运行监督后端，不声称部署tmux或后台监控。CI不可见单独保留未知，不写成功。知识候选继续未发布，不进入本提交。
