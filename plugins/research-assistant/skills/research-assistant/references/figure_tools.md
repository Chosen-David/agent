# 作图工具选型与安装后备

从原作图工作流提取；历史目录不等于当前安装结果。先读 [共享约定](figure_shared.md)，仅在选型或环境检查时读取此文件。以下命令是经选择后才使用的历史配方，不自动执行。

## 1. 第一步：动态发现、评估并选择当下合适的 Skill

**不要直接安装本文列出的历史 Skill。** 每次新项目或用户要求重新选型时，先运行本节；两个专业入口共用本节，按任务只读所需能力。先根据任务说明提取能力需求，再寻找当前候选。无需先完整分析所有论文数据。

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

