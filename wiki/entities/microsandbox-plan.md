# 微沙箱对接计划

> 目标：让 Hermes（本机）和 OpenCode 能通过 NUC 上的 microsandbox 创建/运行/管理沙箱环境

---

## 一、现状诊断 ✅

### 服务信息
| 项目 | 值 |
|------|-----|
| NUC | 192.168.3.20, Dell OptiPlex 7090, Ubuntu 24.04, user nacoo |
| msb | v0.3.14, 已装, `/home/nacoo/.microsandbox/bin/msb` |
| 已拉镜像 | ubuntu (39.6MB) |
| microsandbox-mcp | npm 包 v0.4.6, 可跑 MCP Server (port 8080) |
| SSH | 本机密钥已部署（免密码登录） |

### 昨天失败的根本原因 🔍
**`nacoo` 用户不在 `kvm` 组** → `msb run` 创建虚拟机时无法访问 `/dev/kvm` → sandbox 进程 SIGABRT (code 134)。

```
# /dev/kvm 权限
crw-rw---- 1 root kvm 10, 232  → 只有 root 和 kvm 组成员可读写
# nacoo 的用户组
nacoo : nacoo adm cdrom sudo dip plugdev lxd docker  → kvm 组缺失 ❌
```

### 验证 KVM 支持 ✅
- CPU 有 `vmx` 硬件虚拟化标志
- `/dev/kvm` 设备存在
- 内核 6.8.0 支持 KVM

---

## 二、第一阶段：修复 KVM 权限 🛠️

```bash
# NUC 上执行
sudo usermod -aG kvm nacoo
# nacoo 重新登录（退出当前 SSH 会话重新连）
```

验证：
```bash
groups nacoo                           # 应包含 kvm
msb run ubuntu -- echo 'sandbox OK!'   # 不再 SIGABRT
```

---

## 三、第二阶段：对接方案（二选一）

### 方案 A：SSH 远程执行（推荐，最快上线）
Hermes/OpenCode 通过 SSH 远程调用 `msb` 命令。

```bash
# 本机 Hermes 直接调用 NUC 沙箱
ssh nacoo@192.168.3.20 "msb run ubuntu --timeout 60s -- python3 script.py"

# 前台沙箱（跑完自动销毁）
ssh nacoo@192.168.3.20 "msb run python --timeout 30s -- python3 -c 'print(1+1)'"

# 后台沙箱（可持久化，多次 exec）
ssh nacoo@192.168.3.20 "msb create -n dev-sandbox -p 8080:8080 ubuntu"
ssh nacoo@192.168.3.20 "msb exec dev-sandbox -- python3 -c 'print(\"hello\")'"
ssh nacoo@192.168.3.20 "msb stop dev-sandbox"
ssh nacoo@192.168.3.20 "msb rm dev-sandbox"
```

**优点**：
- 零额外部署，现有 SSH 即可
- msb 完整能力（端口映射、卷挂载、网络策略、TLS 拦截等）
- 本机不占资源，沙箱跑在 NUC 上

**缺点**：
- Hermes 本地没有 sandbox 工具集，靠终端执行
- SSH 往返延迟（NUC 同局域网 <1ms，可忽略）
- 需要写 ssh 命令封装

---

### 方案 B：MCP Server（更优雅，需额外部署）
在 NUC 上运行 `microsandbox-mcp`（v0.4.6），Hermes 注册为 MCP 工具。

**部署步骤**：
1. 启动 MCP Server 容器：
```bash
# 在 NUC 上
cd ~/msb-mcp
docker build -t msb-mcp .
docker run -d --name msb-mcp \
  -v /dev/kvm:/dev/kvm \
  -v /home/nacoo/.microsandbox:/home/nacoo/.microsandbox \
  --device /dev/kvm \
  --group-add kvm \
  --network host \
  msb-mcp
```

2. Hermes 注册 MCP：
```bash
hermes mcp add microsandbox --url http://192.168.3.20:8080
```

3. 验证：
```bash
hermes mcp test microsandbox
```

**优点**：
- Hermes 原生 MCP 集成，自动发现工具
- AI 对话中可直接操作 sandbox（创建/运行/管理）
- OpenCode 也支持 MCP 注册

**缺点**：
- 需要构建和部署 Docker 容器
- 容器内需要访问 `/dev/kvm`（嵌套虚拟化）
- microsandbox-mcp 的功能可能比 CLI 少
- **风险**：容器内运行 msb + KVM 可能性能下降

---

## 四、推荐路径

先 **方案 A** 快速验证 sandbox 可用，再决定是否升级到 **方案 B**。

**2026-05 更新：MCP Server 已落地（有限功能）**
- NUC 上运行 Docker 容器化 microsandbox-mcp（端口 8912，StreamableHTTP 协议）
- Hermes 通过 config.yaml 注册为 MCP 工具
- **但 sandbox_create 不支持 --network-policy、-p、-v 等高级参数**
- 需要网络/端口的沙箱操作走 SSH 直调 msb CLI
- 详见 [[references/microsandbox-handbook#五mcp-server]]