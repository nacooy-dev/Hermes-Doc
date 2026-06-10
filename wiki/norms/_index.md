# 原则总览 — Principles Matrix

> 所有 Agent 行为原则的汇总矩阵。已固化的原则是运行规则，观察中的原则是待审核的候选。

最后更新: 2026-06-10

---

## 矩阵一览

### 已固化（运行规则）

| 原则 | 来源 | 适配 Agent | 状态 | 文件 |
|------|------|-----------|------|------|
| 编码前思考 (Think Before Coding) | Karpathy | Hermes | ✅ 已固化 | [[norms/hermes/karpathy-four]] |
| 简洁优先 (Simplicity First) | Karpathy | Hermes | ✅ 已固化 | [[norms/hermes/karpathy-four]] |
| 精准修改 (Surgical Changes) | Karpathy | Hermes | ✅ 已固化 | [[norms/hermes/karpathy-four]] |
| 目标驱动执行 (Goal-Driven Execution) | Karpathy | Hermes | ✅ 已固化 | [[norms/hermes/karpathy-four]] |

### 观察中（待审核）

| 原则/模式 | 来源 | 关注点 | 当前状态 | 文件 |
|----------|------|--------|---------|------|
| _待填充_ | OpenCode | | ◌ 观察中 | [[norms/opencode]] |
| _待填充_ | Codex | | ◌ 观察中 | [[norms/codex]] |
| _待填充_ | Claude | | ◌ 观察中 | [[norms/claude]] |

### 已吸收（从各方采纳的扩展）

| 原则 | 来源 | 说明 | 文件 |
|------|------|------|------|
| _待填充_ | | | [[norms/hermes/extensions]] |

---

## 快速导航

| Agent | 目录 | 说明 |
|-------|------|------|
| Hermes | [[norms/hermes]] | Karpathy 四原则 + 从各方吸收的扩展 |
| Pi | [[norms/pi]] | Pi 的原则体系（待填充） |
| OpenCode | [[norms/opencode]] | OpenCode 的原则观察（待填充） |
| Codex | [[norms/codex]] | Codex 的实践模式观察（待填充） |
| Claude | [[norms/claude]] | Claude 官方创新观察（待填充） |

---

## 原则生命周期

```
发现（来自各 Agent 官方文档/实践）
   ↓
观察中（记录到 norms/<agent>/，标记为 under-review）
   ↓
审核（大统领判断是否采纳）
   ↓
已吸收（写入 hermes/extensions.md，标记为 adopted）
   ↓
已否决（写入 hermes/extensions.md，标记为 rejected，记录原因）
```

## 状态说明

| 状态 | 含义 |
|------|------|
| ✅ 已固化 | System prompt 级别运行规则，Hermes 每次会话自动加载 |
| ✅ 已吸收 | 从外部来源采纳的扩展原则，写入 hermes/extensions.md |
| ◌ 观察中 | 正在跟踪，待审核后决定是否吸收 |
| ❌ 已否决 | 审核后决定不采纳，记录原因备查 |
