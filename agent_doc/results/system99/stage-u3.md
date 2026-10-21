# 阶段 U3：文档产物原子发布检查点

Task: SYSTEM-99；问题ID `CHAIN-DOCUMENT-ATOMIC`；基线
`a87347c7b1d1d90d5bd2714447a4a4bb4aef7faa`。这是同一系统级批次的可恢复检查点，不计新一轮完成。

## 触发、根因与修前失败

真实入口为 `python -m agent_runtime.documents ... pdf-read`，调用
`agent_runtime.documents.run_adapter` 后进入固定venv的 `documents_adapter.execute`。
两页PDF依次请求1、3页时，第1页PNG已经直接写入公开目标，第3页越界才返回invalid；宿主不回滚目标。
修前真实短日志（CPython3.12.14、Linux x86_64、glibc2.39、既有U2固定profile）：

```text
exit_code=3 status=invalid error="page number outside PDF"
output_exists=true output_files=["page-1.png"]
```

因此失败产物可被误当成完整结果，而且公开合同要求目标目录全新，用户不能用修正后的页码在原路径重试。

## 方案与实现

独立方案审查 `/root/system99_u3_plan_review` 首轮 `REVISE`：Linux `os.rename`会替换并发创建的空目录，
与不覆盖合同冲突。Version30采纳后获 `APPROVE / scope-limited`：

- 公开操作只写目标同父目录的随机staging；probe保持既有内部临时目录。
- 成功且结果envelope校验后，以同一父目录FD调用
  `renameat2(RENAME_NOREPLACE)`整目录发布；`EEXIST/ENOTEMPTY`为invalid并保留抢占者。
- 系统调用缺失或不支持时返回unavailable，绝不退回可能覆盖目标的rename。
- 失败、超时、invalid及发布冲突只清理本次staging；清理前重开并比对`(dev, ino)`，身份变化时不删除
  未知对象并要求人工恢复。

实现位于 `agent_runtime/documents.py` 的发布helper与`run_adapter(..., publish=True)`；未改依赖锁、
adapter文档语义、输入上限、资源限制或公开JSON schema。`docs/documents_profile.md`同步说明恢复合同。

## 当前验证

定向普通与`-O`各20项通过，覆盖invalid后无目标并同路径成功、timeout清理、嵌套父目录、空/非空
并发目标不覆盖、no-replace不可用无回退、staging身份漂移不删除，以及真实四能力与离线复用。
真实profile复验：越界请求仍exit3/invalid，目标不存在；随后同一路径请求1、2页exit0/ok，最终仅
`page-1.png`、`page-2.png`。全库1576项（1565通过/11skip，103.645秒）；三个新集成测试需要
显式文档root，已在定向真实环境执行，其余8项为既有可选检查。Paper Reader 3项、仓库任务入口4项、
`sync_plugin_references.py --check`、`compileall`与`git diff --check`通过。全库原日志SHA-256为
`ac84f68165290bc722f15c1615f078d0f56209a45d7018edbe7427b194b135e2`。

发布前fetch发现并发main已从`a87347c7`推进至`09d523eb`，包含TOK10第1至3轮。U3在新main上
无冲突重放后，文档专项普通/-O仍各20项通过。首次全库重跑真实暴露并发提交新增的三个未索引
详情，以及同批父任务/独立验收详情缺canonical `Task-ID`/`Date`；该次1579项留下3个error和1个
既有`/proc`瞬态failure，没有被改写成成功；失败日志SHA-256为
`29856951d32ed1b7292e024f34c24eeaa8caa60438b25aae360fc34058d59758`。整合只新增五个详情的身份/日期、三条准确索引并把
父摘要由2/10改为3/10；逐文件逆投影证明去掉新增元数据后与`09d523eb`原blob逐字节一致。
仓库任务入口随后4/4通过，最终全库1579项全部执行成功、11项跳过（104.469秒），日志SHA-256为
`86342a19997168736a155a511167c803cc8373954c4b9f3b409d7a03a7e6e14a`。
独立复核在最终重放候选上再次执行任务入口4/4、专项普通/-O各20/20及diff-check，核对最终全库
日志与五份并发详情逆投影后结论为`ACCEPT / usable-with-scope`；未独立重跑最终全库。

第二次发布前fetch又发现main推进到`e5cdac5a`（TOK10第4至8轮）。重放保留其代码、结果和验收原件，
仅把批次摘要纠正为8/10、为第4至8轮增加同样窄范围索引，并补齐新明细身份；第1至8轮及父详情去掉
本候选新增元数据后都逐字节等于各自最新main原blob，独立验收详情的元数据已由并发作者写入而未重复修改。
该main还把`agent_runtime.project_docs`新增的相对导入漏同步到独立分发Skill：第一次全库因此以生成引用
过期失败（日志SHA-256 `92980ab709a2533693560b829851b9859479bf2dd1d06e781df31e8f6ef8ea48`）；
机械同步后又由两个真实isolated CLI回归证明相对导入没有package上下文（日志SHA-256
`809e38b15c741a3c8b0cebb1e9b956483870a7b5ebf692d0a7991d57607d3a55`）。最终修复让
`project_docs`在package内保持相对导入、独立脚本使用同目录绝对导入，并重新生成唯一镜像。
知识索引/读取边界、引用同步和任务入口共24项通过；最新main上的最终全库1579项全部执行成功、
11项跳过（104.120秒），日志SHA-256为
`0f5349d08337506aeba9185bf101f1d35fa8b6a3e26da91e2f308564cf2c0f83`。

第三次发布前fetch发现main又推进至`df5c46fc`（TOK10第9轮）。候选再次重放其全部代码、结果与独立
验收原件，仅把批次摘要更新为9/10、增加绑定该远端提交的窄范围索引，并为新明细补规范身份；去掉
该元数据可逐字节还原远端原blob。受影响验证须在此最新源码上重新执行，不能沿用上一轮全库日志
冒充最终发布证据。

第四次fetch确认TOK10批次以`cb5b60d3`完成第10/10轮。候选在该最终main上重放，只把父项闭合为
10/10、增加绑定远端提交的第10轮窄索引并补明细身份；不改其代码、结果或独立验收原件。此前
`df5c46fc`上的任何通过记录仍只作中间证据，最终发布必须使用本次重放后的隔离专项、全库和独立复核。
最终main上的model-routing、token10、任务入口、生成同步及知识索引/读取边界合计39项通过，Reader3项
通过；全库1579项全部执行成功、11项跳过（106.397秒），最终日志SHA-256为
`e69d31a49eed0b4354d2fbf074b28fe0d586123813663e80aa51232b94a03bf3`。

早期独立结果验收 `/root/system99_u3_plan_review` 仅针对`a87347c7`基线候选，实际重跑普通20/20（4.016秒）、
`-O` 20/20（4.006秒）、任务入口4/4、Reader3/3及同步/编译/diff；另从未修改旧工作树复现修前
残留，从候选复验失败无目标和同路径成功。独立读取全库原日志，SHA与上文一致并重算
1576=1565通过+11跳过、0失败/错误。该早期结论不能替代后续并发重放验收。

最终`cb5b60d3`重放候选的独立复核重新执行知识索引/读取边界与仓库任务入口23/23、文档普通
20/20（4.637秒）、`-O`20/20（4.134秒）、生成同步及核心/镜像逐字节核对；第1至10轮和父详情
逆投影等于最新main，VERIFY无差异。复核读取最终全库日志并核对上述SHA、1579项/11skip/
106.397秒，但未独立重跑全库。报告窄修订后最终结论为`ACCEPT / usable-with-scope`。

第五次fetch取得TOK10最终整合证据提交`528aa9bb`；上游已自行补齐10轮索引、详情身份与最终独立
验收，因此候选完全采用上游任务记录并删除此前本地治理差异。该提交不改U3运行时代码；仍在其最终
源码/文档树上重跑token10、任务入口、引用同步和知识边界27/27，文档普通/-O各20/20，Reader3/3。
全库1579项全部执行成功、11项跳过（108.984秒），发布候选最终日志SHA-256为
`1a5b5f610217c8dd3cd2dc0f58c069ea6423175b488f78ca154bf9c007446e8f`。

冻结文件SHA-256：

```text
agent_runtime/documents.py 10b6d7a14db1458588094ee244ac2ec270cb50a3e89a484e43ffd9ad69de6efd
tests/test_documents.py 8030457feeda3ea8ee5bed745ae17a43a14bd19baeab8e144a8e56423e9d445c
docs/documents_profile.md 6ce00a2c269c1851d3a95a31aecd8643cc1643f151759b04f5e4258020bbdaf5
```

发布仍待执行，不能把本记录视作整批最终验收。

## 未验证边界

本阶段不认证敌意父目录替换、跨主机/网络文件系统、Windows或其它profile；不产生速度、token、费用、
模型质量、视觉质量或TeX编译收益。原生解析器仍非OS沙箱；SYSTEM-99和完整优化轮次继续open。
同UID恶意进程在staging身份复核后瞬时替换随机目录的竞态也不在新增认证范围。
独立Skill导入修复只认证已公布的knowledge index/ingest入口间接加载`project_docs`及生成同步；直接
`python -I .../project_docs.py`仍因隔离模式不加入脚本目录而不可用，且不是已公布Skill入口。此修复
不认证所有安装布局或第三方打包器。
