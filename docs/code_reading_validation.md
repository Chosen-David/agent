# 代码阅读验证与边界

2026-10-03，基线 `a5328e4`。新增独立 skill、轻量源码证据脚本、角色与市场路由、协调/实现技能离线阅读后备、合成 fixture 与评分标准。只扩展代码阅读能力，没有安装第三方后端。

## 分开的验收层次

1. **脚本执行测试**：临时 Git 仓验证固定 commit、AST限定函数、装饰器/行范围、脏工作区隔离、非法路径/对象/行号拒绝、非Python人工标签、歧义符号拒绝。独立review复现了 git replace、目录树误报和formfeed错行，修复并加入回归。脚本禁止替换对象和lazy-fetch，读取缺失对象失败，不借读操作补下载目标仓库。
2. **分发静态契约**：角色/市场/评测目录登记、本地链接、生成引用同步、技能数一致。协调包未携带的可选脚本明确回退人工SHA/函数/行证据；不是后端安装测试。
3. **合成阅读任务**：`evals/fixtures/synthetic_selector.py` 自带刻意误导的模块叙述，覆盖选维/可选基、范围/配额/强制集合、跳far与最终全维评分。评分标准在 rubric；它是阅读任务，不把关键词契约测试冒充模型理解成绩。任务输出和审阅记录见本轮结果目录。
4. **真实只读应用**：读取指定的 Chosen-David/sglang 提交 `271b07026040cf787a50bc0b0a6911cee6e00ebd`，跟踪子空间/可选投影、minmax、精筛、快选、near/far、跳far及最终全维KV；真实使用工具抽取16个源码锚点。具体项目分析交原任务，保存在目标仓库外，不将论文材料或完整任务报告发布到本仓库。没有执行sglang、GPU或性能实验；目标工作区保持干净。

独立review是独立审阅者真实执行，发现与修复记录随最终测试结果报告。没有与旧skill做盲测/多任务基准，因此只宣称增加可调用入口、定位工具及核查契约，不宣称阅读正确率或性能已提升。

## 复现检查

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
```

结果、运行范围与独立review最终意见见 [本轮记录](../evals/results/2026-10-03/code-reading/validation.md)。
