# [COH-T26] 纳入2026-10-06 21:33新增要求：经典图仅作基础回归；在同一批次补充近期CCF A会议及期刊复杂架构真实生成测试，核验正式发表与原文版本、关键结构和最终视觉效果，独立验收及图文交接通过后才发布。初选CVPR2026、ICML2026、TPAMI2026各一例；维护跨场所轮换覆盖，不把三个样本说成所有CCF A论文覆盖。

Task-ID: COH-T26
Date: 2026-10-06

## Plan

纳入2026-10-06 21:33新增要求：经典图仅作基础回归；在同一批次补充近期CCF A会议及期刊复杂架构真实生成测试，核验正式发表与原文版本、关键结构和最终视觉效果，独立验收及图文交接通过后才发布。初选CVPR2026、ICML2026、TPAMI2026各一例；维护跨场所轮换覆盖，不把三个样本说成所有CCF A论文覆盖。

## Progress

### Preserved implementation and evidence

- [x] [COH-T26] 纳入2026-10-06 21:33新增要求：经典图仅作基础回归；在同一批次补充近期CCF A会议及期刊复杂架构真实生成测试，核验正式发表与原文版本、关键结构和最终视觉效果，独立验收及图文交接通过后才发布。初选CVPR2026、ICML2026、TPAMI2026各一例；维护跨场所轮换覆盖，不把三个样本说成所有CCF A论文覆盖。

T24验收：三个真实CPU研究输入生成完整工作论文，3/3通过24/24独立科学标准；作者、独立审稿、独立读者和主AI均实际读完各最终PDF，共19物理页。所有原始数据、负结果和稿件保留；归档解包637文件哈希无误并重验3/3。未复现足以支持新增写作Prompt的通用缺陷，冻结不改Skill后才解封第三篇；模型A/B不确定，不等于投稿就绪。证据：`docs/continuous_optimization/rounds/2026-10-06-eval-coherence/evidence/writing/report.md`。COH-T21发布与COH-T23实际发布状态核验仍待完成。

并发整合说明：本批旧检查点在 e8ee3dc 上使用 T19–T26；远端知识库批次已占用 T19–T23。为保留双方任务语义，本批活动ID显式迁移为 COH-T19–COH-T26，旧冻结证据保留原文并按本映射解析；不把知识库的 T22/T23 记为本批完成。映射与快照见本批 evidence/concurrent-integration.json。

COH-T26验收：2026年AutoGaze（CVPR）、DOUBT（ICML）和DiTFuse（TPAMI）最终3/3，科学24/24、视觉12/12；首轮2/3，保留DiTFuse图例缺失及修复。DOUBT执行者未见原图；实际三图→写作→独立读者交接6/6，6页PDF全部查看，3份嵌入矢量内容与原产物相同，异址重建像素/文本一致。仅为三个现代样本，不声称覆盖全部CCF A或复现原模型性能。证据：`docs/continuous_optimization/rounds/2026-10-06-eval-coherence/evidence/w4-modern-architecture/diagram-results.md`及`handoff-results.md`。本批仍未发布，不计已完成一轮。

### Historical context

Original task: [line 190](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L190).
Shared methods, results and evidence: [source section, lines 178–205](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L178-L205).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
