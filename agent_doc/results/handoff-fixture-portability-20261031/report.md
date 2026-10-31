# Handoff fixture portability repair

新增41项交接回归首次进入原生CI后，macOS实际20项在夹具setUp触发符号链接根守卫；Windows3.10/3.12各4处因默认CP1252解码语料/CLI输出失败。三个完整原失败日志、精确方案、完整双审与修后日志见[evidence-index.json](evidence-index.json)。旧CI：https://github.com/Chosen-David/agent/actions/runs/41180424328 。

只改 tests/test_handoff_basis.py 五处：可信临时夹具根解析为真实路径，三次语料变更保留旧bytes追加相同ASCII后缀，CLI输出二进制捕获后由原json.loads解析，消除locale转换。json.loads(bytes)不是UTF8-only校验。生产链接守卫/工作流/20个BasisTests/全部50个assertion AST不变，无skip或弱化断言。

本机一次41项exit0（16.519s），独立一次41项exit0（12.337s），均0失败/错误/跳过；时间只是unittest观测，不是性能对照。独立六域usable-with-scope，手工实际新上下文审核，不冒称受认证ReviewSession。原生五job/各实际41项步骤在此冻结时待新提交验证，不能由本地结果推定跨平台通过。

修复属于用户既有CI指令与持续升级授权。此前主控将自设审核次数误当必须再次询问的门槛；本次按上级持续执行指令作明确有界补充，旧3/3审核、原deadline和完整反馈保留，不追溯改写或重跑旧性能实验。补充plan/local/result/independent各1、源码CI候选1、自动重试0、09:30Z截止；宿主模型审核用量/费用unknown。稳定Plan65/唯一TASK/人类guide保持，SYSTEM-99仍未完成；无新增模型质量/token/费用或速度收益结论。
