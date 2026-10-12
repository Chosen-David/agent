# 原始日志索引

全部原始路径位于当前本机 /workspace/scratch/88c3234ecfbc/agent-research-2358/agent_doc/results/dag-membership-20261013-0659/；大测试日志不上传Git，保留原字节。此摘要不替代原日志或独立review。

| 本机文件 | SHA256 | 实际结果 |
|---|---|---|
|runtime-tests.log|c3551c0521b5dae25a0942efafbcedc4e19ea8ff536c2cd8abbf6bcba5deca02|39 tests /1新增fixture error|
|full-tests.log|a43a0917718dc302a393a990df99fab80bd32a66fe812254f726b6eaca434387|1177 tests /1同fixture error /8 skipped|
|new-boundary-tests.log|3213e9525e3a7f00a6fc62fd35a75ee44cc84370ca94d08fae6a8e079ba70cda|2 pass|
|runtime-tests-v2.log|4c3fd1ddd87059dc8e15eb49d0e13d8bab583c98e0852e40147b89a3009aea45|39 pass /3.698s|
|full-tests-v2.log|a58c6f1ea5efbb87d0fe85e61976a45aba4dd1a0292b3c240a9445db027bf7a5|1169 pass /8 skipped /71.771s|
|reader-tests.log|76ee6bfe357401b11155b9c9474d7d735887783c39b32e46c63c0eb2d4fb9673|3 pass /1.568s|

初次原异常 ValueError('dependency cycle') 发生在新增测试期待OddHash成功；按实际baseline/candidate均有的晚期判环错误修正测试。原失败不销毁。完整原性能原始样本producer.json与independent.json本次上传，输入hash在两文件中。
