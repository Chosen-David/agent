# STATE-UTF8-01

## Plan

同一SYSTEM-99批次，基线653b1f7d1670208be951fdf22159d588a8381c90。公共atomic_json写入使用默认locale，但读取契约UTF-8；在非UTF-8环境写中文/emoji失败。仅将fdopen显式设encoding=UTF-8，不改变字段、JSON格式、fsync/replace、所有权及回滚边界。普通低风险编码修复按轻量回归，不涉及架构或权限协议变更。

验收：先保存ASCII locale真实子进程失败；创建与替换非ASCII状态成功，严格UTF-8解码值一致；NaN序列化失败仍保留旧状态并清理临时文件；相关task manifest/supervisor/crash回归、-O及实际3.9验证。仅提交本次路径；发布前fetch，不强推，远端回读。无性能/模型或整个批次完成主张。

## Progress

- 修前新增2项测试3个failure（创建/替换两个subtest与序列化异常类型）；UnicodeEncodeError阻断写入。原日志私有保留；最初直接在ASCII环境传中文argv导致命令解码错误，已改ASCII Unicode转义argv并确认进入真实函数，未把前者当生产复现。

- 修后3.12相关47、-O专项2、监督16(1skip)；实际3.9专项5通过。3.9扩大47出现结果检索1error，独立子进程执行基线原模块同样失败；根因另查，不报全绿。见[证据](../../advice/STATE-UTF8-01.md)。单行编码修复由主AI轻量复核；未验真实Windows/后台/性能，SYSTEM99仍open。发布及回读另核。

发布前并发main新增5e2415b7共享引用去重；本次补丁已重放，未覆盖其154文件改动。合并后同组63项17.745s通过(1skip)，日志atomic-utf8-rebased-1803.log；发布父提交为5e2415b7c870dda1221ade0c750c5f2607c85b42。
