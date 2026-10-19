# CONTENT-COPY-60：减少正文重复JSON编解码

基线 `4bdb071f5dc9b83c36cdc1b36df5a28a1a1f7823`，`agent_runtime/knowledge.py:217` 的 get 克隆整个条目，包括不可变Markdown正文。实际context最终入包会重复支付这部分编码、解码和分配成本。不是选集或质量bug。

修复：严格普通dict、ASCII普通字符串外键、普通且无surrogate的正文走元数据JSON克隆并按原序补回正文；其他情况沿用原克隆。保留JSON嵌套值规范化、可变元数据隔离、状态/依赖检查、调用钩子与配额。插件镜像同步，源文件CRLF保留。

固定同机同语料16场景，完整context计时（search预计算，模型未调用），2预热、11交替配对、每样本10次；tracemalloc单独测。主场景matrix/5/related，中位数2.4684909→2.0544492ms，下降16.7731%；峰值97034→49475bytes。所有场景耗时下降2.45%–35.30%，追踪峰值下降18.25%–49.01%。仅单轮本地观测，无独立计时重复、CPU绑核/负载记录或跨机保证，不能推导模型质量/端到端TTFT收益。

环境：AMD EPYC 9V74，Python3.12.14，Linux x86_64，具体平台/输入输出hash/115条语料snapshot见raw.json。无CUDA/kernel。独立审核复算门槛并重现16输出和54边界比较。原始执行脚本measured-probe.py，重放脚本probe.py固定git基线；集成后仅修正重放源码定位，没有重测或改写raw。初次导入路径失败发生在计时前，随后添加项目sys.path。

修前专项4项中正文identity断言失败（其余3项通过）；它证明额外复制，不声称原行为违反公共值契约。修后专项含既有metadata检查8项通过，Reader3通过；全库和最终独立集成审核另附。历史性能结果不改；将来比较get/context须使用新基线，search、生成和构建成本未在该收益内。
最终回归：全库1301项，8跳过，OK；专项8项、Reader3项通过。短原始摘要见validation.txt，完整本地日志供独立审核。生产实现与测量替换逐字节一致。最终发布验收见integration_review.md；远端更新和回读由主控执行。
