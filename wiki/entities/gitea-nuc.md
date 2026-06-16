# Gitea NUC 对接指南

> 自托管 Git 服务 — NUC 192.168.3.20，Docker 部署

---

## 环境信息

| 项目 | 值 |
|------|-----|
| IP | 192.168.3.20 |
| 主机 | Dell OptiPlex 7090, Ubuntu 24.04, nacoo |
| Web URL | <http://192.168.3.20:3080> |
| API Base | <http://192.168.3.20:3080/api/v1> |
| Git SSH 地址 | `ssh://git@192.168.3.20:3022`（映射容器 2222） |
| API Token | 存于 `$GITEA_TOKEN` 环境变量（~/.bashrc 和 ~/.hermes/.env） |
| 用户 | lvyun（管理员） |
| SSH Key | 已部署到 Gitea（key name: `mac-mini-hermes`） |

---

## Git 操作（SSH 协议）

```bash
# 克隆（关键：必须指定 SSH 端口 3022）
GIT_SSH_COMMAND="ssh -p 3022" git clone ssh://git@192.168.3.20:2222/lvyun/仓库名.git

# 已有仓库添加 remote
git remote add nuc ssh://git@192.168.3.20:2222/lvyun/仓库名.git
GIT_SSH_COMMAND="ssh -p 3022" git push nuc main
```

**陷阱**：Gitea 返回的 SSH URL 是容器内端口 2222，外部必须用 3022。`GIT_SSH_COMMAND="ssh -p 3022"` 会强制走主机端口。

**验证 SSH 连通性**：
```bash
ssh -p 3022 git@192.168.3.20
# 返回：Hi there, lvyun! You've successfully authenticated...
```

---

## REST API 操作

### 认证
```bash
TOKEN=$GITEA_TOKEN  # 已写入 ~/.bashrc
```

### 仓库管理
```bash
# 列出用户仓库
curl -s -H "Authorization: token $TOKEN" \
  http://192.168.3.20:3080/api/v1/user/repos

# 创建仓库
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-repo", "description": "...", "private": true}' \
  http://192.168.3.20:3080/api/v1/user/repos

# 删除仓库
curl -s -X DELETE -H "Authorization: token $TOKEN" \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名

# 查看仓库内容
curl -s -H "Authorization: token $TOKEN" \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/contents/
```

### Issue / PR 管理
```bash
# 创建 Issue
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "bug: xxx", "body": "描述"}' \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/issues

# 列出 Issues
curl -s -H "Authorization: token $TOKEN" \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/issues

# 创建 PR
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "feat: xxx", "body": "描述", "base": "main", "head": "feature-branch"}' \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/pulls
```

### 分支与文件
```bash
# 分支列表
curl -s -H "Authorization: token $TOKEN" \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/branches

# 创建文件
curl -s -X POST -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "base64编码内容", "message": "commit msg", "branch": "main": "main"}' \
  http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/contents/路径/文件
```

---

## 对 AI Agent 的操作指南

### Hermes Agent（本机）
- 加载 skill: `skill_view('gitea-workflow')` — 已封装到 github-* 技能体系
- 环境变量 `GITEA_TOKEN` 已在 `~/.hermes/.env`
- SSH key 已部署（key: `mac-mini-hermes`）
- 克隆示例：
  ```bash
  GIT_SSH_COMMAND="ssh -p 3022 -o StrictHostKeyChecking=no" \
    git clone ssh://git@192.168.3.20:2222/lvyun/仓库名.git
  ```

### OpenCode（本机）
OpenCode 通过 AGENTS.md 自动识别 Gitea 仓库。将模板复制到项目根目录：

```bash
# 从 Hermes skill 复制 AGENTS.md 模板到项目根目录
cp ~/.hermes/skills/devops/gitea-workflow/templates/AGENTS.md ./AGENTS.md
```

模板内容（或直接写入 AGENTS.md）：
```markdown
## Gitea 对接要点
- Web: http://192.168.3.20:3080
- Git SSH: ssh://git@192.168.3.20:3022
- 克隆: GIT_SSH_COMMAND="ssh -p 3022" git clone ssh://git@192.168.3.20:2222/lvyun/仓库.git
- API Token: $GITEA_TOKEN（已写入 bashrc）
```
