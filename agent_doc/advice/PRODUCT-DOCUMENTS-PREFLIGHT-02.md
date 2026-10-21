# PRODUCT-DOCUMENTS-PREFLIGHT-02：离线缓存失败可重试

2026-10-21，SYSTEM-99 同批、PRODUCT-20261021 局部可靠性修复。
基线 `2f01f3a24115bfebd0503f240761009b4e8c89a6`。

`agent_runtime/documents.py:291–330` 的 `install` 在验证 wheelhouse 前
创建版本目录、`.incomplete` 和 venv。末个 wheel 缺失、哈希错误或为符号链接
都会失败；补齐缓存后，同一版本仍被 `verify` 拒绝，要求手工恢复。

把全部本地 wheel 的路径/大小/哈希检查前移至版本目录创建前；已安装版本的
复用路径保持原样。预检并非不可变快照，pip 的 `--require-hashes` 继续检查
实际消费文件。真正进入安装后失败仍保留诊断目录、不覆盖旧 current。

本地回归命令：
```
python -m unittest tests.test_documents -v
python -O -m unittest tests.test_documents -v
```
修前新增 retry 用例：`Ran 1 test ... FAILED (failures=3)`；修后两种模式均
`Ran 23 tests ... OK (skipped=3)`，即20通过。三种失败分别修正后均可走完
安装状态转换，另核验 pip 失败仍留下 `.incomplete` 并保留旧 current。
环境：Linux / Python3.12.14；路径、文件读取、哈希和安装状态是真实操作，
版本绑定及 venv/pip/smoke 在新增用例中受控替代，未下载或执行真实 wheel。
三个真实文档能力测试因未指定安装环境跳过；无新速度、模型质量或完整轮次声明。
原始短日志位于本次私有 `.agent-runs/documents-preflight-2104/`，不提交大日志。
