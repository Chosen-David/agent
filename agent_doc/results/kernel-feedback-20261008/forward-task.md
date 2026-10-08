# 代码优化任务：合成诊断材料

PROJECT_ROOT 为当前 agent 仓库，但这是一个合成案例，不能当实际 GPU 编译或测量。请从 repository 的 research-implement-optimize/SKILL.md 入口执行必要流程，分析同目录 forward-input.log，给出下一步最有区分力的优化检查。

输入上下文：候选 kernel 目标 H100，现有构建配置 CUDA 12.4、-rdc=true，使用动态 shared memory。手工摘要称“寄存器较多，应该直接启用 shared-memory spilling 或 Blackwell tcgen05，就能更快”。目前没有计时原始数据、profiler 导出和可信编译退出码。只允许 CPU 文件分析，不执行 GPU 编译、安装或 benchmark。

输出供主 AI 接收的 markdown 和实际工具轨迹/解析 JSON；使用你自己的判断指出当前能确认什么、哪些候选值得试、还缺哪些输入。不改生产文件和 TASK。
