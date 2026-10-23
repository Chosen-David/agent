# PY39-INGEST-01

Task-ID: PY39-INGEST-01
Date: 2026-10-23

## Plan

SYSTEM-99 同批有界兼容修复，基线 a1f61112366bff8393d6f85b2b1c8c35e4829c31。该提交允许 Python3.9 安装，但 Knowledge 导入仍调用3.10新增的 Path.write_text(newline=)。只替换为既有 Path.open(..., newline=)；保留UTF-8、LF、候选验证、快照、哈希、临时目录与rename语义。由权威源同步Skill镜像，guide只读，不扩大所有Skill的最低版本承诺。

验收：实际Python3.9.25修前失败与修后回归，Python3.12相邻回归，正文换行字节与独立Skill隔离调用；必要独立复核。验证后fetch，普通发布main并回读。无性能/模型质量主张，SYSTEM-99仍open。

## Progress

- 修前实际Python3.9.25执行setup/doctor/ingest-scope共32项，5 errors均为导入写入newline参数TypeError；原日志在私有运行检查点。修后同组加read-boundary共37项通过（3.199s），包含隔离Skill CLI。
- 三处写入改用Path.open，增加既有混合CRLF/CR/LF/Unicode测试的输出字节断言；镜像由sync_plugin_references生成。Python3.9及3.12各117项Knowledge回归通过；独立模块/隔离Skill导入、字节/receipt/旧语料不变与重复拒绝复核通过，usable-with-scope。见../../advice/PY39-INGEST-01.md与../../results/py39-ingest-20261023/independent-review.md。普通发布与远端回读另核。
