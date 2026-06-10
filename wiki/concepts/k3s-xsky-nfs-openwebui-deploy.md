---
title: "K3s + XSKY NFS + Open WebUI 多副本部署"
created: 2026-06-08
updated: 2026-06-08
type: concept
tags: [k3s, xsky, nfs, openwebui, ollama, gpu, deploy, infra]
sources: []
---

# K3s + XSKY NFS + Open WebUI 多副本部署

> 在无外网 K3s 集群上部署 Open WebUI 多副本，后端 PostgreSQL + XSKY NFS 持久化，Ollama GPU 推理加速。

---

## 架构

```
用户 → [Ingress / NodePort 32102]
       → Open WebUI (多副本, RWX NFS PVC)
         → 数据库：PostgreSQL (RWO NFS PVC)
         → 文件/上传：XSKY NFS (10.4.201.60:/k3sbase, RWX)
         → LLM 推理：Ollama (7×RTX A4000 GPU)
```

## XSKY NFS CSI 配置要点

### StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: xsky-nfs
provisioner: com.nfs.csi.xsky
parameters:
  product: GFS                          # 必须！否则走 EUS 代码路径 → ListQuotaTrees 404
  shares: "10.4.201.60:/k3sbase"        # 必须 IP:/path 格式
  xmsServers: "10.4.248.61:8051,10.4.248.62:8051,10.4.248.63:8051"
  csi.storage.k8s.io/provisioner-secret-name: csi-secret
  csi.storage.k8s.io/provisioner-secret-namespace: default
  archiveOnDelete: "false"
```

### Secret（必须用 Secret 传认证，不支持 inline token）

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: csi-secret
  namespace: default
data:
  token: <base64 token>
  user: <base64 "admin">
```

关键参数：
- `shares`（复数！不是 `share`）必须 `IP:/export-path` 格式
- `product: GFS` 必须显式声明，否则 XSCALEROS 6.4.x 报 404
- `product: GFS` 时走 GFS 代码路径跳过 `ListQuotaTrees` API 调用

## PostgreSQL 部署

### 镜像

内网 Harbor 镜像：`10.4.77.249/library/postgres:16-alpine`

### 关键配置

- PVC：5Gi, RWO（或 RWX 但 PostgreSQL 只需单写）
- Service：ClusterIP 5432 端口
- Secret：随机密码，通过 `PGPASSWORD` env var 引用
- Open WebUI 数据库名：`openwebui`

## Open WebUI 多副本

### 镜像

当前版本 `10.4.77.249/rancher/open-webui:latest`（v0.8.12）

### 数据库连接（关键！）

Open WebUI 使用 `DATABASE_URL` 连接数据库。需要构造连接串：

```bash
DATABASE_URL="postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE:-openwebui}"
```

**不要**直接把密码写死在 DATABASE_URL 中，通过 Secret 引用：

```yaml
env:
  - name: PGPASSWORD
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: password
  - name: DATABASE_URL
    value: "postgresql://$(PGUSER):$(PGPASSWORD)@$(PGHOST):$(PGPORT)/$(PGDATABASE)"
```

> 注意：Kubernetes 不支持 env var 嵌套展开，需要用启动脚本拼接。

### 启动脚本方式（推荐）

使用 ConfigMap 挂载 entrypoint.sh：

```sh
#!/bin/sh
if [ -n "$PGUSER" ] && [ -n "$PGPASSWORD" ] && [ -n "$PGHOST" ]; then
  export DATABASE_URL="postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT:-5432}/${PGDATABASE:-openwebui}"
fi
exec python3 -m uvicorn open_webui.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-3000} --forwarded-allow-ips "*" --workers 1
```

### 无外网环境

集群无互联网访问时，HuggingFace Hub 连接会阻塞启动。设置：

```yaml
env:
  - name: HF_HUB_OFFLINE
    value: "1"
```

### NFS PVC 数据目录

```yaml
volumes:
  - name: openwebui-nfs
    persistentVolumeClaim:
      claimName: open-webui-data
volumeMounts:
  - name: openwebui-nfs
    mountPath: /app/backend/data
```

PVC：10Gi, RWX（ReadWriteMany 支持多副本共享）

### OLLAMA_BASE_URL

```yaml
env:
  - name: OLLAMA_BASE_URL
    value: "http://ollama-svc:11434"
```

注意服务名是 `ollama-svc` 不是 `ollama`。

## Ollama GPU 加速

### 问题排查历程

1. **镜像选择**：`dify/ollama` 不带 CUDA 支持，必须用官方 `ollama/ollama`
2. **RuntimeClass**：即使容器请求了 `nvidia.com/gpu`，不设 `runtimeClassName: nvidia` 时 GPU 设备不会真正挂载进容器（只有 `/dev/nvidiactl` 没有 `/dev/nvidia0`）
3. **KEEP_ALIVE**：默认 5 分钟后模型被卸载，下个请求需重新加载到 GPU（耗时 15s+）
4. **并发**：默认 `n_slots=1` 串行处理

### 正确配置

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      runtimeClassName: nvidia   # 关键！否则 GPU 设备不进容器
      containers:
        - env:
            - name: OLLAMA_KEEP_ALIVE
              value: "-1"         # 模型永久驻留 GPU
            - name: OLLAMA_NUM_PARALLEL
              value: "4"          # 允许 4 个并发请求
      resources:
        limits:
          cpu: "16"
          memory: 64Gi
          nvidia.com/gpu: 7       # 请求全部 7 张 GPU
        requests:
          cpu: "4"
          memory: 16Gi
          nvidia.com/gpu: 7
```

### 网络

Ollama 端口 11434 通过 NodePort `ollama-svc:11434:31434/TCP` 暴露。

### 验证命令

```bash
# 检查 GPU 检测（日志）
kubectl logs deploy/ollama | grep "inference compute"

# 测试速度
curl http://<node-ip>:31434/api/generate -d '{"model":"qwen3.5:9b","prompt":"hello","stream":false}'

# 从 Pod 内测试（ollama 镜像无 curl，用 python3）
kubectl exec deploy/ollama -- python3 -c "
import urllib.request, json
req = urllib.request.Request('http://127.0.0.1:11434/api/generate',
    data=json.dumps({'model':'qwen3.5:9b','prompt':'hi','stream':False}).encode(),
    headers={'Content-Type':'application/json'})
import ssl
resp = urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=10)
d = json.loads(resp.read())
print(f'Speed: {d[\"eval_count\"]/d[\"eval_duration\"]*1e9:.0f} t/s')
"
```

## 镜像推送流程（内网 Harbor）

集群节点无外网，镜像拉取流程：

1. **NUC** 有外网 + Docker，负责拉镜像
2. **传输**：`docker save <image> | gzip > image.tar.gz` → `scp` → Mac
3. **Harbor**：Mac 上 `docker push 10.4.77.249/<project>/<image>:<tag>`
4. **Harbor 认证**：`admin / Harbor12345`

## 踩坑记录

| 问题 | 症状 | 原因 | 解决 |
|------|------|------|------|
| API 路由不工作 | `/api/health` 返回 HTML | DATABASE_URL 密码写死字面量 | 用 Secret 引用 + 启动脚本拼接 |
| 2 副本启动失败 | 端口 3000 不监听 | 并发启动 HuggingFace 下载冲突 | `HF_HUB_OFFLINE=1` |
| Ollama 极慢 | 0.74 t/s | `dify/ollama` 镜像无 CUDA | 换 `ollama/ollama` + `runtimeClassName: nvidia` |
| Ollama 间歇 15s | HTTP 500 超时 | 模型被卸载，需重新加载 | `OLLAMA_KEEP_ALIVE=-1` |
| OLLAMA_BASE_URL 不通 | 服务名解析失败 | 服务名是 `ollama-svc` 不是 `ollama` | 配 `http://ollama-svc:11434` |
| NFS PVC 创建失败 | ProvisioningFailed | 参数名是 `shares` 不是 `share` | 复数 + `IP:/path` 格式 |
| NFS 404 | ListQuotaTrees 失败 | `product: GFS` 未设置 | 显式声明 `product: GFS` |
| 页面刷新慢 | 每次刷新等 5s+ | 模型频繁卸载 | `OLLAMA_KEEP_ALIVE=-1` |

## API 代理服务（Open WebUI Proxy）

为客户提供 OpenAI 兼容的 API，含 API Key 认证 + 知识库检索。

### 架构

```
客户应用 → API Key → Proxy (FastAPI) → Bearer JWT → Open WebUI (知识库)
                                      → Ollama (推理)
```

### 部署

- 镜像：`10.4.77.249/library/python:3.11-slim`
- 代码：ConfigMap 挂载，启动时 pip install + uvicorn
- Service：NodePort 32122

### 环境变量

| 变量 | 说明 |
|------|------|
| `OPENWEBUI_URL` | Open WebUI 后端地址 |
| `OLLAMA_URL` | Ollama 服务地址 |
| `BOT_USERNAME` | API 机器人用户邮箱 |
| `BOT_PASSWORD` | 从 Secret 引用 |
| `API_KEYS` | 逗号分隔的 API Key 列表 |

### API 端点

**聊天补全** `POST /v1/chat/completions`
```json
{
  "model": "qwen3.5:9b",
  "messages": [{"role": "user", "content": "根据知识库回答"}],
  "options": {"knowledge": true},
  "stream": false
}
```

**模型列表** `GET /v1/models`
**健康检查** `GET /health`

认证方式：`Authorization: Bearer <api-key>`

> 注意：Open WebUI 的原生 `/api/chat/completions` 端点需要 JWT 且模型注册机制复杂，代理直接转发到 Ollama 的 `/api/chat`，同时调用 Open WebUI 的知识库搜索 API 做 RAG。

### bot 用户

在 Open WebUI Admin Panel → Users 创建：
- Name: `API Bot`
- Email: `api-bot@cdp.edu.cn`
- Password: 通过 Secret `openwebui-bot-secret` 管理

### 知识库集成（knowledge）

代理收到 `options.knowledge: true` 时：
1. 用 api-bot 的 JWT 调用 Open WebUI 的知识库搜索 API
2. 获取相关文档片段
3. 作为 system message 注入到 Ollama 的对话上下文
4. 返回含知识库内容的回答

---

## 硬件

- **K3s 节点**：5 节点（3 master + 2 worker），10.4.77.24-28
- **Ollama 节点**：k3s-master03，96核 CPU, 94GB RAM, 7×RTX A4000 (112GB 显存)
- **XSKY 存储**：10.4.201.60 (NFS), 10.100.102.11-13 (iSCSI)
- **Harbor**：10.4.77.249
- **模型**：qwen3.5:9b (~6.6GB) + gemma4:12b (~7.6GB)
- **推理速度**：60 t/s（7 GPU CUDA）
