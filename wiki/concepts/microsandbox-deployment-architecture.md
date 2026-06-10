---
title: Microsandbox 部署架构 — Traefik + Squid + 端口转发
created: 2026-05-30
updated: 2026-05-30
type: concept
tags: [microsandbox, deploy, traefik, proxy, network, nuc, infra]
confidence: high
sources:
  - 实操验证 / microsandbox-webapp-deploy 项目
  - 会话 20260524/20260525 部署调试
---
# Microsandbox 部署架构

> NUC 上运行沙箱 Web 服务的完整三层架构：Traefik（LAN 入口）→ TCP 转发器 → msb 沙箱（内部服务），出站走 Squid 代理。

## 核心问题

`msb run -p HOST:GUEST` 的端口映射默认绑定到 `127.0.0.1`，局域网其他机器无法直接访问。沙箱内部需要访问公网时也没有管道。

## 三层架构

```
Internet/公网
   ↕ (http_proxy Squid 出站)
┌─ NUC (192.168.3.20) ──────────────────────┐
│                                              │
│  ┌─────────┐    ┌──────────────┐    ┌────────┐
│  │ Traefik │───→│ TCP Forwarder │───→│ msb    │
│  │ :80     │    │ 0.0.0.0:1XXXX│    │ sandbox│
│  │         │    │ ↕             │    │ :PORT  │
│  └─────────┘    └──────────────┘    └────────┘
│       │                                   │
│       │  File Provider                    │ --network-policy nonlocal
│       │  (热加载路由)                       │ (访问 LAN 服务)
│       ↓                                   ↓
│  config/*.yaml                      Gitea 等 LAN 服务
│                                              │
│  ┌──────────┐                               │
│  │ Squid    │←── http_proxy 出站 ←──────────-┘
│  │ :8888    │
│  └──────────┘
└──────────────────────────────────────────────┘
```

## 组件详解

### 1. Traefik（LAN 入口）

容器化运行，Docker Compose 编排：

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:v3.3
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/etc/traefik/traefik.yml
      - ./config:/etc/traefik/config  # File Provider 热加载
```

配置使用 **File Provider** 热加载路由目录 `config/`，新增/删除 `.yaml` 文件无需重启 Traefik：

```yaml
# traefik.yml
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: "/etc/traefik/config"
    watch: true
```

**路由规则示例：** `Host(\`appname.nacoolab.lan\`)` → dnsmasq 泛域名解析到 NUC IP。

### 2. Squid 出站代理

沙箱内无公网访问能力（默认 `public-only` 只允许公网出站，但 NUC 本身没有公网出口路由配置），需要显式 HTTP 代理。

**故障历程：** Tinyproxy → Squid

- 先试了 `vimagick/tinyproxy` 和 `ghcr.io/tinyproxy/tinyproxy` 镜像
- 容器启动正常，但代理连接全部超时（从宿主机自身用代理也一样）
- 原因不明（可能是 tinyproxy 与 msb 网络兼容性问题）
- 替换为 `sameersbn/squid` + 自定义配置

```bash
docker run -d --name aproxy --restart unless-stopped \
  -p 8888:3128 \
  -v /home/nacoo/traefik/squid-custom.conf:/etc/squid/squid.conf \
  sameersbn/squid:latest
```

```conf
# squid-custom.conf
acl all src 0.0.0.0/0
http_access allow all
http_port 3128
```

沙箱内使用方式：
```bash
http_proxy=http://192.168.3.20:8888 curl http://httpbin.org/ip
# 或写入环境变量 /etc/profile 持久化
```

### 3. TCP 转发器（sandbox-fwd.py）

**解决 msb 端口映射绑 127.0.0.1 的问题。**

```python
# 核心逻辑：0.0.0.0:LISTEN_PORT → 127.0.0.1:TARGET_PORT
# 用于 Traefik/Docker 容器/LAN 访问沙箱内部服务
```

- 监听 `0.0.0.0:1{PORT}`（如沙箱内端口 8643 → 外部 18643）
- 双向 TCP 转发，使用 Python 标准库，无外部依赖
- 带 PID 文件管理，方便 stop/restart

### 4. create-sandbox.sh — 一键部署脚本

整合全部流程：

```bash
# 用法
./create-sandbox.sh myapp 8643 python:3.11-alpine
```

**自动完成：**
1. 清理旧沙箱 + 旧转发器
2. 创建沙箱：`msb run --detach -p PORT:PORT --network-policy nonlocal IMAGE`
3. 启动 TCP 转发器（nohup + PID 文件）
4. 写入 Traefik 路由文件（`config/myapp.yaml`，热加载）
5. 验证 + 打印管理命令

**清理：**
```bash
msb stop myapp && msb rm myapp
kill $(cat /tmp/fwd-8643.pid)
rm /home/nacoo/traefik/config/myapp.yaml
```

### 5. dnsmasq 泛域名解析

NUC 上 dnsmasq（或路由器 DNS）配置 `*.nacoolab.lan` → `192.168.3.20`，配合 Traefik 路由。

## 实际流量路径

```
用户浏览器 http://myapp.nacoolab.lan/
  → DNS 解析 → 192.168.3.20:80 (Traefik)
  → File Provider 路由匹配 Host(`myapp.nacoolab.lan`)
  → 转发到 http://192.168.3.20:18643 (TCP 转发器)
  → 转发到 127.0.0.1:8643 (msb 沙箱内部服务)
```

## 关键发现

1. **端口映射绑 127.0.0.1**：`-p PORT:PORT` 是 msb v0.3.14 的限制，非配置选项
2. **Tinyproxy 不可用**：容器起得来但代理卡死，换 Squid 解决（原因未深究）
3. **Traefik File Provider 热加载**：改 `config/` 目录下的 yaml 文件即时生效，不重启容器
4. **config/ 被 .gitignore 排除**：路由文件是运行时动态写入的，不入库
5. **--network-policy nonlocal 必要**：沙箱要访问 LAN 上的 Gitea 等服务时必须加此参数
6. **镜像默认可能带 ENTRYPOINT**：如 Blaxel 镜像默认启动 MCP server 占 8080 端口，需 `--entrypoint /bin/sh` 绕过
