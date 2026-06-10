# Hermes Wiki 使用指南

> 基于 Karpathy 理念的持久化知识管理系统

---

## 核心理念

Wiki 是**累积式知识库**——知识只整理一次，后续查询直接查。
Blog 是**工作记录**——有价值的思考和成果，存下来形成上下文。

**博客命名格式**：`{日期}-{项目}-{主题}.md`
例如：`20260505-ai-colleague-browser-auto-方案设计.md`

**博客与 Wiki 的区别**：
- Wiki = 结构化沉淀（entity、concept、comparison）
- Blog = 工作记录（调研、方案、复盘、思考）

---

## Orient（每次操作前必读）

**每次需要读取记忆时，必须先读取这三个文件：**

1. **SCHEMA.md** — 了解规范、标签体系、结构要求
2. **index.md** — 了解已有哪些页面
3. **log.md** — 了解最近做过什么

跳过 orient 会导致重复创建、错过交叉引用、违背规范。

---

## 博客格式

```yaml
---
title: browser-harness 集成调研
created: 2026-05-02
project: ai-colleague
project_phase: research
status: completed
archived: false
blog_origin: 验证 browser-harness 作为浏览器自动化方案的可行性
sources:                     # 标注来源
  - 原始会话/sessions/xxx.md
  - https://github.com/xxx
confidence: high             # high/medium/low
summary: |
  3-5句话，涵盖背景、关键发现、结论
tags: [ai-colleague, browser]
related_blogs:               # 至少2个关联博客
  - 20260505-ai-colleague-xxx.md
  - 20260501-hermes-xxx.md
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 标题 |
| `created` | ✅ | 创建日期 YYYY-MM-DD |
| `project` | ✅ | 项目名 |
| `project_phase` | ✅ | research/design/development/testing/optimization/completed |
| `status` | ✅ | active/completed/paused |
| `archived` | ✅ | true/false |
| `blog_origin` | ✅ | 一句话说明写这篇的原因 |
| `sources` | ✅ | 来源标注 |
| `confidence` | ✅ | high/medium/low |
| `summary` | ✅ | 3-5句话 |
| `tags` | ✅ | 标签（必须来自 SCHEMA.md taxonomy） |
| `related_blogs` | ✅ | 至少2个关联博客 slug |
| `updated` | ❌ | 最后更新日期 |

---

## Wiki 页面格式

```yaml
---
title: 页面标题
created: 2026-04-22
updated: 2026-04-22
type: entity|concept|comparison|query
tags: [from taxonomy]
confidence: high|medium|low
sources: [来源]
---

正文内容...

交叉引用：[[other-page]] 至少2个

来源追溯：段落末尾加 ^[raw/articles/source.md]
```

---

## 归档规则

- **90天无更新** → 标记 `archived: true`
- 归档不是删除，召回时搜得到
- 归档内容**不主动出现在上下文**中（除非被问及）

---

## 定期迭代

- **每月末**：运行 Lint 检查，更新归档状态
- **写新博客**：确保所有必填字段完整，related_blogs ≥2 个
- **创建 Wiki 页面**：确保 wikilinks ≥2 个

---

## 工具

```bash
# Lint 检查（孤立页面、断链、过时）
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --lint

# 召回博客摘要
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --list

# 召回内容中的 wikilinks
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py "内容..."
```
