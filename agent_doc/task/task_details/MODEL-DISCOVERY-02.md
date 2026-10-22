# MODEL-DISCOVERY-02：自动发现的临时文件所有权

Task-ID: MODEL-DISCOVERY-02
Date: 2026-10-22

## Plan

Version: 1

同一SYSTEM-99批次，修复实际安装入口而非新一轮优化。基线d8abd23e。用户授权审查、修复、必要验证后直推main；guide空且只读，保留其他工作。新main引入setup.py `_auto_discover_inventory`；install/doctor均调用它。

已复现：未配置ANTHROPIC_BASE_URL时helper返回None，但finally仍删除项目同名`.claude/agent-workflows/_discovery_tmp.json`。首次安装输出父目录不存在；发现脚本写入失败会回退空inventory。TimeoutExpired未被现有OSError/ValueError捕获。共享固定路径也不能区分调用所有权。

方法：保留已有环境条件、发现命令、30秒上限及返回协议；先查网关环境，再在系统临时区域创建调用独占TemporaryDirectory，读取结果后由上下文清理自己的目录；不读写/删除项目固定临时文件，TimeoutExpired按既定发现不可用语义返回None。不改模型偏好、能力猜测、协议/凭据、真实网关或doctor其他逻辑。

先新增失败回归并在基线运行保存；覆盖无网关原文件保留、首次发现成功（模拟发现进程）、超时回退、失败/非法JSON清理、两个调用输出隔离、完整安装消费inventory和既有目标文件保留。使用mock只替代发现子进程，不运行模型/网络，不把fixture称真实后端验证。普通/-O及setup/model-routing/install相关回归，独立复核实际源码、原始失败和结果后发布；不主张性能或模型质量收益。独立计划审核与结果审核分别进行，缺runtime认证不伪造回执。

已有结果检索：`auto discover model inventory temporary setup`仅命中无关advice/历史同步候选，max100部分检索且历史若干文件缺失；无相同改动验收可复用。继承SYSTEM99阅读检查点14篇，不把小修或技能安装计新轮。发布前fetch，处理并发，不强推/建PR；精确文件暂存并回读远端SHA/整树/关键内容。

## Progress

- 原始最小复现输出：`{'result': None, 'existing_user_file_preserved': False}`。修前日志和回归待录入，未宣称修复成功。

- 原始7项回归在基线出现3failure/5error，完整短日志保存；独立git-show加载基线复现相同失败。候选普通/-O各7通过，setup/model-routing/install-profiles/role-process相关40通过；独立另跑7/7+40，并补测缺结果、OSError、部分写入后timeout、坏UTF8/重复JSON、非零退出、无环境不分配/不调用进程以及真实安装消费模拟native inventory。首次独立探针对角色偏好的错误预期已更正，原记录保留，不当生产缺陷。
- 独立计划approve、结果ACCEPT usable-with-scope；仅普通本地正确性回归，不假称runtime认证回执。独立检查安装器确实把模拟inventory用于符合当前policy的角色/生成model字段。无真实网关或模型调用，不报告速度/质量/费用收益；不能外推显式discover或doctor全链。
- 方法与源码位于setup.py:237–257；临时输出改为标准库独占TemporaryDirectory，保留30秒上限、错误时None和原消费接口。旧项目同名文件不读写/删除。已有不同目标和未提交修改未覆盖，人类guide未改。
- 后续未决：显式discover仍使用项目model_inventory.json路径，doctor局部os导入与模型快照更新需独立复现/规划，不由本提交冒领修复；SYSTEM99真实模型质量/usage/成本、tmux宿主等缺口保持open。新文献阅读数没有增加，不计新一轮完成。
- 公开证据：agent_doc/results/model-discovery-1701/；中文简报：agent_doc/advice/MODEL-DISCOVERY-02.md。候选已验证，发布前fetch及远端SHA/整树/关键内容由主控最后回读，实际结果记对话与私有检查点。
