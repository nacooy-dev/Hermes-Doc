# Hermes Wiki Schema

> 规范：结构、约定、标签体系

---

## 域名

`Hermes Agent Knowledge` — Hermes助手知识库

## 文件命名规范

### 博客
```
{日期}-{项目}-{主题}.md
```
日期格式：`YYYYMMDD`
项目名：全小写、连字符（如 `ai-colleague`、`hermes`）

### Wiki 页面
- 文件名：小写字母、连字符
- 页面必须有 frontmatter (YAML)
- 用 `[[wikilinks]]` 链接其他页面

## 多 Agent 读写约定

> 本 Wiki 可能被多个 Agent 使用（Hermes、Pi、Codex、OpenCode 等）。
> 正式页面（`concepts/`、`entities/`、`comparisons/`、`queries/`）**仅由 Hermes 写入**，
> 其他 Agent **只读不写**。贡献内容请放入 `inbox/`。

### 读规则（所有 Agent 遵守）

- 路径：`~/TianCe-Lab/Hermes-Doc/wiki/`
- 角色：**只读消费者**
- 推荐在 System Prompt 中加入：
  ```
  Wiki 位于 ~/TianCe-Lab/Hermes-Doc/wiki/，只读不写。
  如需贡献，将内容以 .md 格式放入 inbox/ 目录。
  ```

### 写规则（仅 Hermes）

- 正式页面（`concepts/`、`entities/`、`comparisons/`、`queries/`）由 Hermes 创建/更新
- 索引（`index.md`）和日志（`log.md`）由 Hermes 维护
- 格式、frontmatter、wikilinks、标签体系按本 SCHEMA 执行

### 贡献规则（所有 Agent）

- 有价值的发现 → 写入 `inbox/` 目录
- 文件名格式：`{agent名}-{主题}.md`（如 `pi-transformer-attention.md`）
- 自由格式，不需要完整 frontmatter
- Hermes 定期审核 `inbox/`，消化后移入正式区并归档
- 归档后的 inbox 文件移至 `inbox/_archived/`

### git 审计

- 所有变更通过 git 追踪
- 任何 Agent 误写正式区 → `git diff` 可见，`git checkout .` 可回滚
- 建议其他 Agent 在 prompt 中声明 `wiki_path` 为只读引用

## 博客 vs Wiki

| | 博客 | Wiki |
|---|---|---|
| 位置 | `blogs/` 目录 | `entities/`, `concepts/` 等 |
| 目的 | 工作记录、调研、复盘 | 知识沉淀、结构化总结 |
| 触发 | 感觉有价值就写 | 知识被反复验证后沉淀 |

## 页面类型 (type)

| type | 含义 | 示例 |
|------|------|------|
| `entity` | 实体（人物、公司、产品） | `entities/user-d统领.md` |
| `concept` | 概念（主题、技术） | `concepts/karpathy-method.md` |
| `comparison` | 对比分析 | `comparisons/llm-vs-rag.md` |
| `query` | 有价值的查询结果 | `queries/esp32-selection.md` |

## 标签 Taxonomy

> 每个标签必须在这里定义后才能使用。新标签先加到这里再加到页面。

```yaml
# 主题标签
- ai-agent         # AI agent 相关（框架、设计模式、协作）
- memory          # 记忆系统、上下文管理
- wikilinks       # wiki 召回机制、链接
- browser         # 浏览器自动化

# 项目标签
- ai-colleague    # AI 智慧员工项目
- nanobot         # Nanobot 项目
- ip-research     # IP research 项目

# 系统标签
- hermes          # Hermes 系统配置、优化
- tooling         # 工具链、开发效率
- productivity    # 工作流优化

# 知识标签
- tech            # 技术方案、代码
- knowledge       # 知识总结、概念澄清
- comparison      # 对比分析
- research        # 调研过程、探索

# 质量标签
- draft           # 草稿，待完善
- archived        # 已归档
```

## Provenance 标注

> 标注来源，便于追溯

**博客**：在 frontmatter 的 `sources` 字段标注：
```yaml
sources:
  - 原始对话/sessions/xxx.md
  - 参考文章/https://example.com/article
```

**Wiki 页面**：当页面内容来自具体素材时，在相关段落后加：
```
^[raw/articles/source-file.md]
```

## 必需字段

### 博客
```yaml
---
title: 标题
created: YYYY-MM-DD
project: 项目名
project_phase: research|design|development|testing|optimization|completed
status: active|completed|paused
archived: false
blog_origin: 写这篇的原因
sources: [来源列表]
confidence: high|medium|low   # 结论可信度
summary: |
  3-5句话，涵盖背景、关键发现、结论
tags: [from taxonomy]
related_blogs: [slug1, slug2]  # 至少2个关联博客
---
```

### Wiki 页面
```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity|concept|comparison|query
tags: [from taxonomy]
confidence: high|medium|low
sources: [来源]
---
```

## 置信度说明

| 值 | 含义 |
|-----|------|
| `high` | 多方验证、反复测试、有数据支撑 |
| `medium` | 单次验证、逻辑推导、方向正确但细节待定 |
| `low` | 初步探索、可能需要修正 |

## 归档规则

- **90天无更新** → `archived: true`
- 归档不是删除，召回时搜得到
- 归档内容**不主动出现**在上下文，除非被问及

## 交叉引用要求

- Wiki 页面之间：至少 2 个 `[[wikilinks]]`
- 博客之间：通过 `related_blogs` 字段关联，至少 2 个
- 博客 → Wiki：通过 `related_blogs` 引用 Wiki 页面

## 创建阈值

- **创建博客**：感觉有价值，核心问题有阶段性答案
- **创建 Wiki 页面**：一个实体/概念在 2+ 博客中出现，或在核心博客中占主导
- **不创建**：仅一次提及、minor 细节
- 每个 Wiki 页面至少链接 2 个其他页面

## 目录结构

```
wiki/
├── SCHEMA.md           # 本文件
├── index.md            # 内容目录
├── log.md              # 操作日志
├── blogs/              # 博客目录
│   └── {日期}-{项目}-{主题}.md
├── inbox/              # 各 Agent 贡献入口（自由格式，Hermes 审核后消化）
│   └── _archived/      # 已消化的 inbox 归档
├── entities/           # 实体页面
├── concepts/           # 概念页面
├── comparisons/        # 对比分析
└── queries/           # 有价值的查询结果
```

## Lint 检查清单

定期检查：
1. 孤立页面（无 inbound wikilinks）
2. 失效链接（指向不存在的页面）
3. 标签不在 taxonomy 中
4. 90天未更新的 blog（触发归档检查）
5. `confidence: low` 的页面是否需要补充验证
6. 归档内容被频繁召回 → 解除归档或合并
7. 页面超过 200 行 → 考虑拆分

## 定期迭代

- **每月末**：运行 Lint 检查，更新归档状态
- **写新博客**：确保 project + project_phase + status + blog_origin + sources + related_blogs 完整
- **创建 Wiki 页面**：确保 wikilinks ≥2 个
