# SYSTEM-99 阶段N独立方案审核

首次结论：**revise**。审核者独立只读复算初稿的12目录、418文件、5227489字节、
名称/原件哈希、Git跟踪与ResultStore不授信语义均一致，但发现一个身份冲突：
`comm20-20261009/final-integration/{contract,manifest}.json` 明确声明另一run
`comm20-20261009-final-integration`，且该run已有独立顶层native record。把整棵父目录再次
登记会重复包入已登记子run，不满足“单一顶层身份”的前提。

方案据此排除 `comm20-20261009`，并新增机械条件：子树不得有contract/manifest声明与顶层
不同的run_id/result_id。返修冻结值为11目录、358文件、3349153字节、最大105432字节；
名称SHA256 `4b9183b865b80a59978819cb20b7abc6733de18dcb1cd4619ed8b374bbbe7c11`，
排序 `path<TAB>sha256` SHA256
`cd94f4498658227686e55ce913690ea40dd8e5b6e10e3274782aa3203a2fc370`，预期错误38→27。

第二次复核结论：**revise**，仅因方案末段残留“418个原文件”，与返修后的358不一致；
机械集合、哈希、HEAD blob一致性、同run的pre-sync保留及错误38→27预测均通过。该残留已改为
358。

最终结论：**approve-with-scope**。只允许在基线 `4240287294ee7c90fc675902c7af5fc40a0a9cef`
为列明11目录各新增一个现有 `register_history` 生成的unknown历史record，绑定冻结358原件并
使用顶层H1摘要。原件、既有record、runtime/schema/guide/TASK索引不得改；写前fetch重算，
漂移即停。批准不覆盖其余27目录，不接受旧结论/复用、模型质量、token/速度/费用、真实宿主
或多轮质量，也不表示SYSTEM-99完成。
