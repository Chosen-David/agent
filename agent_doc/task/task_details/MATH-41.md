# [MATH-41] 旋转对的交织映射与跨频率融合条件

Task-ID: MATH-41
Date: 2026-10-08

## Plan

有限二维旋转的实线性交织分类，整数位置频率alias/符号与0、pi退化；近似缺陷与长度界。单卡，32公开CPU案例、六检索、一完整包。producer→真实独立verify_experiment_result→消费者。主AI唯一TASK/卡作者；独立owner按AGENTS由宿主另上下文指派。无SGLang/模型/GPU/付费/生产更改；有界直接宿主，tmux不可用不冒充受管部署。

## Progress

先pullmain152167d，空GUIDE只读、既有角色/索引/状态已读，上一轮completed；实际先查结果，旧低秩卡只有警告、不能替代本轮分类证明/数据。

独立六域验收usable-with-scope：32公开样例、25有理解空间维数及混合块/受限等距；75位Decimal参考最大误差6.98e-15。六检索、2716tokens、74回归通过；无模型/形式化/节省保证。发布待远端核对。

实现提交 `1c2fd6b9e59122324eb9fcaf4cebf1a3e179587a` 已直接推送main；远端提交与本地树一致，工作树干净。
