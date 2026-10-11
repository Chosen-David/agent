# GPU 实验多机派单作战手册

来源：2026-10 四机 20 卡（本地 2 + H20 8 + .187 8 + .251 2）真实调度链
（E109 海选全量 → E119 RULER 三档收口 → E123 小试判决 → E116b 新口径全量
重跑）沉淀。所有「坑」均为真实事故，非推演。

## 1. 接入：从 SSH 进资源池开始

### 1.1 SSH 封装

密码放 `SSHPASS` 环境变量 + sshpass，封装成 `/tmp/rssh.sh` 一行命令：

```bash
export SSHPASS='<密码>'
exec sshpass -e ssh -p 8416 -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  -o ConnectTimeout=15 user@host "$@"
```

**坑（真实事故）**：密码凭记忆写错 → 三台远程机全部 Permission denied，
差点误诊为节点批量宕机。解法：密码以机内已有封装文件（`/tmp/rssh.sh`）
为准，grep 出来用，不凭记忆输入。

**坑**：ssh 远程 awk 的 `$1` 在双引号包裹下被本地 shell 展开成主机名，
与阈值的字符串比较恒真 → 误报 8/8 busy。远程命令整体单引号包裹。

### 1.2 环境栈部署

远程机通常无 root、无系统 python 包。一次部署三件套（rsync 推送）：

```bash
rsync -a --rsync-path=$HOME/.local/bin/rsync \  # 远端 rsync 常在 ~/.local/bin
  -e "ssh -p 8416 -o StrictHostKeyChecking=no" \
  ~/.local/lib/python3.9/site-packages/ remote:~/.local/lib/python3.9/site-packages/
rsync ... ~/code_repo/ remote:~/code_repo/     # 代码（几十 MB）
rsync ... ~/datasets/ remote:~/datasets/      # 数据集（几百 MB）
```

**坑**：rsync 不创建父目录——目标 `~/datasets/LongBench` 的父目录
不存在时直接 code 11 失败。先 `ssh remote 'mkdir -p ~/datasets/LongBench'`。

### 1.3 逐机盘点清单（点火前必查，一台不落）

| 盘点项 | 命令 | 坑 |
|---|---|---|
| GPU 卡数/空闲 | `nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader` | 只看 memory.used=1MiB 判空闲 |
| 模型路径 | `ls -d ~/Qwen3-8B <共享挂载路径>` | **逐机确认**——本地走共享挂载、远程走家目录的混合布局是常态；拿本地路径直接套远程 → HFValidationError 秒挂 |
| 数据集覆盖 | `ls ~/datasets/.../data/ \| wc -l` | **真实事故**：.251 从未跑过 LongBench、无数据集，派单前才发现，临时补推 794M |
| 基准数据 root | RULER 等 third_party 数据路径逐机 ls | 与数据集不同源，单独盘点 |
| Python/磁盘 | `python3 --version; df -h ~` | 5.9T 级随便跑，小盘机要先算产物体积 |

### 1.4 代码同步

```bash
rsync -a --delete --exclude=.git --exclude=exp --exclude=__pycache__ \
  --exclude='*.pyc' --exclude=.pytest_cache \
  --rsync-path=$HOME/.local/bin/rsync \
  -e "ssh -p 8416 -o StrictHostKeyChecking=no" \
  ~/主仓/项目目录/ remote:~/部署目录/
```

- `--delete` 保证代码精确镜像（防重命名后旧文件残留 shadow import）；
- `--exclude=exp` **保护远端既有实验数据不被删**（rsync 排除路径默认
  不参与删除）——远端 exp/ 里可能有还没拉回的数据；
- 同步后冒烟（三机全绿才派单）：`python3 -m compileall -q <代码目录>`
  + 关键新接口 import（如 `from sparse_attn.info import
  resolve_treatment_snapshot`）。

## 2. 规划：任务属性 → 分配

### 2.1 任务清点矩阵

派单前先列全矩阵：臂（arm/配置）× 任务 × 档位 × 期望行数。期望行数
逐任务精确（`EXPN` 表）：多数 200，数据集特例如 multifieldqa_en=150、
lcc=500、repobench-p=500、RULER=100、lbv2=503。期望行数同时是完成度
对账门禁与 SKIP 阈值。

### 2.2 复用判定（省一半算力的关键）

口径 = 影响被测方法行为的代码语义。变更（bug 修复/算法改动）后：

- **口径相关臂**（行为被改变）：全部重跑，绝不与旧数据混池比较；
- **口径无关臂**（不走被改路径，如 dense baseline `--method none`）：
  复用旧数据，只补从未跑过的缺口任务；
- 边界情形（如单池臂可能间接受选择路径修复影响）：宁可重跑，
  跨口径混比的污染不可逆。

### 2.3 成本权重与分配

相对权重按历史实测校准（示例：RULER 128K 任务 ≈ 4 单位、64K ≈ 2、
32K ≈ 1；LB 任务 ≈ 1、500 行任务 ≈ 2.5）。总量 ÷ 总卡数 ≈ 每卡单位数，
再按四原则分：

1. **长路径档位独占大机**：128K 全量独占 8 卡机，4+4 链按臂均分；
2. **重任务独占链头**：历史最重任务（fwe/cwe 128K、lcc/repobench 500
   行）放链头，一条链至多一个超重任务；
3. **确定性分片互斥**：每个任务只属一机一卡（例：LB v1 16 任务拆
   首段 8 给本地 + 中段 6 给 2 卡机 + 重活 2 给 8 卡机的空闲链）——
   分片互斥则 SKIP 撞车、重复烧卡、rsync 合并冲突全部免疫；
4. **串行链内轻后重前**：链是串行的，估算链总时长 = 各任务和，最长
   链决定全局工期，监控时只盯最重链。

### 2.4 SKIP 幂等：best-file 口径

```bash
e116b_best_rows () {  # 单文件最大行数（非累计！）
  local best=0 r f
  for f in "$1"-*.jsonl; do
    [ -e "$f" ] || continue
    r=$(wc -l < "$f"); [ "$r" -gt "$best" ] && best=$r
  done; echo $best
}
# SKIP 判定：best_rows ≥ 期望行数
```

**坑（真实事故）**：SKIP 按累计行数（`cat $T-*.jsonl | wc -l`）而正式
打分按 best-file 仲裁（多文件取最大），两格 mismatch：cum=104 但
best=91，正式收口被 min-samples 拒收，还要补跑。两条口径必须同源。
部分文件（< 期望行数）保留无害：重跑产出新时间戳文件，打分取最大。

## 3. 派单脚本骨架

两层结构，机器脚本只写路径与链分工，函数与臂参数全在 lib：

```
/tmp/e1xx_ruler_lib.sh    # 臂 TLV 参数串、best_rows、run_ruler(GPU,ARM,LEN,EXTRA,TASKS...)
/tmp/e1xx_lb_lib.sh       # EXPN 行数表、run_lb / run_lb_fullkv
/tmp/e1xx_<machine>.sh    # 路径 + 每卡一条链的后台启动 + wait
```

要点：

- 每卡一条**串行链**：`run_xxx 0 arm ... > log 2>&1 &` × N + `wait`；
  一卡同时只跑一个任务（显存与吞吐都可预期）；
- 远程点火：`nohup bash /tmp/e1xx_<machine>.sh > ~/e1xx.log 2>&1 < /dev/null &`
  ——`< /dev/null` 防 ssh 断开的 SIGHUP；
- `--pred_postfix _<实验代号>_<臂>` 保证文件名互异（防跨臂同名互覆）；
- 产物目录与旧实验完全隔离（新 root 目录），复用数据单独引用旧目录。

**坑**：bash 后台任务的重定向目标目录在**函数体 mkdir 之前**求值——
`cmd > $OUTDIR/.log &` 中 OUTDIR 不存在时整链秒挂。机器脚本里先
`mkdir -p $OUTROOT` 再起链。

**坑**：`python ... 2>&1 | tail -2` 管道缓冲——日志要等任务结束才可见，
链运行中看 log 是空的属预期；**进度监控一律数产出文件行数**，不看 log。

**坑**：派单任务名必须用 argparse choices 全名。真实事故：任务名写成
两词缩写（"fwe mv"），argparse 秒拒，该任务从未被认领而链显示正常推进。

## 4. 点火验证（三重确认，30 秒内）

```bash
ssh remote 'ps aux | grep -c "<模块名>"; nvidia-smi --query-gpu=index,memory.used --format=csv,noheader; tail -3 ~/e1xx.log'
```

- **进程数** = 起跑链数；
- **显存**：每卡应升到模型加载量级（8B bf16 ≈ 16G+，长上下文 KV 更多）；
- **log tail**：无回溯即正常（有报错按 log 修后重派，SKIP 幂等保证重派安全）。

只看 pid 存在**不算验证**。真实事故：模型路径是另一台机的路径，
25s 内 HFValidationError 两任务全挂但 DONE 标记照打，GPU 空转 42min。

## 5. 真实踩坑总账（速查）

| # | 坑 | 后果 | 解法 |
|---|---|---|---|
| 1 | SSH 密码凭记忆 | 误诊节点宕机 | 以机内封装文件为准 |
| 2 | 拿本地模型路径套远程 | 静默失败空转 | 逐机盘点模型路径 |
| 3 | 远程机数据集缺失 | 派单后才发现 | 点火前逐机 wc -l 盘点 |
| 4 | rsync 父目录不存在 | code 11 失败 | 先 ssh mkdir -p |
| 5 | --delete 未排除数据目录 | 远端数据被删 | --exclude=exp 保护 |
| 6 | 重定向目录先于 mkdir 求值 | 整链秒挂 | 脚本开头 mkdir -p |
| 7 | 累计 vs best-file 口径不一致 | 收口被拒收 | 两口径同源 best-file |
| 8 | 只看 pid 不看显存/log | 42min 空转 | 三重确认 |
| 9 | `tail -2` 管道缓冲 | 误判链死掉 | 监控产出文件行数 |
| 10 | 任务名非 argparse 全名 | 任务静默漏跑 | choices 全名派单 |
| 11 | 多机同任务 | SKIP 撞车重复烧卡 | 确定性分片互斥 |
| 12 | ssh 双引号包 awk $1 | busy 误报 | 远程命令单引号 |
| 13 | 判决只落汇总 JSON | 审计不可复验 | 原始数据+manifest+脚本入库 |
| 14 | CI 含 0 写「持平」 | 统计措辞超证据 | 「未证明优于/未检出差异」 |
| 15 | nohup 不带 </dev/null | ssh 断开链死 | 显式 < /dev/null |

## 6. 监督与收割

- **定时监督器**（2h cron 足够）：四机巡检 GPU + 产出行数 →
  GPU 空闲 = 任务完成或异常信号，两种都触发收割动作：
  ①完成：rsync 拉回（`--exclude='*.lock'`，generation 协议文件不拉）
  → 官方 scorer 打分 → 判决 JSON 落袋入库；
  ②异常：log 定位 → 修复 → 重派（SKIP 幂等使其零成本）；
- **空卡补位**：某机提前收官，把在飞链队尾最重的未跑任务包抄到空卡
  （新派单跑同任务，与原链 SKIP/文件名互不冲突——但注意分片互斥原则
  的例外只在链即将自然跑到该任务时允许，否则纯重复烧卡）；
- **断点续跑**：一切链脚本可整链重跑（SKIP 幂等），重启安全；
- **拉回对账**：按 best-file 口径盘点缺口（多文件取最大行数），
  全格达期望行数才算收官，再走正式打分门禁。

## 7. 判决与证据纪律

- 小试判决：任务级配对差 + bootstrap（显式记录 RNG 类型、B、seed、
  任务顺序、CI 取法——只记 seed 不足以唯一复现）；
- 判决 JSON 绑 `input_manifest`（逐文件 basename/行数/sha256），
  分数与原始预测的绑定不断链；小数据（<10M）整库入库；
- 措辞纪律：CI 含 0 = 未证明优于/未检出差异；显著才写显著；
  等价主张须 TOST + 事前界值；
- 双口径铁律：microbench 与 e2e 都测都报，排序反转如实并报。
