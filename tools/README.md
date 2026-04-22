# 开发工具配置指南

> Hermes-Doc 支持的 AI 开发工具配置说明

---

## 工具链概览

| 工具 | 版本 | 配置位置 | 状态 |
|------|------|----------|------|
| **Hermes Agent** | - | `~/.hermes/config.yaml` | ✅ 已配置 |
| **OpenCode CLI** | 1.3.7 | `~/.opencode/config.yaml` | ⚠️ 需配置 |
| **Claude CLI** | 2.1.85 | `~/.claude/` | ⚠️ 需配置 |
| **Qwen CLI** | 0.14.0 | `~/.qwen/settings.json` | ⚠️ 需配置 |

---

## 核心原则

所有工具共享同一套行为规范 — **Karpathy 效率四原则**：

1. **编码前思考** — 不假设，不猜测，主动澄清
2. **简洁优先** — 最少代码解决问题，拒绝过度设计
3. **精准修改** — 只改必要的，匹配现有风格
4. **目标驱动执行** — 明确成功标准，验证后再交付

---

## 各工具配置方法

### Hermes Agent（主力框架）

**配置文件：** `~/.hermes/config.yaml`

**当前状态：** 已配置

**关键设置：**
- 默认模型：`minimax-m2.5-free`
- Provider: `opencode-zen`
- Personality: `kawaii`（可改为 `concise` 或 `technical`）

**注入行为规范：** 见下方 "统一配置方案"

---

### OpenCode CLI（最常用）

**配置文件：** `~/.opencode/config.yaml`（需创建）

**配置步骤：**

```bash
# 创建配置目录
mkdir -p ~/.opencode

# 创建配置文件
cat > ~/.opencode/config.yaml << 'EOF'
# OpenCode CLI 配置
# 遵循 Karpathy 效率四原则

# 系统提示词（所有会话的默认行为准则）
system_prompt: |
  你是一个高效的 AI 编程助手，遵循 Karpathy 效率四原则：
  
  1. 编码前思考 — 不假设，不猜测，主动澄清
  2. 简洁优先 — 最少代码解决问题，拒绝过度设计
  3. 精准修改 — 只改必要的，匹配现有风格
  4. 目标驱动执行 — 明确成功标准，验证后再交付
  
  在开始编码前，如果需求不明确，必须先提问确认。
  实现时优先选择最简单的方案。
  修改现有代码时，只改动必要的部分。
  完成后提供验证步骤。

# 默认模型（可根据需要调整）
model: qwen/qwen3.5-397b-a17b

# 工具使用权限
tools:
  - terminal
  - file
  - search_files
  - read_file
  - write_file
  - patch

# 上下文窗口
context_window: 8192
EOF
```

**验证配置：**
```bash
opencode "写一个 Python 函数，计算两个数的和"
# 预期：AI 应该先确认需求，然后给出简洁实现
```

---

### Claude CLI

**配置文件：** `~/.claude/projects/global.json` 或项目级 `.claude.json`

**配置步骤：**

```bash
# 创建全局配置
cat > ~/.claude/projects/global.json << 'EOF'
{
  "systemPrompt": "你是一个高效的 AI 编程助手，遵循 Karpathy 效率四原则：\n\n1. 编码前思考 — 不假设，不猜测，主动澄清\n2. 简洁优先 — 最少代码解决问题\n3. 精准修改 — 只改必要的，匹配现有风格\n4. 目标驱动执行 — 明确成功标准，验证后再交付\n\n在开始编码前，如果需求不明确，必须先提问确认。",
  "tools": {
    "enabled": ["terminal", "file", "search", "read", "write", "patch"]
  }
}
EOF
```

**项目级配置：** 在项目根目录创建 `.claude.json`

---

### Qwen CLI

**配置文件：** `~/.qwen/settings.json`

**配置步骤：**

```bash
# 编辑现有配置
cat > ~/.qwen/settings.json << 'EOF'
{
  "systemPrompt": "你是一个高效的 AI 编程助手，遵循 Karpathy 效率四原则：1.编码前思考 2.简洁优先 3.精准修改 4.目标驱动执行。在开始编码前，如果需求不明确，必须先提问确认。",
  "model": "qwen-max",
  "temperature": 0.7
}
EOF
```

---

## 统一配置方案（推荐）

为确保所有工具行为一致，建议采用以下方案：

### 方案 A：使用 Hermes-Doc 作为中心

1. 将 `Hermes-behavior-guide.md` 作为所有工具的 system prompt 来源
2. 各工具配置中引用该文件路径

### 方案 B：创建统一的 system prompt 文件

```bash
# 创建全局 system prompt
cat > ~/.ai-system-prompt.md << 'EOF'
# AI 助手行为规范

你是高效的 AI 编程助手，遵循 Karpathy 效率四原则：

1. **编码前思考** — 不假设，不猜测，主动澄清
2. **简洁优先** — 最少代码解决问题，拒绝过度设计
3. **精准修改** — 只改必要的，匹配现有风格
4. **目标驱动执行** — 明确成功标准，验证后再交付

详细规范：/Users/lvyun/TianCe-Lab/Hermes-Doc/Hermes-behavior-guide.md
EOF
```

然后在各工具配置中引用此文件。

---

## 验证配置

### 测试 1：简单任务
```bash
# 所有工具都应该表现一致
opencode "写一个 Python 函数，计算两个数的和"
claude "写一个 Python 函数，计算两个数的和"
qwen "写一个 Python 函数，计算两个数的和"
```

**预期行为：**
- AI 先确认需求（需要异常处理吗？有类型要求吗？）
- 给出简洁实现（不超过 10 行）
- 提供验证方法

### 测试 2：复杂任务
```bash
opencode "帮我重构这个文件，提高性能"
```

**预期行为：**
- AI 应该先询问性能瓶颈在哪里
- 要求提供基准测试或性能数据
- 不盲目重构

---

## 常用工作流

### 日常开发（OpenCode）
```bash
# 启动交互式会话
opencode

# 或直接执行任务
opencode "实现用户登录功能，使用 bcrypt 加密密码"
```

### 代码审查（Claude CLI）
```bash
claude "审查这个 PR 的代码，关注：
1. 是否有不必要的复杂度
2. 是否有未处理的边界情况
3. 是否符合简洁优先原则"
```

### 调试问题（Qwen CLI）
```bash
qwen "这个测试失败了，帮我分析原因并修复"
```

---

## 故障排除

### AI 过度发挥
**问题：** AI 添加了不需要的功能

**解决：** 在 system prompt 中强调：
```
严格遵循：不添加需求之外的功能，不为一次性代码创建抽象
```

### AI 不提问直接编码
**问题：** AI 直接开始写代码，没有确认需求

**解决：** 在 system prompt 中强调：
```
如果需求有任何不明确，必须先提问，不能猜测
```

---

## 参考文档

- [Hermes-behavior-guide.md](../Hermes-behavior-guide.md) — 完整行为规范
- [EXAMPLES.md](../EXAMPLES.md) — 使用示例
- [Hermes-LLM-Wiki.md](../Hermes-LLM-Wiki.md) — 知识库使用指南
