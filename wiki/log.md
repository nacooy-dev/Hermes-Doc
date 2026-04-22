# Hermes Wiki Log

## 2026-04-22

### 下午工具链完善（克鲁斯执行）

- [create] scripts/init-hermes-doc.py — 新项目一键初始化脚本
- [create] scripts/analyze-project.py — 项目上下文自动分析脚本
- [create] skills/project-context/SKILL.md — 项目上下文技能说明
- [update] README.md — 更新目录结构，添加 scripts 和 skills
- [update] wiki/log.md — 记录工具链完善工作

**工具说明：**
- `init-hermes-doc.py`: 为新项目创建 `.opencode/config.yaml` 和 `.claude.json`，注入 Karpathy 原则
- `analyze-project.py`: 自动识别项目类型（Python/Node.js），提取依赖、框架、测试命令，生成项目摘要

### 下午修正（克鲁斯执行）

- [delete] .cursor/ 目录 — 用户不使用 Cursor，已删除
- [create] INTEGRATION.md — 各 AI 工具集成指南（OpenCode/Claude/Qwen/Hermes）
- [update] README.md — 更新工具集成说明，移除 Cursor 引用
- [create] blog-post-draft.md — 博客草稿《拒绝"网约车"思维》

### 上午完善工作（克鲁斯执行）

- [create] README.md — 项目总览和使用说明文档
- [create] EXAMPLES.md — 8 个使用场景示例和最佳实践
- [update] wiki/index.md — 完善索引页面格式和内容
- [update] wiki/log.md — 记录本次完善工作

### 早期设置

- [create] Wiki initialized — 创建目录结构和 SCHEMA.md
- [create] index.md initialized — 空索引页面
- [create] log.md initialized — 操作日志
- [update] system_prompt.txt — 加载行为规范（Karpathy 四原则）
- [update] config.yaml — 添加 prefill_messages_file 引用
- [create] wiki/WIKI_GUIDE.md — Wiki 使用指南
- [create] wiki 目录结构 — raw/articles, raw/papers, entities, concepts, comparisons, queries
