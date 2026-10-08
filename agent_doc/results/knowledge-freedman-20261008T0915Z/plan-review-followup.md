# Preserved independent plan-review follow-up

Actor: /root/knowledge_review. This is the actual independent host response transcribed from the conversation; it is not a signed runtime ReviewSession receipt. The earlier plan assessment and scientific conditions are retained in plan.md, source-review.json and the candidate contract. The follow-up corrects the earlier overstrict PDF-hash recommendation and independently checks the finite counterexample.

计划 approve，允许在本轮45分钟、最多1项知识的边界内推进候选与验证。不恢复旧 neuro lineage，不重建其预算；发布仍依赖另一上下文的独立结果验收及逐查询非退化。

更正我前次措辞：PDF 字节哈希是建议的增强追溯证据，不是必要科学阻塞。可使用固定 arXiv:1101.3039v1（2011-01-16）、作者刊物 PDF 的明确定位、实际 web 读取记录，并如实写 original_pdf_sha256=unavailable。不要把 arXiv 版本与刊物 PDF 当作字节相同文件，页码分别记录。

已核查指数符号：作者 PDF §2.3 证明得到 exp(-θx+g(θ)v)，§3 用正函数 h(u) 与其下界得到负指数；定理抽取中的双负号不能照抄。作者 PDF，印刷268–270页：https://tropp.caltech.edu/papers/Tro11-Freedmans-Inequality.pdf

DP负例逻辑正确，且独立复算一致：
- 公平随机游走满足 R=1,V_n=n。
- b_n=2+sqrt(6n) 满足 b_n²≥6n+2b_n，故每个固定预算 v=n 的 Freedman 指数至少3。
- 整数谓词 s≥2 且 (s−2)²≥6n 与越界事件严格等价。
- 我独立以整数路径计数、吸收首次越界并逐步检查总质量2^n，得到 P(存在n≤1024:S_n≥b_n)=0.060713409787025684 > exp(-3)=0.049787068367863944。
- 这证明不能把各固定方差预算的保证不花错误预算地拼成同时保证。此例中V_n=n是确定的；准确称为“逐时刻改变预算的负例”，也足以否定一般的随机V_t直接代入主张。

认可隔离评测副本临时published、正式库保持candidate的方案。保留现有context/morphology基线失败和全部逐查询结果；新增退化未解决则不发布。
