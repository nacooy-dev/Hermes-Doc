---
title: 本地 Docker Registry + msb 镜像灌入流程
created: 2026-05-30
updated: 2026-05-30
type: concept
tags: [microsandbox, infra, nuc, sandbox]
confidence: high
sources:
  - 实操验证 / microsandbox-webapp-deploy 项目
---
# 本地 Docker Registry + msb 镜像灌入流程

## 问题

`msb pull` 强制使用 HTTPS 连接 registry，本地 Docker Registry 默认 HTTP 会被拒绝。带自签名 TLS 的 registry 又需要额外信任配置。

## 架构

```
ghcr.io / Docker Hub
    ↓ docker pull
Docker Daemon
    ↓ docker tag / docker push
Local Registry (127.0.0.1:5000, 自签名 TLS)
    ↓ msb pull (SSL_CERT_FILE=...)
msb 缓存
    ↓ msb run / msb create
Microsandbox 沙箱
```

## 全流程

### 1. 自签名证书

```bash
mkdir -p /home/nacoo/registry-certs && cd $_
openssl req -x509 -newkey rsa:4096 -nodes -keyout ca.key -out ca.crt -days 365 \
  -subj '/CN=Local Dev CA'
openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj '/CN=localhost'
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out server.crt -days 365 \
  -extfile <(echo 'subjectAltName=DNS:localhost,IP:127.0.0.1')
```

### 2. 启动带 TLS 的 registry

```bash
docker run -d --name nuc-registry --restart unless-stopped \
  -p 5000:5000 \
  -v /home/nacoo/registry-certs:/certs \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/server.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/server.key \
  registry:2
```

验证：`curl -sk https://127.0.0.1:5000/v2/_catalog` 返回 `{"repositories":[]}`

### 3. CA 信任 bundle

msb 使用 rustls（非 OpenSSL），不能通过系统 CA 安装信任自签名证书，只能通过 `SSL_CERT_FILE` 环境变量：

```bash
cat /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem > /tmp/msb-ca-bundle.pem 2>/dev/null || true
cat /home/nacoo/registry-certs/ca.crt >> /tmp/msb-ca-bundle.pem
```

### 4. 镜像灌入（docker → registry → msb）

```bash
docker pull ghcr.io/blaxel-ai/sandbox-playwright-chromium:latest
docker tag ghcr.io/blaxel-ai/sandbox-playwright-chromium:latest 127.0.0.1:5000/playwright-chromium:latest
docker push 127.0.0.1:5000/playwright-chromium:latest
SSL_CERT_FILE=/tmp/msb-ca-bundle.pem msb pull 127.0.0.1:5000/playwright-chromium:latest
```

### 5. 验证 playwright-chromium 沙箱

已验证：Playwright 1.58.2 + Chromium 145，沙箱内运行 Playwright 自动化成功（5s）。

```bash
msb run --entrypoint /usr/local/bin/node \
  127.0.0.1:5000/playwright-chromium:latest -- -e "
process.env.NODE_PATH = '/usr/local/lib/node_modules';
require('module').Module._initPaths();
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  const page = await browser.newPage();
  await page.goto('https://example.com', { timeout: 15000 });
  console.log('TITLE:', await page.title());
  await browser.close();
  console.log('SUCCESS');
})().catch(e => { console.log('ERROR:', e.message); process.exit(1); });
"
```

## 已缓存的沙箱镜像

| 镜像 | 大小 | 已验证 |
|------|------|--------|
| `microsandbox/claude-code` | 183.8 MB | ✅ node v22 + claude 2.1.44 |
| `127.0.0.1:5000/playwright-chromium` | 800.5 MB | ✅ Chromium 145 自动化 |

## 注意事项

- msb 使用 rustls，`SSL_CERT_FILE` 必须每次 `msb pull` 时设置（或写入 shell profile）
- Playwright 在沙箱内需 `--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage`
- 默认 `entrypoint.sh` 可能启动 MCP server 占 8080 端口，创建沙箱时用 `--entrypoint /bin/sh` 绕过
- 镜像先 docker pull（Docker Cache）再 msb pull，利用 Docker 缓存层避免重复下载
