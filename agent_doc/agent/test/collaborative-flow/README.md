# COLLAB-01 全流程验收

`python scripts/project_test.py --workflow-root ROOT --target ROOT --project agent --task collaborative-flow --output EXTERNAL_NEW_DIR`。同一用例接入根 tests/test_collaborative_flow.py。

先准备测试后实现；红灯缺少模块，属于功能未实现，不是已杀死业务变异。验收重点是默认模式、正常等待/超时接续/答复及重启、关键决定不能委托、过期写入/取消/异常不得重放、环境能力正文加载、任务定向测试和真实 CLI。用户不要求精准十分钟计时，不做毫秒级阈值测试。

临时 Git 项目实际生成代码、运行任务脚本并核验 report；错误结果、被改测试和崩溃作负例。双模型身份与回应由合成可信宿主模拟，不调用真实模型，不证明理解准确率、GPU 性能或后台服务已部署。主 AI 自检与独立模型验收分别报告。
