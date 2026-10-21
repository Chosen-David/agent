# U2 独立复核

实际工具上下文 `/root/documents_u2_plan_review`；主控按原答整理归档，独立角色未写源码/TASK。
以下保留最终答复及先前返修，不把文本本身当宿主认证回执。

## 最终原答

最终结论：`ACCEPT / usable-with-scope`，U2 当前实现未发现剩余阻断。

独立审查与执行范围：

- 当前基线 `1d1c579ad9a8ac4b1a675f40e2ea577b26e477ca`，审阅安装器、公开 adapter、wheel 锁、锁生成脚本及测试。
- 初轮发现并要求修复：install/probe 外层 schema 缺失、非法输入误报 unavailable、Windows 导入 fcntl 提前崩溃、PPTX 分别限额绕过合计 16000 字节。当前源码均已修复。
- 自有根 `/tmp/agent-doc-u2-review-wcqhZH/managed` 真实离线首次安装、四能力 smoke、probe、离线重复安装均成功。第一次版本和最终 adapter 变更后的新 identity 环境均保留。
- 10 个 wheel 的本地 SHA-256、版本、`Requires-Dist` 与冻结 lock 一致；当前依赖闭包/tag 检查通过。
- 真实坏 wheel 安装失败后，旧 `current.json` 原 207 字节保持；旧环境 probe 仍成功。未知 `.incomplete` 重试拒绝，mock 证明未重新创建 venv。
- 普通与 `-O` 定向各 14/14 通过，含四个公开 CLI 的实际产物和离线复用不调用 pip/venv。
- 独立补验腐损 PDF：退出 3、`documents-result/v1`、`invalid`、`Failed to open stream`，无输出文件。
- 独立补验 title/body 合计 18000 字节 PPTX：退出 3、`invalid`、`slide text exceeds 16000 UTF-8 bytes`，无输出文件。
- probe 成功外层为 `documents-result/v1/status=ok`。

执行命令：

```bash
python -m agent_runtime.documents \
  --root /tmp/agent-doc-u2-review-wcqhZH/managed install \
  --pymupdf-license agpl-3.0 --offline \
  --wheelhouse /tmp/agent-doc-profile-wheels

python -m agent_runtime.documents \
  --root /tmp/agent-doc-u2-review-wcqhZH/managed probe

python -m agent_runtime.documents \
  --root /tmp/agent-doc-u2-review-wcqhZH/managed install \
  --pymupdf-license agpl-3.0 --offline

AGENT_DOCUMENTS_TEST_ROOT=/tmp/agent-doc-u2-review-wcqhZH/managed \
  python -m unittest tests.test_documents -v

AGENT_DOCUMENTS_TEST_ROOT=/tmp/agent-doc-u2-review-wcqhZH/managed \
  python -O -m unittest tests.test_documents -v
```

最终检查代码摘要：

```text
documents.py
aafdc98f85ce5c4b480700e200701622c176c1d1f0dd4601b9af113ed3085db2
documents_adapter.py
744eca3dd912b52c7ed9334b7cf0125ffc19b225c88c5d15755d75327f950554
documents-linux-cp312-v1.json
dd3ab2926ea691e724b8fada91bdc01b84e92519966f6ef2e5563a1b3cedfb01
test_documents.py
680904fbb628bb8d8b36a849290af312849c13551dcaa90664ccda9b5b40ce52
```

并发文档整合修复亦批准：两份 TOK-MEM 详情只新增匹配 `Task-ID` 和 `Date: 2026-10-21`。
必须保持其余字节与历史证据不变，并按现有规则将旧整体文档 bindings 标为 stale。

限制：本次 AGPL 选择只用于隔离开发验证；没有替用户部署选择许可证。未验证其他平台、TeX 编译、
视觉质量、LLM 质量、性能/费用或真实部署。未修改源码或 TASK，也未发布。

## 方案首轮返修原文

已核对 current main 1d1c579a、空人类 GUIDE 和 U2 方案 L120–169。方向在现有用户授权及已接受 U2 范围内；但实现前需冻结三个具体接口条件，否则暂为 REVISE：① current 用受限 JSON 指针而非任意可跟随 symlink，锁须普通文件/O_NOFOLLOW/NONBLOCK、覆盖整个 install/reuse/probe 发布窗口，旧receipt/current失败保持；② adapter 固定具体 byte/page/pixel/timeout 上限、结构化失败状态，并为 Markdown 明确 HTML 禁用/不承诺安全浏览器沙箱、LaTeX反斜线和{ }等完整转义；③ receipt 除版本还绑定 adapter源码哈希和解释器实际身份，reuse/probe重新核对版本+smoke，已存在 incomplete 不可当成功、清理仅可确认本工具拥有的目录。

## 实现首轮返修原文

首轮代码审查发现一个合同阻断：documents.main 的install/probe成功输出分别是 {status:installed/reused,...}/{status:ready,...}，缺schema_version，与已冻结所有公开命令 documents-result/v1 + ok/invalid/unavailable 不一致；run_adapter把adapter invalid统一转成ValueError，main再报unavailable，非法用户输入与能力缺失混淆。请统一外层CLI envelope(status=ok, result内放install_state/receipt等)，保留invalid与unavailable错误类别并定向测实际CLI。另 Linux-only v1顶层import fcntl在Windows导入即崩；可移到Linux路径或明确平台check前不导入，若不承诺其它平台CLI则如实记录。

冻结“每页文本<=16000”，adapter当前分别允许title/body各16000（合计32000），请按合计16000检查或明确版本化实际字段限额，不默改冻结边界。

## 最终发布整合原答

最终发布整合 ACCEPT(scope-limited)，无blocker。四源码hash与我的冻结完全一致；docs命令与当前argparse/API相符，SETUP/docs/stage-u2本地Markdown链接均存在；两个TOK-MEM通过独立Python逐字节逆删除新增metadata后与HEAD blob完全相同；专项 tests.test_repository_task_integration 独立4/4通过(0.479s)，diff --check通过。实际读回全库两个/tmp原log并重算SHA，分别42c8cb...aed0a(1570/3error/10skip)和5f9c5c...2da7(1570/OK/10skip)，与归档短日志相符；没有重跑全库。报告保留失败、latex unavailable、未验证平台/质量/成本/部署及SYSTEM99 open，未过度claim。可进入fetch/并发复查/普通发布与远端回读。
