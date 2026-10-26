# 调用范围补充

正文和独审中的“未做模型调用”仅指没有另行启动被评测 Agent、provider benchmark
或真实后端任务。主控与独立审查者本身进行了实际 AI 推理；精确模型版本、所有 actor 的
provider 输入/输出/cache tokens、延迟与费用未由当前接口完整暴露，均为 unknown，
不能记作零，也不能据此声称任务总成本下降。

现有 record.json 保持原始三个冻结引用及 unknown 状态，不改写为实证验收。
此补充修正调用口径，不改变论文数值、稳定 Plan、生产代码或旧预算。
