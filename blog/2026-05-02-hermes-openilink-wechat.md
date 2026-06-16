# 从微信指挥多个 AI 平台：OpenILink Hub 实战配置指南

> 作者：大统领  
> 日期：2026-05-02  
> 标签：Hermes Agent, OpenILink, WeChat, 微信, Gateway, 多渠道, OpenClaw

---

## 一、背景：一个实际的工作场景

你今天可能会遇到这样的事：

- 走在路上，突然想起明天有个会议，顺手在微信里说："帮我记一下，明天上午 10 点和产品开会"
- 到了公司，需要重构一个模块，在微信里发："@opencode 重构我的 auth 模块"
- 下午要查个技术问题，顺手在微信问："@hermes 这段代码为什么报错"

**这三个请求，来自同一个微信对话，但处理它们的是三个完全不同的 AI 平台。**

这就是本文要解决的问题。

---

## 二、设计哲学：总机模式 vs 秘书模式

在开始配置之前，我想先说清楚一个设计选择，因为它会决定整个系统的架构。

### 2.1 两种路线

**秘书模式（一个 AI 平台管一切）**

所有事情都丢给一个 AI 平台。它内部帮你路由到子 Agent、管理多轮上下文、处理记忆。你只需要和一个 Bot 说话，它来协调一切。

听起来很美好。但实际用下来：

- **记忆会混乱** —— 你和它聊完私人事务，下一轮对话它可能带着写代码的上下文来回复你
- **单点故障** —— 这个平台崩了，你所有工作全部停摆
- **调度不可控** —— 你不知道它什么时候开新线程、什么时候复用、什么时候失败回退
- **系统臃肿** —— 一个平台试图覆盖所有场景，变得越来越重

**总机模式（消息网关 + 专业平台分工）**

微信只负责接收消息，OpenILink Hub 根据规则把消息路由到对应的 AI 平台。每个 AI 平台各管各的事：

```
微信 → OpenILink（总机） → "记会议" → Hermes（私人管家）
                       → "@opencode" → OpenCode（代码工厂）
```

**OpenILink 只做两件事：**
1. **消息分发** —— 根据规则，把消息发给正确的 AI 平台
2. **响应回传** —— 把 AI 的输出发回微信用户

**它不管的事（这些是 AI 平台自己的职责）：**
- 对话上下文 ❌
- 记忆/知识库 ❌
- 多轮状态 ❌
- 工具调用逻辑 ❌

### 2.2 为什么我选择总机模式

我长期使用 Hermes Agent。它是单 Agent 平台，记忆、项目、工具链完全独立，不会出现"多 Agent 之间的记忆污染"。

但我也需要 OpenCode 来处理复杂的代码任务（多 Agent 并行、PR review 等）。

总机模式让我可以从**一个微信入口**，同时调用这两个完全独立的 AI 平台，而它们之间互不干扰。

---

## 三、OpenILink 是什么

### 3.1 背景痛点

微信生态在国内工作场景中无可替代，但微信没有官方 Bot API。传统的"微信机器人"方案面临两难：

| 方案 | 问题 |
|------|------|
| 网页版微信 API | 2017 年后大规模封号，技术风险极高 |
| iPad协议 | 不稳定，容易掉线，维护成本大 |
| 企业微信 | 需要企业主体，功能受限 |
| Hook DLL | 依赖 Windows，需要注入进程 |

### 3.2 OpenILink 的解决思路

**OpenILink** 是一个开源的微信第三方协议网关（GitHub: [openilink/openclaw-channel-openilink](https://github.com/openilink/openclaw-channel-openilink)），它通过 **OpenILink Hub**（一个本地服务）提供标准化的 Bot API，支持：

- WebSocket 长连接推送消息
- REST API 发送消息
- 多账号管理
- 消息格式标准化（文字、图片、语音、卡片等）

简单说：**OpenILink Hub = 微信的"中控台"，通过标准 API 暴露微信消息**，让任何 AI Agent（Hermes、OpenClaw 等）都能以 Bot 身份接入微信。

### 3.3 架构图（多平台路由）

```
┌──────────────────────────────────────────────────────────────────────┐
│                         微信 App                                       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ 扫码登录 / 协议通信
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     OpenILink Hub                                     │
│  (本地服务，默认 localhost:9800)                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ @hermes →   │  │ @opencode → │  │ @claude →   │  │ 默认 →   │ │
│  │ Hermes App  │  │ OpenCode App │  │ Claude CLI  │  │ Hermes   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │
│              ← 消息路由规则（正则匹配 @mention）→                       │
└──────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │   Hermes     │     │  OpenCode    │     │  其他 Agent  │
   │  Agent      │     │  CLI        │     │  平台       │
   │ (单 Agent,  │     │ (多 Agent,  │     │             │
   │  记忆隔离)  │     │  项目隔离)  │     │             │
   └──────────────┘     └──────────────┘     └──────────────┘
```

**关键点**：所有 AI 平台共用同一个 OpenILink Hub，但各用各的 Bot Token，各管各的记忆和状态。Hub 只负责路由，不管 AI 平台的内部逻辑。

---

## 四、Hermes Agent 接入 OpenILink：完整步骤

### 4.1 前置条件

- [x] OpenILink Hub 已安装并运行（`http://localhost:9800`）
- [x] Hub 管理后台中已创建一个 Bot 应用，获得 `token`
- [x] Hermes Agent 已安装

### 4.2 配置 .env 文件

在 `~/.hermes/.env` 中添加（或更新）以下环境变量：

```bash
# OpenILink Hub 地址（默认）
OPENILINK_HUB_URL=http://localhost:9800

# Bot Token（从 Hub 管理后台获取）
OPENILINK_TOKEN=app_xxxxxxxxxxxxxx

# 允许所有微信用户（生产环境建议改为 false 并配置白名单）
OPENILINK_ALLOW_ALL_USERS=true
```

> **安全提示**：`OPENILINK_ALLOW_ALL_USERS=true` 表示任何微信用户都能与 Hermes 对话。生产环境建议设为 `false`，并通过 `OPENILINK_ALLOWED_USERS` 配置用户 ID 白名单。

### 4.3 配置 config.yaml（关键步骤）

这是最容易踩的坑。需要在 `gateway.platforms` 下注册 openilink：

```yaml
gateway:
  platforms:
    openilink:
      enabled: true
```

> **为什么需要这一步？**  
> Hermes Gateway 不会自动加载所有渠道。它只启动 `config.yaml → gateway.platforms` 中声明且 `enabled: true` 的平台。虽然 `OPENILINK_TOKEN` 环境变量设置了凭证，但若 `platforms` 字典为空，Gateway 完全不知道要启动 openilink 适配器。

### 4.4 重启 Gateway

```bash
# 方法一：通过 launchctl（推荐，生产环境用法）
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
sleep 2
hermes gateway start

# 方法二：直接前台运行（调试用）
hermes gateway run
```

### 4.5 验证连接

检查日志：

```bash
tail -f ~/.hermes/logs/gateway.log
```

成功日志：

```
2026-05-02 02:11:53,234 INFO gateway.run: Connecting to openilink...
2026-05-02 02:11:53,237 INFO gateway.platforms.openilink: [Openilink] Connected to OpenILink Hub: http://localhost:9800
2026-05-02 02:11:53,238 INFO gateway.run: ✓ openilink connected
2026-05-02 02:11:53,238 INFO gateway.platforms.openilink: [Openilink] Init: bot=d89e6dee-f529-4c85-bce7-0d3ea7ebfd06 app=hermes
2026-05-02 02:11:53,238 INFO gateway.run: Gateway running with 2 platform(s)
```

或者用命令检查：

```bash
hermes gateway status
```

### 4.6 测试使用

在微信中找到你的 Bot，给它发一条消息，Hermes 应该会响应了。

---

## 五、踩坑记录：本次配置遇到的问题

### 踩坑 1：SyntaxError 导致 Gateway 完全无法启动

**表现**：gateway error log 中出现 `SyntaxError: ':' expected after dictionary key`

**根因**：`gateway/run.py` 中新增 OpenILink 相关代码时，`platform_env_map` 和 `platform_allow_all_map` 两个字典字面量**缺少闭合的 `}`**。

**修复**：手动补全缺失的 `}`。

### 踩坑 2：缺少自动启用逻辑

**表现**：日志只显示 `qqbot connected`，没有 openilink。

**根因**：`gateway/config.py` 中所有其他平台（DingTalk、Feishu、WeCom 等）都有"检测 env 变量 → 自动启用"逻辑，但 **OpenILink 的自动启用块完全缺失**。代码中没有 `if OPENILINK_TOKEN:` 分支，导致即使 env 变量存在，平台也不会被加入 `config.platforms`。

**修复**：在 `gateway/config.py` 中添加了 OpenILink 的自动启用逻辑：

```python
# OpenILink Hub (WeChat via OpenILink)
openilink_token = os.getenv("OPENILINK_TOKEN")
if openilink_token:
    if Platform.OPENILINK not in config.platforms:
        config.platforms[Platform.OPENILINK] = PlatformConfig()
    config.platforms[Platform.OPENILINK].enabled = True
    config.platforms[Platform.OPENILINK].extra.update({
        "hub_url": os.getenv("OPENILINK_HUB_URL", "http://localhost:9800"),
        "token": openilink_token,
        "allow_all": os.getenv("OPENILINK_ALLOW_ALL_USERS", "false").lower() in ("true", "1", "yes"),
        "allow_from": os.getenv("OPENILINK_ALLOWED_USERS", ""),
    })
```

### 踩坑 3：Adapter 方法名错误

**表现**：日志中 `WebSocket connect failed: 'OpenILinkAdapter' object has no attribute '_set_connected'`

**根因**：`openilink.py` 中使用了 `_set_connected()` / `_set_disconnected()`，但 `BasePlatformAdapter` 基类实际提供的方法名是 **`_mark_connected()`** / **`_mark_disconnected()`**。

**修复**：修正了 3 处方法调用。

---

## 六、OpenClaw 接入 OpenILink

**结论：OpenILink 官方支持 OpenClaw，有独立插件 `openclaw-channel-openilink`。**

OpenILink 不是只支持 Hermes，而是"微信中控台"——通过插件架构同时支持多种 AI 客户端（OpenClaw、Hermes 等都在列）。

### 6.1 安装插件

```bash
openclaw plugins install openclaw-channel-openilink
```

### 6.2 前置步骤

1. 部署或访问一个 [OpeniLink Hub](https://github.com/openilink/openilink-hub) 实例
2. 进入 Hub 管理后台 → Bot 详情页 → **应用市场** → 找到 **OpenClaw** → 点击安装
3. 安装完成后，在 Installation 详情页复制 **Hub URL** 和 **Token**

### 6.3 配置 channels

编辑 `~/.openclaw/openclaw.json`，在 `channels` 下添加 openilink 条目：

```json
"channels": {
  "qqbot": {
    "allowFrom": ["*"],
    "appId": "102852575",
    "clientSecret": "hHrS4gJwaEtYEubJ1kTDxiTF1obPE3tj",
    "enabled": true
  },
  "openilink": {
    "hub_url": "http://localhost:9800",
    "app_token": "app_你的token",
    "allowFrom": ["*"]
  }
}
```

**关键参数说明：**

| 参数 | 说明 |
|------|------|
| `hub_url` | OpenILink Hub 地址（本地为 `http://localhost:9800`，远程需公网可达） |
| `app_token` | 从 Hub 安装 OpenClaw App 后获取的 Token |
| `allowFrom` | 允许访问的用户 ID 列表，`["*"]` 表示允许所有人 |

### 6.4 多账户（可选）

连接多个 Bot：

```json
"channels": {
  "openilink": {
    "accounts": {
      "bot-1": {
        "hub_url": "http://localhost:9800",
        "app_token": "app_bot1_token"
      },
      "bot-2": {
        "hub_url": "https://hub.openilink.com",
        "app_token": "app_bot2_token"
      }
    }
  }
}
```

### 6.5 重启生效

```bash
openclaw restart
```

---

## 七、OpenClaw 是否支持 OpenILink？

**结论：支持，通过官方插件 `openclaw-channel-openilink` 接入。**

| | Hermes + OpenILink | OpenClaw + openilink |
|---|---|---|
| 接入方式 | 内置 adapter（`gateway/platforms/openilink.py`） | 官方插件（`openclaw plugins install`） |
| 配置位置 | `~/.hermes/.env` + `config.yaml` | `~/.openclaw/openclaw.json → channels` |
| Bot 账号 | 从 Hub 管理后台直接创建 | 从 Hub 应用市场安装 OpenClaw App |
| 多账户 | 需要在 `config.yaml` 中配置多个条目 | 支持 `channels.openilink.accounts` |

> **注意**：OpenClaw 的 openilink 和 Hermes 的 openilink **共用同一个 OpenILink Hub**，但 Bot 账号体系是独立的。如果你想让同一个 Hub Bot 同时被两个 AI 客户端处理，需要在 Hub 后台为每个客户端创建独立的应用（App）。

---

> **注意**：OpenClaw 的 openilink 和 Hermes 的 openilink **共用同一个 OpenILink Hub**，但 Bot 账号体系是独立的。如果你想让同一个 Hub Bot 同时被两个 AI 客户端处理，需要在 Hub 后台为每个客户端创建独立的应用（App）。

---

## 八、Hub 的 App 市场：不装 Agent 也能有功能

### 8.1 OpenILink 不只是消息通道

OpenILink Hub 有一套 **App 市场**，相当于 Bot 的"功能商店"。每个 App 是一个独立服务，通过标准协议与 Hub 交互。

| App 类型 | 说明 | 例子 |
|---------|------|------|
| 内置 App | Hub 自带，无需额外部署 | Bridge、Command Service、OpenClaw |
| 市场 App | 从远程 Registry 安装 | Lark、Slack、GitHub、Weather |
| 自定义 App | 你自己开发 | 你的业务系统 |

**平台互通** — 微信与第三方平台双向消息互通 + AI Tools：
Lark（飞书）、Slack、Discord、钉钉、企业微信

**效率工具** — 在微信里用自然语言操作主流 SaaS：
GitHub（36 个 AI Tools）、Google Workspace、Notion、Linear

**生活工具** — 轻量实用，零配置或免费 API：
天气、汇率、记账、地图、RSS、定时提醒

### 8.2 内置 App 一览

**Bridge（内置）—— 微信消息转发到你的服务器**

开启后，所有微信消息以 HTTP POST 形式推送到你配置的 URL。简单场景不需要 Agent，直接写一个 HTTP 服务处理：

```json
// Hub → 你的服务器
POST https://your-server.com/webhook
{
  "event": "message",
  "sender": "wxid_xxxx",
  "content": "原始消息内容",
  "timestamp": 1746182400
}
```

适合：简单自动回复、消息记录、系统集成。

**Command Service（内置）—— Hub 自带斜杠命令**

不需要接 Hermes/OpenClaw，Hub 自己就能响应命令。配置一个 AI API key 即可：

| 命令 | 功能 |
|------|------|
| `/s 600519` | 实时股价查询 |
| `/a 帮我写一封邮件` | AI 对话 |
| `/gi 赛博朋克城市夜景` | AI 生成图片 |
| `/w 北京` | 查天气预报 |
| `/c 1USD=?CNY` | 汇率换算 |
| `/gold` | 实时黄金价格 |

**这和 Hermes/OpenClaw 有什么关系？**

**互不干扰，各走各的。**

---

## 九、关键机制：App 之间怎么不打架？

### 9.1 核心设计：消息模式匹配

这是最关键的设计点——**Hub 不是把所有消息广播给所有 App，而是通过消息模式匹配来分发**。

每个 App 在 Hub 后台注册时，声明自己响应哪种消息模式。只有匹配的消息才会被投递到对应的 App。

```
微信用户发送消息
        │
        ▼
   OpenILink Hub
        │
   模式匹配引擎
        │
   ┌────┴──────────────────────┐
   │                            │
   ▼                            ▼
@hermes "..."              /a "..."
   │                            │
   ▼                            ▼
Hermes WebSocket           Command Service（Hub 内置）
（AI Agent 执行）          （Hub 自己响应）
```

**这意味着：**

- `@hermes xxx` → Hermes（AI Agent 接管）
- `/a xxx` → Command Service（Hub 自己处理）
- 两者收到的消息完全不同，自然不会冲突

### 9.2 实际使用时的边界控制

用表格来说明哪种场景走哪个通道：

| 微信发送 | 匹配模式 | 处理方 | 说明 |
|---------|---------|--------|------|
| `帮我记一下明天开会` | 默认（无 prefix） | Hermes | 普通对话，Hermes 处理 |
| `@hermes 帮我写代码` | `@hermes ` | Hermes | 显式指定 Hermes |
| `/w 北京` | `/w ` | Command Service | Hub 内置查天气 |
| `/s 600519` | `/s ` | Command Service | Hub 内置查股价 |
| `帮我转发到 Slack` | Lark App 匹配 | Lark App | 平台互通 |
| `帮我创建一个 GitHub Issue` | GitHub App 匹配 | GitHub App | SaaS 操作 |

### 9.3 如何让 Hermes 和 Hub App 和平共处

**原则：模式之间不要重叠。**

| 如果你不想让某件事干扰 Agent | 解决方案 |
|-----------------------------|---------|
| Hub 内置 App 抢消息 | 确保 App 的匹配模式和 Agent 的 `@mention` 不重叠 |
| Bridge 转发太多无关消息 | 在 Bridge 配置中设置 `filterPatterns`，只转发特定消息 |
| Command Service 干扰对话 | `/` 命令只在 Command Service 中注册，Agent 不处理 `/` 开头消息 |
| 多 Agent 之间抢消息 | 每个 Agent 用不同的 `@mention`，严格隔离 |

**一个干净的分工示例：**

```
/ → Command Service（Hub 内置，斜杠命令）
@lark → Lark App（飞书互通）
@github → GitHub App（SaaS 操作）
@hermes → Hermes（私人助理，记忆/日程/笔记）
@opencode → OpenCode（复杂代码任务）
默认 → Hermes（最常用，放最后兜底）
```

### 10.4 配置建议

在 Hub 后台配置时，**优先级从高到低**：

1. **精确匹配优先**：`@hermes`、`/w`、`/s` 等有明确前缀的规则
2. **兜底规则放最后**：默认消息（无 prefix）路由到 Hermes

**不要这样配置（会冲突）：**

```
规则1: pattern=.*      → Hermes      ← 所有消息都匹配 Hermes
规则2: pattern=/.*     → Command     ← 永远轮不到 Command Service
```

**应该这样配置：**

```
规则1: pattern=/.*     → Command     ← 斜杠命令先匹配
规则2: pattern=@opencode.* → OpenCode ← OpenCode
规则3: pattern=@hermes.* → Hermes     ← Hermes
规则4: pattern=.*      → Hermes      ← 默认兜底
```

---

## 十、路由规则：让消息精准到达

这是总机模式的核心——**OpenILink 怎么知道把消息发给 Hermes 还是 OpenCode？**

路由规则在 OpenILink Hub 管理后台配置，本质上是一个"消息 → AI 平台"的映射表。

### 9.1 最简单的路由：@mention 显式指定

在 Hub 后台的路由规则中配置：

```json
{
  "rules": [
    {
      "pattern": "^@hermes\\s",
      "target": "hermes",
      "description": "发送给 Hermes"
    },
    {
      "pattern": "^@opencode\\s",
      "target": "opencode",
      "description": "发送给 OpenCode"
    },
    {
      "pattern": ".*",
      "target": "hermes",
      "description": "默认路由到 Hermes"
    }
  ]
}
```

这意味着：

| 微信发送 | OpenILink 路由到 |
|---------|-----------------|
| `@hermes 帮我查一下明天的日程` | Hermes |
| `@opencode 重构我的 auth 模块` | OpenCode |
| `帮我记一下明天开会` | Hermes（默认） |

### 9.2 多 Bot 场景：一个 Hub Bot 服务多个 AI 平台

实际使用时，一个微信 Bot（同一个 Hub Installation）可以同时连接 Hermes 和 OpenCode。用户在微信里看到的是同一个 Bot，但实际上消息被路由到了不同的 AI 平台：

```
同一个微信 Bot（同一个 Hub Token）
     │
     ├── @hermes "..." → Hermes（专属 Bot Token A）
     ├── @opencode "..." → OpenCode（专属 Bot Token B）
     └── "..."（无 mention）→ Hermes（默认）
```

**每个 AI 平台在 Hub 后台创建独立的 App**，获取独立的 Token，然后在各自的配置文件中填入对应的 Token。这样 Hub 知道把哪条消息路由到哪个 App（对应哪个 AI 平台）。

### 9.3 路由规则配置位置

路由规则在 OpenILink Hub 管理后台配置，通常在：
- **Bot 详情页 → 路由规则** 或
- **Installation 详情页 → 消息路由**

具体 UI 因版本而异，但核心逻辑不变：配置 `pattern`（正则表达式匹配消息内容）和 `target`（目标 App/Installation）。

---

## 十一、配置汇总

### Hermes 涉及的文件

| 文件 | 修改内容 |
|------|---------|
| `~/.hermes/.env` | 添加 OPENILINK_HUB_URL、OPENILINK_TOKEN、OPENILINK_ALLOW_ALL_USERS |
| `~/.hermes/config.yaml` | `gateway.platforms.openilink.enabled: true` |
| `hermes-agent/gateway/run.py` | 修复两个字典语法错误 |
| `hermes-agent/gateway/config.py` | 新增 OpenILink 自动启用逻辑 |
| `hermes-agent/gateway/platforms/openilink.py` | 修正 BasePlatformAdapter 方法名 |

### OpenClaw 涉及的文件

| 文件 | 修改内容 |
|------|---------|
| `~/.openclaw/openclaw.json` | 在 `channels` 下添加 openilink 条目 |
| `openclaw plugins install openclaw-channel-openilink` | 安装官方插件 |

### 最小配置（Hermes，仅 .env）

如果你不想改 `config.yaml`，`gateway/config.py` 中的自动启用逻辑已经补上。只要设置了 `OPENILINK_TOKEN`，Gateway 就会自动启用 openilink 平台，**config.yaml 中的 `gateway.platforms` 条目可以省略**。

---

## 十二、下一步

- [ ] 配置 OpenILink Hub 路由规则（`@mention` → 对应 AI 平台）
- [ ] 为 Hermes 和 OpenCode 各自在 Hub 后台创建独立的 App，获取独立 Token
- [ ] 配置 `OPENILINK_ALLOWED_USERS` 白名单，实现用户权限控制
- [ ] 通过 OpenILink Hub 管理后台设置 Bot 的主动消息推送规则
- [ ] 尝试通过 OpenILink 发送图片、语音等多模态消息

---

*本文档基于实战配置经验整理，适用于 Hermes Agent v0.11+、OpenClaw 和 OpenILink Hub。核心设计理念：消息网关只做消息通道，不做 AI 调度。*
