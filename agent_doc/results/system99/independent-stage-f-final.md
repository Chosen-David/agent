# SYSTEM-99 阶段F最终独立验收

结论：`usable-with-scope; blocking_findings=[]`。仅接受Plan6中完整已知v1词法查询的纯扫描计数漂移修复，范围为本地CPU合成链与有限回归；不表示SYSTEM-99整轮完成、发布、生产宿主认证或模型质量/性能收益。

本角色独立读取AGENTS、决策/项目文档/结果复用/结果验收流程、唯一SYSTEM-99 Plan6及Progress、暂停恢复记录、search-review与旧independent-stage-f全文，全文审查生产diff和新14方法，核对实际算术fixture/独立验证器。主控持锁99917及源码/TASK单写权；本角色只新增本文，未改旧证据、源码、任务或guide，未发布或启动真实host/model/收费任务。基线HEAD为`789697f2b3e2e190a6954248d4b18cbbe0b44a4d`；远端同步/后续发布由主控负责，本验收不冒称已核验发布。

## 固定输入与先查

| 对象 | SHA-256 |
| --- | --- |
| `agent_runtime/task_manifest.py` | `b9bef1029d9aa1b5b0d83c793c0f676b05ccdacc20a21be948f1cccaefcf1729` |
| `tests/test_prior_search_drift.py` | `4778fc87b0c0e279f729b866ef2c34a33befc8de39c207089da0b906d69bed7b` |
| `tests/test_result_validation.py` | `79e3840fe6b39432526e4c75fcf98f9c6bf2a3aa410e58d2d281550902482377` |
| `SYSTEM-99.md`（核对时完整Plan6/Progress） | `b639ade3b4135ef68c4b5c6a33e68f03c7c20b578b869aa3ea74d1a2b4e457af` |
| `search-review.md` | `7f8f399c9a2ccb52c97012a8b6bb408554de70dcc7eba5f324a9d1d743fa7a24` |
| 旧`independent-stage-f.md` | `056d8865158886de7e683c2a078d1b9d1e75b7e2a8dc42cc76162d7b83dfa73d` |
| 主控最终`stage-f.md` | `a9f61a2193eb6662215943f8f4aaccb1bbec106e543ab3b605263ebb0bf855b1` |

新增复验之前真实调用`ResultStore('.').search('prior_result_search scanned drift', limit=5, max_scan=5000)`（亦实际调用同查询CLI）：scanned252、errors81、partial=false、status=incomplete、results=[]。未命中不证明没有历史结果；旧独审仅作定位和版本沿革，不直接恢复信任。决定`verify_delta`：重读当前字节、补独立14项及Reader/sync，复核主控最终v3日志，避免重复无新信息全库。

## 代码、数据与恢复边界

- 新例外限定两端完整9键v1/lexical、合法类型、默认扫描0..200且覆盖返回项、无errors/partial、合法候选结构；去掉scanned后JSON完全相同。候选新增/消失/hash/顺序/分数、query/authority/status/未知字段和缺口变化均不能走该例外。相同旧格式保留既有same路径，不把此兼容写成新白名单许可；原结构加JSON比较拒绝bool/int、tuple/list和对象键编码碰撞。
- 正向真实CPU链alpha→verify-alpha→beta→verify-beta完成，两个producer handler恰各派发一次，整个handler task与冻结任务相等，持久plan全对象、plan SHA和receipt不改；实际新lookup仍完整入journal，另有0→1分类。重开Engine仍传原搜索且计划审核请求只有一次。
- 新候选/缺登记目录负控实际查询；partial/unknown/bool/负值各独立fixture并断言lookup及journal，避免旧版本共享blocked状态的空过。helper表覆盖候选hash/score/order与双侧相同畸形元数据仅count变化。白名单不会仅因“其它字段不等”才拒绝。
- 分类日志抛OSError时beta底层handler未执行，恢复日志并重开Engine仍blocked、未重放。显式reproduction/new_claim仍真实执行，不转成复用；既有结果/授权/审核gate未被替换。
- 独立算术验证使用不同闭式公式复算平方和、样本ID/重复、边界和代码错误类型，原始n=[0,1,2,7,19]、repeats3、seed0、dimensionless；测量有效性因无性能主张而按协议N/A。setup的make_fixture也执行准备代码，因此“各一次”仅指受管producer handler。测试adapter角色隔离不是多模型宿主身份认证；有限整数数据不代表真实任务质量。既有check/effect非原子、声明依赖完整性及不完整搜索仍可能阻塞等局限保留。

## 本角色直接复验

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_prior_search_drift -v
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s apps/paper-reader/tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
git diff --check
```

分别14/14通过（4.974s）、Reader应用3/3通过（1.106s）、sync实际工具exit0且无输出、diff检查exit0。结果为当前独立执行，不拿旧139或-O14自报替代。本轮未重复全库或优化模式；下表是主控日志的独立核算，非本角色独立全库实跑。

## 主控最终日志逐行核算

实际读取全部日志、逐条计数outcome并核对终结行；路径均在`.agent-runs/system99/`，作为冻结历史路径/hash引用，未声称搬移原始日志。

| 日志 | 核算结果 | SHA-256 |
| --- | --- | --- |
| `full-f-v3.log` | 1391条：1383 ok、8 skipped、0 FAIL/ERROR；105.909s，终结OK(skipped=8) | `c69d89ea4bdbb713a25f0be8e5a35bda16dd36baa5fa1ae05652195a1514cb29` |
| `focused-f-v3.log` | 106 ok、0跳过/失败/错误，14.725s | `dd07ca33c0d571791934cb2315c3dfa5054e7305efb76dfa1e17de1765b7d48f` |
| `optimized-f-v3.log` | 14 ok、0跳过/失败/错误，7.388s | `4cacb30ff1e3e9333607ff5a21264de08c87a3c9d13aad15f69432f62f226a32` |
| `reader-app-f-v3.log` | 3 ok、0跳过/失败/错误，1.585s | `a644317e288bdfa877d208b98a0e9139f14b5d57e0b638ddfa9de52b9c771d69` |
| `sync-f-v3.log` | 空文件；其本身不能证明成功，本角色已独立执行check且exit0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

8跳过中7项为crossfeature绘图依赖/字体缺失，1项为真实tmux opt-in，均不算通过。根Reader/Memory4项是全库子集，与Reader应用3项分列。主控stage-f最终计数、版本区分及fixture描述与当前日志/字节一致；旧v4/full-v2只归旧候选，before-v3生产红证与fixture错误记录均未覆盖。本报告关闭旧独审“v5最终全库v3未读”的pending，仅限本阶段结果接受。

剩余历史登记覆盖、真实协作/记忆更正消费者、Claude新会话、多模型任务质量/总成本、tmux/SSH宿主等仍由SYSTEM-99保留open；本阶段接受不解除这些门禁。下一owner为主控：仅按当前授权维护Progress与发布检查点，任何源码/测试/输入变化须重新判断受影响验收。
