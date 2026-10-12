# 保留初次定向回归失败

初次与第二次运行 42 项 artifact 测试均得到 1 FAIL：`test_changed_content_still_uses_matcher` 的短替换现在满足新的下界守卫，因此 `Expected SequenceMatcher to have been called once. Called 0 times.`。本次未出现 packet 或恢复不一致。最初主控误将此失败归到另一 nonunique fixture，独立复核纠正了定位。

nonunique fixture 的插入已加长以继续核验 matcher fallback；真正失败的 identical-fastpath fixture 改用 custom counter，核验变更输入的计数模式保留 matcher。没有放松生产判决或修改输出协议。初次 measurement 原始数据保留；定向回归复跑另见 tests-final.log。原首次 tests.log 被第二次覆盖，第二次失败 tests.log 与独立失败 independent-tests.log 保留；不宣称保留完整首次日志。
