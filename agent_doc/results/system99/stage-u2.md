# 阶段 U2：可复用文档工具链检查点

Task: SYSTEM-99；基线 `1d1c579ad9a8ac4b1a675f40e2ea577b26e477ca`。
本阶段续接现有 U2 方案，不计新的优化轮次。

## 既有结果与方案

实际 `result_store.py search 'documents profile pdf markdown pptx latex install'
--limit 3 --max-scan 500` 扫描255，partial=true、13个既有缺record错误；三条候选为
advice-context-20261009、combined-integration-v2/v3，仅有旧文档集成证据，没有安装能力，
不复用其数值或验收。当前U1只提供结构harness，基线不存在documents模块；
`git show HEAD:agent_runtime/documents.py` 实际退出128。

独立原生上下文 `/root/documents_u2_plan_review` 在当前基线读取方案后首次REVISE，要求
固定current JSON指针、安全普通文件锁、具体资源限额、adapter及解释器绑定和离线恢复；
主控采纳后APPROVE。真实工具上下文承担本次独立审核；没有伪称已部署ReviewSession或tmux服务。
宿主未提供tmux，本次不部署常驻监督器；没有新增付费模型调用、商业服务或凭据。

## 实现与依赖

- `config/documents-linux-cp312-v1.json`：10个直接/传递依赖，精确版本、wheel文件/tag、URL、
  SHA-256、许可和Requires-Dist；安装前复核当前tag和依赖闭包。
- `agent_runtime/documents.py`：显式install/probe及四种公开操作，专用root marker与flock、
  最终路径venv、`.incomplete`、原子receipt/current；同锁/adapter/解释器/许可组合重复安装
  复用既有环境，不调用pip/网络。失败保留旧current及未知incomplete诊断目录。
- `agent_runtime/documents_adapter.py`：PDF真实打开/提取/渲染、Markdown转换、PPTX生成重开、
  LaTeX严格模板及字符转义；same execute入口用于smoke。时间/地址空间/文件和输入上限见
  `docs/documents_profile.md`，不宣称OS沙箱或视觉/语义验收。
- SETUP新增显式入口，普通setup/import不安装；没有vendor二进制、TeX、FFmpeg、商业TTS。

2026-10-21通过PyPI每包发布JSON重新核对filename/hash，再从锁内files.pythonhosted.org URL
重新下载全部10个wheel，共37,453,456字节（包缓存不提交）；每个SHA都与锁一致。
`scripts/lock_documents_profile.py` 是显式维护入口，读取wheel metadata与PyPI记录，不安装。
官方依据：[pip hash模式](https://pip.pypa.io/en/stable/topics/secure-installs/)、
[PyMuPDF许可](https://pymupdf.io/licensing)。AGPL参数只用于本次隔离开发验证；没有替用户
生产部署选择或验证商业许可证。

## 实际结果与失败保留

CPython3.12.14、Linux x86_64、glibc2.39。首次受管离线安装10包成功；四能力均ready，
latex_compile unavailable。之后 `install --offline`（无wheelhouse）为reused，probe成功。
定向测试以mock禁止venv.create与subprocess.run，真实smoke仍通过，证明重复安装未调用pip。

```text
AGENT_DOCUMENTS_TEST_ROOT=/tmp/agent-documents-u2-smoke \
  python [-O] -m unittest tests.test_documents -q
普通: Ran 14 tests in 2.800s — OK
-O:   Ran 14 tests in 2.729s — OK
```

测试包含四个公开CLI实际产物、输出目录不覆盖、Markdown原始HTML关闭、LaTeX转义、平台、
root/祖先symlink、FIFO/symlink锁、互斥、许可、完整依赖、current路径穿越及incomplete拒绝。

首轮独审发现install/probe缺统一schema、非法输入误报unavailable、fcntl平台导入、PPTX合计
限额四项问题，已修复。最终公开CLI统一documents-result/v1：ok=0、unavailable=2、invalid=3。
独审自有root重新安装，普通/-O各14项通过；腐损PDF与18000字节PPTX实际CLI均退出3/invalid。
损坏wheel首次安装失败后旧current原207字节不变，旧环境probe继续ready；相同未知incomplete
重试被拒且未重建venv。最终结论 `ACCEPT / usable-with-scope`，见独立答复摘要。

首轮全库1570项：3错误/10跳过，三个错误均为最新并发提交TOK-MEM两详情缺Task-ID/Date，
阻断canonical snapshot/prepare。经独立确认仅补标题后两字段，其余原字节不改；原Plan/数据/
独审不重写，旧whole-file binding按既有stale规则处理。修后实际入口专项4/4通过。
全库最终1570项、1560通过/10跳过、99.840秒；两项新集成测试需要显式环境root，已在上述定向
真实环境执行，其余8项为既有可选检查。首轮失败与最终短日志另存stage-u2-tests.txt。

Paper Reader 3/3通过；sync_plugin_references --check、compileall、git diff --check通过。

## 独立答复摘要及冻结源码

实际 reviewer：`/root/documents_u2_plan_review`；生产者：`/root`。reviewer只读源码，执行仅
自有临时目录，未写实现或TASK。其最后答复明确接受当前实现范围并保留平台/质量/成本限制。

```text
documents.py aafdc98f85ce5c4b480700e200701622c176c1d1f0dd4601b9af113ed3085db2
documents_adapter.py 744eca3dd912b52c7ed9334b7cf0125ffc19b225c88c5d15755d75327f950554
documents-linux-cp312-v1.json dd3ab2926ea691e724b8fada91bdc01b84e92519966f6ef2e5563a1b3cedfb01
test_documents.py 680904fbb628bb8d8b36a849290af312849c13551dcaa90664ccda9b5b40ce52
```

## 未完成边界

能力从“仅有方案”变成当前平台4种实际操作可用，离线复用不再下载；没有实测模型质量、理解率、
任务成功率、TTFT、token/费用或普遍速度提升。LaTeX仅源码，编译仍unavailable；Windows/其它
Python/架构、敌意原生解析、排版与媒体质量、用户服务器部署均未验。SYSTEM-99整体继续open。
沿用同一未结束批次已有正文阅读记录；本检查点没有把旧批次阅读或官方安装文档冒充新论文精读。
