# Hermes Wiki Schema

> 规范：结构、约定、标签体系

---

## 域名

`Hermes Agent Knowledge` — Hermes助手知识库

## 文件命名规范

- 文件名：小写字母、连字符
- 页面必须有 frontmatter (YAML)
- 用 `[[wikilinks]]` 链接其他页面

## 页面类型 (type)

| type | 含义 | 示例 |
|------|------|------|
| `entity` | 实体（人物、公司、产品） | `entities/user-d统领.md` |
| `concept` | 概念（主题、技术） | `concepts/karpathy-method.md` |
| `comparison` | 对比分析 | `comparisons/llm-vs-rag.md` |
| `query` | 有价值的查询结果 | `queries/esp32-selection.md` |

## 标签体系

```yaml
tags:
  - user          # 用户相关
  - project      # 项目相关
  - tech         # 技术相关
  - preference   # 偏好设置
  - environment  # 环境配置
  - skill        # 技能/工作流
  - knowledge    # 知识库
```

## 必需字段

每个页面必须有：

```yaml
---
title: 页面标题
created: 2026-04-22
updated: 2026-04-22
type: entity | concept | comparison | query
tags: [标签1, 标签2]
sources: [raw/articles/源文件.md]  # 可选
---
```

## 创建阈值

- **创建页面**：一个实体/概念在 2+ 个素材中出现，或在一个核心素材中占主导
- **不创建**：仅一次提及、minor 细节
- 每个页面至少链接 2 个其他页面

## 目录结构

```
wiki/
├── SCHEMA.md           # 本文件
├── index.md            # 内容目录：一句话概要
├── log.md              # 操作日志：按时间记录所有行为
├── raw/                # 原始素材（不可修改）
│   ├── articles/       # 网页文章
│   papers/         # 论文
├── entities/           # 实体页面
├── concepts/           # 概念页面
├── comparisons/        # 对比分析
└── queries/           # 有价值的查询结果
```

## Lint 检查

定期检查：

- 孤立页面（无 inbound 链接）
- 失效链接（指向不存在的页面）
- 矛盾内容（同一主题不同说法）
- 过期内容（90天未更新）