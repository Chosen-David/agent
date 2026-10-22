# MODEL-DISCOVERY-02：自动模型发现临时文件误删与首次安装回退

状态：候选已独立接受（限定范围），main发布回读由主控闭环。基线 `d8abd23e4626a5d5ee43b9a6cf77388b86da842e`；相关实现 `setup.py:237–257`，新增回归 `tests/test_model_discovery_setup.py`。

自动发现先于安装预检，却使用项目固定 `.claude/agent-workflows/_discovery_tmp.json`。没有网关时也进入finally删除同名文件；首次安装父目录不存在，发现进程无法写输出而回退；超时异常没有被捕获。两个调用还会共享结果路径。

修复使用标准库调用独占临时目录，环境缺失时不创建临时输出，也不碰项目固定文件；成功/失败只清理自己目录。发现子进程的30秒上限、原返回值及安装消费接口保留，TimeoutExpired作为发现不可用返回None。没有更改模型策略、凭据、网关API或外部服务。

真实执行：基线7项出现3failure/5error；修后普通与优化模式各7通过，相关安装/路由40项通过。独立上下文重新加载基线复现失败，候选7/7+40通过，另核输出清理、无环境不分配、部分超时写入、非法输出与安装消费模拟native库存。首次独立探针错误选择角色预期，原错误和更正均保留。环境Linux/Python3.12，输入为公开CPU fixture，代码/输入hash、原始短日志及完整独审见[证据](../results/model-discovery-1701/manifest.json)。

这是一项所有权和回退正确性修复，没有性能/JIT/GPU/质量/费用数据。网关与模型由进程替身隔离，不把模拟响应当真实服务可用；两个重叠helper调用不保证整个installer并发事务。显式discover、doctor其他逻辑仍需审查，原SYSTEM99未决项保留。
