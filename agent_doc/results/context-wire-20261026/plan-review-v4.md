# CONTEXT-WIRE-01 v4 发布CI增量方案审核

Verdict: **approve**，仅批准在现有 portable-install.yml 的 test_context_cli_output.py 步骤后新增：

`- run: python -B -m unittest discover -s tests -p test_context_cli_wire.py -v`

已读 plan-v4.md、当前完整 workflow、当前 fixture/runner hashes及主控 result.log/json。此候选是在已有四组 Ubuntu/Windows × Python3.10/3.12 安装CI加入同一新回归；不得改变原 matrix、timeout-minutes:10、contents:read、固定 actions、runner、其余步骤或触发方式。当前审核时该行尚未写入。

七域：intent=pass（把已固定CLI回归纳入既有发布CI）；guide=pass（不写guide，不替代SYSTEM-99）；assumptions=pass（CI未来状态未知，原生Windows须看该提交实际jobs）；prior_results=pass（主控119项通过仅本机局部证据，失败原件保留）；acceptance=pass（新行精确运行现有7方法，非fullsuite）；risk=pass（无权限/服务/依赖增加，失败保留且不手动rerun）；resources=pass（沿用既有push授权/矩阵/10分钟边界，本地主控3/3不重置，独审仍仅一次原固定suite/120s）。

本地无原生Windows声明；未来CI成功也仅支持其实际7方法覆盖，不支持完整suite、PID/全局模型质量/性能。此审核不代表CI已执行、发布结果通过或替代独立结果验收。本次仅写本文件，尚未执行独审suite。

| 路径 | SHA-256 |
| --- | --- |
| `agent_doc/results/context-wire-20261026/plan-v4.md` | `e3c28b172190e9db3207826659304cb6f43c774b7a6636543103874ddfccdd91` |
| `.github/workflows/portable-install.yml` | `3d2c5511acfe11031cd8efed148c74a2fb048c1ccdc981aea2aa9ab9d4ae63c0` |
| `tests/test_context_cli_wire.py` | `9be90cda92adc5c68d238d1e778f7d45e0fc170ca378196b66c396e6667904fb` |
| `agent_doc/results/context-wire-20261026/run_checks.py` | `80565f43d01e48cd6304ec5eb11323243fe06dc9dd421aaca5f0ba57f80d9c53` |
| `agent_doc/results/context-wire-20261026/result.json` | `1552f3f924e781f2c5e4a7fdedd1c1792c86bcc42d56aa4096b55abd690fb52a` |
| `agent_doc/results/context-wire-20261026/result.log` | `11285d0b390a108fc4803569dcff9ae722d18edfc33a43f9614563ced57baec3` |
