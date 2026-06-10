---
title: browser-harness 集成调研
created: 2026-05-02
project: ai-colleague
project_phase: research
status: completed
archived: false
blog_origin: 验证 browser-harness 作为 AI-colleague 浏览器自动化方案的可行性
sources:
  - 原始会话
  - https://github.com/nicepkg/browser-harness
confidence: high
summary: |
  browser-harness 是 YAML workflow 驱动的浏览器自动化框架，不需要 LLM 判断每一步。
  核心组件：action runner + YAML 配置 + 视觉模型识别验证码。已集成到 Nanobot 作为 browser.py skill。
  部署方案：Chrome 在 K8s 外部（保登录态）+ Agent 在 Pod 内（无状态扩缩）。Linux Server 支持 Chrome headless。
  结论：方案可行，browser-auto 项目在此基础上演进。
tags: [ai-colleague, browser, ai-agent, nanobot]
related_blogs:
  - 20260502-hermes-wikilinks-召回机制.md
  - 20260505-hermes-agent-memory-philosophy.md
---

# browser-harness 集成调研

（正文略，内容量大，这里只是占位符）
