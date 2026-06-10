---
title: Hermes wikilinks 召回机制
created: 2026-05-02
project: hermes
project_phase: memory-optimization
status: completed
archived: true
blog_origin: 建立博客 frontmatter 规范，使 Hermes 能召回而不只是存储
sources:
  - 原始会话
  - karpathy-llm-wiki 模式
confidence: medium
summary: |
  恢复了 Hermes 完整行为规范到 config.yaml system_prompt，重启后生效（~246 tokens）。
  wikilinks 在 Hermes 中无原生支持，实现了一套基于 frontmatter summary 的博客召回机制：
  写博客时加 summary，召回时只读摘要不读全文。
  核心文件：~/.hermes/skills/wikilinks/scripts/wikilinks.py，支持 [[blog:slug]] 和 [[pagename]] 两种格式。
tags: [hermes, wikilinks, memory]
related_blogs:
  - 20260502-ai-colleague-browser-harness-调研.md
  - 20260505-hermes-agent-memory-philosophy.md
---

# Hermes wikilinks 召回机制

## 背景

Hermes 行为规范（Karpathy 四原则）一直写在文件里，但从未真正加载到 system prompt 中。同时 wikilinks 方案也只是纸面设计，没有工具支撑。

今天完成了这两件事。

## 一、行为规范恢复

**问题：** `~/.hermes/Hermes-behavior-guide.md` 文件存在，但 config.yaml 里的 system_prompt 只有简短版引用，实际不会加载。

**解决：** 把完整规范写入 config.yaml 的 `agent.system_prompt`（YAML literal scalar `|+` 格式）。

**效果：** ~246 tokens，重启后每个新会话生效。

**重启命令：**
```bash
kill <hermes_pid> && hermes gateway run --replace
```

## 二、wikilinks 现状评估

Hermes **没有内置** wikilinks 解析能力：
- `[[pagename]]` 只是普通文本
- 没有自动跳转、backlinks、孤立页面检测
- 完全依赖人工遵守规则

Wiki 从未被用起来的根本原因就是没有工具约束。

## 三、博客召回机制设计

针对"博客量大、召回时只想要关键内容"的场景，采用 **frontmatter summary** 方案。

### wikilinks 工具

`~/.hermes/skills/wikilinks/scripts/wikilinks.py`

```bash
# 召回对话中的 [[...]] 引用
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py "内容..."

# 列出所有博客
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --list
```

**两种引用格式：**
- `[[blog:slug]]` — 从 `~/.hermes/wiki/blogs/` 查找
- `[[pagename]]` — 从 `~/.hermes/wiki/` 查找

**召回逻辑：** 只读 frontmatter，不读正文。需要详情时再读全文。

## 四、文件清单

| 路径 | 用途 |
|---|---|
| `~/.hermes/config.yaml` | system_prompt 已更新为完整行为规范 |
| `~/.hermes/wiki/WIKI_GUIDE.md` | 加了博客 frontmatter 规范 |
| `~/.hermes/skills/wikilinks/SKILL.md` | wikilinks skill 说明 |
| `~/.hermes/skills/wikilinks/scripts/wikilinks.py` | 召回工具脚本 |
| `~/.hermes/wiki/blogs/` | 博客存放目录 |

## 使用流程

1. 写完博客 → 加 frontmatter summary
2. 之后提到这个话题 → 调用 wikilinks 工具 → 只召回 summary
3. 需要详情 → 再读正文
