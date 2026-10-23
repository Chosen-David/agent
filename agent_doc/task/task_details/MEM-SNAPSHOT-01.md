# MEM-SNAPSHOT-01

Task-ID: MEM-SNAPSHOT-01
Date: 2026-10-23

## Plan

同SYSTEM-99，基线6e32ef824603bc891f36e15787d7e5d4bc64b309。reconcile的active读取另开连接，与状态/依赖读取不共用快照，确定性更正可生成既非更正前也非更正后的报告。拟机械提取list原连接内正文为私有_list_on(db,status,scope)，公共list仍校验status/开连接后调用，reconcile复用其已打开事务读active/状态/依赖。保留原过滤、错误优先级、_get和JSON解析、不改字段、写入、更正权限或预算；独立复核计划后再改生产代码。

验收：WAL真实SQLite在_get水合时另一连接correct完成，更正前2active0flag、更正后1active0flag，报告不得混合2active1flag；修前失败保留，核对公共list原AST正文机械等价，相关3.9/3.12记忆/元数据/作用域/交接/错误回归和-O。独立复核候选与范围；不宣称livehost/模型质量或性能。发布前fetch，不强推，普通发布及完整远端回读。

## Plan v2

独立复核接受同事务方案并要求保留list覆盖。缓存bound_list，仅当__func__为原生list且__self__为当前对象时复用事务；子类/实例/绑定其他账本的覆盖仍调用一次，现有scope字段标明自定义快照一致性未知。补覆盖及继承路径回归，不新增字段。

## Progress

- 私有确定性探针已复现before2/0 mixed2/1 after1/0；真实WAL更正在_get回调内提交，新回归修前1failure(0.019s)。没有修改真实用户账本、没有sleep时序假定。生产改动待独立计划复核。

- V2按独审绑定对象guard实施；原list连接正文与helper AST相同。修后专项4/-O4通过；正确fixture入口后3.12相关138通过，3.9相关138项1error。独立隔离6e32基线schema9项同1error，既有自定义行工厂DDL锁边界保留未决；首轮fixture导入失败亦保留。最终独审及发布回读待补。

- 最终独审accept/usable-with-scope；独立3.12相关49、3.9去除旧schema模块40、两解释器-O专项各4通过；额外确认原生仅一连接、首次读前更正及账本不写入。受管候选哈希已绑定私有审核记录；详情见../../advice/MEM-SNAPSHOT-01.md。SYSTEM-99未完成，普通发布/远端回读另核。
