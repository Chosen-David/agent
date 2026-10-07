# 工程持续学习：跳蛛REM样行为与证据边界

北京时间2026-10-07，轮次172253。核查4个来源家族，新增`neuro.spider-rem-like-state@1`候选，新增published科学卡0条。关键补充方法与原始统计子集未核完，因此不升级；没有动物实验、作者代码执行、AI效果或意识测量、模型权重修改。

## 对应任务与实际运行

本轮只维护根TASK的EK-172253-01–03；主AI唯一作者，无委派。启动`git status --short`为空，本地HEAD与连接GitHub main均为`013cfa15b72d354ef87ec18eb9698b58f75e3b6d`。宿主已先fetch/fast-forward；模型不写.git、不执行本地fetch/commit、不改权限，不修改SGLang。输入原始字节哈希见[inputs.json](inputs.json)，九项规定输入及最近122522报告已读；另核对最新数学dependence收尾，保留其成果。

决策EXECUTE。按当前用户先补神经科学缺口，从问题结构查重，确认线虫传播已覆盖，转向现有蜘蛛睡眠缺口。数学顶层游标、history/open_questions，RL/概率待研主题及AI Infra→AI算法→数据结构队列保持。priority.next_domain仍为reinforcement-learning，下轮RL，再概率论，再神经科学。

私有DAG沿review→verify→publish有依赖、证据谓词、最多2次尝试和2700秒总预算，经agent_runtime.core.validate检查；它不是已部署的模型适配器。读取既有`.agent-runs/engineering-kb/maintenance/live.json`：session=`agent-knowledge-maintenance`，active_round=`20261007-172102`，pid=476、runner_pid=514，interval_seconds=3600。本模型没有独立核验WSL进程或tmux pane，不宣称新monitor启动或未来唤醒已验证；文档轮次172253不是另一个调度器。宿主既有桥负责固定周期、互斥、错过不并发追补及45分钟终止；未新增Agent、付费/API/GPU资源或后台任务。

## 来源、版本、采用与拒用

[sources.json](sources.json)保存实际URL、版本/日期、读取范围、SHA256对象、私有缓存位置及访问失败。四个家族不是四次独立实证；论文、作者源码、宣传和作者出版索引可能来自同一研究。只提交原创说明与核查证据，不镜像论文/源码或公开私人数据。

| 来源 | 本轮读取 | 处置 |
| --- | --- | --- |
| [Rößler等PNAS2022](https://doi.org/10.1073/pnas.2204754119) | 正式接受2022-05-27，在线2022-08-08，119(33)；EuropePMC9388130全文XML，主文Methods and Results、Discussion、Fig1A–F图注 | 候选。SI Extended Methods、原始CSV、九视频和模型训练划分未核；相关方法读过，不冒称整套附录已核完 |
| [作者Zenodo6616655 v1](https://doi.org/10.5281/zenodo.6616655) | 2022-06-06；元数据及README_file.txt、REMSleep.rmd、REM_retinaAnalysis.m完整源码，逐文件SHA256；元数据CC-BY-4.0 | 接口/许可诊断，不采用实现卡。固定DOI/哈希不是40位Git commit；没有伪造commit或执行R/MATLAB/DLC |
| [Konstanz机构说明](https://www.uni-konstanz.de/en/university/news-and-media/current-announcements/news/koennen-springspinnen-traeumen-1/) | 2022-08-09，完整可见报道；保存web工具响应JSON哈希，直接TLS证书链读取失败 | 仅解释与导航。报道开头关于梦的措辞超出本轮证据，PNAS日期处还留有XX；不将其作为梦的实证 |
| [Rößler作者出版索引](https://danielaroessler.weebly.com/publications.html) | 实际下载HTML的2026 under-review/accepted/in-press分栏及2022入口 | 两阶段睡眠列accepted但无核实venue/DOI/日期；野外反应延迟列in press并给DOI；均未读原始结果，不发表相关实证结论 |

五年窗口2021-10-07至2026-10-07；2022论文补覆盖缺口，不包装成最近发表。近90天检索使用2026-07-09至10-07边界，但返回许多无关结果，未确认本轮新近正式原始实证。作者索引的web open缓存把两阶段稿列under review，当前直接HTML及搜索则列accepted；记录此差异，以实际读取对象为准，保留终版核对清单，不能仅靠作者列表确认发表日期。Wild sleep ecology仍under review。另一野外研究DOI`10.1016/j.anbehav.2026.123719`的终版、方法与数据独立性待核。

PMC补充PDF路径实际返回HTML挑战页，检查字节头后拒作PDF；PNAS补充端点403。未关闭TLS校验，不反复重试、不下载含大量视频的整套归档。592MB DLC训练项目不下载，7.3MB knitted报告未读；未用它替代附录。一次可选DLC GitHub元数据查询遇匿名API限流后停止，没有使用未固定源码形成实现卡。

## 观测、条件、负例与代码接口

候选保留物种Evarcha arcuata、出壳后1–9天幼蛛、幼蛛性别未核与成蛛一雌两雄；34只幼蛛总录像数与330事件/29个体时长、260事件/17个体间隔分别记录。计数不是独立动物重复；家系、重复夜和子集排除未核。红外视频及人工评分/DLC角度示例是行为尺度，不是脑电或连接组。LLM长度/batch不适用；DLC GPU/dtype、训练划分和预算、相机与软件完整版本未知，不能填默认值。

主文中的卷腿→眼部运动135/135与眼部运动→卷腿135/342不互换。342与时长子集330也不可擅自统一；不同可见性和排除原因待原表核对。幼蛛背面透明与成蛛色素遮挡、站立正面观察有差异，不能把成蛛全部录像当直接眼部读出。协调清洁/伸展期间未见同类运动，只是行为对照，不能替代随机觉醒阈值、睡眠剥夺或稳态调节验收。外观共现不确认梦、记忆重放或同源神经机制。

作者R源码glmmTMB使用log10时长/间隔及SpiderID随机截距，明确提示残差分布不完美；本轮没有复算拟合、P值或夜间增幅。数据读取含绝对路径，Plot用的`AME_R_angle/AME_L_angle/time_mins`是处理后的字段，不能把未经处理的DLC列直接接上。成蛛某夜间隔受干扰被排除、阶段采样不均的源码说明需在原数据复核；不是本轮新实验。

MATLAB `handleSmoothing→fillIslands→smoothIslands`依赖固定坐标/置信度列，30fps、阈值0.9、minSpan10、smoothWindow50及二次平滑20；这些是已读脚本参数，不代表所有动物/训练运行。fillIslands对不超过10帧短缺口以前值填充，注释中的interp不能读成线性插值。可见性flag使用处理后标记，不能未经审计当独立原始可见性真值；默认exportFlag=0。工具箱/package版本未固定，无可直接采用的40位commit实现卡，local_execution=not-run。实现正确性、迁移性能和GPU速度均未测。

候选可支持后续补读、状态判据/可见性缺失/统计单位审查，减少把周期动作当睡眠或做梦的重复探索。AI离线重放仅为待验证假设；卡中给出等参数、数据和更新预算的无重放、随机、打乱时序、结构重放对照及未见序列误差/遗忘指标。随机或打乱相当即拒绝特定时序机制收益。显式复现与用户必做实验保留。

## 真实检查与接受范围

不直接命名方法的问题“夜间静止的小动物出现周期性眼部运动和抽动，怎样区分睡眠与运动节律？”已用files/SQLite真实检索，返回ID见[verification.json](verification.json)。章鱼卡全文已读并固定完整refs，物种/干预/LFP条件不匹配，拒用作蜘蛛实证；只帮助审查证据边界，见[knowledge-use.json](knowledge-use.json)。新候选在search/get/decision隔离。

同一章鱼卡的接口检查：条件缺失→insufficient_context、条件字符串匹配→reuse_for_planning、改为跳蛛→minimal_transfer_check、显式复现→run_requested_experiment；均automatic_skip_authorized=false。135/342≈39.47%、短缺口10/30=1/3秒和平滑跨度50/30=5/3秒仅是独立算术，不是原始统计或MATLAB算法执行。

7目录×两后端逐题排序/有预算上下文（去除耗时）与本轮干净基线完全一致。工程、RL/概率、神经科学、熊蜂目录保持满分；基础/round2/morphology原始漏检及退出1保留，逐项Recall@3/MRR/context recall见verification，不能称所有检索测试全绿或已修复旧漏检。接受标准为相同输入无新增退化；未更改查询、预算或测试期望来美化指标。

validate为83记录（80published/3candidate），插件生成/闭包、SQLite索引重建、refs检查通过。相关单测reuse7、math5、plugin1共13通过，Reader3通过并复用现有项目私有PyMuPDF依赖；未新增安装。全部命令、退出码、耗时、日志见[checks/final-commands.json](checks/final-commands.json)。[verify.py](verify.py)可复验逐题非退化、候选隔离、四个条件边界和算术。脚本初次调用的Python导入路径错误及成对文件写入顺序错误修正并保留[失败记录](checks/review-failures.json)。本轮只改知识维护内容，未跑POSIX相关全仓suite，不声称全仓或GPU通过。单模型自编回归不是独立盲测、科学复验、形式化证明或真实模型A/B。

## 任务验收、发布与下轮

EK-172253-01来源核查完成，科学晋级仍因附录缺口拒绝；02在上述范围验收通过，coverage缺口不因candidate消失。learning_state只追加本轮工程/神经科学历史及priority证据，数学和其他历史/队列逐字段保持。03须完成发布前main读回、并发整合、expected_sha/force=false更新及完整树独立核验；实际发布回执单独记录，不能在提交内自指自身SHA。

下一owner为既有小时维护主AI：先核查2026正式接收RL探索/信用分配/离线评估原论文，再概率论；神经科学待补蜘蛛SI/原始分母/遮挡敏感性、2026两阶段与野外反应延迟终版、既有两栖和头足类候选。宿主在模型结束且完整工作文件树等于远端树后才更新Git元数据/轮间技能同步，本模型不宣称已经执行这些宿主动作。
