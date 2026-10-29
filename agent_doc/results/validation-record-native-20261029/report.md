# Windows原生fixture纠正：短/长路径名不能代替文件身份

保留生产修复1e8283fb及CI40889582083的原始失败。Windows3.12 job123502416415中，13个方法的两个失败断言均为C最后目录成员Path字面比较：RUNNER~1与runneradmin短/长名不同；bytes/inode/mode/同字节接受/异字节拒绝及其余12方法均通过。完整相关step摘录与明确来源另存，不冒充整个job日志。原失败不改判为success。

仅将C最后一行列表Path比较改为读取members、断言len==1及members[0].samefile(target)。原所有其他断言保留，不改生产、CI、错误边界或增加skip。samefile效果需新源码原生CI验证；原日志未直接测量samefile，不以别名解释代替新版结果。

原Version55上限2的第二次/最后静态方案审核已approve，七域pass；手工意见非可信runtime回执。使用原截止前的审核与一次新源码提交，外部CI可稍后结束，仅观察不延长/重启任何旧本地分支。baseline/fixed/independent已耗尽，未执行新本地测试或重跑旧CI/job；只允许本次一个新source提交自动触发一个新workflow。Version55旧原始证据和testhash完整保留，不能称其覆盖新版。

test-before/test-after为冻结输入证据，当前变更只有一行变三行。唯一TASK55→56/AK-native与Progress更新，guide及无关文件保留。新四组Ubuntu/Windows×Py3.10/3.12完整13方法与4新方法日志待回读；macOS job不跑本模块。没有生产新修复、性能/模型质量/费用结果或新论文计数，40篇同批正文及SYSTEM99全部系统级未决继续保留。
