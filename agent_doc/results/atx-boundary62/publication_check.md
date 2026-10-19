# 发布前核对

仅发布v2生产实现；独立结果验收在result_review.md，生产hash ab45ef3d0a9005741951a1e8c114366533338c861373cbdd78ac1efd41558a8c，原始72case及已验新增控制不改。收尾TASK/Progress/CODEMAP只归纳结果，旧稳定计划hash和原审核保留。结果登记为historical-external-reference/unknown，仅用于检索，不能替代独立验收。

暂存检查发现一项纯空白提示：已执行且hash绑定的 independent_probe_v2.py:189 末尾有额外空行。为保持冻结实验脚本身份，原样保留，不事后格式化。普通 `git diff --cached --check` 会报告此一提示；忽略 blank-at-eof 后的检查用于确认无其他空白问题。validation.txt里此前 `git diff --check` 的成功仅是当时已跟踪工作区的检查，不冒称覆盖全部最终新暂存文件。

四份完整独立raw约7.8MB不入git；紧凑摘要、full-file hash、生产原始小矩阵与重放脚本发布。原始完整文件仍本地，不能承诺本地scratch永久保留。未暂存无关归档临时文件、guide文件或凭据；没有强推/PR/额外分支。

发布前origin/main再次fetch核对仍b69b4150e41492183433b1061add742aaa44510b；实际push及远端SHA/tree回读由主控在交付中报告，本文不预报成功。
