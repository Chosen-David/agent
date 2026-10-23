# PY39-INGEST-01：有界 Python3.9 导入兼容

基线 a1f61112366bff8393d6f85b2b1c8c35e4829c31 允许3.9安装；agent_runtime/knowledge_ingest.py:43/44/51仍用3.10新增的Path.write_text newline参数。Python3.9.25真实运行setup/doctor/ingest-scope共32项，5 errors均为导入TypeError。无语料发布成功；历史Python3.10+导入数据不因此失效。

修复：三处使用Path.open('w', encoding='utf-8', newline='\n')，保留序列化、LF、哈希、候选验证与rename；同步model-with-knowledge生成镜像。混合换行测试增加精确body字节检查。

本地原始短日志（各exit0，修前exit1）：
```text
3.9 修前: Ran 32 tests in 1.322s; FAILED (errors=5)
TypeError: write_text() got an unexpected keyword argument 'newline'
3.9 修后 setup/doctor/scope/read-boundary: Ran 37 tests in 3.199s; OK
3.9 Knowledge: Ran 117 tests in 29.291s; OK
3.12 Knowledge: Ran 117 tests in 20.115s; OK
```
命令：python -m unittest tests.test_setup tests.test_setup_doctor tests.test_knowledge_ingest_scope [修后另加tests.test_knowledge_read_boundary]；Knowledge为python -m unittest discover -s tests -p 'test_knowledge*.py'，分别使用实际3.9.25和3.12.14。同步--check与git diff --check通过。以上秒数仅日志，不是性能A/B。

独立复核见[结果](../results/py39-ingest-20261023/independent-review.md)及可复现probe。Linux x86_64，CPython3.9.25/3.12.14，无第三方导入依赖、无GPU/kernel配置。输入为仓库固定测试/临时语料，probe覆盖UTF-8、CRLF/CR/LF/U+2028/无末换行；哈希见结果manifest。未用私密数据。

采用兼容文件API；不更改Skill原3.10+文档为全目录3.9承诺。Windows、其它模块3.9兼容、真实宿主/模型/全任务质量/usage/性能仍未验证，无速度/内存收益声明。SYSTEM-99同批继续open，十篇私有正文记录不替代全链验收。
