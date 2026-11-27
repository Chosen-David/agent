# 静态网页设计与验收

由当前主 agent 串行执行，复用 research-implement-optimize。HTML 展示页、研究项目页、结果浏览页和教学页面按本流程制作；纯数据图继续走 research-data-visualization，精确示意继续走 research-diagrams，保留可编辑 SVG/PNG 导出路径。

## 设计、实现、查看

1. 读取用户内容、现有页面和品牌约束，确定读者、页面主要用途及交付方式。缺少不影响结果的细节可自行选择；不能编造实验数据、客户、引用或产品能力。
2. 写简短设计 brief：信息层次、版面重点、字体及中文后备、颜色 token、间距、移动端重排。根据真实内容形成视觉方向，不把统一卡片、渐变或某套字体当所有页面的固定模板。用户指定风格优先。
3. 静态内容默认语义 HTML + CSS，必要时少量 JavaScript；沿用目标项目既有框架。只有交互复杂度确实需要才引入 React/组件库和构建链。离线交付使用本地资源和字体后备，不能依赖远程 CDN 才可读。外部字体、图片和代码核查许可。
4. 实现可读的排版、明确的主次和留白、响应式 grid/flex、合适的图片比例。保留真实文本与数值；科学图的语义/数值验收独立于页面美观。交互使用 button/link/label 等原生元素，提供可见键盘焦点、图片 alt、合理标题层级和 prefers-reduced-motion；不禁用缩放，不用 overflow:hidden 掩盖溢出。
5. 从真实交付入口打开页面；至少检查窄屏约 390px 和桌面约 1440px，实际查看截图。检查中文缺字、长标题/URL、遮挡、横向溢出、资源失败、控制台错误；用键盘操作全部实际控件并验证链接、展开/筛选/复位等行为。无交互则不制造控件。修复后重验受影响尺寸/状态。
6. 交付 HTML/CSS/资源及实际检查范围，复杂页面附复现命令和截图路径。没有可用浏览器或未查看截图时明确视觉验收未完成；静态检查不能证明精美、可访问性合规或交互可用。不要声称加载 Skill 就已安装 Playwright；必要依赖在项目 .venv 中安装并实测。当前主 agent 的检查仅为自检。

## 外部方法取舍与版本

2026-11-25 实际读取以下官方正文，适配为上面的现有 Skill 执行路径；本文件为本库自有精简规范，不复制上游 Skill，也不运行远程安装命令。后续更新先固定新版本并核对差异，不在每次任务中自动拉取 main 的可执行指令。

- [Anthropic frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)，Git blob `a5333457c414d20d625f307df945842c0952ecc3`：采纳内容驱动的视觉方向、简短设计 token、实现后截图自评；不照搬默认风格、不为普通制作增加逐步人类批准。
- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md)，Git blob `3eb3a212b7b89493922ea418489d4c6f67ae8bd5`：采纳语义元素、焦点、减少动画、资源尺寸与长内容检查；框架专用 hydration/路由规则仅在实际框架需要时应用，不为静态 HTML 引入 React。字体大小写与文案规则服从用户语言和品牌。

这两份材料是工具/官方指南，不计入 SYSTEM-99 的论文正文阅读数。没有真实页面对照评测前，不宣称页面质量或性能已提升。

## 论文交互页的设计转译

以作者实际项目页和对应实现为参照，选择服务当前理解障碍的方法，不复制整站皮肤、遥测或模型依赖。先比较同题材范例的首屏、主图、操作、展开与来源；把拟借鉴的方法落实为用户可操作的行为，再看成品返修。通用前端规范负责排版与可用性，不能代替领域图形设计。

- 主图承担解释：固定一个可手算的例子，让读者点选对象后联动高亮相关节点、连线、数值和说明；对象身份与颜色跨视图保持。提供点击/键盘路径，不只支持hover。实际验收至少一次“选择对象 → 改参数/步骤 → 对照 → reset”，检查高亮与数值仍一致。
- 先概览，再局部展开推导/证据；展开保留原对象参照，返回后恢复上下文。时间轴、单步与暂停用于观察机制变化，不把自动滚屏或装饰动画当交互。读者应能预测一个未展示输入，再通过控件核对；这只是验收题，不冒充学习效果实验。
- 字体层级、行宽、配色和图形密度由内容决定。科学视图保留单位、假设、图注与事实来源；窄屏重排或明确局部滚动，不把全图缩到文字不可读。借鉴论文展示的内容组织，不凭网页精美宣称达到发表/科学正确性标准。
- explain-research-concepts与research-implement-optimize包内可运行 `python scripts/check_page.py DELIVERY.html --offline --with-video`，无视频省略最后参数。它检查声明的HTML资源、锚点、控件名称和视频回退；通过仅为structural-pass，visual_review=pending。动态生成资源、CSS布局、交互语义和媒体解码仍需真实浏览器；不能用该工具给审美打分。

2026-11-27实际打开并操作：[Transformer Explainer](https://poloclub.github.io/transformer-explainer/) 的Temperature解释跳转与主图，[Diffusion Explainer](https://poloclub.github.io/diffusion-explainer/) 的Refiner展开及步进视图。前者代码固定 `poloclub/transformer-explainer@bfe50afba10b9b560b84143ee1107d977defa74f`，读AttentionMatrix前155行、Temperature全文、Textbook前85行；后者固定 `poloclub/diffusion-explainer@0820016ce908a8e66619b7a1c9369af1498160d6`，读controller全文。采纳对象联动、局部解释、可暂停时间轴到本流程与HSDP实例；不引600MB浏览器模型、遥测、默认自动播放和仅鼠标SVG控件。实现选节不等于全库审计，网站/代码不是论文正文精读。

同日复核Anthropic frontend-design `e4bb5d960d87126ff3b3a8af1a104b7db67560ba` 与Vercel agent-skills `5a37a6329fbad3666c3207392a6a7c0110e92efb`：继续采用内容驱动设计、实现后截图检查和原生控件，保留本库单一流程，不另装竞争Skill或执行远程安装命令。[Distill Feature Visualization](https://distill.pub/2017/feature-visualization/)仅阅读概览与目标定义选节；本次不引其旧组件/外观模板，前两者已覆盖当前交互需求。

## 从代码与数据流制作 HTML

源码讲解页先按 code-reading 的证据包核对真实入口、调用点、分支与配置；目录依赖不能当执行顺序。冻结 commit/path/symbol/行号；每条边写出数据、形状或单位、状态变化及成立条件。不知道的标 unknown，静态推断标 static_inference；源码位置不能证明运行时已经执行。

按“概览 → 节点 → 连线条件 → 源码证据”渐进展开，图中文字保持短小，长说明留在原生 details 中。精确拓扑使用 SVG；复杂跨模块图先拆视图，不塞成无法阅读的全景图。主 agent 串行完成源码核查、设计与浏览器自检。

code-reading 包内提供无依赖离线入口 `scripts/render_flow.py MANIFEST.json --out OUTPUT_DIR`，生成 index.html 和 flow.svg；它只排版人工核对的关系，不自动提取或认证调用图。manifest 含 title、nodes、edges：node 为 id/label/kind/detail/evidence；edge 为 source/target/label/kind/condition/evidence。kind 只接受 source_fact/static_inference/unknown；evidence 非空列表，每项为完整 commit、path、symbol、start_line、end_line。仅允许简短唯一节点 ID，最多40节点/100边；超过时拆图。由 source_evidence.py 取得定位后，人工核实关系，再构造 manifest；输入应落在项目临时目录，输出遵守目标项目写入授权，不写只读源码目标。

模板只是起点，按页面内容调整视觉层次。离线 SVG 保留连线编号、条件和推断状态；PNG 沿现有精确示意导出路径处理，未生成不声称已交付。使用真实入口在390px/1440px查看截图、缩放和所有 details/下载链接；缺浏览器时报告视觉验收未完成。渲染器不会核验源码内容、性能或真实性，也不能把格式检查称为语义验收。


## 教学与论文演示页面

论文讲解页先沿 [论文原图与关键图串讲](visual_explanation_workflow.md) 保留原图、来源版本及编码表，再选关键图组织全篇；重绘示意与作者原图分开。知识讲解页沿 [叙事与教学图型](explanation_patterns.md) 定位理解障碍，并按 [视频讲解](video_explanation_workflow.md) 制作必要短片。参考3Blue1Brown的图形推理：贯穿例子、稳定对象、保留变换前参照、图形变化后连接公式；不把黑底/配色当教学方法。科研展示同时核对论文来源、假设、单位、坐标和误差，不用装饰替代证据。

- 首屏呈现一个关键问题、核心图形和简短答案；以对象/数据为视觉中心，正文、公式和细节按“现象 → 操作 → 推导 → 边界”展开。用字体尺度、留白、对齐、有限颜色和清晰图注建立论文演示的层次，不把整篇内容铺成同尺寸卡片。复杂页提供章节导航和可寻址锚点，折叠推导仍能找到来源。
- 只有改变理解的控件才保留。滑杆/切换/单步/对照必须绑定真实计算或固定可追溯数据；改变输入时同步图、数值、公式标签和单位，保留reset及初始状态。播放/暂停与逐步观察可并存，不依靠随机动画伪造实验。说明参数范围、极值、非法输入和例子的适用边界。区分原始数据、教学模拟与静态推断。
- SVG/Canvas用于精确图形时保留可读文本/描述与数值表，公式使用实际可用的本地数学渲染或可读后备；离线页面不依赖CDN。代码流图证据沿code-reading，不把目录箭头当执行或数据流证明。
- 可嵌入自己制作的MP4/WebM短片，使用原生 `<video controls preload="metadata" playsinline poster="...">`，相对资源路径和真实宽高；需要字幕时提供带语言的WebVTT track及完整文字稿链接。默认不自动有声播放。大视频单独交付而非内联base64，标记资源体积，测试缺媒体时的文字/图形回退。先检测浏览器的实际编解码支持；FFmpeg编码成功不证明浏览器可播。
- 画面交互不以鼠标悬浮为唯一入口：控件有label、可见焦点和键盘操作，状态变化有可感知文本；减少动画模式保留静态/单步路径。视频字幕开关与音量不能被自定义UI遮挡。

验收必须从交付目录打开真实页面，390px/1440px观察关键状态截图；逐个操作控件、reset、参数边界、折叠、锚点和键盘路径，核对同一输入的数值/形状不变量。嵌入视频时实际播放、暂停、拖动、启用字幕，核对声画和相对路径；检查离线资源失败与控制台错误。无浏览器或未试听/查看则保留相应pending，不以静态DOM、技术媒体检查或截图存在代替实际观看。精美与理解效果仍需自检，不声称已获论文发表/可访问性认证。
