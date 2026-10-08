# 初次回归保留记录

命令：python -m unittest tests.test_knowledge tests.test_knowledge_index tests.test_knowledge_math tests.test_knowledge_handoff tests.test_knowledge_reuse tests.test_result_validation -q

实际结果：70 tests, 5.952s, 1 failure。test_bundle_exact_and_cli_without_repository检查发现插件快照缺少新增math.support-conditioning.json/md；尚未同步的预期集成缺口。其他69项通过。此状态不能作为发布通过证据；运行现有sync脚本并重新验收。
