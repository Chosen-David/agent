# 固定上游源码阅读与适配取舍

日期 2026-10-06；本库基线 `cb3e133ded7f2c878b3eddb10a0e7876fe6cac2b`。只研究源码，没有安装、调用外部 runtime 或修改宿主配置。

| 固定来源与实际阅读 | 入口 → 依赖 → 输出/验收 | 取舍 |
|---|---|---|
| [Anthropic skill-creator/SKILL.md](https://github.com/anthropics/skills/blob/683bc88e56f3e09ba94f7055977f3d3aa499f202/skills/skill-creator/SKILL.md)，commit 日期 2026-10-05；实际读渐进加载、测试/基线、改进、盲评及 description 优化章节，未宣称逐字读全部文件 | 元数据 → Skill 正文 → 按需资源；实际任务产物与独立评分，再比较有/无 Skill | 本库已具备渐进加载和独立产物验收，保留单一规范与现有 pipeline；没有证据支持追加一套重复组织规则 |
| 同 commit [scripts/run_eval.py](https://github.com/anthropics/skills/blob/683bc88e56f3e09ba94f7055977f3d3aa499f202/skills/skill-creator/scripts/run_eval.py) 与 [scripts/utils.py](https://github.com/anthropics/skills/blob/683bc88e56f3e09ba94f7055977f3d3aa499f202/skills/skill-creator/scripts/utils.py)，两文件全文读取 | `parse_skill_md` → 临时 Claude command → `claude -p` 流事件 → 首次 Skill/Read 判断 → 触发比例。不是完整任务正确性评测 | 拒绝照搬：宿主未提供 Claude CLI；首个其他工具事件可结束为未触发；异常算 false 会让负例误报通过。复用本库实际执行/日志/产物门禁，分别报告触发与任务成功 |
| [verification-before-completion/SKILL.md](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/verification-before-completion/SKILL.md)，commit 日期 2026-09-25，全文读取 | 明确待证明的完成声明 → 真正执行验收命令 → 读完整结果 → 据证据报告；无依赖脚本 | 证据优先已在本库；拒绝无变化时反复跑完整测试或用下级自报替代产物验收。按变更影响执行必要检查 |

固定来源经连接的 GitHub 接口读取；不将全文复制到本库。Skill 组织本轮保持 14 个已注册角色、通用主AI路由、科研/旅行/代码阅读及 Claude marketplace 接入。校验器是共享交接验收链中的工具，本轮精修其资源开销，不新增角色或平行评测体系。

后续可测组织候选：先统计真实载入的重复文件与硬约束遗漏，再决定是否缩小镜像；先测有效记忆筛选，再引入检索索引。论文建议不自动成为 Prompt 或可信经验。
