# 当前真实路径覆盖

这是一张验证映射，不是第二任务清单。目标源码基准为d0f7766b；每次报告另记录实际HEAD和工作树指纹。先核对当前prompt和现有 `agent_doc/guide/GUIDE.md`，不把这张表当授权。

| 功能/要求 | 实际入口与操作 | 可观察通过条件 | 检查 |
| --- | --- | --- | --- |
| 文档初始化与人类guide保护 | scripts/project_docs.py --root 临时项目 init | 唯一索引存在、guide没有生成文件、无错误cwd写入 | test_live_project_docs.py |
| 重复初始化 | 同一真实CLI重复init | 既有文件逐字节不变 | test_live_project_docs.py |
| 错误目标拒绝 | 对不存在的目录调用init | exit2、目标仍不存在 | test_live_project_docs.py |
| 外置测试执行与停止 | scripts/project_test.py 对相邻Git项目执行脚本 | 目标绑定正确、失败/超时后后续not-run | test_project_test.py |
| 禁止新普通Python注释 | comment_policy.py 对Git新增行检查 | 原版通过、普通注释变异失败、必要指令保留 | test_comment_policy.py |

启动/健康检查：使用agent的.venv解释器，真实CLI --help成功后在临时项目运行；CLI正常退出后核对文件，不能只看进程存在。运行命令见README。原始CLI动作/返回值进入regression.log；临时项目清理后日志仍由外层检查入口保存。维护时每行核对源码并重跑，产品回归不能改表掩盖。

尚未覆盖：集中GUIDE/TASK迁移、真实模型后端、服务/界面驱动及受管恢复全链。这里验证的是现有文档CLI行为，不把其旧项目内布局称作已完成新架构。
