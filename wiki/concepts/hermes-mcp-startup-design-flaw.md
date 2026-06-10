---
title: Hermes MCP 启动时全量加载的设计缺陷
created: 2026-05-18
updated: 2026-05-18
type: concept
tags:
  - hermes
  - ai-agent
confidence: high
sources:
  - 实测日志分析 errors.log
  - 代码分析 tui_gateway/entry.py, tools/mcp_tool.py
---

# Hermes MCP 启动时全量加载的设计缺陷

## 问题描述

Hermes TUI 在启动时会同步阻塞，等待所有配置的 `mcp_servers` 全部连接成功后才显示界面。如果任何一个 MCP 服务器不可达，启动会卡住数分钟。

## 根因

### 代码路径

`tui_gateway/entry.py:212-215`：

```python
# 检测到 mcp_servers 有配置
from tools.mcp_tool import discover_mcp_tools
discover_mcp_tools()  # ← 同步阻塞！
```

### 调用链

```
entry.py → discover_mcp_tools()
  → register_mcp_servers()
    → asyncio.gather(并行连接所有 enabled 的 MCP 服务器)
      → 每个服务器 3 次重试 × connect_timeout(60s) = ~3 分钟
  → 所有连接完成后才发 gateway.ready 信号
```

### 核心问题

1. **启动阻塞**：`discover_mcp_tools()` 是同步调用，在发 `gateway.ready` 之前等待所有 MCP 连接完成。一个不可达的 MCP 服务器就能让 Hermes 卡 3 分钟。
2. **重试策略不适合启动**：启动阶段应该快速失败（连一次不行就跳过），而非重试 3 次。重试策略更适合运行时掉线恢复。
3. **全量预连 vs 按需连接**：设计上为了"第一次调 MCP tool 时零延迟"，选了启动时全量预连所有 MCP 服务器。这在 VS Code 等 IDE 中早已被放弃——现代编辑器都是懒加载插件。

## 触发条件

- 配置了 `mcp_servers`（任何服务器）
- 其中有服务器不可达（端口未开、IP 不通、服务挂掉）

## 修复方向（未实施）

- MCP 连接改为后台异步进行，不阻塞 `gateway.ready`
- 启动时只连一次，失败不重试，重试留给 `/reload-mcp` 命令或运行时掉线恢复
- 或改为按需连接：第一次调用具体 MCP tool 时才建立连接

## 相关链接

- [[concepts/hermes-mcp-config-guide]]
- [[blog:20260502-hermes-wikilinks-召回机制]]

## 备注

这个设计缺陷在对 Hermes 做 MCP/skill 沙箱化时需要重点考虑——沙箱的目的是安全隔离，如果启动时全量拉起沙箱，启动时间会进一步恶化。