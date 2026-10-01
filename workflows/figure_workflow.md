# 通用论文作图 Agent Workflow

[返回仓库首页](../README.md) · [主 AI 调度入口](../prompts/orchestrator.md)

从动态发现当前合适的 Skill，到理解研究材料、选择图型、绘制、精修、拼版和交付。

适用范围：不同学科的理论、方法、实验、仿真、观察、综述、定性及混合论文；既支持新图，也支持已有图精修和投稿修改。包括各类 Infra 技术论文，但不绑定某个模型、技术点或指标。

**每次新项目的第一步是重新评估当下可用的 Skill；本文现有 GitHub 清单只是后备。** 同一论文持续出图时锁定已选版本，保持可复现。模板不要求每次追逐最新工具，也不把过时仓库当永久最佳推荐。

使用顺序：第 1 节动态选型 → 按实际选择安装（第 2 节为后备配方）→ 第 3–4 节识别任务与准备材料 → 第 5 节执行 → 第 6 节完整 Agent Prompt。已有材料不需要先整理成固定目录，直接把材料位置和第 6 节 Prompt 交给 Agent 即可。

本文件提供工作流程，不代表已在你的机器安装工具或执行研究。历史后备资料核查日期为 2026-10-01；未来运行应填写当次实际查询日期和版本。“投稿级”以内容准确、表达清晰、最终尺寸可读、源文件可编辑及生成过程可追溯为验收目标。

## 1. 第一步：动态发现、评估并选择当下合适的 Skill

**不要直接安装本文列出的历史 Skill。** 每次新项目或用户要求重新选型时，先运行本节；本节也包含在第 6 节总 Prompt 中。先根据任务说明提取能力需求，再寻找当前候选。无需先完整分析所有论文数据。

本模板长期稳定的是作图目标、证据要求与验收方法；Skill 名称、仓库、安装路径和推荐版本均可替换。没有可验证的更合适替代时，再采用第 2 节的后备组合。不能把“未找到已验证的更优候选”表述成“网上不存在更好的 Skill”。

### 1.1 按能力检索，而不是只搜旧名称

先读取当前 Agent 平台的官方 Skill 文档，确认它现在支持的格式、安装位置、触发方式和工具权限，再检查本机已安装的能力。平台不限于 Claude Code；使用其他 Agent 时依据该平台当前文档调整，不机械照搬 `.claude/skills/`。

| 需要的能力 | 可使用的搜索方向示例 | 评估时实际查看什么 |
| --- | --- | --- |
| 研究材料→图规划 | `scientific figure planning agent skill`、`research visualization skill` | 是否先看研究问题和证据；能否解释图型选择 |
| 方法/结构/理论示意 | `academic diagram SVG TikZ skill`、`paper architecture figure agent` | 可编辑源、符号/箭头准确性、最终尺寸示例 |
| 数据图和精修 | `publication visualization skill`、`matplotlib figure refinement skill` | 真实数据读取、统计边界、脚本和矢量导出 |
| 多面板与验证 | `scientific multipanel layout skill`、`figure visual QA agent` | 是否实际渲染读图，是否保留正确尺度和主源 |
| 当前研究的专门图 | `[当前技术点] [图类型] visualization skill` | 是否匹配真实对象和现有工具，不只是关键词相近 |

例如 Infra 论文可能需要调度时间线、设备拓扑、通信模式、性能拆解、内存布局或执行追踪；这些由本次研究内容触发，不固定在通用模板中，也不预设一定属于某个模型或算子。

从公开搜索、GitHub、Agent 平台当前官方目录等发现候选；合集和排行榜只是线索。关键事实回到仓库实际 `SKILL.md`、README、release、代码与示例核实。优先查看和本任务相近的样例，不凭宣传用语判断“顶会级”。

### 1.2 实用的检索与停止范围

默认每项实际需要的能力筛选 2–3 个可信候选，合并重复仓库和套壳项目。若一个已验证的候选覆盖多项能力，可以少装几个 Skill。单张图任务只评估其需要的能力，不遍历整个生态。

初筛后只对最有希望的候选做深入阅读或小规模试绘。覆盖所需能力、明确取舍后即可停止；声称全网穷尽或无限检索没有必要。GitHub star 数、更新时间和“latest”标签都不能单独决定质量。

### 1.3 对候选做可核实比较

| 比较维度 | 需要回答的问题 |
| --- | --- |
| 任务匹配 | 能否处理本次实际图类型、素材和语言？ |
| 科学内容保持 | 是否保留原始数据、单位、分析定义、来源与结果边界？ |
| 输出与编辑 | 是否给出真正的 SVG/TeX/绘图源码，而不只是不可编辑图片？ |
| 视觉质量 | 可见样例在论文实际尺寸下是否清楚；复杂图是否有成功例子？ |
| QA 与复现 | 是否真的渲染、检查、修正并记录生成过程？ |
| 当前可用性 | 最近 release/commit、文档与代码是否一致，相关未解决问题是否影响本任务？ |
| 运行代价 | 与当前平台兼容吗；需要哪些依赖、API、付费服务和本地资源？ |
| 迁移成本 | 是否保留既有可编辑图源、style、项目结构和重绘流程？ |

把“仓库自述”“阅读源码确认”“示例观察”“本次实际运行”分开记录。没有试运行，不能声称已验证运行质量。长期稳定且可复现的工具可能比刚更新但依赖失效的工具更适合任务。

### 1.4 什么情况下算有更合适的替代

不是必须在所有指标上全面胜出。替代某个既有 Skill，需要：

1. 满足本任务必须的能力与输出要求；
2. 在重要问题上有具体收益，例如更好的公式支持、稳定拼版或有效的视觉 QA；
3. 代价和缺失能力已明确，不损害本任务所需的准确性、编辑性和可复现性；
4. 有足够的可验证资料，必要时通过最小试绘。

按**能力角色**替换，允许只替换一个环节。新套件确实覆盖多个环节时，可合并；不要为了让清单显得新而整体换工具。

为选择结果写一张简表：

| 能力角色 | 候选与网址 | 已验证事实 | 取舍或未验证项 | 决策 |
| --- | --- | --- | --- | --- |
| [本次需要的角色] | [实际检索结果] | [来源和验证级别] | [依赖、限制等] | [采用/保留/后备] |

首次选型可用不含用户研究材料的最小测试案例：有公式和分支的示意图、小型带明确标签的合成数据图、组合 panel 等。合成值只用于工具测试，写入隔离的 `tool_eval/` 并标为 synthetic，绝不进入论文结果。已有可靠运行证据时不必重复测试。

### 1.5 版本、安装与后备决策

选型完成后，再按选中仓库和当前平台官方说明安装。读取实际入口及依赖，不把任意 README 中的脚本当通用安装器。自动化范围内可完成项目级安装；需要新增付费账号或权限而当前无法满足时，报告具体限制并继续其他可用路径。

“查看最新版本”和“固定所用版本”要同时做到：检查当前稳定 release/tag 和默认分支状态，选择有依据的版本，记录 tag（如有）和精确 commit；不要无条件选择最新提交。记录复制安装后的实际文件校验和/本地修改状态，避免 lock 中只有上游版本而丢失本地差异。

建议将选择结果写入 `docs/skill_selection.md` 和 `docs/skill_registry.yaml`，实际版本写入 `docs/skill-sources.lock.json`。单图可将前两份合并到图的工作记录。

```yaml
checked_at: null                 # 实际查询时间，由 Agent 填写
platform: null
platform_docs_url: null          # 本次核对过的官方文档
selection_status: unresolved     # evaluated / offline_fallback / provisional
roles: []                       # 每项记录 role、name、repo_url、entry_path、version、reason
evaluation_artifacts: []         # 若实际试绘，记录路径
unverified_items: []
```

按下列规则处理特殊情况：

- **没有验证出更适合的候选**：保留可用的已安装 Skill，或采用第 2 节后备候选，并核查其当前入口是否还有效。
- **无法联网**：使用本地已验证版本；若只有历史网址而无工具，不称其为已安装。允许用已有绘图库或 SVG/TikZ 完成可行部分，标记 `offline_fallback`。
- **旧仓库已删除、归档或不兼容**：不因为它在后备清单中就强装，重新寻找符合能力要求的替代。
- **同一论文继续作图**：优先沿用已锁定版本和风格，不在每一张图前重新选型。
- **新论文、跨平台迁移、原工具失效，或明确要求更新**：重新发现和评估。必要时对新旧版本做小样比较后再切换。

## 2. 后备 Skill 清单及安装配方

以下是 **2026-10-01 核查过的后备起点**，不是未来每次运行时的默认赢家。先完成第 1 节，再安装被选中的条目；若采用其他候选，依据其实际文档生成安装步骤，不执行不相关的旧命令。


### 2.1 历史后备能力映射

这组候选覆盖示意图、数据规划、数据绘制和精修。按本次实际需要选择，TikZ 和多面板布局可补充。新候选可以替换或合并这些角色。

| 优先级 | 仓库 / GitHub 地址 | 实际 Skill 入口 | 本工作流分工 |
| --- | --- | --- | --- |
| 对应角色后备 | [ThalesGroup/agilab：scientific-svg-figures](https://github.com/ThalesGroup/agilab/tree/main/.claude/skills/scientific-svg-figures) | `.claude/skills/scientific-svg-figures/SKILL.md` | 架构图、方法图、数据流图，SVG 主路线 |
| 对应角色后备 | [Haojae/scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill) | 仓库根目录 `SKILL.md`，名称 `scipilot-figure-skill` | 检查数据、确定实验图型及表达目标 |
| 对应角色后备 | [tvhahn/matplotlib-skill](https://github.com/tvhahn/matplotlib-skill) | `skills/matplotlib/SKILL.md`，名称 `matplotlib` | 编写可复现的数据绘图脚本 |
| 对应角色后备 | [preordinary/science-plot-formatter](https://github.com/preordinary/science-plot-formatter) | `.claude/skills/beautify-chart/SKILL.md`，名称 `beautify-chart` | 对现有脚本按最终论文尺寸精修 |
| 可选后备 | [Noi1r/tikz-academic](https://github.com/Noi1r/tikz-academic) | 仓库根目录 `SKILL.md` | 公式、张量符号较多时，用 TikZ 替代 SVG 主路线 |
| 可选后备 | [sai-tv/academic-figures](https://github.com/sai-tv/academic-figures) | 仓库根目录 `SKILL.md` | 为混合架构图与实验图设计多面板布局草案 |

三个需要纠正的使用细节：

1. `science-plot-formatter` 是仓库名；调用时应指定 **`beautify-chart`**。
2. `scientific-svg-figures` 的文档引用了同仓库 `svg-diagrams/scripts/check_svg_markers.py`。下载时保留关联目录；若当前版本缺失，应明确报告并做替代检查，不能声称运行过这个检查器。
3. `academic-figures` 的主要交付包含布局变体和数据图占位框。它不是已经完成实验图嵌入的自动拼版器；替换真实图、检查字体与矢量导出仍由作图 Agent 完成。

架构图以 SVG 或 TikZ 中的一种为主源文件，不要默认先画 SVG、再整张转写成 TikZ。纯实验多面板优先由 Matplotlib 统一排版；只有混合不同类型素材时，才需要额外拼版。

本流程不依赖 PaperBanana 等图像生成后端。模块、箭头、张量、公式和实验数值优先采用确定性的矢量构造。

### 2.2 后备组合的 Claude Code 安装示例

仅在第 1 节评估后决定采用这组后备 Skill、且当前平台仍支持下述机制时使用。以下完整配方安装四个核心角色；只需要其中一部分时，保留函数定义，仅执行对应下载/复制段。选中新替代时使用其当前安装文档。

#### 2.2.1 确定运行位置

在你实际启动 Claude Code 的机器上安装：如果 Claude Code 在远程 Ubuntu 上运行，就在远程安装；如果在 WSL 中运行，就在 WSL 中安装。

推荐项目级安装：`你的论文项目/.claude/skills/`。用户级安装位置是 `~/.claude/skills/`。本文统一采用项目级目录，便于每篇论文记录所使用的版本。[Claude Code 官方 Skill 文档](https://code.claude.com/docs/en/skills)

先进入项目根目录，例如：

```bash
mkdir -p ~/research/my-paper
cd ~/research/my-paper
```

#### 2.2.2 下载并复制 Skill

下面整段在同一个 Bash 会话执行。它下载四个核心仓库，保留 Skill 的 references、scripts 等资源，并记录提交号；遇到同名已安装目录时会停止，避免覆盖你的修改。

```bash
set -euo pipefail

FIG_PROJECT_ROOT="$PWD"
FIG_VENDOR_ROOT="$FIG_PROJECT_ROOT/.figure-skill-sources"
FIG_SKILL_ROOT="$FIG_PROJECT_ROOT/.claude/skills"
mkdir -p "$FIG_VENDOR_ROOT" "$FIG_SKILL_ROOT" "$FIG_PROJECT_ROOT/docs"

clone_once() {
  local url="$1" dest="$2"
  if [ -e "$dest" ]; then
    test -d "$dest/.git" || { echo "Not a git checkout: $dest" >&2; return 1; }
    test "$(git -C "$dest" remote get-url origin)" = "$url" || {
      echo "Unexpected repository at $dest" >&2
      return 1
    }
    echo "Reuse checkout without updating: $dest"
  else
    git clone --depth 1 "$url" "$dest"
  fi
}

copy_skill() {
  python3 - "$1" "$FIG_SKILL_ROOT/$2" <<'PY'
import shutil
import sys
from pathlib import Path

src, dst = map(Path, sys.argv[1:])
if not (src / "SKILL.md").is_file():
    raise SystemExit(f"Missing SKILL.md: {src}; inspect repository layout first")
if dst.exists() or dst.is_symlink():
    raise SystemExit(f"Already installed: {dst}; inspect or back up before replacing")
shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
print(f"Installed: {dst}")
PY
}

# agilab 较大：只检出架构图 Skill 及其关联检查目录。
if [ ! -e "$FIG_VENDOR_ROOT/agilab" ]; then
  git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/ThalesGroup/agilab.git "$FIG_VENDOR_ROOT/agilab"
  git -C "$FIG_VENDOR_ROOT/agilab" sparse-checkout set \
    .claude/skills/scientific-svg-figures .claude/skills/svg-diagrams
else
  test "$(git -C "$FIG_VENDOR_ROOT/agilab" remote get-url origin)" = \
    "https://github.com/ThalesGroup/agilab.git"
fi

clone_once https://github.com/Haojae/scipilot-figure-skill.git \
  "$FIG_VENDOR_ROOT/scipilot-figure-skill"
clone_once https://github.com/tvhahn/matplotlib-skill.git \
  "$FIG_VENDOR_ROOT/matplotlib-skill"
clone_once https://github.com/preordinary/science-plot-formatter.git \
  "$FIG_VENDOR_ROOT/science-plot-formatter"

copy_skill "$FIG_VENDOR_ROOT/agilab/.claude/skills/scientific-svg-figures" scientific-svg-figures
if [ -f "$FIG_VENDOR_ROOT/agilab/.claude/skills/svg-diagrams/SKILL.md" ]; then
  copy_skill "$FIG_VENDOR_ROOT/agilab/.claude/skills/svg-diagrams" svg-diagrams
else
  echo "svg-diagrams is absent; record checker unavailability in QA."
fi
copy_skill "$FIG_VENDOR_ROOT/scipilot-figure-skill" scipilot-figure-skill
copy_skill "$FIG_VENDOR_ROOT/matplotlib-skill/skills/matplotlib" matplotlib
copy_skill "$FIG_VENDOR_ROOT/science-plot-formatter/.claude/skills/beautify-chart" beautify-chart

python3 - "$FIG_VENDOR_ROOT" "$FIG_PROJECT_ROOT/docs/skill-sources.lock.json" <<'PY'
import datetime
import json
import subprocess
import sys
from pathlib import Path

root, output = map(Path, sys.argv[1:])
records = []
for repo in sorted(root.iterdir()):
    if (repo / ".git").is_dir():
        def git(*args):
            return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
        records.append({"repository": repo.name, "url": git("remote", "get-url", "origin"),
                        "commit": git("rev-parse", "HEAD"),
                        "dirty": bool(git("status", "--porcelain"))})
output.write_text(json.dumps({"recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              "sources": records}, indent=2) + "\n")
print(output)
PY
```

如果安装中断，先检查已成功复制的目录，再只补装缺少的部分。不要盲目重跑并删除全部目录。上述安装命令是按核查到的目录编写的操作配方，本文件没有对未来仓库版本做兼容保证。

#### 2.2.3 可选安装

公式和张量维度较多、希望和 LaTeX 字体直接统一时，加装 TikZ；要比较混合多面板的布局方案时，加装 academic-figures。先完成函数定义，保留同一 Bash 会话中的变量与函数，再执行所需部分。

```bash
# 可选 A：TikZ
clone_once https://github.com/Noi1r/tikz-academic.git \
  "$FIG_VENDOR_ROOT/tikz-academic"
copy_skill "$FIG_VENDOR_ROOT/tikz-academic" tikz-academic

# 可选 B：多面板布局草案
clone_once https://github.com/sai-tv/academic-figures.git \
  "$FIG_VENDOR_ROOT/academic-figures"
copy_skill "$FIG_VENDOR_ROOT/academic-figures" academic-figures
```

可选安装后，重新运行上一节最后的 Python 版本记录块，把新增仓库记入 lock 文件。不要复制 README 中未替换的 `<your-username>` 示例地址。

#### 2.2.4 Python 与渲染环境

Skill 是工作指令和资源，不等于 Python 依赖已经安装。新项目可建立独立绘图环境；已有环境则复用并记录版本。

```bash
python3 -m venv .venv-figures
source .venv-figures/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib seaborn scipy pillow pyyaml cairosvg pypdf

# 检查 SciPilot 的实际 requirements 后，安装其需要的依赖。
if [ -f .claude/skills/scipilot-figure-skill/requirements.txt ]; then
  cat .claude/skills/scipilot-figure-skill/requirements.txt
  python -m pip install -r .claude/skills/scipilot-figure-skill/requirements.txt
fi

python -m pip freeze > docs/figure-environment.lock.txt
```

按需要补充：

- `pdftoppm` / `pdffonts` / `pdfinfo`：PDF 预览、字体和页尺寸检查，通常由系统 Poppler 工具包提供。
- Inkscape：SVG 编辑和 PDF 导出；含复杂文本或公式时要实测导出结果。
- `latexmk` 与包含 TikZ、standalone 的 TeX 发行版：仅 TikZ 路线需要。
- 中文字体：中文草图可用 Noto Sans CJK；英文投稿图按正文模板的字体要求配置。
- CairoSVG 缺系统 Cairo 库时，按机器环境补装依赖，或改用已有的 Inkscape 导出。不要假定 `pip install` 能安装所有系统组件。

#### 2.2.5 验证 Claude 能读取

重新启动项目中的 Claude Code，在对话中发送：

```text
请只检查本次选型后实际安装的 Skill；如果使用了完整后备组合，则检查
scientific-svg-figures、scipilot-figure-skill、matplotlib、beautify-chart。
读取它们的 SKILL.md，报告实际 name、入口路径、关联文件是否存在。
核对 scientific-svg-figures 引用的 SVG marker 检查脚本。
不要画图，也不要凭仓库名假定安装成功。
```

若自动发现失败，可明确要求读取 `.claude/skills/<目录>/SKILL.md`。这是直接遵循本地指令的回退方式，不代表 Skill 已被正常注册。检查是否有同名用户级 Skill 覆盖了项目级版本。

## 3. 从现有材料选择起点

用户不必先整理成固定目录，也不必填写全部模板。给出论文、Idea、数据、旧图或文件夹中的任意一种，Agent 先盘点，再决定哪些阶段可以执行。已有项目结构优先，不为适配本文而移动原始文件。

### 3.1 任务模式

| 当前材料 / 需求 | 运行模式 | 可以直接完成 | 暂不具备条件时如何处理 |
| --- | --- | --- | --- |
| 只有 Idea 或研究计划 | `concept` | 问题示意、概念框架、拟议方法、研究流程、待验证实验的图规格 | 标注 proposed；不生成虚构结果图 |
| 有方法、公式或代码，没有实验结果 | `method` | 方法流程、系统结构、算法步骤、理论关系、实验设计示意 | 代码与文字冲突先记录，不自行判定哪版正确 |
| 有原始或整理后的数据 | `results` | 数据审计、合适的数据图、caption、复现脚本 | 未知字段/单位只阻塞依赖它的 panel |
| 已有论文全文和数据 | `full-paper` | 对照论证结构规划必要图、补齐图文关系、统一全篇风格 | 保留已有编号；新增和重排说明对应关系 |
| 已有图和绘图源码 | `polish` | 直接渲染现状、按最终尺寸精修、比较前后效果 | 不无故重做研究叙事、图型和统计分析 |
| 只有截图、PNG 或 PDF 图，没有源码 | `reconstruct` | 检查可读性；按可确认内容重建结构，或恢复可提取的矢量元素 | 不把估读曲线当原始数据；精确结果重绘需数据 |
| 一批风格不一致的图 | `harmonize` | 统一尺寸、字体、图例、颜色语义、panel 标签 | 对不可编辑的图说明可修改边界 |
| 投稿修改或新增实验 | `revision` | 建立意见—图—数据依赖映射，修改受影响内容 | 不重新生成无关图；旧结果不自动代表新方法 |
| 单张图或某个 panel | `single-figure` | 走所需最短路径，完成该图及最小复现记录 | 不创建无关的整篇论文文档体系 |

支持组合模式，例如 `full-paper + polish`。`auto` 表示 Agent 根据当前材料选择模式并说明理由。

### 3.2 论文类型与表达对象

“通用”体现在统一规划与验收，同时允许不同论文走不同绘制路线。下列类型可以同时出现，不强制归类为一种。

| 论文内容 | 常见表达对象 | 首选路线 | 不能默认的内容 |
| --- | --- | --- | --- |
| 算法、机器学习、软件与系统 | 方法、结构、流程、性能、误差分析 | SVG/TikZ + 数据绘图 | 所有论文都有 baseline、消融或速度指标 |
| 理论、数学与形式化方法 | 定义关系、几何构造、证明结构、函数性质 | TikZ/SVG；必要时公式计算与绘图 | 数值示例等于理论证明 |
| 实验科学、工程、材料等 | 装置、样品、过程、响应、测量结果 | SVG 示意 + 数据图 + 原始图像 panel | 每个测量点都是独立重复 |
| 仿真、数值计算、计算科学 | 边界条件、场分布、轨迹、参数扫描 | 已有领域渲染器导出 + 通用排版 | 仿真输出是实测数据，网格单元是独立实验 |
| 观察、调查与社会科学研究 | 样本构成、变量关系、效应与不确定性 | 数据图 + 研究设计图 | 相关关系表示因果，重复观测相互独立 |
| 综述、文献计量与证据综合 | 分类体系、证据分布、时间趋势、检索筛选过程 | SVG/TikZ + 来源明确的统计图 | 检索计数、分类和效应量可以凭文献摘要补齐 |
| 定性研究、案例研究、人文研究 | 概念、主题、过程、论据与案例关系 | SVG/TikZ + 可追溯的文字/表格 panel | 主题可以随意量化，视觉连线自动构成因果 |
| 图像、地理空间、结构或三维对象为核心 | 样本图、地图、结构、场景、局部放大 | 原有专业工具导出 + 注释与拼版 | 通用 Skill 能替代专业几何、测量或领域模型 |

化学结构、分子、解剖、地图投影、复杂三维场等内容，优先保留经验证的领域工具和源文件。通用 Agent 负责输入盘点、版式、标注、组合和 QA；需要新的领域工具时先查官方文档，不能编造其命令或宣称通用 Skill 原生支持。

## 4. 准备输入：最简说明和完整模板

### 4.1 最少只需要这一段

```text
请按 figure_workflow.md 处理我的论文作图任务。
材料位置：[论文/Idea/数据/已有图/代码的路径，或“本次上传的文件”]
本次范围：[单图 / 指定几张图 / 全篇配图 / 仅精修已有图]
目标用途：[会议或期刊与年份；未定可写“通用投稿草稿”]
我最希望读者理解：[一句话；不确定时请你结合材料提出]
必须保留：[已有图号、配色、术语或布局；没有就写“无”]
请先识别任务模式与材料缺口，再完成所有具备条件的图。
```

没有目标 venue 时继续做通用草稿；没有数据不妨碍概念图；没有参考图不妨碍原创设计。只有影响科学含义且无法从材料判断的缺口才需要提问。

### 4.2 推荐目录，不强制迁移

| 路径 | 用途 | 什么时候需要 |
| --- | --- | --- |
| `inputs/research_brief.md` | 问题、研究对象、方法、结论边界、图需求 | 没有完整论文时尤其有用 |
| `inputs/manuscript/` | PDF、LaTeX、Word 或已有正文 | 全篇规划或图文一致性检查 |
| `inputs/figure_brief.yaml` | 任务模式、尺寸、风格、产物配置 | 多图项目或固定出图流程 |
| `inputs/references/` | 风格参考及来源 | 可选 |
| `inputs/source_assets/` | 原始照片、实验图像、领域工具导出等 | 需要图像或专业图形时 |
| `data/raw/` | 不改写的源数据 | 有定量图时 |
| `data/processed/` | 由可追溯转换产生的数据 | 需要转换时 |
| `figures/src/` | 可编辑图源、绘图脚本、拼版脚本 | 正式产出时 |
| `figures/drafts/` | 初稿、布局比较、未完成 panel | 尚未通过检查时 |
| `figures/final/` | 检查完成的输出候选 | 检查通过时 |
| `figures/qa/` | 最终尺寸、灰度及局部预览 | 视觉检查时 |
| `docs/` | 规划、数据来源、风格、caption、QA 与复现说明 | 按任务复杂度合并或拆分 |

单图任务可将计划、来源、caption 和 QA 合并为一个 `figure_notes.md`。完整论文再采用详细的多个记录文件，不为流程本身生成空文档。

### 4.3 `research_brief.md`

```markdown
# 研究与作图说明

## 研究问题和研究对象
[这项工作研究什么？读者需要什么背景？]

## 论文类型与研究阶段
[理论 / 方法 / 实验 / 仿真 / 观察 / 综述 / 定性 / 混合；计划或已完成。]

## 方法、框架或研究设计
[实际步骤、对象关系、条件、输入输出；不适用的项略去。]

## 希望回答的问题
- Q1: [...]
- Q2: [...]

## 已有证据和对应位置
[数据、公式、证明、文献、代码、图像或案例路径。]

## 已支持的结论与待验证假设
[分别列出；没有结果可以明确写“尚未验证”。]

## 本次图的范围
[解释概念 / 展示方法 / 呈现结果 / 分析机制 / 综述归纳 / 精修现有图。]

## 目标读者、投稿位置与限制
[领域、venue、版面、语言、需要保留的术语、编号和样式。]
```

### 4.4 `figure_brief.yaml`

```yaml
project: my-research-paper
task_mode: auto                 # 支持 auto 或第 3 节中的模式
scope: requested_figures        # single_figure / requested_figures / full_paper
paper_types: []                 # 由材料确定，可多选
research_stage: auto
venue: null                     # venue 名称与年份；未定保持 null
figure_language: auto           # 按用户、正文或 venue 确定
notes_language: zh

inputs:
  research_brief: null          # 填真实路径；不要强制改名
  manuscript: []
  data: []
  code: []
  assets: []
  existing_figures: []
  references: []

intent:
  reader: null
  questions: []
  required_figures: []          # 不预设每篇论文都要 Figure 1–5
  preserve: []

design:
  diagram_backend: auto         # svg / tikz / existing / auto
  data_backend: existing_or_python
  layout: auto                  # 不假定所有期刊都是双栏
  width_source: provisional
  target_width_mm: null         # 优先从模板或用户要求获取
  font_family: auto
  base_font_pt: null
  palette: auto
  semantic_colors: {}           # 按实际对象填写，非固定 method/ours 配色
  panel_label_style: auto

evidence:
  allow_synthetic_results: false
  allow_labeled_schematic: true
  analysis_plan: null           # 已有分析方案的路径，如适用
  source_data_read_only: true

skills:
  discovery: at_project_start  # 新项目或显式更新时重新检索
  prefer_locked_for_continuation: true
  fallback_catalog_date: 2026-10-01
  require_verified_replacement: true
  registry: docs/skill_registry.yaml

execution:
  allow_new_experiments: false
  allow_new_simulations: false
  allow_external_material_upload: false
  allow_network_for_discovery_and_guidelines: true
  visual_revision_limit: 3

outputs:
  editable_source: true
  publication_format: auto      # 依 venue 与图的类型决定
  preview_format: png
  preview_dpi: 300              # 预览默认值，不等于所有投稿图的要求
  captions: true
  reproducible_build: true
```

这些是 Agent 的任务配置字段，不是第三方 Skill 的官方 API。未填写项允许合理推断并记录；不推断不存在的实验结果、统计方法或结构细节。

### 4.5 数据与证据说明

每张图只填写适用项：来源路径与版本、变量定义与单位、研究对象、分组/条件、采样或测量方法、时间点、独立实验单位、重复/配对/嵌套关系、排除规则、转换与聚合、分析方案、缺失与不确定性。

来源不仅是 CSV。公式对应假设与定义；综述图对应检索记录和文献编码；定性图对应主题定义和支持材料；图像对应样本、采集条件和尺度；仿真图对应模型、初边值与参数。没有定量数据的论文不应被强制套入数据分析步骤。

## 5. Skill 路由与执行顺序

先确定图的科学用途，再选 Skill。不是让所有 Skill 依次修改每张图。

| 阶段 | 使用哪一个 Skill | 输入 | 产物与检查点 |
| --- | --- | --- | --- |
| 0. 动态 Skill 选型与环境检查 | Agent + 当前官方文档/仓库 | 任务范围、所需能力、已装工具 | 候选比较、选型、版本锁定与实际可用入口 |
| 1. 盘点、模式选择与研究理解 | Agent；有定量数据时用当前选中的数据规划 Skill | 正文、方法、数据、公式、文献、图像等 | 执行范围、研究事实表、适用的数据审计 |
| 2. 规划图及 panel | SciPilot 规划数据图；SVG/TikZ Skill 规划示意图 | 研究问题与证据 | 每图一份 Figure Spec |
| 3. 定尺寸与统一风格 | Agent；混合布局可选 academic-figures | 模板、参考、panel 内容 | style 配置与低细节布局 |
| 4A. 概念/方法/结构图 | scientific-svg-figures 或 tikz-academic | 已确认的关系、符号和步骤 | SVG 或 TeX 主源、PDF/PNG 预览 |
| 4B. 定量图 | matplotlib；已有专业脚本可继续使用 | 审核过的数据和分析定义 | 可运行绘图脚本、数值快照、图 |
| 4C. 图像/专业对象 | 原有领域工具 + Agent 排版 | 原始素材、已验证输出 | 可追溯的裁剪、标注、尺度和 panel |
| 5. 按最终尺寸精修 | Matplotlib 脚本用 beautify-chart；其他格式用原生成路线 | 实际渲染、物理尺寸、style | 修改记录与重新渲染结果 |
| 6. 组合 | Matplotlib / SVG / LaTeX / 原项目工具 | 真实的各 panel | 主图和组合源码，检查相对尺度 |
| 7. 验收与交付 | Agent | 图、证据、caption、脚本 | 科学、视觉、技术、复现四类 QA |

表内名称是后备实现示例；执行时应由第 1 节选出的当前 Skill 注册表替换，对应职责保持不变。

任务相关的 Skill 缺失时，可以用现有代码或确定性的 SVG/Python 方法完成，并如实记录回退路径；不能声称调用了未加载的 Skill。专业对象超出工具能力时，先做可完成的版式和图规格，明确缺什么源素材或工具。

### 5.1 Figure Spec：每张图都先写清楚

```yaml
id: fig_unique_id
role: auto                     # concept / method / design / result / analysis / synthesis
reader_question: null
takeaway_or_purpose: null       # 无结果时写解释目的，不预写“优于”结论
evidence_type: auto             # conceptual / measured / simulated / theoretical / literature / qualitative
source_refs: []                 # 文件、公式、文献条目、样本等的明确定位
evidence_status: unresolved     # verified / unresolved；概念图也能被正确验证
panels: []
data_transforms: []
analysis_definition: null
visual_encoding: {}
dimensions: {}
primary_skill: null
editable_source: null
caption_points: []
missing_inputs: []
```

每张图围绕一个主要问题组织；多 panel 可以提供相互补充的证据。正文中没有重要用途的重复图可建议删减。不要默认论文必须包含架构图、三张性能图和一张消融图。

### 5.2 从表达目的选择图型

| 想让读者理解什么 | 可优先考虑 | 需要避免 |
| --- | --- | --- |
| 对象、层级、组成关系 | 结构图、分层布局、分类树 | 把无方向关系画成因果箭头 |
| 步骤、时序、状态变化 | 流程图、时间线、状态图 | 将真实并行或反馈过程画成单链 |
| 总体与局部细节 | 主图 + 局部放大、分层 panel | 放大区域无法对应，比例含义不明 |
| 组间差异 | 点区间图、柱状图、小多图 | 只有均值而隐藏关键分布或样本数 |
| 随有序变量变化的趋势 | 折线 + 点、区间带 | 将无序类别随意连接，跨缺失点假造连续性 |
| 分布、稳定性、异常 | 原始点、箱线、直方、ECDF；适用时密度图 | 用过度平滑掩盖小样本和多峰 |
| 两个量的关系 | 散点；有依据时加拟合与区间 | 把拟合线或相关性称为因果 |
| 多指标权衡 | 散点、小多图；适用时 Pareto 前沿 | 预设某方法必定在前沿，混合不兼容量纲 |
| 矩阵、空间分布、条件组合 | 热力图、场图、分面图 | 对比 panel 各自缩放色标却不说明 |
| 组成和贡献 | 互斥类别的堆叠图、条形图 | 堆叠重叠集合、包含时间或不同分母 |
| 文献分类和证据分布 | 分类图、证据矩阵、时间趋势 | 虚构类别计数、遗漏检索边界 |
| 定性主题和过程 | 主题关系图、过程图、证据表 | 未经编码就用频次代表重要性 |
| 图像或样本对照 | 对齐的图像 panel、标注、局部放大 | 不同尺度或处理条件造成误导 |

专门图型如生存曲线、效应量森林图、地图或三维场，只有在数据结构、研究目的、统计定义及工具均适用时启用。图型选择不授权 Agent 新建未经确认的统计模型。

### 5.3 美观化的具体做法

先读内容再定画面；初稿先确定阅读顺序、区域比例和层次，再细化颜色和标注。对概念/总览图可比较两种低细节布局，然后自行选定更清楚的一种继续；小修改无需生成多个方案。

统一颜色的含义，而不是要求所有图用同一种色表：类别用离散配色，单向量值用顺序色表，围绕明确中点的偏差可用发散色表。方法、材料、实验组、状态或主题等对象在不同图中保持身份一致，搭配线型、形状或文字，避免只靠颜色区分。

文字与线条按最终物理尺寸设计。优先减少不必要标签、拆分拥挤 panel、调整留白，避免靠缩小字体解决所有问题。用短标签、对齐、统一 panel 标号、适当外置图例和清楚的局部注释控制信息密度。3D 仅在数据本身需要空间表达时使用。

投稿规格优先读取指定 venue 当前要求或用户模板；不能照搬 Skill 中预设的会议尺寸。未知规格时记录临时宽度和字体，交付为 provisional。照片/实验图像按实际分辨率与要求处理；提高文件 DPI 字段不增加真实细节。

### 5.4 每条绘制路线的关键检查

**示意与结构路线：** 明确节点和连线分别表示什么，检查方向、分组边界、符号与量纲。概念关系、物理过程、因果主张、数据流和时间顺序不能共用没有解释的箭头。拟议方法明确标为 proposed；示意几何或示意矩阵标为 schematic。理论图中的数值例子要写出参数、定义域和假设，不作为证明的替代。

**数据路线：** 先识别研究单位，再决定聚合与不确定性。沿用论文的分析方案；仅有汇总数值时保留其信息边界。缺误差不能补误差棒，缺原始样本不能恢复不存在的分布。排除、归一化、平滑、拟合和分组都要有依据并记录；不为追求美观更改结论。允许直接使用用户给出的可追溯汇总表，无需虚构更底层的原始数据。

**图像与专业对象路线：** 保留原始素材。裁剪、旋转、对比度、色标、投影和局部放大记录处理过程，并保持可比条件。尺度条依据真实校准，未知尺度不估造。专业工具输出要保留单位、坐标、视角或关键参数。AI 生成插图仅可在任务允许时作为明确标记的概念素材，不能替代照片、显微图或其他研究证据。

**已有图精修路线：** 先运行或查看原图、列出具体问题，再修改。beautify-chart 用于能运行的 Matplotlib 脚本；其职责保留数据、颜色、线型、轴限和既定构图。若任务要求更换配色或图型，先作为明确的设计修改处理，再进入精修；统计更正单独记录。其他源格式继续用原工具，避免为调用 Skill 强制重写。

### 5.5 组合、caption 和验收

多 panel 先确定整图和各 panel 的最终大小，再导出素材。纯数据多 panel 通常由一个绘图工程统一构建；混合素材可用 SVG/LaTeX 或已有工具组合。academic-figures 可提供布局草案，数据占位框必须由真实 panel 替换。

保留每张图的主源。文字转路径仅用于需要兼容性的发布副本；SVG 合并检查 ID、marker、clipPath 和外部资源；图像素材保持必要分辨率。不要把整张矢量数据图截图后拼版。

caption 说明图的目的、panel、符号、设置与证据来源；按适用情况交代样本量、重复单位、误差定义、尺度、仿真条件或文献编码规则。没有数据图的 caption 不强塞统计检验信息，概念图也不因没有实验数据而判定为未完成。

每轮执行：渲染 → 实际读图 → 列出具体问题 → 修改 → 重渲。通常最多三轮，通过即停止；未解决问题保留 draft 状态，说明原因。不会使用图像查看工具时，只能报告程序检查已完成，不能宣称视觉验收通过。

| 验收维度 | 通过条件 |
| --- | --- |
| 科学与内容 | 和来源一致；重要未知项已解决或诚实标注；示意、理论、仿真和实测的性质明确 |
| 数值与来源 | 适用时可复算关键值；变换、单位、样本、分析定义有出处 |
| 视觉 | 最终尺寸可读；无误导性裁剪、遮挡、连线、比例或色标；系列可区分 |
| 技术 | 实际导出格式、尺寸、字体、分辨率和引用资源可用 |
| 复现 | 保留主源、输入定位、变换和导出步骤；手工修改有记录，不伪称全自动 |
| 投稿规格 | 已核对的要求通过；未知项明确写为未验证，不能与科学内容检查混淆 |

输出状态分开记录：`draft`、`ready-for-review`、`submission-spec-verified`。后两者分别表示已完成内容/视觉检查的候选，以及额外核对了目标投稿规格；均不代表论文结论获得外部学术认可。

## 6. 完整通用作图 Agent Prompt

将下面整个 Prompt 交给当前使用的 Agent（例如 Claude Code）。只需补充“本次任务”；不要求预先有所有配置文件。Prompt 先动态选型，后备地址也已包含，单独复制即可使用。平台安装规范须在运行时重新核实。

```text
你是我的通用论文作图 Agent。请基于现有研究材料，完成本次范围内的论文图，
包括需要的规划、可编辑源文件、实际渲染、精修、caption 和复现说明。
适配研究本身，不预设学科、论文结构、图的数量、实验指标或主张方向。

【本次任务】
材料位置：[填写路径，或使用本次提供的文件；未填写时在当前项目中盘点]
任务范围：[填写；未填写时依据当前请求，不自动扩展为整篇论文重做]
目标会议/期刊/用途：[填写；未定使用通用草稿规格并标为 provisional]
最想回答的问题：[填写；未定从材料中提出并说明]
必须保留的元素：[图号、术语、配色、结构等；没有则无]
配置：[有 figure_brief.yaml 或研究说明则读取；没有也继续]
语言：[优先遵循用户、正文或投稿语言；工作说明默认中文]

【总原则】
1. 先确认任务与证据，再决定画什么；每张图有明确问题或解释目的。
2. 分清概念/拟议方法、理论、实测、仿真、文献综合与定性证据。
   不虚构实验值、样本、统计显著性、文献、方法细节或图像证据。
3. 保留原始数据与素材；已有人工作品和源码先保留版本，再修改。
4. 不为提高视觉吸引力修改科学含义、筛掉不利结果或补造误差。
5. 沿用既有统计/分析方案；必要但未定义的分析选择明确提出，不能擅自
   将相关解释为因果、将数值例子解释为证明或把重复观测当独立样本。
6. 不运行未请求的新实验或大规模仿真，不自动上传研究材料到外部服务或发布。
7. 在授权范围内自主完成常规布局、配色、编码和可逆修正。关键科学信息未知时
   只询问必要问题，先完成不受影响的图，不为每一轮视觉调整停下来确认。
8. 交付必须来自实际文件和实际检查，不声称运行了不可用的 Skill 或渲染器。

【首先执行：动态发现和评估当前 Skill】
这是第一步，不要先无条件安装下面的历史推荐。
1. 先从本次请求和材料标题提取能力需求，例如方法示意、数据图、理论图、
   专业对象、精修、拼版和 QA；完整研究分析放在选型之后。
2. 若是同一项目的继续任务，先读取已有 skill_registry 和版本锁，正常可用时沿用。
   新项目、平台变化、工具失效或用户明确要求更新时重新检索。
3. 阅读当前 Agent 平台官方 Skill 文档，检查本机能力和安装机制。
   搜索现在可用的相关 Skill/插件/仓库，以能力和当前研究需求为关键词，
   不限定下方旧名称；候选关键事实回到仓库实际文件、版本、示例与问题核实。
4. 每项需要的能力通常筛选 2–3 个可信候选，合并重复项。比较任务匹配、
   科学内容保持、源文件编辑、实际尺寸可读性、渲染 QA、复现、兼容性、
   依赖/费用和迁移成本。star、多次宣传或最近提交不能单独证明“最好”。
5. 分清仓库自述、源码确认、示例观察和实际运行；必要时做最小试绘。
   试绘的合成数据必须标 synthetic 并隔离在 tool_eval/，不得混入论文结果。
6. 新候选满足必需能力且有可验证收益、代价可接受时，替换对应角色。
   允许一个工具覆盖多个角色，不要求整体换套件，也不强制所有角色各装一个。
7. 没有验证出更合适的替代，再用本地已验证版本或下列历史后备。
   无法联网时明确 offline_fallback，不能声称检索了最新生态。
8. 采用前核对当前入口、依赖和平台安装方式；根据稳定 release 与分支实际情况
   选择版本并锁定 commit，不把“最新提交”直接等同于推荐版本。
   记录选择理由、查询日期、仓库 URL、版本、实际入口、文件校验和和本地修改。
9. 写入 docs/skill_selection.md、skill_registry.yaml 和 skill-sources.lock.json，
   单图可合并选择说明。不要为了选工具无限检索；覆盖能力并明确取舍后开始作图。

历史后备（核查于 2026-10-01，未来仍需验证可用性）：
- SVG 示意：https://github.com/ThalesGroup/agilab/tree/main/.claude/skills/scientific-svg-figures
- 数据规划：https://github.com/Haojae/scipilot-figure-skill
- 数据绘制：https://github.com/tvhahn/matplotlib-skill
- 现有图精修：https://github.com/preordinary/science-plot-formatter
- TikZ：https://github.com/Noi1r/tikz-academic
- 混合多 panel 布局：https://github.com/sai-tv/academic-figures
旧仓库删除、不兼容或关键依赖不可用时不要强装，选择可用替代并记录。

【选型完成后：盘点和选择任务路径】
读取现有正文、说明、数据、图像、代码、已有图、模板和参考图。
沿用项目目录，不要求用户先把所有文件重排为固定格式。
选择 auto / concept / method / results / full-paper / polish / reconstruct /
harmonize / revision / single-figure 中的一个或组合，并说明判断。
- 只有 Idea：做准确标记的概念/拟议方法图和待验证图规格，不制造结果。
- 有完整论文：按正文论证规划图，保留已有编号和有用内容，不默认生成固定套图。
- 仅精修：从现有图和源码开始，避免重做无关研究分析。
- 只有截图：能确认的内容可以重建，不能把估读数值称为原始数据。
- 有领域素材：保持专业源与渲染路线，通用流程负责排版、标注和验收。
列出输入、可执行部分、缺口和已有工具；缺少非关键输入时采用明确的临时设置。

【按能力路由，名称由本次选型替换】
先读取本次 skill_registry，加载真正选中的 Skill 入口和相关资源。
下面仅解释历史后备对应的职责；采用更合适的新 Skill 时以注册表代替旧名。
不一次让所有 Skill 重写同一张图：
- scipilot-figure-skill：定量数据审计、图型选择和表达目标。
- scientific-svg-figures：概念、结构、方法、流程和其他可用 SVG 准确表达的图。
- tikz-academic：可选，公式/几何/符号适合 LaTeX 的示意图路线。
- matplotlib：定量图的 Python 绘制和初稿。
- beautify-chart：已有可运行 Matplotlib 脚本的最终尺寸精修。
  其仓库名为 science-plot-formatter，不要混淆。
- academic-figures：可选，混合多面板的布局草案，不假定它自动嵌入真实实验图。
Claude Code 的历史项目级入口为 .claude/skills/<目录>/SKILL.md；
实际运行以当下平台文档和注册表为准，不能假定多年后或其他平台路径相同。
若已有合适的专业工具、R/Python/领域绘图脚本，继续使用，不强制迁移。
专业结构、地图、三维场等超出通用工具能力时，读取项目文档并核实工具能力。
缺少 Skill 时允许确定性代码回退，记录实际使用方式；不要编造命令或兼容性。
每张图确定一个主源；共享 style 和用户要求优先于不同 Skill 的默认风格。

【阶段 1：理解研究与证据】
整理研究问题、研究对象、方法/设计、术语、符号、结论及限制。
把已确认事实、待验证假设、缺失信息分开；正文与代码/数据冲突显式记录。
只启用适用的审查：
- 定量材料：字段、单位、缺失、分组、独立实验单位、配对/重复/嵌套、
  排除和聚合规则、已有分析定义、条件可比性。
- 理论材料：定义、假设、符号、定义域、命题与图示之间的对应。
- 仿真材料：模型、初边值、参数、坐标/单位、运行条件和输出来源。
- 图像材料：样本来源、采集条件、校准尺度、处理过程和允许的对照方式。
- 文献材料：检索与筛选记录、分类规则、条目来源和证据边界。
- 定性材料：主题定义、案例/材料来源、关系依据，避免未经依据的量化。
不要求不适用的字段，不将所有论文转换为机器学习 benchmark。

【阶段 2：Figure Plan】
为每张必要图写 Figure Spec，至少包含：
id、角色、读者问题、解释目的/有证据的结论、证据类型、来源定位、
panel、数据变换/分析定义（如适用）、图型与编码、尺寸、主 Skill、主源、
caption 要点、缺失输入与当前状态。
图型由目的和数据结构决定，不预设架构图、性能图或消融图的固定组合。
多 panel 应共同回答一个主要问题；重复或无关图建议删减。
理论示意和概念图可以独立完成；只有需要实测而未取得数据的 panel 才是缺数据。
单图任务将规划和审计合并成简短记录；多图任务写 docs/figure_plan.md 等文件。
在范围明确时自行选择最合适的设计继续执行，不停在建议清单。

【阶段 3：尺寸、风格与初稿】
优先读取用户模板和指定 venue 对应年份的官方要求，记录来源。
单栏/双栏、字体、宽高、文件格式、分辨率都按实际用途确定，不照抄 Skill 预设。
无法核实的规格标 provisional；可继续做图，但不声称满足投稿要求。
先计算整图和各 panel 的最终物理尺寸，再设置文字和线宽。
建立共享 style：对象→颜色/形状/线型、字体、标签、图例、间距和标号。
颜色按类别/连续量/有中点的偏差分别设计；同一对象跨图身份一致。
在有必要的总览图上先比较两种低细节布局，选清晰的一种继续。
通过阅读顺序、对齐、局部放大和层次提高表达质量，不靠缩小文字塞满信息。
风格参考可借鉴布局和信息密度，不能移用其研究内容和数值。

【阶段 4：按图类型实际制作】
A. 概念、方法、理论或流程图：
   使用 SVG 或 TikZ 中合适的一种作为主源。
   节点、连线、分组、方向、符号和尺寸含义必须有来源。
   区分关系、因果、物理过程、数据流、时间和反馈；必要时给图例。
   拟议方案标 proposed，非量化几何/矩阵等标 schematic。
   数值示例注明定义域、参数与假设，不代替理论证明。
   scientific-svg-figures 引用的 marker 检查器存在才运行，不存在则报告回退检查。
B. 定量图：
   使用 matplotlib 或已有合适脚本，读取可追溯的原始/汇总数据。
   关键标注由数据计算；不要为了符合预期而手填结果。
   沿用适用的分析方案，记录所有筛选、变换、聚合、拟合和归一化。
   明确误差定义和独立重复单位；缺失信息不补造。
   分类与连续变量分别编码；轴限、对数轴、色标和缺失点处理清楚。
   组成项只有在定义上可加和时才堆叠；关联图不自动宣称因果。
   保存用于绘图的数值快照和导出脚本。
C. 图像、空间或专业对象：
   采用原始素材或已经验证的领域工具输出，保留专业源文件。
   记录裁剪、旋转、强度/对比度调整、色标、投影、相机和放大处理（适用项）。
   对比 panel 的处理方式与尺度应可比；未知尺度不造尺度条。
   不用生成图片替换研究证据，不把低分辨率插值称为恢复真实细节。
   标注和拼版可用矢量层，真实图像保留必要的栅格分辨率。
D. 已有图恢复/精修：
   先保留并查看原图，优先编辑源文件。没有数据则不擅自重建精确曲线。
   明确哪些元素可精确恢复、哪些只是视觉重建、哪些需要补源文件。

【阶段 5：精修与多 panel 组合】
Matplotlib 脚本使用本次选定的精修 Skill（历史后备为 beautify-chart）：
先渲染并查看，再修改，再重渲。
若使用 beautify-chart，遵循其保留数据、颜色、线型、轴限和既定构图的精修职责。
采用新 Skill 时同样以用户明确要求和科学含义不变为边界。
用户要求的配色/图型变化在上游设计阶段处理；分析更正另行记录。
非 Matplotlib 图继续用原路线精修，不为调用 Skill 强制改工具。
纯数据多 panel 尽量由同一工程排版；混合素材用适当的 SVG/LaTeX/原工具组合。
占位框必须替换为真实素材；缺源素材的 panel 留在 draft。
合并后重新检查实际字号、相对尺度、色标、图例、编号、SVG ID 和资源路径。
保留可编辑主源；需要文字转路径时另存发布副本；不将整张矢量图截图拼版。

【阶段 6：验收与 caption】
执行渲染→实际读取图片→记录具体问题→修改→重渲的闭环。
通常最多三轮，通过即停；未解决的图保留 draft 并写明原因。
检查四类问题：
1. 科学和证据：与方法/公式/来源一致；证据性质不混淆；未知项无伪装。
2. 数值和可比性：适用时复算关键值，确认单位、条件、误差和处理方式。
3. 视觉和技术：最终尺寸可读、无裁切遮挡、方向清楚、图例可辨、字体完整、
   格式和资源可用；图像有效分辨率与向量元素符合目标用途。
4. 复现：输入定位明确，主源和转换/导出步骤保留；手工步骤写明。
无法实际查看图片时报告“视觉检查未完成”，不能以脚本成功代替读图。
Caption 根据图的类型解释问题、panel、符号、设置和来源：
统计信息、尺度、参数、文献分类规则等只在适用时填写。
写清限制，结论不超出证据；不要凭美观程度给研究结论背书。
将 draft / ready-for-review / submission-spec-verified 分别记录；
投稿规格核实程度与科学内容完成程度分开。

【阶段 7：交付和复现】
交付本次真正需要并已完成的文件，不生成空目录/空文档凑清单：
- 主源：SVG、TeX、Python/R/领域工具文件，或记录完整操作的原生工程。
- 成图：目标用途要求的矢量/栅格格式；另给便于查看的 PNG 预览。
- 简短或完整的记录：Figure Plan、来源/转换、style、caption、QA、缺口。
- 重绘入口或逐步复现说明：自动化做不到的手工部分明确说明。
- 多图项目的 manifest：id、来源/版本/哈希、主源、依赖脚本、输出、状态。
- 实际使用的 Skill 提交号和环境版本；未知版本不编造。
单图可以合并记录到 figure_notes.md；整篇论文再拆分 docs 下的文件。
最后用简短表格列出图、目的、Skill/工具、文件路径、检查状态和未完成项。
现在从材料盘点开始，完成具备条件的工作，不只给出计划。
```

## 7. 常见任务的补充 Prompt

这些指令追加到总 Prompt 后即可，不需要为每个学科另写一套固定流程。

### 只有 Idea

```text
目前只有研究 Idea，没有实验结果。本次完成问题示意与拟议研究方案图。
明确区分已有事实、拟议方法和待验证假设。为可能需要的结果图列规格和缺失数据，
但不生成带虚构曲线的“实验效果图”。
```

### 全文已有，但不知道画哪些图

```text
阅读全文，按“读者需要理解什么、正文现有证据在哪里”规划必要图。
对每张图说明对应段落与用途；保留有用的现有图，不默认每节都配图。
先完成证据齐备的图，并指出哪些叙述需要数据才能图示。
```

### 现有数据不知道如何呈现

```text
先用 SciPilot 检查数据结构与研究问题，再推荐并自行选定最合适的图型。
不要预设柱状或折线。沿用已有分析定义；缺失的统计定义单独提出，
先完成无需该定义的描述性展示。
```

### 已有图只想变漂亮

```text
本次是 polish 模式，优先用现有源码。先渲染并检查原图，
按实际展示尺寸修正文字、线宽、图例、留白和对齐。
保留数据、科学含义与指定视觉编码，不重做无关图。
```

### 理论、综述或定性论文

```text
本论文的核心证据不以实验性能表为主。请根据公式/文献/主题材料选择表达方式，
保留可追溯的定义和依据，不强制增加架构、性能、消融或显著性图。
未被材料支持的计数、因果箭头和量化强弱不要补画。
```

### 新数据或审稿意见来了

```text
依据新增材料或审稿意见建立“变化→受影响的图/panel/caption”清单。
只更新有依赖关系的内容，保持稳定的术语、图号和对象配色。
研究方法变更时，检查旧结果是否仍适用；不能把旧实验直接归属新版方法。
```

## 8. 来源与版本说明

GitHub 地址、目录与职责沿用 2026-10-01 核查的仓库内容；工作流的模式选择、输入模板、跨学科路由、验收和 Prompt 是本文组织的执行规范，不是第三方仓库提供的一键产品。

- [Claude Code：Skills 官方文档](https://code.claude.com/docs/en/skills)
- [Scientific SVG Figures：SKILL.md](https://github.com/ThalesGroup/agilab/blob/main/.claude/skills/scientific-svg-figures/SKILL.md)
- [SciPilot Figure Skill](https://github.com/Haojae/scipilot-figure-skill)
- [Matplotlib Skill](https://github.com/tvhahn/matplotlib-skill)
- [Science Plot Formatter / beautify-chart](https://github.com/preordinary/science-plot-formatter)
- [TikZ Academic](https://github.com/Noi1r/tikz-academic)
- [Academic Figures](https://github.com/sai-tv/academic-figures)

第 1 节动态选型优先于历史清单；安装时记录提交号，出图周期内固定版本。专业内容以研究材料、领域规范和实际工具能力为准；通用 workflow 提供一致的工作方法，不替代专门科学模型或统计分析方案。
