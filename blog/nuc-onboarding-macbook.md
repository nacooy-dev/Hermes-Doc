# 第二台 MacBook 对接 NUC 基础设施配置指南

> 目标：让所有 Mac 都能通过 Hermes 使用 NUC 的 Gitea 和 Microsandbox
> 适用：大统领的 MacBook Pro 2 号机

## 前置条件

- Hermes Agent 已安装并可用（`hermes --version`）
- NUC 已开机，网络可达（ping 192.168.3.20）
- macOS 终端可用

## 第一步：SSH 免密登录 NUC

需要将本机 SSH public key 添加到 NUC 的 `authorized_keys`。注意：**不要用带 `command=` 前缀的 key**（那是关机专用）。

```bash
# 1. 如果还没有 SSH key，先生成
ssh-keygen -t ed25519 -C "lvyun@MacBook-Pro-2.local"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub
# 输出类似：ssh-ed25519 AAAAC3... lvyun@MacBook-Pro-2.local

# 3. 添加到 NUC（需要 nacoo 的密码，首次一次）
ssh-copy-id nacoo@192.168.3.20
# 或手动追加：
# ssh nacoo@192.168.3.20 'echo "ssh-ed25519 AAAAC3... lvyun@MacBook-Pro-2.local" >> ~/.ssh/authorized_keys'

# 4. 验证
ssh nacoo@192.168.3.20 'echo SSH OK && uname -a'
```

> ⚠️ **重要**：NUC 上 `~/.ssh/authorized_keys` 里已有几个 key：
> - `lvyunt@163.com` — 原始管理员 key（保留）
> - Mac mini 的 key（已存在）
> - MacBook Pro 2 的 **poweroff 专用 key**（已有，但带 `command=` 前缀，不能用于正常 SSH）
> 
> 你需要**新增一个不带 `command=` 的 key**，直接用 `ssh-copy-id` 即可。

## 第二步：Gitea 配置

### 生成 Gitea API Token

在 MacBook 上操作：

```bash
# 1. 登录 Gitea Web（浏览器打开 http://192.168.3.20:3080）
#    用户：lvyun  密码：Gitea 登录密码

# 2. 生成 Token：设置 → 应用 → 管理 Access Token → 生成新 Token
#    权限勾选：所有（read + write）

# 3. 保存到环境变量
cat >> ~/.bashrc << 'EOF'

# Gitea (NUC 192.168.3.20)
export GITEA_HOST=192.168.3.20:3080
export GITEA_TOKEN=这里填你刚生成的token
export GITEA_SSH_PORT=3022
EOF
source ~/.bashrc
```

### 添加 SSH Key 到 Gitea

用于 Git SSH 操作（clone/push/pull）：

```bash
# 通过 API 添加（GITEA_TOKEN 用上面生成的）
curl -X POST "http://$GITEA_HOST/api/v1/user/keys" \
  -H "Authorization: token $GITEA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"MacBook-Pro-2\",
    \"key\": \"$(cat ~/.ssh/id_ed25519.pub)\"
  }"

# 验证
ssh -p 3022 git@192.168.3.20
# 应该看到：Hi there, lvyun! You've successfully authenticated...
```

### 测试 Git 操作

```bash
# 克隆一个现有仓库
GIT_SSH_COMMAND="ssh -p 3022" \
  git clone ssh://git@192.168.3.20:2222/lvyun/hermes-doc.git

# 或测试 API
curl -s "http://$GITEA_HOST/api/v1/user/repos" \
  -H "Authorization: token $GITEA_TOKEN" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'共 {len(data)} 个仓库:')
for r in data:
    print(f'  {r[\"name\"]}  {\"private\" if r[\"private\"] else \"public\"} ')
"
```

## 第三步：Hermes MCP Server 配置（Sandbox）

Microsandbox 的 MCP Server 已在 NUC 上容器化运行，MacBook 只需要在 Hermes 配置中注册。

### 安装 MCP Python 包

Hermes 的 MCP 客户端需要 `mcp` Python 包。Hermes 使用 Python 3.11，需要用对应的 pip 安装：

```bash
# 查看 Hermes 使用的 Python 版本
hermes --version | grep "Python"
# → Python: 3.11.x

# 用对应版本的 pip 安装
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip install mcp

# 验证
python3.11 -c "import mcp; print(mcp.__version__)"
```

> 💡 如果 Hermes 是用其他方式安装的，用 `which python` 找到正确的 Python。

### 注册 MCP Server

```bash
hermes mcp add microsandbox --url http://192.168.3.20:8912
# 提示 authenticate? 选 n
# 提示 Enable all 6 tools? 选 y
```

验证配置：

```bash
cat ~/.hermes/config.yaml | grep -A 4 "mcp_servers:"
# 应该显示：
# mcp_servers:
#   microsandbox:
#     url: http://192.168.3.20:8912
#     enabled: true
```

### 测试 Sandbox

新开一个 Hermes 会话（`/new`），测试沙箱功能：

```bash
# 直接问 Hermes：
# "在 NUC 沙箱里跑一下 echo hello from macbook"

# 或直接用 curl 验证 MCP 连通性：
curl -s http://192.168.3.20:8912 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 -m json.tool

# 返回 server info 即为成功
```

### 可用的 MCP 工具

新 Hermes 会话中，这 6 个工具会自动以 `mcp_microsandbox_` 前缀出现：

| Hermes 工具名 | 功能 |
|--------------|------|
| `mcp_microsandbox_msb_run` | 创建沙箱 + 执行 + 销毁（一次性） |
| `mcp_microsandbox_msb_create` | 创建持久沙箱 |
| `mcp_microsandbox_msb_exec` | 在已有沙箱中执行命令 |
| `mcp_microsandbox_msb_rm` | 停止并删除沙箱 |
| `mcp_microsandbox_msb_list` | 列出运行中的沙箱 |
| `mcp_microsandbox_msb_pull` | 拉取容器镜像 |

## 第四步：安装 Hermes Skills（可选，但推荐）

将 Mac mini 上的技能复制到 MacBook，方便 Hermes 自动使用正确的命令模板。

```bash
# 复制 gitea-workflow skill
scp -r nacoo@192.168.3.20:/Users/lvyun/.hermes/skills/devops/gitea-workflow \
  ~/.hermes/skills/devops/

# 复制 microsandbox-nuc skill
scp -r nacoo@192.168.3.20:/Users/lvyun/.hermes/skills/devops/microsandbox-nuc \
  ~/.hermes/skills/devops/
```

> 💡 如果两台 Mac 不互通，让大统领从 Mac mini 上手动拷过来就行。路径是 `~/.hermes/skills/devops/` 下的两个目录。

## 第五步：写 Hermes Persona 备忘

把 NUC 基础设施的信息写进 `~/.hermes/persona.md`，让 Hermes 每次自动记得。

```markdown
# NUC 基础设施
- NUC: 192.168.3.20, 用户 nacoo, SSH 免密
- Gitea: Web :3080, SSH :3022, API token 在环境变量 $GITEA_TOKEN
- Microsandbox MCP: http://192.168.3.20:8912, 容器化, --restart=always
```

或者直接让 Hermes 通过记忆系统记录——第一次用沙箱时告诉它一次就够了。

## 验证清单

完成后逐个验证：

- [ ] `ssh nacoo@192.168.3.20 'echo ok'` → 免密登录成功
- [ ] `ssh -p 3022 git@192.168.3.20` → Gitea 认证成功
- [ ] `curl -s http://192.168.3.20:3080/api/v1/user/repos -H "Authorization: token $GITEA_TOKEN"` → 返回仓库列表
- [ ] `hermes mcp list` → 显示 microsandbox 已配置
- [ ] 新 Hermes 会话中创建沙箱 → 成功

## 参考

- Gitea skill: `devops/gitea-workflow`（含 AGENTS.md 模板）
- Sandbox skill: `devops/microsandbox-nuc`（含 MCP 重启命令）
- NUC 基础设施总结: `nuc-infra-integration-summary.md`
- Gitea wiki: `~/TianCe-Lab/Hermes-Doc/wiki/entities/gitea-nuc.md`