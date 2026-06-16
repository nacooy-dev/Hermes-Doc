# NUC 基础设施搭建：Gitea + Microsandbox + MCP 全栈集成

> 日期：2026-05-18
> 作者：大统领

## 背景

NUC (192.168.3.20, Ubuntu 24.04, Docker 28) 作为家里的小型服务器，跑了两个核心服务：

```
NUC ─┬─ Gitea (Docker, :3080 Web / :3022 SSH)
     └─ Microsandbox (KVM microVM, msb v0.3.14)
```

目标是通过 Hermes Agent 让两台 Mac 都能无缝使用 NUC 的设施——代码托管 + 隔离沙箱执行。

## 架构总览

```
Mac mini ──┬── Hermes MCP (StreamableHTTP) ──▶ NUC:8912 ──▶ msb CLI ──▶ KVM Sandbox
           └── Gitea API (:3080) + SSH (:3022) ◀── Gitea Container
```

Hermes 端不需要额外安装任何东西，MCP 工具是原生集成的。

## 一、Gitea 代码托管

### 部署

Gitea 以 Docker 容器运行，轻量、维护成本极低：

```bash
# 容器名 nuc-gitea，已运行 7+ 小时稳定
# 端口映射:
#   3080 → 3000 (Web UI)
#   3022 → 2222 (SSH)
```

### Hermes 对接

通过 REST API 操作仓库、Issues、PR，完全兼容 Hermes 现有的 `github-*` 技能体系。

```bash
export GITEA_HOST=192.168.3.20:3080
export GITEA_TOKEN=e9c8688d1f5cdcf60182459bc30eece5dca7a2
export GITEA_SSH_PORT=3022
```

已封装为 Hermes Skill `devops/gitea-workflow skill，含 AGENTS.md 模板供 OpenCode 使用。

### 对 OpenCode 的支持

每个 Gitea 仓库根目录放 AGENTS.md，OpenCode 自动识别为 Gitea 仓库连接信息。

## 二、Microsandbox 沙箱执行

### 部署

Microsandbox 是 KVM 微 VM 方案，秒级启动的沙箱工具，已缓存 ubuntu 和 python 镜像。

有两个对接方案：

#### 方案 A：SSH 远程执行（快速验证）

直接通过 SSH 调 msb CLI：

```bash
ssh nacoo@192.168.3.20 "msb run ubuntu --timeout 30s -- echo hello"
```

已封装为 `devops/microsandbox-nuc` skill。

#### 方案 B：MCP Server（原生工具，推荐）

Microsandbox 通过 MCP Server 变成 Hermes 的原生工具——新打开的 Hermes 会话自动拥有 6 个沙箱工具。

##### MCP Server 技术细节

- **协议**：StreamableHTTP（单端口 POST JSON-RPC）
- **地址**：`http://192.168.3.20:8912`
- **部署**：Docker 容器 (msb-mcp 镜像)，`--restart=always`
- **实现**：纯 Python stdlib（asyncio + json + subprocess），零外部依赖
- **代码**：`/home/nacoo/msb-mcp/msb_mcp_server.py`（~300 行）

##### 容器挂载要点

```yaml
msb 二进制:  /usr/local/bin/msb → /usr/local/bin/msb (ro)
libkrunfw:   .microsandbox/lib  → /usr/local/lib      (匹配 RUNPATH)
沙箱缓存:    .microsandbox/cache → /root/.microsandbox/cache
沙箱状态:    .microsandbox/db   → /root/.microsandbox/db
KVM 设备:    /dev/kvm
```

##### “无 Docker → 容器化”的曲折

最初检查 NUC 环境时漏掉了 `docker --version`，只看了 `pip3` 就说 NUC 无 Docker，写了个纯 Python 的 nohup 方案。大统领一句话点醒——Gitea 就是 Docker 跑着的。改容器化部署后，自动恢复能力（`--restart=always`）比 nohup 靠谱得多。

教训：检查环境别只看自己想看的，跑一遍 `docker --version` 不费事。

##### 6 个原生 MCP 工具

| 工具 | 功能 | 典型参数 |
|------|------|---------|
| `msb_run` | 创建 + 执行 + 销毁（一次性） | image, command, timeout |
| `msb_create` | 创建持久沙箱 | image, name |
| `msb_exec` | 在已有沙箱中执行命令 | sandbox_id, command |
| `msb_rm` | 停止并删除沙箱 | sandbox_id |
| `msb_list` | 列出运行中的沙箱 | （无参数） |
| `msb_pull` | 拉取容器镜像 | image |

##### 从 Mac 端调用效果

```
🔨 Create sandbox...  → 成功
⚡ Exec echo...        → Hello from Mac via MCP!
                        root
                        Mon May 18 10:59:17 UTC 2026
🗑️ Remove sandbox...  → 自动 stop + rm，清理干净
```

## 三、关键发现和陷阱

### msb 二进制是动态链接的

```bash
$ ldd /home/nacoo/.microsandbox/bin/msb
→ libdbus-1.so.3, libsystemd.so.0, libcap.so.2, libgcrypt20...
$ readelf -d msb | grep RUNPATH
→ RUNPATH: $ORIGIN/../lib:$ORIGIN
```

容器化时需要：
1. 安装这些系统库（`libdbus-1-3 libsystemd0 libcap2 libgcrypt20` 等）
2. 将 `.microsandbox/lib/` 挂载到 `/usr/local/lib/`（匹配 RUNPATH）

### msb rm -f 不能删除运行中的沙箱

`msb rm -f` 的文档说 "Stop the sandbox if running, then remove it"，但实测会报 `error: sandbox still running`。需要在 MCP Server 中先调用 `msb stop` 再 `msb rm`。

### Docker 镜像构建耗时

Ubuntu 24.04 的 apt-get update 下载 38MB 元数据需要 3-4 分钟，加上安装包的 8MB 下载，总共 5-6 分钟。耐心等待。

## 四、第二台 MacBook 对接指南

详见同目录下的 `nuc-onboarding-macbook.md`。

## 五、后续方向

- [ ] MCP Server 代码加 watchdog 健康检测
- [ ] 在 Gitea 上建立 CI/CD 流水线
- [ ] 沙箱内挂载宿主目录实现持久化存储
- [ ] 用 Hermes cron 定时清理过期沙箱