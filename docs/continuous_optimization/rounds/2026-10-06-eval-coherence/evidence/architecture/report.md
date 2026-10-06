# 真实论文架构图与图文交接验收 — 2026-10-06

对应 TASK T25；T20 十篇研究综合已完成，T24 完整论文写作升级、T21 最终候选发布验收尚未完成。基线 `e8ee3dca5dc8cd076fc031dd4510dabde214e046`。本次未修改图表或写作 Skill：先实测现有能力，未发现值得新增提示词的共性缺陷。

## 实际结果

| 原始论文与版本 | 真实生成任务 | 独立检查 | 最终尺寸 / 最小字号 |
| --- | --- | --- | --- |
| [Attention Is All You Need](https://papers.nips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf), NIPS 2017 Figure 1 | 从固定方法说明生成完整原始 post-norm 编解码架构 | 6/6，通过；检查 Q/K/V、五个残差归一化、因果掩码和输出头 | 180 mm / 8.5 pt |
| [Deep Residual Learning for Image Recognition](https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf), CVPR 2016 Figures 2/5 | basic 与 bottleneck 同形状 identity 残差块 | 6/6，通过；检查通道、卷积顺序、独立相加及相加后的 ReLU | 85 mm / 8 pt |
| [U-Net: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/pdf/1505.04597v1), MICCAI 2015 对应 v1 原始方法 | 四级 valid-convolution 编解码架构，保留输入输出尺寸和全部裁剪拼接 | 6/6，通过；检查四条 skip、通道、裁剪尺寸及 concat | 180 mm / 8.0037 pt |

审查者实际打开原图、最终彩色/灰度/页面图，核对连接端点、布局和可读性；隔离复建的 SVG 和比较 PNG 完全一致。主执行者另行查看全部三张原图和最终彩色及页面图。生成者只收到方法说明，未收到原图和评分答案；共享文件系统使用指令隔离，不是安全沙箱，也无法排除模型预训练知晓经典架构。

随后实际将三位生成者的冻结产物交给独立写作 Agent，生成 597 词正文加图注范围内的比较性方法节和四页 PDF，再交给独立最终读者。四项预定验收全部通过：15 个输入 hash 一致、三张图未修改、科学解释与图注一致、全部四页实际审读且无阻塞问题。独立两次 pdflatex 编译成功，四页渲染像素一致。主执行者也查看了全部四页。

这是一篇有来源的比较性方法短文，不是完整原创科研论文、研究复现或顶会录用质量证明。原始论文只做架构相关选择性阅读，不计入本批十篇 Agent 优化全文精读。

## 五类验证与边界

| 类型 | 证据和结论 |
| --- | --- |
| 程序测试 | 本次图表合同测试 14/14；w2 保留运行时 367 通过、8 跳过，为历史证据，本次未改其实现 |
| 真实角色任务 | 三个独立图表生成任务 3/3，实际写作任务 1/1；源码/来源阅读和独立审查另有记录。未执行最终发布候选全部 14 角色任务 |
| 跨角色交接 | 来源阅读→图表生成→独立图表审查→真实写作→独立逐页阅读，交接 4/4 |
| 旧新版 A/B | 未运行，inconclusive；Skill 未改、准确模型快照和 seed 不可观察，无效果提升或加速声明 |
| 外部集成 | 宿主 Agent 和已安装的 Inkscape/LaTeX 实际执行；无用户服务器 tmux 或外部模型 backend 集成验证 |

保留失败：首个准备目录错误地将 reviewer-only sources.json 纳入执行者输入，两个准备上下文在产物写入前停止；重新冻结 method-only 输入并用三个全新上下文执行。生成者在同一提交尝试内修正了 ResNet 页面说明溢出、U-Net pooling 标签重叠、Transformer 标题/连接和字体问题，早期图和说明保留。因此 3/3 是首个正式收集提交通过，不是原始首稿成功率。正式多尝试 correct-to-wrong/wrong-to-correct 均为 0；内部布局修正不冒充独立评分的科学推理恢复。Transformer 一处可选 2 pt 间距优化不影响验收。

真实模型/seed、完整工具事件流、tokens 和费用未知；收发记录是宿主观察，不是加密执行证明。内部修订说明是生成者产物，不独立证明每一个操作。未做实物打印、全色觉模拟、全网络训练或运行。原始论文 PDF/图不加入归档。

## 可复查产物

- `architecture-comparison.pdf`：最终四页图文稿。
- `diagram-run.zip`：三个图表的 editable SVG、构建程序、矢量 PDF、PNG、早期修改、固定输入/Skill 快照、收集 hash 和独立评分。
- `writing-run.zip`：实际图文交接的 LaTeX、图、PDF、页面、固定输入/Skill 快照、运行和独立评分。排除重复独立重建文件，保留检查和渲染 hash。
- `diagram-report.json`、`handoff-report.json`：既有 `scripts/agent_eval_pipeline.py` 的验收结果。
- `archive-replay.json`、`handoff-archive-replay.json`：归档重新解包后完整性与评分回读通过；不计为新的模型执行。
- `independent-review.md`、`final-reader.md`：实际审查覆盖和限制。
- `status.json`、`paper-sources.json`：版本、范围、失败、来源 hash 和角色注册表。
- `../../research/synthesis.md`：十篇论文同表对照；逐篇作者、版本、实际范围和原文证据见对应研究记录。

## 研究与取舍

本次新增精读八篇，加此前两篇，批次 10/10。图表论文共同支持将语义忠实与美观分开；PaperBanana 和 AutoFigure 的负结果说明整体/美观分上升不能替代准确性。SciFlow 的路径评价可能宽容缺失中间步骤，SciFig 提醒高质量版面仍可含错误边或公式。写作相关研究提示：结果正确不等于解释正确，段落/图的位置及评分者一致也不能证明论文完整性。

采用已有流程的真实产物评测和独立检查；保留针对图表损坏的审查负例、证据到主张的绑定和完整论文写作 heldout 作为待测候选。不引入上游整套 runtime，不机械添加十篇对应 Prompt。详细十篇原文链接与采用/待测/拒绝理由在 synthesis.md。

未 commit/push：本次是未改变基线 Skill 的限定验收，完整候选没有冻结，已有未发布运行时改动尚缺全部角色门禁，不能以本次通过替代。下一接续点是 T24/CO-023：三个不同题目的完整写稿基线、论证/语言/证据独立验收及必要修复；本批研究不重置。保持现有持续任务，不创建重复调度。
