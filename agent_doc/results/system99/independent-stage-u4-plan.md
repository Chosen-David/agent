# SYSTEM-99 / U4 tmux 使用体验方案独立复核

状态：`APPROVE plan / resources blocked`。本记录只批准
[Version 34受阻方案](stage-u4-plan.md)，不是实现、真实会话或体验收益回执。

## 返修轨迹

- Version 32：`REVISE`。要求收窄平台与许可陈述、避免把`dpkg-deb -x`部分失败当成功、固定resolver
  与既有server漂移处理、澄清鼠标语义，并补可恢复卸载合同。
- Version 33：`REVISE`。剩余阻塞为共享库SONAME输出未闭合、错误承诺`utmp_updates=false`、固定
  socket下非current卸载及current部分删除恢复不完整，且配置读回不够穷尽。
- Version 34：只读复核文件SHA-256
  `e20a92de56e386d26c392e25c9dea2c4169ce57b37b19610ceb8c7d701f56454`，结论`APPROVE`。

## 最终复核结论

1. tmux及两项动态库均已固定archive、真实ELF源成员、普通SONAME输出、mode、SHA-256与
   `LD_LIBRARY_PATH`；缺SONAME输出是明确负控。
2. 许可/copyright边界保留完整archive集合；libutempter只承诺
   `bundled_utempter_helper=false`，utmp行为明确为宿主相关/未知，并要求各阶段记录绝对helper状态。
3. resolver对显式root、默认root和PATH均fail-closed；既有及新server都须精确读回config ID、其余
   九项配置和root `WheelUpPane`绑定，漂移时不杀server、不换socket、不覆盖会话。
4. 固定socket下删除任意version前均须得到明确无server；current原子撤销/切换、version墓碑rename、
   receipt清单删除和逐中断恢复保证current不指向部分删除目录。
5. 目标、guide边界、假设、既有结果、验收和风险均通过。资源域为`blocked`：当前宿主禁止
   AF_UNIX socket，无法真实创建tmux server/session；方案已据此禁止接入默认supervisor或向main发布
   生产实现。

复核者未修改文件，未把静态检查、archive核对或`tmux -V`当成真实session验证。当前可发布内容仅为
`PROPOSED / blocked-on-real-host`方案检查点；真实宿主门禁通过前不得声称U4功能完成。
