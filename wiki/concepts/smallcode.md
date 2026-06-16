---
title: SmallCode — AI编写Agent for Small LLMs
created: 2026-06-16
updated: 2026-06-16
type: concept
tags: [tech, project, comparison]
confidence: high
sources: [https://github.com/Doorman11991/smallcode/]
---

# SmallCode — AI编写Agent for Small LLMs

[[smallcode]] 是一个专为 8B-35B **小参数模型**设计的 AI 编程助手，核心思路是通过**工程手段填补模型能力差距**，而非依赖模型自身的智能提升。宣称在 Gemma 4 E4B（~4B active）上达到 87% 单文件任务成功率。

> GitHub: [Doorman11991/smallcode](https://github.com/Doorman11991/smallcode) | 1.9k Stars | MIT | v1.6.0

---

## 核心假设

与 [[hermes-agent]] 和 OpenCode 不同，SmallCode 的设计前提是：

- 模型只有 **8-32k context**，不是 128k+
- 模型的 JSON 输出经常**格式不对**
- 模型第 3 步就**忘记**第 1 步做了什么
- 写大文件会被 **llama.cpp 的 JSON parser 截断**（~13KB 限制）

每个架构决策都从这类约束出发。

---

## 8 大针对小模型的优化

### 1. 二级工具路由（Two-Stage Tool Routing）

| 模式 | 上下文 <16k | 上下文 ≥16k |
|------|------------|-------------|
| direct | — | 一次发全部工具（~2000 tokens） |
| two_stage | 先发 category selector（~200 tokens），模型选 read/write/search/run，再发该类的工具 schema | 可选 |

`respond` 分类完全不注入工具 schema，节省约 800 tokens。

***确定性的** regex 分类器做第一轮，不是 LLM 调用。

### 2. 上下文预算引擎（Context Budget Engine）

- 默认用检测到的 context window 的 **70%**
- 超 80% 阈值时自动压缩：优先语义摘要，失败则丢弃最早非 system 消息
- 保留最近 **6 条**消息完整，旧消息压缩为一条 system 摘要

### 3. Forgiving 工具调用解析器

解析 5 种格式的 tool call：

| 格式 | 示例 |
|------|------|
| `<tool_call>{...}</tool_call>` | Hermes / Qwen2.5 原生 |
| `<|tool_call_start|>[func(kw=val)]` | Liquid AI lfm2.x |
| ` ```json ... ``` ` | Qwen-coder / 通用 |
| ` ```tool_call ... ``` ` | 某些 Llama3 微调版 |
| 裸 JSON（内容首位） | 兜底 |

还从 `reasoning_content` 里提取 tool call（有些模型把工具调用放进思维链而不是 content 字段）。

### 4. Patch-first 编辑

- 主要编辑原语是 **search-and-replace patch**，不是全文件重写
- write_file 有 **8KB / 60 行**上限——超限则拒绝并要求 skeleton+patch 策略
- 因为小模型重写整个文件时会：截断、幻觉导入、缩进漂移

### 5. Improvement Loop（自动验证链）

每次编辑后自动验证：`python3 -m py_compile` / `node --check` / `tsc --noEmit` / `go build`

```
写文件 → 验证通过 → ✅ 继续
写文件 → 验证失败 → 🔄 重试（最多 2 次，带完整历史）
        ↓ 仍失败
分解策略 → 拆文件/逐错修复/重写段
        ↓ 仍失败
Escalation → 云端模型收尾（opt-in）
```

### 6. Decompose 策略（分解）

2 次重试失败后，分析错误类型选择策略：

| 条件 | 策略 |
|------|------|
| 文件 >80 行 | split_file — 拆成小文件 |
| 多个不相关错误 | one_error_at_a_time — 一次只修一个 |
| 同错误持续失败 | rewrite_section — 换方案重写 |
| 上述都不行 | 调用 LLM 做 decomposeTask |

### 7. Escalation（云模型后备）

- 本地模型所有尝试失败后 → 自动 fallback 到云端模型
- 支持 **Anthropic**（默认首选）、**OpenAI**、**DeepSeek**
- 自带格式转换：OpenAI ↔ Anthropic messages API
- 每次 escalation 带上下文："本地小模型试了不行，帮你收尾"
- 默认每会话 **5 次上限**，完全 opt-in（需配置 API Key）

### 8. Model Profiles

内置模型能力描述表，按名称模糊匹配：

| 模型 | context | tool_format | 弱点 |
|------|---------|-------------|------|
| gemma-4 | 32k | native | very_long_planning |
| qwen3 | 32k | hermes | verbosity |
| qwen2.5-coder | 32k | hermes | multi_file |
| deepseek-coder | 16k | json | tool_use_reliability |
| codellama | 16k | text（不支持 tool） | 基本不会用工具 |

profile 的 `weaknesses` 驱动 routing 和 budget 决策。

---

## 其他值得注意的点

### Compound Tools

把 3-4 步工具调用合并成 1 步的组合工具：

| 工具 | 等价于 |
|------|--------|
| `read_and_patch` | read_file + patch |
| `create_and_run` | write_file + bash |
| `find_and_read` | find_files + read_file |
| `search_and_read` | search + read_file |

### Plan Tracker

多步骤任务强制模型输出编号计划，之后每轮加上进度锚点重新注入：

```
ACTIVE PLAN (step 3 of 5):
✓ 1. Read the existing auth module
✓ 2. Identify the JWT validation function
→ 3. Add the refresh token handler
  4. Update the route middleware
  5. Run tests
```

### Read-before-write Guard

模型没读过文件就写？第一次拒绝 + 提示，第二次才放行。防止小模型凭猜测直接覆盖。

### 大文件摘要

>200 行的文件自动用 LLM 生成摘要替换全文返回。

### Knowledge Injection

`knowledge/` 目录放短参考笔记（算法速查表、语法备忘），按关键词匹配注入 system prompt，上限 1500 tokens。

### Bayesian Tool Scorer

记录每个工具在各任务类型上的成功/失败率，confidence < 0.35 自动避让。

### RTK（Rust Token Killer）集成

如果装了 `rtk` 二进制，自动重写 bash/git/test 命令来减少输出 token（60-90% 压缩）。

### Token Monitor

追踪每次调用的 prompt/completion 比例，输出 efficiency 指标。

---

## 与 Hermes 对比

| 维度 | SmallCode | [[hermes-agent]] |
|------|-----------|-----------------|
| 目标模型 | **8B-35B 小模型** | 任意模型（无偏见） |
| 架构 | 单 npm 包，Node.js | Python + Go Gateway |
| Tool 路由 | 2 级动态路由 | 一次性全部注入 |
| JSON 容错 | 5 种格式解析 + 自动修复 | 依赖模型本身 |
| 验证链 | Built-in: 编译→重试→分解→escalation | 无强制验证 |
| 上下文管理 | 自动压缩/摘要/丢弃 | 手工管理 |
| 系统面积 | ~8.6k 行 JS（bin/） | 更大（Hermes + Gateway） |

---

## 4B 模型能跑出 87% 的本质原因

不是魔法——SmallCode **替模型做了它做不到的事**：

1. 小模型写不完整文件？→ 用 patch，只改几行
2. 小模型 JSON 写不对？→ 解析器兜底
3. 小模型 3 步后忘记目标？→ 每轮注入 plan 锚点
4. 小模型写坏文件？→ 自动编译检查 + 重试
5. 小模型真搞不定？→ escalation 到云端

**代价是多了 1-2 轮 round-trip**（category selector + 重试），但对于本地跑的小模型来说值得——模型慢几秒，换回正确执行。

---

## 部署

```bash
npm install -g smallcode
# 或直接用 npx
npx smallcode

# 预编译二进制（无需 Node.js）
bash <(curl -fsSL https://raw.githubusercontent.com/Doorman11991/smallcode/master/install.sh)
```

要求：Node.js 18+、Python 3 + Git

配置支持 `.env` 和 `smallcode.toml`，支持模型分级：

```env
SMALLCODE_MODEL=qwen2.5-coder:14b
SMALLCODE_BASE_URL=http://localhost:11434/v1
SMALLCODE_MODEL_STRONG=deepseek-v4-flash
SMALLCODE_BASE_URL_STRONG=https://api.deepseek.com/v1
```

支持的 Provider：Ollama、LM Studio、llama.cpp、OpenAI-compatible、Anthropic

---

## 参看

- [[hermes-agent]] — 大统领的主力 AI 助手
- [[WIKI_GUIDE]] — Wiki 使用指南
- [GitHub: Doorman11991/smallcode](https://github.com/Doorman11991/smallcode)