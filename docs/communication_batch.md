# 原子批量发布

`publish_many(events)` 接受1..100条稳定的JSON信封，按顺序返回与单条 `publish` 同结构的结果列表；重复项复用原seq并标记duplicate。每条均执行原有校验，预算按事务内最新精确账本逐项检查。失败会回滚这批新增事件、全部投递和账本，既有历史不变。原有 `publish`、ACK、inbox和消费者选择的交接编码保持原行为。

```python
results = mailbox.publish_many([event_a, event_b])
```

```bash
python -m agent_runtime.communication --db RUN.sqlite --plan PLAN.json --root . publish-many events.json
```

数组里的每条信封仍需完整字段、具体动作和有效产物引用。空数组、超过100条或非数组被拒绝。CLI成功输出JSON结果数组并返回0；失败输出error对象并返回1。接收者验证与ACK仍是后续独立步骤，发布成功不代表任务完成。

调用者必须选择批量的原子提交语义：中途失败不会像逐条发布循环那样保留前面新消息，消费者提交后才看到整批。需要尽早单条交付时使用publish，不自动攒批。连接仅在本次调用内使用并关闭；不跨线程共享SQLite连接。条数有界但引用验证时间无硬上限，不能据此保证部署公平性或请求时延。

[31组四路径固定对照及独立复测](../agent_doc/results/comm-batch-20261010/report.md) 比较逐条调用与批量调用，并加入已共享事务的强基线。主要收益是事务/连接摊销；不声称优于所有已有批量实现，不改变信封大小、引用字节、模型token或网络负载。
