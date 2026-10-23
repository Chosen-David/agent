# UNINSTALL-PREFLIGHT-01：卸载前验证所有清单结构

基线 `0b2453a67b6b22a537bdd3dcefd2c457a33a57f3`；修复 `setup.py:410–416`，回归 `tests/test_uninstall_manifest.py:18–56`。同属未完成 SYSTEM-99。

触发：installation.json 的 links 为列表、链接值非字符串，或 skill_copies 非映射。旧预检未覆盖后续删除循环的输入类型；links=[] 能通过空迭代预检，待 files 删除完成后才在 links.items() 崩溃。真实安装最小探针修前输出：

```text
AttributeError 'list' object has no attribute 'items'
managed files removed before exception: 22 of 22
manifest preserved: True
```

修复：首次删除前确认顶层、files/links、可选 skill_copies 是映射，files/links 值均为字符串；异常抛 ValueError，由既有 CLI 返回2并报告 blocked。旧安装省略 skill_copies 仍兼容，原路径/所有权/本地编辑保护保留。拒绝坏清单，不自动修复清单。

## 实际验证

Linux CPU，本地临时真实安装，Python3.12.14／3.9.25；无GPU、框架或kernel参与，无性能输入hash或速度/内存主张。测试输入由固定 EMPTY_INVENTORY 和文中六种清单变形构造，逐文件bytes及symlink目标快照比较。修前同一新增2项测试：1 failure、6 subtest errors；不是7项独立测试。

```text
python -m unittest tests.test_uninstall_manifest tests.test_setup tests.test_install_recovery -v
Ran 35 tests in 1.455s — OK
python -m unittest tests.test_setup_portable -v
Ran 4 tests in 0.933s — OK
/root/.local/bin/python3.9 -m unittest tests.test_uninstall_manifest tests.test_setup tests.test_install_recovery tests.test_setup_portable -v
Ran 39 tests in 2.394s — OK
python -O -m unittest tests.test_uninstall_manifest -v
Ran 2 tests in 0.199s — OK
```

[独立复核及可复现探针](../results/uninstall-preflight-20261023/independent-review.md)：两解释器各39项通过，独立旧代码各复现22文件先删后异常；另6种异常形态快照完全不变；缺skill_copies的旧清单和复制安装中编辑过的agent/Skill均保留既有行为。结论 usable-with-scope，无阻断问题。源码/测试SHA256见该记录。git diff --check通过。

历史影响：坏清单下的卸载失败不能推定安装仍完整；需先核对实际文件，禁止根据旧异常日志声称无删除。正常清单的既有卸载回归通过。修复不使卸载具备事务性，磁盘I/O中断、并发文件变化、掉电、Windows和真实宿主/模型未验；类型检查也不认证语法正确但被篡改的所有权记录。未跑全套，main既有orchestrator/canonical决策门冲突仍待对齐，不修改该协议。整体任务质量、上下文/usage成本及真实后端验收仍open，不计系统批次完成。
