# Hermes Wiki — 知识导航

> 累积式知识库。博客是工作记录，Wiki 是知识沉淀。

---

## 项目索引

> 所有博客按项目分组。项目确定后不新建，仅归档。

### ai-colleague（AI 智慧员工）

**方向**：用 AI agent 自动化办公室工作（OA登录/审批、填表、查数据、提交流程）

| 日期 | 博客 | 项目阶段 | 状态 |
|------|------|---------|------|
| 2026-05-02 | [[blog:20260502-ai-colleague-browser-harness-调研]] | research | ✅ 结论已出，后续演进 |

**核心结论**：browser-harness 方案可行，browser-auto 项目在此基础上演进。

### hermes（Hermes 系统优化）

| 日期 | 博客 | 项目阶段 | 状态 |
|------|------|---------|------|
| 2026-05-02 | [[blog:20260502-hermes-wikilinks-召回机制]] | memory-optimization | ✅ 已归档 |

**核心结论**：wikilinks 召回机制建立，blog frontmatter 规范落地。

---

## 博客总览

### 活跃博客（未归档）

| 日期 | 项目 | 主题 | 阶段 |
|------|------|------|------|
| 2026-05-02 | ai-colleague | browser-harness 调研 | research |

### 已归档博客

| 日期 | 项目 | 主题 |
|------|------|------|
| 2026-05-02 | hermes | wikilinks 召回机制 |

---

## Wiki 页面

### concepts/

| 页面 | 说明 | 标签 |
|------|------|------|
| [[concepts/hermes-mcp-startup-design-flaw]] | Hermes MCP 启动时全量加载的设计缺陷 | hermes, ai-agent |
| [[concepts/agent-framework-feature-bloat]] | Agent 框架的功能膨胀陷阱与精简内核哲学 | hermes, ai-agent, ai-colleague |
| [[concepts/hermes-soul-config]] | Hermes 灵魂配置统一方案 — persona.md + prefill + personality 清理 | hermes, configuration, persona |
| [[concepts/local-registry-msb-import]] | 本地 Docker Registry + msb 镜像灌入流程 — 自签名 TLS + 沙箱验证（playwright-chromium） | microsandbox, infra, nuc |
| [[concepts/microsandbox-deployment-architecture]] | NUC 沙箱部署三层架构 — Traefik + Squid + 端口转发 + create-sandbox.sh | microsandbox, deploy, traefik, proxy, network, nuc, infra |
| [[concepts/k3s-xsky-nfs-openwebui-deploy]] | K3s + XSKY NFS + Open WebUI 多副本部署 — PostgreSQL + Ollama GPU 推理 + 多副本 NFS | k3s, xsky, nfs, openwebui, ollama, gpu, deploy, infra |
| [[concepts/k3s-xsky-iscsi-csi]] | K3s + XSKY iSCSI CSI 配置 — CRD AccessPath + StorageClass + 踩坑记录 | k3s, xsky, iscsi, csi, storage, infra |

### entities/

| 页面 | 说明 | 标签 |
|------|------|------|
| [[entities/gitea-nuc]] | NUC 自托管 Gitea 对接指南 — SSH/REST API/Agent 操作 | infra, git, gitea, nuc |
| [[references/microsandbox-handbook]] | microsandbox v0.3.14 完整使用手册 — 核心概念/CLI/MCP/网络/代码传入/常见问题 | infra, sandbox, microsandbox, NUC, MCP |

### norms/

> 原则体系 — 所有 Agent 的行为规范汇总。详见 [[norms/_index]]。

| 页面 | 说明 | 状态 |
|------|------|------|
| [[norms/hermes/karpathy-four]] | Karpathy 效率四原则 — Hermes 核心行为准则 | ✅ 已固化 |
| [[norms/hermes/extensions]] | Hermes 从各方吸收的扩展原则 | 📋 待填充 |
| [[norms/pi]] | Pi 原则体系 | ◌ 观察中 |
| [[norms/opencode]] | OpenCode 原则观察 | ◌ 观察中 |
| [[norms/codex]] | Codex 实践模式观察 | ◌ 观察中 |
| [[norms/claude]] | Claude 官方创新观察 | ◌ 观察中 |

---

## 标签索引

| 标签 | 相关博客/页面数 |
|------|------|
| `ai-colleague` | 1 |
| `hermes` | 1 |
| `microsandbox` | 3 |
| `infra` | 3 |
| `nuc` | 3 |
| `ai-agent` | 2 |
| `deploy` | 1 |
| `traefik` | 1 |
| `proxy` | 1 |
| `network` | 1 |
| `memory` | 1 |
| `browser` | 1 |
| `wikilinks` | 1 |

---

## 定期迭代

- **月底**：检查活跃博客，标记 90 天无更新的为归档
- **写新博客**：确保 project + project_phase + status + blog_origin 字段完整
- **创建 Wiki 页面**：必须链接 ≥2 个已有页面

---

## Schema 版本

当前规范版本：v2（2026-05-05）
- v1：基础 Wiki 结构
- v2：增加博客命名规范、project frontmatter、归档机制
