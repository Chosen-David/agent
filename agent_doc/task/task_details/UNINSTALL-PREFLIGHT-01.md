# UNINSTALL-PREFLIGHT-01

Task-ID: UNINSTALL-PREFLIGHT-01
Date: 2026-10-23

## Plan

同一SYSTEM-99批次，基线0b2453a67b6b22a537bdd3dcefd2c457a33a57f3。仅修卸载受管manifest类型预检：在删除前确认对象、files/links映射、skill_copies可选映射及files/links字符串值。保留所有权、已编辑文件保留、旧manifest缺skill_copies兼容、路径/guide与原I/O语义，不承诺任意磁盘异常回滚。

验收：保留损坏links触发22文件先删后异常的修前复现；六种坏形态和实际CLI均删除前拒绝、文件及链接逐字保留；普通/-O、3.9及便携回归与独立复核。仅提交本次路径，发布前fetch，普通push及远端回读。无性能或系统批次完成主张。

## Progress

- 修前2项测试出现1 failure/6 subtest errors；最小复现links=[]导致AttributeError之前22/22受管文件已删除，manifest与Skill链接仍在。原日志私有检查点保留。
- 新增删除前类型校验，失败转为现有CLI支持的ValueError；修后普通专项及setup/recovery35通过、-O专项2通过。实际Python3.9.25与3.12.14各39相邻回归通过；独审另验6种坏清单快照不变、旧清单兼容和复制安装本地编辑保留，结论usable-with-scope；SYSTEM-99原协议冲突/真实宿主与全任务quality/usage缺口继续open。

- 完整证据见[简报](../../advice/UNINSTALL-PREFLIGHT-01.md)和其中独立探针；没有性能主张。发布及远端回读另核。
