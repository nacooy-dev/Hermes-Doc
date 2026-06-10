# LLM Wiki 配置指南

> 本文档记录 LLM Wiki 从零开始配置的完整步骤。
> 基于 Karpathy's LLM Wiki 模式构建。
> 迁移说明（2026-05-19）：本文原属 Hermes-Doc 旧路径配置指南，保留作历史参考。当前统一 canonical wiki 路径为 `/Users/lvyun/.hermes/wiki`，`WIKI_PATH` 也应指向该路径。


## 配置概述

| 项目 | 值 |
|------|-----|
| 域名 | Hermes Agent Knowledge |
| 路径 | `/Users/lvyun/.hermes/wiki` |
| 环境变量 | `WIKI_PATH` |

---

## 配置步骤

### Step 1: 创建目录结构

```bash
mkdir -p wiki/{raw/{articles,papers,transcripts,assets},entities,concepts,comparisons,queries}
```

生成的目录结构：

```
wiki/
├── SCHEMA.md           # 规范定义
├── index.md            # 内容目录
├── log.md              # 操作日志
├── raw/                # 原始素材（不可修改）
│   ├── articles/       # 网页文章
│   ├── papers/        # 论文
│   ├── transcripts/   # 会议记录
│   └── assets/        # 图片资源
├── entities/          # 实体页面
├── concepts/          # 概念页面
├── comparisons/       # 对比分析
└── queries/           # 有价值的查询结果
```

### Step 2: 创建 SCHEMA.md

在 wiki 根目录创建 `SCHEMA.md`，定义：

- **域名**：Wiki 覆盖的领域
- **文件命名规范**：小写字母、连字符
- **页面类型**：entity, concept, comparison, query
- **标签体系**：预定义标签列表
- **必需字段**：frontmatter 规范
- **创建阈值**：何时创建新页面

核心 frontmatter 字段：

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query
tags: [标签1, 标签2]
sources: [raw/xxx.md]  # 可选
---
```

### Step 3: 创建 index.md

内容目录，按类型分类：

```markdown
# Wiki Index

> 内容目录 — 累积式知识库

---

## 最新页面

| 页面 | 类型 | 更新时间 | 简介 |
|------|------|----------|------|
| xxx.md | concept | 2026-04-22 | 说明 |

## 按类型

### entities/

### concepts/

### comparisons/

### queries/

## 最近更新

---

## 使用说明

- 创建新页面后，请更新此索引
- 每个页面至少链接 2 个其他页面
- 定期检查孤立页面和失效链接
```

### Step 4: 创建 log.md

操作日志，记录所有行为：

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`

## [2026-04-22] create | Wiki initialized
- Domain: Hermes Agent Knowledge
- Structure created with SCHEMA.md, index.md, log.md
```

### Step 5: 创建 WIKI_GUIDE.md (可选)

面向用户的快速入门指南。

### Step 6: 配置环境变量

编辑 `~/.hermes/.env`，添加：

```bash
# LLM Wiki路径
WIKI_PATH=/Users/lvyun/.hermes/wiki
```

### Step 7: 创建符号链接 (可选)

当前 canonical 路径已经是 `~/.hermes/wiki`，不需要再创建符号链接。

如果未来选择把 wiki 放回项目仓库目录，再使用：

```bash
ln -sfn /path/to/canonical/wiki ~/.hermes/wiki
```

---

## 验证配置

```bash
# 检查目录结构
ls -la $WIKI_PATH

# 检查环境变量
echo $WIKI_PATH

# 检查必需文件
ls $WIKI_PATH/{SCHEMA.md,index.md,log.md}
```

---

## 相关文档

- [WIKI_GUIDE.md](./WIKI_GUIDE.md) — Wiki 使用指南
- [SCHEMA.md](./SCHEMA.md) — 规范定义

---

## 配置时间线

| 日期 | 操作 |
|------|------|
| 2026-04-22 | 初始化 Wiki，创建目录结构、SCHEMA.md、index.md、log.md |
| 2026-04-24 | 补充 WIKI_PATH 环境变量 |