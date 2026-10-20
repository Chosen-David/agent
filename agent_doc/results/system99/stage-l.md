# CHAIN-MANIFEST-SNAPSHOT：消费的字节必须匹配消息引用

基线 `b5aab6e4320299da931fe3aa5eb787bb8972d004`。
`agent_runtime/communication.py:350–360`先检查envelope引用哈希，再按路径
重新加载manifest。两次读取之间文件被替换，旧实现仍能返回并持久化不同
内容；事后恢复原路径的ABA也不能证明已解析内容属于原消息。

修复：`scripts/validate_handoff.py:21–35`可选expected_sha256，对一次读取
的原字节先校验、再严格UTF-8/JSON解析；consume传原event引用哈希。
保留其它refs/consumer/basis检查、重复键及非有限数拒绝，ACK仍独立。
只新增一条说明快照边界的注释，不迁移目录、增加schema或加载规则。

## 固定反例与验证

Linux x86_64、Python3.12.14、glibc2.39；临时文件+真实SQLite，无模型/GPU。
冻结回归`tests/test_communication_snapshot.py` SHA256
`8e512967921da878baae9040d7fab32dd7f01d4e5b6f0116c22a8cddcbe3f147`，
复用夹具`tests/test_communication.py` SHA256
`232f4bad46429e8408c902ff486bb8023fde7b0715f9b233cb3a522b1293f442`。

修前4方法：3 failure/4 error；其中替换/ABA两项subtest失败才是漏洞反证，
单读钩子失败是实现路径约束，4个TypeError只是新增keyword尚不存在，
不表示旧严格parser接受非法JSON。旧误导入基类导致20方法的初始日志保留，
不采用其计数。真实探针短结果：`returned_replacement=true`、
`persisted_replacement=true`、`event_hash_matches_current_manifest=false`。
修后普通/-O四方法均通过，替换拒绝且无basis/ACK；读后替换只能返回原
绑定快照，后续impact能报告漂移；UTF-8/CRLF及严格parser边界通过。

实际命令均为`python [-O] -m unittest discover -s tests -p PATTERN -v`：
新回归4、handoff70、communication45、更正链1通过；Reader应用3通过，
`python scripts/sync_plugin_references.py --check`通过。
全库1396项：1388通过，7项缺可视化依赖/字体、1项真实tmux未启用跳过。
[独立六域复核](independent-stage-l.md)接受usable-with-scope，另独立通过
5项边界/精确HEAD反证；不是部署或普遍无bug认证。
原日志在私有运行区`system99/manifest-l-*.log`，修前最终日志SHA256
`b98790aeaf2ea6a675b8b0e30cfa5dc00ef0c10993dc62ac2b8a1557c85654af`。
全库日志SHA256
`3ae8c0696edc5a80d4d37bdbeac24f3a28e79afdc8ebf24bdbbac427de44e3c8`。

生产候选SHA256：communication
`d6115a7bbba9eddda5ce46d0c6b7f56e2b58451c17fe6ffbda6d348fe299dbcd`；
validate_handoff
`c9cde9f95e738b7ee644ed1c5a093f93cf5c67d28eec3071821faec6b1eb89f3`。

这是正确性修复，未测速，不报延迟、内存或模型质量收益。其它artifact不
自动获得事务快照；来源哈希仍不证明语义，OS恶意修改隔离亦未验证。
原历史数据不重写。真实宿主、多轮任务质量/成本及历史登记覆盖仍open；
[论文17正文记录](research-i.md)不把本阶段算成完成一轮。
