---
title: "K3s + XSKY iSCSI CSI 配置"
created: 2026-06-09
updated: 2026-06-09
type: concept
tags: [k3s, xsky, iscsi, csi, storage, infra]
sources: []
---

# K3s + XSKY iSCSI CSI 配置

> XSKY iSCSI CSI 驱动的完整配置流程，含 CRD AccessPath 管理、StorageClass 参数、踩坑记录。

---

## 架构

```
K8s API → CRD AccessPath (type=Kubernetes) → XSKY 存储侧 AP
        → StorageClass (iscsi.csi.xsky.com) → 动态 PV 创建
          → Secret (API token) → XSKY API (10.4.248.61:8051)
```

三层：
1. **CRD** `AccessPath`（namespace `xsky-csi`）— 定义 AP 类型和网关，CSI controller 同步到存储侧
2. **StorageClass** — 定义池、AP 名称、目标门户、认证
3. **Secret** — XSKY API 认证 token

## 网络拓扑

| 平面 | IP | 端口 |
|------|----|------|
| NG 管理 | 10.4.248.61, .62, .63 | 8051 |
| iSCSI 业务 | 10.100.102.11, .12, .13 | 3260 |
| NFS 业务 | 10.4.201.60 | 2049 |

## CRD AccessPath 配置

**必须使用 CRD 方式创建 AP，type 必须是 `Kubernetes`。** 工程师在 Web UI 创建 type=iSCSI 的 AP 后，CSI 驱动不识别（`accessPaths` 配置无效）。

使用 `multi_gateway` 指定纯 iSCSI 业务 IP，避免 `gateway` 字段将管理 IP 也加入 AP：

```yaml
apiVersion: sds.xsky.com/v1
kind: AccessPath
metadata:
  name: csi-ap
  namespace: xsky-csi
spec:
  name: csi-ap
  type: Kubernetes
  cluster_info:
    xmsServers: 10.4.248.61,10.4.248.62,10.4.248.63
    secret_name: xsky-csi-secret
    secret_namespace: xsky-csi
  multi_gateway:
    - hostname: xsky-1
      gateway_ips: 10.100.102.11
    - hostname: xsky-2
      gateway_ips: 10.100.102.12
    - hostname: xsky-3
      gateway_ips: 10.100.102.13
```

CRD 创建后，CSI controller 自动同步到存储侧生成 AP。**Client group 绑定由 CSI controller 在 volume provisioning/attach 时自动完成**，不需要手动 PATCH API。

## StorageClass 参数

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: xsky-storage
provisioner: iscsi.csi.xsky.com
parameters:
  accessPaths: csi-ap              # AP 名称（不是 IP 地址！）
  apName: csi-ap                   # 必须匹配 CRD name
  pool: pool-a0927149045946098d8b8e89f31aa01d  # 用 UUID（不是池名）
  targetPortal: 10.100.102.11:3260 # 任一 iSCSI 网关
  user: admin
  password: <...>
  xmsServers: 10.4.248.61:8051,10.4.248.62:8051,10.4.248.63:8051
```

### 关键参数说明

| 参数 | 值要求 | 踩坑点 |
|------|--------|--------|
| `accessPaths` | **AP 名称**（如 `csi-ap`） | 填 IP 地址会导致 `Failed to select valid access path` |
| `apName` | 必须匹配 CRD `.spec.name` | 不匹配则 provisioning 失败 |
| `pool` | **UUID**（`pool-a0927149...`） | 用池名可能不被识别 |
| `targetPortal` | 任一 iSCSI 网关 IP:3260 | 随便选一个即可 |
| `password` | 明文 | 支持 Secret 引用（待验证） |

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: xsky-csi-secret
  namespace: xsky-csi
data:
  token: <base64>
  user: <base64 "admin">
```

## 踩坑记录

| 问题 | 症状 | 原因 | 解决 |
|------|------|------|------|
| PVC 正常 Bound，Pod 挂载失败 | `Failed to select valid access path from [IP IP IP]` | `accessPaths` 填了 IP 地址，应为 AP 名称 | 改 `accessPaths: csi-ap`（不是 IP） |
| PVC 创建即 Bound，Pod 挂载失败 | 同上的 `accessPaths` 错误 | `accessPaths` 为 IP/AP 名不匹配 | 重新创建 SC |
| CRD `csi-ap` 删不掉 | `deletionTimestamp` 卡住，finalizer 阻止删除 | CSI controller 未移除 finalizer | `kubectl patch ap csi-ap -n xsky-csi -p '{"metadata":{"finalizers":[]}}' --type=merge` |
| StorageClass 参数不可修改 | `Forbidden: parameters is immutable` | K8s 限制 | 必须 delete + create |
| AP 有非 iSCSI 网段的 IP | CRD 用 `gateway` 字段简写 | `gateway` 加的是所有 XSKY 节点 IP | 改用 `multi_gateway` 只列 iSCSI IP |
| 工程师 Web UI 创建 AP 不工作 | CSI 不识别 | 手动创建的 AP type=iSCSI，CSI 需要 type=Kubernetes | 必须通过 CRD 创建 |
| `pool` 用名字失败 | provisioning 错误 | 池名可能重复 | 使用 `pool-<uuid>` |

## 清理流程

重建 AP 的标准步骤：

1. 删除使用该 AP 的测试 PVC/Pod
2. (如 CRD 有 `deletionTimestamp`) patch 移除 finalizer：`kubectl patch ap <name> -n xsky-csi -p '{"metadata":{"finalizers":[]}}' --type=merge`
3. 等待 CRD 自动删除，存储侧 AP 也被清理
4. 重新 apply 新的 CRD YAML

不需要手动删除存储侧 AP——CRD 删除时 CSI controller 负责同步清理。

## 验证

创建测试 PVC 后立即 Bound 说明配置正确。Pod 挂载后检查：

```bash
kubectl exec <pod> -- df -h /data
```

输出应为 `/dev/mapper/36005853...` 的 multipath 设备，容量与 PVC 规格一致。

---

关联页面：[[concepts/k3s-xsky-nfs-openwebui-deploy]]，[[entities/gitea-nuc]]
