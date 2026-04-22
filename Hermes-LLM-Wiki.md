# Hermes Agent LLM Wiki 知识库

> 基于 Karpathy 理念的持久化知识管理系统

---

## 核心理念

LLM Wiki 是一个**累积式知识库**——知识只编译一次，后续查询直接查。不像传统 RAG 每次都从头检索，Wiki 的内容已经过整理、交叉引用、矛盾标记。

**你（Agent）负责**：总结、交叉引用、写入、维护一致性。  
**人类负责**：提供素材、指出方向。

---

## 目录结构

```
wiki/
├── SCHEMA.md           # 规范：结构、约定、标签体系
├── index.md            # 内容目录：一句话概要
├── log.md              # 操作日志：按时间记录所有行为
├── raw/                # 原始素材（不可修改）
│   ├── articles/       # 网页文章
│   └── papers/         # 论文
├── entities/           # 实体页面（人物、公司、产品）
├── concepts/           # 概念页面（主题、技术）
├── comparisons/        # 对比分析
└── queries/           # 有价值的查询结果
```

---

## 关键规则

### 每次操作前必读（Orient）

**每次会话开始，必须先读取这三个文件：**

1. **SCHEMA.md** — 了解规范、标签体系、结构要求
2. **index.md** — 了解已有哪些页面
3. **log.md** — 了解最近做过什么

```python
# 伪代码
read_file("wiki/SCHEMA.md")
read_file("wiki/index.md")
read_file("wiki/log.md", offset=-30)  # 最近30条
```

**跳过 orient 会导致**：重复创建页面、错过交叉引用、违背规范。

### 页面格式（Frontmatter）

每个 wiki 页面开头必须有 YAML 头：

```yaml
---
title: 页面标题
created: 2026-04-22
updated: 2026-04-22
type: entity | concept | comparison | query
tags: [标签1, 标签2]
sources: [raw/articles/源文件.md]
---
```

### 交叉引用

用 `[[wikilinks]]` 链接其他页面。每个页面至少链接 2 个其他页面。

### 页面阈值

- **创建页面**：一个实体/概念在 2+ 个素材中出现，或在一个核心素材中占主导
- **不创建**：仅一次提及、 minor 细节

---

## 对接 Memory

LLM Wiki 可以作为 Hermes 的长期记忆系统使用。

### 工作方式

1. **写入记忆** → 作为新 entity 或 concept 写入 wiki
2. **读取记忆** → 先查 index.md，再用 `search_files` 精确搜索
3. **查询记忆** → 从 wiki 中合成答案，标明来源

### Memory 工具 vs Wiki

| | Memory 工具 | Wiki |
|---|---|---|
| 格式 | 扁平笔记 | 互联页面 + frontmatter |
| 查找 | 关键词检索 | 索引 + 搜索 + 交叉引用 |
| 一致性 | 不检查 | lint 检查重复/矛盾 |
| 累积 | 线性增长 | 有结构、可视化 |

### 使用场景

- **用户偏好** → 写入 `entities/user-[name].md`，包含标签、偏好、习惯
- **环境信息** → 写入 `entities/macos-setup.md`，记录 Python 版本、路径
- **项目规范** → 写入 `concepts/hermes-conventions.md`
- **API 知识** → 写入 `entities/openai-api.md`，包含端点、使用方式
- **代码片段** → 写入 `concepts/python-patterns.md`

---

## 核心操作

### 1. Ingest（写入素材）

```
1. 保存原始素材到 raw/
2. 提取实体/概念
3. 创建或更新 wiki 页面
4. 添加交叉引用（至少2个）
5. 更新 index.md
6. 追加 log.md
```

### 2. Query（查询）

```
1. 读取 index.md 定位相关页面
2. search_files 精确搜索（可选）
3. 读取相关页面
4. 合成答案，标明来源
5. 有价值的答案写入 queries/ 保留
```

### 3. Lint（检查一致性）

```
- 孤立页面（无 inbound 链接）
- 失效链接（指向不存在的页面）
- 矛盾内容（同一主题不同说法）
- 过期内容（90天未更新）
- 标签合规性
```

---

## 使用建议

### 首次设置

```bash
mkdir -p ~/wiki/{raw/articles,entities,concepts,comparisons,queries}
```

然后创建 SCHEMA.md、index.md、log.md（参考 skill 中的模板）。

### 每次新会话

```
1. 先 orient：读 SCHEMA + index + recent log
2. 对于需要记忆的场景，写入 wiki
3. 交付时说明写入位置
```

### 查询时

```
1. 先 orient（如果会话刚开始没有）
2. 从 wiki 查
3. 需要补充再问用户
```

---

## 与现有 Memory 工具的关系

- **Memory 工具**：适合临时、快速存取（如本次会话的TODO）
- **Wiki**：适合长期、累积、有结构的信息

**建议**：两者配合使用。临时信息用 memory，长期知识用 wiki。

---

## 配置（可选）

```bash
# 在 ~/.hermes/.env 中设置
WIKI_PATH=~/wiki
```

如果不设置，默认是 `~/wiki`。

---

## 快速开始

```bash
# 1. 创建目录结构
mkdir -p ~/wiki/{raw/articles,raw/papers,entities,concepts,comparisons,queries}

# 2. 创建 SCHEMA.md（简化版）
echo '# Wiki Schema\n\nDomain: Hermes Agent Knowledge\nConventions:\n- 文件名: 小写字母、连字符\n- 页面必须有 frontmatter\n- 用 [[wikilinks]] 链接\n' > ~/wiki/SCHEMA.md

# 3. 创建 index.md
echo '# Wiki Index\n\n> Content catalog\n' > ~/wiki/index.md

# 4. 创建 log.md
echo '# Wiki Log\n\n## [2026-04-22] create | Wiki initialized\n' > ~/wiki/log.md
```

然后就可以开始用了。