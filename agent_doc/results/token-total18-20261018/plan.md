# TOKEN-TOTAL-18 有界输入校验修复 v1

基线91d7545b75b090a9eea977af185a6f8d13b5a736。用户已授权Agent实现/测试及验收后main发布；TwoLevel暂停不在本计划。目标：short_appserver_usage拒绝伪装成整数累计计数的bool/float，合法last/total输出逐字段不变。本计划不扩大成模型计数或KV优化。

源码假设：agent_runtime/token_usage.py:46–50严格校验last int，但total只比较数值，Python True==1、100.0==100可绕过完整整数协议。结果仍来自last，不宣称错误计数金额或已污染旧实验；影响是损坏total却获得严格fresh统计凭据。

方法：1独立审查本plan/当前source与既有tests；2添加JSON往返真实基本类型的回归，保留修前失败；3最小guard校验total每字段type is int/非负，再维持原cumulative比较；4专项普通/-O、独立基线重放与额外边界；5串行全库/Reader；6报告/任务Progress，最终fetch/staged独立检查、仅明确文件普通非强推/原子CAS main，回读SHA与内容。没有受管Engine派发或伪造ReviewSession；手工新上下文审核仅作用本次。

固定验收：每个total字段浮点等值均拒绝；零/一计数bool拒绝；合法全零和常规整数/多snapshot不变；已有prior-history拒绝保留。只有final snapshot算数，早期snapshot规则不改。测试用unittest断言可在-O运行；补丁只有total guard，不改事件协议/JSONL路径/模型backend或全局配置。不做计时，不声称性能收益；必要输入校验开销如实未测。

资源：现有本地CPU与现有工具，无模型API/GPU/新付费资源；最多一次实现+一次必要返修，全库一次（失败则明确定位）。已有MEM-STORAGE-01模型质量/KV未完成。当前未提交改动无；不触碰人类guide，既有结果不改。

先前查询候选词法相关但条件未知，不作接受；本轮保存实际结果与适用性。小改动不引入库/JSONschema依赖，简单exact-type guard是同接口低维护方案；更多系统论文不证明输入协议，Python官方类型文档作该机制依据。
