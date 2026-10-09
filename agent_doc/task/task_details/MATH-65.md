# [MATH-65] 近似耦合的边际修正与保守证书

Task-ID: MATH-65
Date: 2026-10-10

## Plan

EXECUTE；用户持续建设数学知识授权。仅agent知识/索引/state与本轮证据，不修改SGLang、人类guide或生产。复用research-explore/知识入口；缺guide保持缺失。

有界主题：有限归一化a,b，任意非负有限F，全矩形允许边。先行裁减再列裁减得到Y≤F，其行列均不超目标；r=a−Y1,s=b−Yᵀ1,τ=1−sumY；τ>0时G=Y+rsᵀ/τ，否则G=Y。证明非负及精确边际，||G−F||1≤(sumF−sumY)+τ，0≤C≤D时<G,C>≤<F,C>+Dτ。归一化F时进一步≤行列L1残差之和（自己的推导，不冒称经典Lemma7原界）。实际value代价继承运输输出卡；任意对偶f,g经h=max(0,max(f+g−C))与f−h修正给L≤OPT≤U；下界不是输出下界。经典NIPS2017 Altschuler/Niles-Weed/Rigollet Algo2、Lemma7实际PDF检查，零缺额保护与矩形/后验代价推导单列。

近期限定核查Wang 2606.28973v1（2026-06-27提交；HTML显示2026-08-24文内日期须区别，预印本）§1/2.3/Thm1.1，O(1/k)非有限步精确可行；Forde 2609.07954v1（2026-09-07，预印本）§1/2.1固定support正边际/两半步，abs和HTML题名不一致如实标记，不能套为普通softmax或变mask质量证书。只筛选不复现/全面证明评审。

fixtures冻结八例（T7明确含不等质量及同总质量2的非法边际变体），跨域同量纲力混合，非法质量/负值、禁止边拒用、虚假低raw cost、对偶修复。三条无定理名问题两后端Top3六命中，三必要卡≤22000字符；aliases仅公开词法结构。34知识/索引回归。未用holdout只哈希不读；所有旧卡/candidate保持。无Lean/模型/GPU/真实tokens或e2e声明，精确样例不代替一般证明。

预算1800秒/最多2计划返修：独立计划approve→producer→不同fresh owner独立结果验证→主AI钉定实际完成receipt→native gate→publish。没有可宣称部署的tmux/supervisor/ReviewSession身份适配器；只执行宿主当前有界工具。最新main同步、并发保护及发布CAS，直接main读回树/父/SHA。保留所有旧领域和GPU游标。失败保留原证据，不放松验收。

## Progress

- 最新main同步fac9c18，唯一TASK/角色/知识/state读取；同主题本地run目录无任务，远端未知。现有结果实际命中两项并记录区别。来源相关章节读取。

- 冻结T6预期成本错误：实际修复后矩阵四项1/4，成本1；预期1/2导致原verify exit1且T7/T8未执行。失败诊断仅六例，五个费用匹配；不能记八例通过。计划两次审核限额已用，不静默修订冻结输入。
- 独立结果审核确认原scope不通过，主AI钉定实际完成receipt后native gate为invalid；不登记usable或让科学消费者继续。草稿移至本轮candidate_card.json/md，不发布新KB条目。其T6错例及outputs.json的初始计数均不作为验收依据。
- 34回归与6次检索/16368字符是在历史临时草稿语料上完成，不代表当前语料含该卡；原231条路径及holdout字节保持。没有模型/GPU/Lean/e2e/token收益。
- 当前全局文档问题为TOK-003/TOK-004 Progress边界，未改。coverage/state仅记录失败缺口；全部既有领域/GPU游标保留，TASK仍未完成。下一步明确版本化修正T6并重新计划/完整重测/独立验收。失败归档直接main读回见publication.json，未改SGLang/人类guide。
