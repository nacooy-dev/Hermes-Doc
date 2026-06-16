# AGENTS.md — OpenCode Workspace

This project lives on **自托管 Gitea** (NUC 192.168.3.20:3080).

## Gitea 对接要点

```bash
# Git 操作（SSH 协议）
# Web: http://192.168.3.20:3080
# Git SSH 地址: ssh://git@192.168.3.20:3022（注意端口 3022 而非 2222）
# API Base: http://192.168.3.20:3080/api/v1

# 克隆仓库
GIT_SSH_COMMAND="ssh -p 3022" git clone ssh://git@192.168.3.20:2222/lvyun/仓库名.git

# 统一配置 SSH 端口（推荐）
git config core.sshCommand "ssh -p 3022"

# REST API 调用
curl -H "Authorization: token $GITEA_TOKEN" http://192.168.3.20:3080/api/v1/user/repos

# 创建 Issue
curl -X POST http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/issues \
  -H "Content-Type: application/json" \
  -H "Authorization: token $GITEA_TOKEN" \
  -d '{"title": "bug: xxx", "body": "描述", "labels": ["bug"]}'

# 创建 PR
curl -X POST http://192.168.3.20:3080/api/v1/repos/lvyun/仓库名/pulls \
  -H "Content-Type: application/json" \
  -H "Authorization: token $GITEA_TOKEN" \
  -d '{"title": "feat: xxx", "body": "描述", "base": "main", "head": "feature-branch"}'
```

## 关键环境变量

- `$GITEA_HOST` = `192.168.3.20:3080`（已在 ~/.bashrc 定义）
- `$GITEA_TOKEN` = Gitea API token（已在 ~/.bashrc 定义）
- `$GITEA_SSH_PORT` = `3022`

## 陷阱与注意事项

- Gitea 返回的 SSH URL 端口是 **容器内 2222**，外部必须使用 **3022**
- `GIT_SSH_COMMAND="ssh -p 3022"` 是绕过容器端口映射的关键
- SSH key 名称 `mac-mini-hermes` 已部署到 Gitea 账户
- Gitea API PATH 是 `/api/v1/`（不是 GitHub 的 `/api/v3/`）

## 完整参考

详细文档：`~/TianCe-Lab/Hermes-Doc/wiki/entities/gitea-nuc.md`
Hermes Skill：`gitea-workflow`（更多命令示例）