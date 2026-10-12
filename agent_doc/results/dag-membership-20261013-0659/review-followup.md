# 独立回归 fixture 修正复核

本次仅复核 tests/test_task_runtime.py 的两个新增方法；未重跑性能，未修改 core.py 或测试。

当前测试文件 SHA256：`8f1c322083f26c1c1f2152ddebc59ae59b5041d93cfbb88c1ecbdb9c5ad5197f`；candidate core.py 仍为 `d137bd76e938283611e47acad4eec5bf8b706f9f3e3dcf9d0b264ba5df4196d8`。基线仍 git `6886c3ff3f4c5238d733d9da9ac349933f3020de` 的真实 core.py。

独立 git-show 加载基线，与候选分别执行两种输入：`OddHash('parent')` 作 ID、普通 'parent' 作依赖；普通 ID、`OddHash('parent')` 作依赖。四次实际结果均为 `ValueError('dependency cycle')`。这是原 cycle detector 已用 set、异哈希 str 与普通 str 不在同一集合桶造成的既有行为；原 list 成员先通过。候选保留同样晚期错误，不能改成 `unknown dependency`。初始新增 fixture 把此输入期望为成功，期望错误；不构成本次运行时新增 bug。

修正后的 test_dependency_membership_retains_string_subclass_equality 对两种输入都断言精确 cycle 文本；test_dependency_membership_preserves_invalid_input_error_order 断言未知 list 依赖先于缺 risk、非法 list ID 在 set 构建前报 unique-ID 错误。独立以 unittest.TestSuite 只运行这两个方法，2 tests PASS。补充 probe 第一条 shell Python 有括号语法错误，未运行任何检查；更正 probe 后取得上述四次及 2-test 实测，未改变 candidate 或验收阈值。

历史负结果保留：runtime-tests.log SHA `c3551c0521b5dae25a0942efafbcedc4e19ea8ff536c2cd8abbf6bcba5deca02`，39 tests / errors=1；full-tests.log SHA `a43a0917718dc302a393a990df99fab80bd32a66fe812254f726b6eaca434387`，1177 tests / errors=1 / skipped=8。错误均指向原 fixture 成功断言。full 日志中的 traceback 显示行文本可能因执行期间 root 修改 fixture 而读回新源码，不能把该文本当初始字节快照；错误栈和结果仍保留，不覆盖日志。

完整修正后全库结果尚由主 AI 独立收尾核对；本次 2-test 通过不代替全库重测，不改写原性能 independent.json。
