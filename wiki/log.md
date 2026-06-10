# Wiki Changelog

## 2026-06-10

### 结构优化
- **inbox/** 新增多 Agent 贡献入口目录，下设 `_archived/` 归档子目录
- **SCHEMA.md** 新增"多 Agent 读写约定"章节，明确：其他 Agent 只读不写正式区，贡献内容放入 `inbox/`
- **SCHEMA.md** 目录结构更新，加入 `inbox/` 和 `inbox/_archived/`
- **norms/** 新增原则体系目录，下设 hermes/pi/opencode/codex/claude 子目录
- **index.md** 新增 norms/ 导航表格

### 新增
- **norms/_index.md**: 原则总览矩阵 — 已固化/观察中/已吸收/已否决四类状态
- **norms/hermes/karpathy-four.md**: Karpathy 四原则正式文档（含执行标准 + 违反记录）
- **norms/hermes/extensions.md**: Hermes 扩展原则骨架（待填充）
- **norms/pi/_index.md**, **norms/opencode/_index.md**, **norms/codex/_index.md**, **norms/claude/_index.md**: 各 Agent 原则观察骨架

---

## 2026-05-30

### 新增
- **concepts/microsandbox-deployment-architecture**: NUC 沙箱三层架构详细记录（Traefik + Squid + 端口转发）

### 修正
- **references/microsandbox-handbook**:
  - MCP 部分：从模糊的"参数可能比 CLI 少"改为明确列出不支持的功能（--network-policy, -p, -v, --env）
  - 网络策略：补充端口映射绑 127.0.0.1 的关键限制 + 转发器/Traefik 解决方案
  - 新增出站公网（Squid）说明
  - 新增常见问题：MCP 不支持网络、镜像 entrypoint 占端口
- **entities/microsandbox-plan**: MCP 状态从"已落地"改为"有限功能"，注明不支持高级参数，需 SSH 补位

### 杂项
- index.md 标签索引新增 deploy/traefik/proxy/network
- index.md 添加新页面链接

|---

## 2026-06-09

### 新增
- **concepts/k3s-xsky-iscsi-csi**: K3s + XSKY iSCSI CSI 配置全流程（CRD AccessPath multi_gateway、StorageClass 参数、踩坑记录、清理流程）

### 杂项
- index.md 标签索引新增 iscsi/csi/storage

## 2026-06-08

### 新增
- **concepts/k3s-xsky-nfs-openwebui-deploy**: K3s + XSKY NFS + Open WebUI 多副本部署知识记录（NFS CSI 参数、PostgreSQL 部署、Open WebUI 启动脚本/OLLAMA_BASE_URL/GPU Ollama/踩坑表）
- **concepts/k3s-xsky-nfs-openwebui-deploy**: 补充 API 代理服务章节（Open WebUI Proxy 架构/部署/API 端点/bot 用户/知识库集成）

### 杂项
- index.md 标签索引新增 k3s/xsky/nfs/openwebui/ollama/gpu

## 2026-05-05

### 新增
- **concepts/hermes-mcp-startup-design-flaw**: Hermes MCP 启动时全量加载所有工具，token 浪费
- **concepts/agent-framework-feature-bloat**: Agent 框架膨胀问题分析
- **concepts/hermes-soul-config**: Hermes 灵魂配置统一方案
- **concepts/local-registry-msb-import**: 本地 Docker Registry + msb 镜像灌入流程
- **entities/gitea-nuc**: NUC 自托管 Gitea 对接指南
- **references/microsandbox-handbook**: microsandbox v0.3.14 完整使用手册

### 结构优化
- 首页重构：博客按项目分组（ai-colleague/hermes），wiki 按类型分类（concepts/entities/references）
- 标签系统：每个 wiki 页面带 frontmatter tags，标签索引汇总
