# [SELF-SYNC-01] 核对 Codex 技能与真实入口

Task-ID: SELF-SYNC-01
Date: 2026-10-07

## Plan

用户要求本会话接入 agent，并随每次 pull 更新技能。主 AI 唯一作者；保护本机修改与已取消研究，不改模型权重/权限；保留原 3600 秒任务。验收：核对 Codex 技能与真实入口，以源码、测试与真实远端/安装回执为准。

## Progress

原基线 a52e95e 的实现及 553 项回归已记录在 docs/codex_adoption/pull-sync/。并发 main ed6b7a2 改为 doc/task/；本轮保持其迁移与新增角色契约，合并后再验。最后发布与安装等待完成；未完成项继续由主 AI 负责。
