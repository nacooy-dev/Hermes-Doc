# Hermes-Doc

> **Hermes Agent 的行为规范与知识库系统 — 基于 Karpathy 效率四原则**
>
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> [![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-blue)](https://github.com/hermes-agent)

**[🌎 English Version](README.md)**

---

**拒绝“网约车”思维，把 Hermes 打造成您的“专属公务车”。**

---

## 🚀 快速开始

### 一键初始化新项目

```bash
# 克隆或下载此仓库后
cd /path/to/Hermes-Doc

# 在新项目中运行初始化脚本
python3 scripts/init-hermes-doc.py /path/to/your/new-project
```

这将自动创建：
- `.opencode/config.yaml` (OpenCode CLI 配置)
- `.claude.json` (Claude CLI 配置)
- 更新 `.gitignore`

### 手动配置 Hermes

在 `~/.hermes/config.yaml` 中添加：

```yaml
system_prompt: |
  你是 Hermes，一个高效的 AI 编程助手。你的行为遵循以下四大原则：
  
  1. 编码前思考 — 不假设，不猜测，主动澄清
  2. 简洁优先 — 最少代码解决问题
  3. 精准修改 — 只改必要的，匹配现有风格
  4. 目标驱动执行 — 明确成功标准，验证后再交付

  详细规范见：/path/to/Hermes-Doc/Hermes-behavior-guide.md
```

---

## 📚 核心文档

| 文档 | 用途 |
|------|------|
| [Hermes-behavior-guide.md](Hermes-behavior-guide.md) | **行为宪法**：Karpathy 四原则完整阐述 |
| [EXAMPLES.md](EXAMPLES.md) | **实战教材**：8 个场景的正反案例 |
| [INTEGRATION.md](INTEGRATION.md) | **集成指南**：OpenCode/Claude/Qwen 配置方法 |
| [wiki/](wiki/) | **知识库**：累积式知识管理系统 |
| [scripts/](scripts/) | **自动化工具**：初始化与分析脚本 |

---

## 🛠️ 工具链

### 1. 项目初始化 (`scripts/init-hermes-doc.py`)

为新项目一键注入 Karpathy 原则。

```bash
python3 scripts/init-hermes-doc.py [项目路径]
```

### 2. 项目分析 (`scripts/analyze-project.py`)

自动识别项目类型（Python/Node.js），提取依赖、框架、测试命令。

```bash
python3 scripts/analyze-project.py [项目路径]
```

---

## 📖 背景故事

这篇文档源于一次**认知突围**：

> 我曾误用 OpenCode 的“调度思维”配置 Hermes，导致它既失去了深度思考能力，又丢掉了长期记忆优势。
> 
> 直到我意识到：**Hermes 不是“网约车平台”，而是“专属公务车”**。
> 
> 于是，我引入 Karpathy 效率四原则，重塑了 Hermes 的行为模式，让它从“混乱的调度器”变成了“核心助手”。

---

## 🏗️ 目录结构

```
Hermes-Doc/
├── Hermes-behavior-guide.md   # 行为宪法
├── EXAMPLES.md                # 正反案例
├── INTEGRATION.md             # 工具集成指南
├── README.md                  # English Version
├── README_zh.md               # 中文版本
├── LICENSE                    # MIT 协议
├── scripts/                   # 自动化工具
│   ├── init-hermes-doc.py
│   └── analyze-project.py
├── skills/                    # 专属技能包
│   └── project-context/
└── wiki/                      # 知识库
    ├── SCHEMA.md
    ├── index.md
    ├── log.md
    └── WIKI_GUIDE.md
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 🙏 致谢

- **Andrej Karpathy**：提出 LLM 协作四原则，为本项目提供理论基础。
- **Hermes Agent 团队**：打造优秀的 AI 智能体框架。
- **社区贡献者**：每一位提出建议和反馈的朋友。

---

## 📬 联系方式

- 邮箱：nacoolaby@2925.com
- GitHub Issues: [提问题/建议](https://github.com/nacooy-dev/Hermes-Doc/issues)

---

> **车是好车，关键看你怎么开。**
> 
> 愿 Hermes 成为您最得力的“专属公务车”。
