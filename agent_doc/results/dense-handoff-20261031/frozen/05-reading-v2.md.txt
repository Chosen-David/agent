# The Physical Cost of Context — 2610.34763v1

实际续读2026-10-26 v1全部可用正文：§§1–7及所有小节、完整49参考文献、Appendix A/Frozen Protocol and Artifact Notes/Assets and Licenses、Tables1–6、Eq1–7、Figures1–2图注。前次[0,15000)未计完成，本次连续读取[15000,31000)、[31000,47000)、[47000,61061)，与原text SHA匹配。无PDF像素/图中精确曲线审读，未访问或运行CodeNib作者实现/原始数据/模型。来源hash/精确模型与代码缩写版本见source.json；不补造原件未给的完整commit。

## 方法与因果对照（§2、§3）

Eq1: logical prompt=sum每次完整输入，uncached=logical−prefix hits；改变请求次数和前缀命中都改变执行量，删去的逻辑token少于失去的命中token时会增加prefill。Eq2–4把scope/scaffold、开头top10证据、可见序列化拆开，原始history留作审计。Grep(loc)/Mini(patch)无seed保留history；Eager预置固定dense top10并留history；Compact首次成功读源后做一次锚定改写，保留query一次/成功读/有限assessment；Mask5只在patch，保留action/toolID而将五次前observation换行数标记，持续改写。两种序列化都不调用额外LLM。seeded arms的候选逐字节相同；Compact−Eager是retrieval匹配的保留策略对照，Eager−Grep仍混合证据及交付改变。

Eq5资源向量包括prompt/output/请求/uncached/TTFT/墙钟/KV time-area与peak/统一内存压力/GPU能耗proxy。Eq6: paired95% lower endpoint(Qp−Qc)>−.05才入资源推荐，非劣不等于质量更好；离线验后gate非运行时控制器。loc E/C控制Grep，patch只有M5控制Eager被gate，其他patch比较描述性。失败留分母与server资源，不用便宜失败装高效；另报成功endpoint成本。

## 样本、栈、计量（§3、附录A）

三个研究不混分母：①质量450 SWE-rebench V2 Python issue，各异repo/每政策1轨迹，共1350cells；goldpatch可应用、≤5000trackedPython且有patch触碰的base-visible function/class，故质量endpoint是answer-block Recall@5，不是修复成功。用100题pilot方差估441独立例而取450。②资源100个CodeNib synthesis问题、25repo(五语言各5)、每snapshot6种issue-like中roundrobin取4、三政策三重复=900cells，25独立repo组；queries LLM-curated/judged且模型ID缺失，非人类issue分布。③相同100loc题cacheflag干预600cells，25pairedrepo/每政策缓存regime；不同于900cache-off。外部patch100 SWE-bench Verified、12Pythonrepo、预定hash平衡不看gold/test/outcome，四arm各1轨迹，32call/1800s预算，官方harness评分，不能当不限预算SWE能力。

主栈DGX Spark GB10/128GB coherent统一内存、Qwen3.6-35B-A3B-FP8/vLLM、context65536、temp0、一次一个测量request；资源matrix关prefixcache，相同模型干预只开该flag并按repo块reset/salt。外部mini-SWE-agent2.4.6、Qwen3.8-27B-FP8/SGLang+DFlash8drafttoken；模型/框架/运行时同时不同，不能跨栈归因于cache，绝不混绝对资源。精确缩写版本：target95a723d08a94/vLLM0.19.2rc1.dev134+gfe9c3d6c5；embedding97b0c614be4d；外部target017b9c7af6b5、draftdedf8df68adf、SGLang0.0.0.dev1+gc0b6474b4、image codenib/sglang-dflash2:c14312a6-cu130-arm64；CodeNib88e88b38b978；mini a83fcae82d2a/harness7a21e0577295/LastN3ea751c087f3。只抄作者缩写，无完整manifest核验。

source编译/embedding构建另摊销，query encode/search计preload任务。Latin square/固定轮换分散漂移，warmup/idle不计measuredblocks。GPU功率1秒采样梯形积分减各块idle均功率×时长(Eq7)，负值留作noise、不裁零；不是全系统能耗，CPU/主存/评分/服务器驻留/开发开销未全计。KV GiB*s是allocated time-area，外部只normalized fullattentionpool，不能相互当GiB；统一主存看/proc/cgroups，不用KVpeak推容量收益。未锁频/无powerlimit，Xorg/desktop常驻，100题primary墙钟区间按25个完整repo组重采样，primary block-level server/KV/energy区间仅按3个paired shards并保留重复；cache干预按25paired repo，patch物理量按8paired shards、质量按12repo。bootstrap10000draw：质量/primary墙钟等适用端点按完整repo组保留重复和政策配对，block-level counters按上述shards；不把300cells当300独立题。

## 结果与负结果（§4、Tables1–6）

450题G/E/C Recall@5 .470/.478/.494，Full@5 .307/.318/.329，format .904/.976/.987；E差+.8pp/95%下界−2.6pp，C差+2.4pp/下界−.9pp，均过−5pp非劣。资源来自另一100题集：G/E/C prompt136.8/90.5/98.2ktok、successfulcalls13.02/8.38/9.49、wall68.32/48.22/52.20s、KV25.88/16.67/18.21GiB*s、GPUproxy2.007/1.340/1.466kJ。E对G请求−35.7%、proxy−33.2%。C对E反而prompt+8.5%、call+13.3%、wall+8.2%、proxy+9.4%，无额外节省；“锚丢候选导致再查”仅假说，trace无callintent。per-fullrecall204.2/133.7/151.9ktok与3/1.98/2.27kJ使用100题instrumented full率，不能除以450题Full@5重算。

3个MicroPython Compact cells因61441prompt+4096output=65537比65536多1失败，不是KV OOM。900attempts仍算，897persistedtraces；失败trace serializer缺candidatehash是次级audit失败，保留selectionmanifest而不伪造原字段。作者报告headline含1.204M failed-requesttokens、C98.2k/attempt与28.2%节省；去该charge是另一297completedcells口径95.1k/30.5%，不能择优替headline。25repo index147387chunks/731MB，767.7s/36.1kJ另计；十query/snapshot摊3.07s/.144kJ，100query时能耗占<1.1%，不是免费检索。TTFT变化<2%，percall延迟E更高5.721vsG5.218s，任务快主要少calls；peakKV/内存太噪，不支持capacity结论。

600cell同模型cache干预：E prompt+8.3%CI[−5.7,+24.7]跨零，uncached−67.7%CI[−71,−63.8]；C−E cacheinteraction −7.1k CI[−17.3,+2.3]，wall+.1s CI[−5.4,+5.7]，均跨零。相同主模型cache-on C对G uncached−38.2%，没有复现探索性换栈的+5.2%，不能把探索性差异写成cache因果作用。Table4探索性Qwen3.8仅100题1重复，G/E/C Recall .772/.800/.802、uncached18.245/13.749/19.192k；Table5percall比率描述而非paired估计。

外部patch Mini/E/C/M5 resolved30/29/30/26 of100；submitted/capped45/55、44/56、45/55、40/60。prompt220.7/225.6/210.8/150.5k，calls26.13/25.66/25.84/26.33，uncached9.8/10.0/12.2/70.8k，wall120.2/122.7/116.6/167.9s，proxy1.833/1.956/1.917/4.412kJ。M5对E prompt−33.3%却uncached+608.5%、wall+36.9%、proxy+125.6%；少75.1k logical但少135.9kdevicehits→多60.8kuncached，prefix约96%→53%。M5差−3pp下界−8.6跨−5gate，因此未证非劣，不能推断已证普遍劣效或推荐它的资源改善。八shards两个方向一致，但轨迹改变仍可能贡献，非完全隔离cachehit的反事实。ρ≈.55拐点仅按两个政策命中同倍率缩放的一阶估算，不是实测batch阈值。

附录保留invalid Astropy gitlink引发整13cell Eager block(277requests/20.8min)隔离并reset后重跑，原失败/telemetry留存且不入aggregate。reported正式primary/exploratory14.11/4.23devicehours、build .213h、cache7.90h/.183kWh、patch14.65h/.281kWh；上述成本仍非所有开发/驻留/评分或全部尝试成本。Tables3/6固定模型/25repo仅缩写版本，作者原数据/代码未复核。仅一台Spark、串行请求；batch/缓存竞争/云GPU、Mask-window扫描、LLM摘要/learnedprune/externalmemory未测。

## 对本库关系

采用后续评价拆分：任务包/只读活跃视图对全量读取时保留更正/异议/依赖及真实任务质量；另计请求数、实际loaded prompt/cachehit/uncached/output、构造恢复费用和所有角色。字节、char、本地tokenizer和供应商账单/物理KV/能耗各不同。先检验质量非退化再看资源，保持失败分母和bootstrap有效独立单位；不因文件更短就称token/费用收益。

暂缓套用固定top10、一次锚压缩/Mask5或自动LRU/newpool/agent_doc迁移：本库无同条件provider完整输入/最终质量/全费用，且论文Compact无额外节省。当前全角色安装/安装后工具验收为独立接口验证，不是论文policy实验，不能算本论文创新性能收益。旧Windows/FD/backend/StageI等不重开，旧结果/缺原件/反例保留，SYSTEM99仍open。v2按原完整反馈R1仅精确区分重采样单位，原稿/反馈保留；复审待完成，历史64不变，完成前0credit。
