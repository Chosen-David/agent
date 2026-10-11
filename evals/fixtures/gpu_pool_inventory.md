# 合成 GPU 资源池盘点快照（示例数据）

## local（本机，2 卡）

| GPU | memory.used | 空闲判定 |
|---|---|---|
| 0 | 1 MiB | 空闲 |
| 1 | 1 MiB | 空闲 |

- 模型路径：/shared/models/Qwen-8B（共享挂载）
- 数据集：~/datasets/LongBench 完整（16/16 子目录）
- python 3.9，磁盘 5.9T 可用

## node-a（8 卡机）

- GPU 0–6：memory.used=1 MiB，空闲；GPU 7：memory.used=71 GiB，占用中（他人任务在跑）
- 模型路径：~/models/Qwen-8B（家目录，非共享挂载）
- 数据集：~/datasets/LongBench 完整
- python 3.9，磁盘 1.8T 可用

## node-b（2 卡机）

- GPU 0–1：memory.used=1 MiB，空闲
- 模型路径：~/models/Qwen-8B（家目录）
- 数据集：~/datasets/LongBench **缺失**（目录不存在）
- python 3.9，磁盘 400G 可用

## 远程既有实验数据

node-a:~/proj/exp/ 含未拉回的上批预测文件（约 2.3G）；代码同步不得删除。
