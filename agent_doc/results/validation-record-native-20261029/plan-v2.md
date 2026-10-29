# VALIDATION-RECORD-FIX-01 native continuation / proposed Version56

保留1e8283fb生产修复、旧Version55本地baseline/fixed/independent全部已用额度及原CI40889582083失败。Windows3.12 job123502416415的13方法中，仅C的两种matching子场景在最后目录成员Path字面比较失败；此前bytes/inode保护与其余12方法通过。日志显示C:/Users/RUNNER~1与C:/Users/runneradmin指向同一个临时目录，不能由Path字符串不等推断竞争目标改变。原始step excerpt已保存，不重试该job。

只把C最后一行 `self.assertEqual(list((self.root / relative).iterdir()), [target])` 改成：
```
                members = list((self.root / relative).iterdir())
                self.assertEqual(len(members), 1)
                self.assertTrue(members[0].samefile(target))
```
原bytes/inode/mode/接受拒绝/发布调用数全部断言保留，无skip或异常吞掉；现在检查“只有一个目录成员且实际是竞争目标”。不改任何生产代码、CI矩阵或其它测试。

独立方案审核使用原Version55 max2中的第二次（完成后2/2），必须在原共享截止2026-10-29T14:24:07Z前完成；不运行或重置任何本地baseline/fixed/independent。审核通过后同一SYSTEM99稳定计划55→56并追加native说明、Progress；一次新源码提交触发一个新CI，不手动rerun旧job/旧workflow。新source native四Ubuntu/Windows×Python3.10/3.12完整13方法结果由真实CI日志读回，提交上限1，不重试；外部CI可在本地测试共享截止后结束，仅观察不派发旧分支。若失败继续保持未验，不回退/修剪旧失败记录。

这是同一修复的原生fixture纠正，不是新优化轮次、生产补丁或性能实验。手工独审不是可信runtime回执；无真实宿主/模型质量/全费用保证，macOS job不运行本模块。main唯一writer、guide只读、唯一TASK、无关untracked归档与全部旧耗尽/暂停门禁保持。发布前fetch，普通非forcemain和逐字回读，旧Version55证据不可修改为覆盖新testhash。
