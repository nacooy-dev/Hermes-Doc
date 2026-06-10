# microsandbox 使用手册

> 来源：官方文档 (docs.microsandbox.dev) + CLI --help + MCP Server README
> 版本：v0.3.14（NUC 当前安装版本）
> 官方 GitHub：superradcompany/microsandbox（6.2k stars）
> 官方 MCP：superradcompany/microsandbox-mcp

---

## 一、核心概念

microsandbox 是一个**硬件级隔离的轻量微 VM**。每个沙箱是独立的 Linux VM，不是 Docker 容器。

| 特性 | 说明 |
|------|------|
| 启动速度 | < 100ms |
| 隔离级别 | 硬件级（KVM），每个 VM 独立内核 |
| 镜像来源 | 任何 OCI 镜像（Docker Hub、GHCR、ECR 等） |
| 运行方式 | 本地嵌入进程，无长期 daemon（CLI 除外） |
| 支持平台 | Linux（KVM）、macOS（Apple Silicon） |

**关键误解澄清：**
- 沙箱不是 Docker 容器，不能在沙箱内 apt install 预装软件（应该用完整镜像或 `--script` 注入）
- 沙箱设计哲学：**创建 → exec 命令 → 拿结果 → 销毁**（短生命周期）
- MCP Server 才是长期运行的进程，沙箱按需创建/销毁

---

## 二、CLI 快速参考

### 安装（NUC 上已装好）
```bash
curl -fsSL https://install.microsandbox.dev | sh
# 二进制位置：~/.microsandbox/bin/msb
```

### 核心命令

```bash
# 临时沙箱：创建 → 运行命令 → 自动销毁
msb run ubuntu -- python3 -c "print('hello')"

# 命名沙箱（持久，可反复 exec）
msb run --name devbox ubuntu -- bash     # 后台运行
msb exec devbox -- python3 -c "print(1)" # 追加命令

# 查看
msb ls                    # 所有沙箱
msb ps                     # 运行中的沙箱
msb inspect devbox          # 详细配置
msb logs devbox -f          # 实时日志

# 停止 / 删除
msb stop devbox
msb rm devbox

# 镜像
msb pull python            # 预拉镜像
msb image ls               # 缓存的镜像

# 卷（持久存储）
msb volume create data --size 10G
msb volume ls
msb volume rm data
```

### 常用选项（msb run / msb create）

| 选项 | 说明 |
|------|------|
| `--name <NAME>` | 沙箱名称，不指定则自动生成临时名称 |
| `-c, --cpus <N>` | 虚拟 CPU 数量，默认 1 |
| `-m, --memory <SIZE>` | 内存，如 512M、1G |
| `-v, --volume <SRC:DST>` | 挂载宿主机路径或命名卷 |
| `-e, --env KEY=value` | 设置环境变量 |
| `-p, --port HOST:GUEST` | 端口映射（HOST 端口 → 沙箱端口） |
| `--network-policy <POLICY>` | 网络策略（见下节） |
| `--secret ENV=VALUE@HOST` | 秘密注入，只发给指定目标 |
| `--replace` | 同名沙箱存在则替换 |
| `-t, --tty` | 分配伪终端（交互模式） |
| `--timeout <DURATION>` | 命令超时，如 30s、5m、1h |
| `--idle-timeout <DURATION>` | 空闲超时，停止沙箱 |
| `--max-duration <DURATION>` | 最大运行时长 |
| `--tmpfs <PATH:SIZE>` | 内存文件系统，如 /tmp:100M |
| `--script NAME:PATH` | 将宿主机文件作为脚本注入沙箱 |
| `-w, --workdir <PATH>` | 默认工作目录 |

---

## 三、网络策略

### 默认策略
- **仅公网出站**：可访问公共互联网
- **阻止**：私网（10.0.0.0/8、172.16.0.0/12、192.168.0.0/16）、loopback、link-local、云元数据（169.254.169.254）

### `--network-policy` 选项

```bash
--network-policy public-only  # 默认，阻止私网
--network-policy nonlocal      # 公网 + 私网/LAN，阻止 loopback/link-local/云元数据
--network-policy allow-all    # 无限制
--network-policy none         # 完全无网络
```

### 宿主机访问

要让沙箱访问**宿主机上的服务**（如 Gitea 192.168.3.20:3080），需要：

```bash
msb run --name devbox --network-policy nonlocal ubuntu -- python3 script.py
```

### ⚠️ 端口映射关键限制

`-p HOST:GUEST` 的端口默认绑定到 **127.0.0.1**（localhost），局域网其他机器不可达。

```bash
# 验证：宿主机本地可访问
curl http://127.0.0.1:8081/     # ✅ OK

# 但局域网其他机器不行
curl http://192.168.3.20:8081/  # ❌ 拒绝连接
```

**解决方案：** 使用 TCP 转发器在 `0.0.0.0` 上监听，转发到 `127.0.0.1:PORT`：

```bash
# 宿主机上运行转发器
python3 sandbox-fwd.py 18643 8643  # 0.0.0.0:18643 → 127.0.0.1:8643
```

配合 Traefik 做反向代理暴露给 LAN。详见 [[concepts/microsandbox-deployment-architecture]].

### 出站公网

NUC 本身没有自动公网路由。沙箱访问公网需要显式配置 HTTP 代理：

```bash
http_proxy=http://192.168.3.20:8888 curl http://httpbin.org/ip
```

NUC 上运行 Squid 容器提供代理服务（端口 8888）。

---

## 四、代码/文件传入沙箱

### 方式 1：挂载卷（推荐，适合大文件/目录）
```bash
# 宿主机路径 → 沙箱路径
msb run -v /tmp/project:/app ubuntu -- python3 /app/main.py
```

### 方式 2：--script 注入脚本文件
```bash
# NAME:PATH，注入后可在沙箱内直接执行
msb run --script main.py:/tmp/main.py ubuntu -- python3 /tmp/main.py
```

### 方式 3：base64 通过 exec stdin 传入（小文件）
```bash
# 在沙箱内解码
msb exec devbox -- bash -c "echo '<base64>' | base64 -d > /tmp/script.py"
```

---

## 五、MCP Server

### 现状（NUC）

NUC 上运行标准 `microsandbox-mcp`，端口 8912，StreamableHTTP 协议。

```yaml
# config.yaml
mcpServers:
  microsandbox:
    enabled: true
    url: http://192.168.3.20:8912
```

### ⚠️ 已知限制：MCP 不支持高级 CLI 参数

标准 `microsandbox-mcp` 的 `sandbox_create` 工具**不支持**：
- `--network-policy`（无法创建带 LAN 访问的沙箱）
- `-p` 端口映射
- `-v` 卷挂载
- `--env` 环境变量
- `-c`/`-m` CPU/内存限制

MCP 只提供基础操作：`sandbox_run`、`sandbox_create`、`sandbox_exec`、`sandbox_list`、`sandbox_stop`、`sandbox_remove`。

**凡需要网络/端口/卷的沙箱，必须用 SSH 直调 msb CLI：**

```bash
ssh nuc "msb run --name devbox --network-policy nonlocal -p 8643:8643 python:3.11-alpine"
```

**历史：** 曾经尝试修改 MCP server 以支持更多参数（Mac Mini 修改版），但：
1. 默认协议是 SSE（Hermes 只支持 StreamableHTTP）
2. 改到 StreamableHTTP 后与 Hono web 框架有适配问题
3. 最终选型：MCP 管基础操作，复杂需求走 SSH + CLI

### 可用工具

| 工具 | 说明 |
|------|------|
| `sandbox_run` | 临时沙箱：创建 → 运行 → 返回结果 → 销毁 |
| `sandbox_create` | 创建持久命名沙箱（仅基础参数） |
| `sandbox_exec` | 在运行中的沙箱内执行命令 |
| `sandbox_shell` | 执行带管道的 shell 命令 |
| `sandbox_list` | 列出所有沙箱 |
| `sandbox_stop` | 停止沙箱 |
| `sandbox_remove` | 删除沙箱 |
| `sandbox_fs_read` | 读取沙箱内文件 |
| `sandbox_fs_write` | 写入沙箱内文件 |
| `sandbox_fs_list` | 列出沙箱内目录 |
| `volume_create` | 创建命名卷 |
| `sandbox_metrics` | 实时资源监控 |

---

## 六、常见问题

### Q: 沙箱内无法访问宿主机局域网
A: 创建时加 `--network-policy nonlocal`

### Q: 端口映射外部访问不到
A: 默认绑 127.0.0.1，需要 TCP 转发器 + Traefik。见 [[concepts/microsandbox-deployment-architecture]].

### Q: `msb run` 报 SIGABRT / KVM 权限错误
A: 执行 `sudo usermod -aG kvm <username>`，然后重新登录 SSH

### Q: 如何在沙箱内访问 Gitea 代码仓库？
A: 方案 1：`--network-policy nonlocal` 后沙箱可直连 `192.168.3.20:3080`
   方案 2：沙箱内无 git，用 `--volume` 挂载宿主机路径，或用 `--script` 注入代码

### Q: MCP Server 连接超时
A: 确认 NUC 上 MCP 进程活着：`ps aux | grep microsandbox-mcp`
   确认端口可达：`curl http://192.168.3.20:8912/health`

### Q: 沙箱内需要长期运行服务
A: 用 `msb run --detach --name devbox ubuntu` 后台运行，再用 `msb exec devbox -- ...` 追加命令

### Q: MCP 创建沙箱没有网络访问能力？
A: 是的，`sandbox_create` 不支持 `--network-policy`。需要用 SSH 直调 msb CLI：`ssh nuc "msb run --network-policy nonlocal ..."`

### Q: 很多镜像的 entrypoint 会启动服务占端口？
A: 是的，如 Blaxel 镜像默认 entrypoint 启动 MCP server 占 8080。创建沙箱时用 `--entrypoint /bin/sh` 绕过。

---

## 七、官方资源索引

| 资源 | 地址 |
|------|------|
| GitHub 仓库 | https://github.com/superradcompany/microsandbox |
| MCP Server | https://github.com/superradcompany/microsandbox-mcp |
| 官方文档 | https://docs.microsandbox.dev |
| 文档索引（llms.txt）| https://docs.microsandbox.dev/llms.txt |
| Discord 社区 | https://discord.gg/T4YZp8BPe8 |
| 安装脚本 | `curl -fsSL https://install.microsandbox.dev \| sh` |

### 文档页面导航
- 入门：getting-started/introduction、getting-started/quickstart、getting-started/agents
- CLI：cli/overview、cli/sandbox-commands、cli/image-commands、cli/volume-commands
- 沙箱：sandboxes/overview、sandboxes/lifecycle、sandboxes/commands、sandboxes/volumes、sandboxes/secrets
- 网络：networking/overview、networking/security-model、networking/tls
- 配置：configuration
- 食谱：recipes/docker（沙箱内跑 Docker）、recipes/docker-in-sandbox（Docker in 沙箱）
