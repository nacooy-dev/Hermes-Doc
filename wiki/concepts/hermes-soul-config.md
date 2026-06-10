---
title: Hermes 灵魂配置统一方案
created: 2026-05-19
updated: 2026-05-19
type: concept
tags: [hermes, configuration, persona, wiki]
sources: []
---

# Hermes 灵魂配置统一方案

> 核心结论：四原则常驻 system_prompt；SOUL.md 只放简短身份；LLM Wiki 不整库进上下文，按需 Orient。

## 背景

Mac mini 一开始没有按四原则和 Wiki 方式工作。排查后发现：
1. `agent.system_prompt` 为空，四原则没有常驻。
2. `SOUL.md` 曾被误当成承载所有行为规则的地方，导致上下文膨胀风险。
3. `display.personality` 设成 `kawaii`，这是装饰字段，且会误导排查。
4. `prefill_messages_file` 注入整份行为规范会和 system_prompt 重复，不利于控制上下文大小。

## 最终三层架构

| 层级 | 文件/位置 | 作用 | 上下文策略 |
|------|-----------|------|------------|
| 1 | `config.yaml -> agent.system_prompt` | 常驻行为准则：Karpathy 四原则 | 常驻，但压缩到约 800-1000 chars |
| 2 | `~/.hermes/SOUL.md` | 简短身份声明：我是克鲁克，大统领的贴身助手 | 常驻，保持很短 |
| 3 | skills + `~/.hermes/wiki/` | 具体工作法和长期知识 | 按需加载，不整库常驻 |

## 为什么这样设计

四原则不是“某件事怎么做”，而是“所有事怎么做”，所以必须常驻 `agent.system_prompt`。

LLM Wiki 是长期知识库，不应该整库塞进系统提示。正确方式是：当任务涉及长期知识、沉淀、查询或写入时，加载相关 skill，然后执行 Orient：
1. 读 `~/.hermes/wiki/SCHEMA.md`
2. 读 `~/.hermes/wiki/index.md`
3. 读 `~/.hermes/wiki/log.md` 最近记录
4. 再按需读取具体页面

## config.yaml 关键配置

```yaml
agent:
  system_prompt: |
    # Hermes Agent 行为规范
    ...Karpathy 效率四原则精简版...

display:
  personality: ''

# 避免与 system_prompt 重复注入
prefill_messages_file: ''

updates:
  pre_update_backup: true
  backup_keep: 10
```

## SOUL.md 推荐内容

```markdown
# Hermes Agent Persona

我是克鲁克，大统领给我取的名字。我是大统领的贴身 AI 编程助手。

行为准则遵循 `config.yaml -> agent.system_prompt` 中定义的 Karpathy 效率四原则。
长期知识遵循 LLM Wiki 方式：不整库常驻上下文，需要时按技能执行 Orient 后再读取。
```

## shared-skills 恢复工具

MacBook 已上传到 `lvyun/shared-skills`：

```bash
cd ~/shared-skills && git pull
bash scripts/deploy.sh
bash ~/shared-skills/scripts/check-persona.sh
```

如果 `system_prompt` 丢失：

```bash
hermes -s persona-recovery chat -q '检查并修复我的四原则 system_prompt'
```

## 验证结果（Mac mini）

`bash ~/shared-skills/scripts/check-persona.sh` 输出：

```text
system_prompt: 833 chars
包含四原则: ✅
SOUL.md 存在: ✅
```

## 关联

- [[gitea-nuc]] — Wiki 同步的 Gitea 仓库
- `~/shared-skills` — 跨机器同步的技能仓库
- `persona-recovery` — 升级或重装后恢复三层人格架构
