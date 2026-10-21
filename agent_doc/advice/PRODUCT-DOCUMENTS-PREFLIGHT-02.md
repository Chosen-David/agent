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

## 真实安装补验（同批续接）

当前基线 `621fab93c40c7073ee0c45244dbb6ef28c042e8d`。先查现有结果：查询
`documents preflight retry profile` 扫描270、partial=true、17条缺登记错误；三个候选
仅token/通信材料，不适用于安装。U2/U3旧正文证据保留，但不能替代本次修复的真实重试。

新增显式opt-in的 `DocumentsOfflineInstallTests`：复制锁内10个真实wheel，故意漏掉
末包，公开CLI须返回invalid/3、旧current逐字节不变、版本目录不存在；补包后真实
venv/pip与四能力smoke成功，再删本地wheelhouse、无wheelhouse离线复用为reused。
没有替代venv、pip或解析器。默认未提供缓存时跳过，不隐式下载/安装。
相同新测试在修前 `2f01f3a2` 的实际模块/锁副本上1项失败，断点为残留版本目录；
在当前源码上1项通过。其后已有四公开命令及多页失败重试也在新自有root实际运行。

主控设置两个显式环境变量后执行完整 `tests.test_documents`，测试解释器普通及`-O`
各24/24通过、无跳过。CLI子进程不自动继承`-O`，不将此说成全部CLI均优化模式。
独立新上下文另建自有临时root，真实安装回归普通/-O各1/1、公开能力各3/3通过，
10个源wheel逐项SHA与锁相等；无opt-in时20通过/4明确跳过。结论为usable-with-scope。

输入锁SHA256 `dd3ab2926ea691e724b8fada91bdc01b84e92519966f6ef2e5563a1b3cedfb01`；
新测试SHA256 `a88d88be163708f60e374fbe817214471e73eb62ad06052a82db10646d21fa43`。
主控修前失败、普通与-O日志SHA256分别为
`6c1f9c10def4ad5bdcf9d9e9addd620133439a35674d9c5860b0ee15b600e08c`、
`9697e3b80f238dafb39b54c14ce3b08eed7773192b2d6bca241ebf317a199bca`、
`38682d857e5ae44bc44f7d2e60dd6a449aaac99f61b2b82987a3b9a28a1a8168`。
短原日志、源模块副本、独审及wheel逐项哈希保存在私有
`.agent-runs/documents-real-retry-2158/`。环境仍为Linux x86_64、Python3.12.14、glibc2.39。
AGPL参数只用于隔离开发验证，不代替用户生产许可选择。

另保留一次共享工作区root失败：安装返回成功后读到`.incomplete`，完整套件2失败1错误。
主控及独审均用不调用documents的普通文件复现“写入、等待4秒、unlink后同次不存在，
下次调用重新出现”；具体写入者/同步机制未知，也不能证明是原marker的唯一成因。
故障root未删marker补成成功；实际通过范围限定自有`/tmp`目录，不认证共享工作区持久化。
此检查点没有新生产修改、新论文正文阅读或速度/质量收益，SYSTEM-99继续未完成。
