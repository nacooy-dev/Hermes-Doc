# Hermes-Doc

> **Behavioral Guidelines & Knowledge Base for Hermes Agent — Based on Karpathy's Efficiency Principles**
>
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> [![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-blue)](https://github.com/hermes-agent)

**Stop treating Hermes like a "ride-hailing app". Turn it into your "dedicated executive car".**

---

## 🚀 Quick Start

### Initialize a New Project

```bash
# Clone or download this repository
cd /path/to/Hermes-Doc

# Run the initialization script in your new project
python3 scripts/init-hermes-doc.py /path/to/your/new-project
```

This will automatically create:
- `.opencode/config.yaml` (OpenCode CLI config)
- `.claude.json` (Claude CLI config)
- Update `.gitignore`

### Manual Configuration for Hermes

Add the following to your `~/.hermes/config.yaml`:

```yaml
system_prompt: |
  You are Hermes, an efficient AI programming assistant. Your behavior follows these four core principles:
  
  1. Think Before Coding — No assumptions, no guessing, clarify proactively.
  2. Simplicity First — Solve problems with minimal code.
  3. Surgical Changes — Only modify what's necessary, match existing style.
  4. Goal-Driven Execution — Define success criteria, verify before delivering.

  Full specification: /path/to/Hermes-Doc/Hermes-behavior-guide.md
```

---

## 📚 Core Documents

| Document | Purpose |
|----------|---------|
| [Hermes-behavior-guide.md](Hermes-behavior-guide.md) | **Constitution**: Full elaboration of Karpathy's 4 principles |
| [EXAMPLES.md](EXAMPLES.md) | **Case Studies**: 8 scenarios with dos and don'ts |
| [INTEGRATION.md](INTEGRATION.md) | **Integration Guide**: Configs for OpenCode/Claude/Qwen |
| [wiki/](wiki/) | **Knowledge Base**: Cumulative knowledge management |
| [scripts/](scripts/) | **Automation**: Initialization and analysis scripts |

---

## 🛠️ Toolchain

### 1. Project Initialization (`scripts/init-hermes-doc.py`)

Inject Karpathy principles into new projects with one command.

```bash
python3 scripts/init-hermes-doc.py [project-path]
```

### 2. Project Analysis (`scripts/analyze-project.py`)

Automatically detect project type (Python/Node.js), extract dependencies, frameworks, and test commands.

```bash
python3 scripts/analyze-project.py [project-path]
```

---

## 📖 Background Story

This project stems from a **cognitive breakthrough**:

> I mistakenly configured Hermes using "ride-hailing" logic (routing/dispatching), causing it to lose its ability for deep thinking and long-term memory.
>
> Then I realized: **Hermes is not a "ride-hailing platform"; it's a "dedicated executive car".**
>
> I then introduced Karpathy's Four Efficiency Principles to reshape Hermes' behavior, transforming it from a "chaotic dispatcher" into a "core assistant".

Read the full story in our blog draft: [blog-post-draft.md](blog-post-draft.md)

---

## 🏗️ Directory Structure

```
Hermes-Doc/
├── Hermes-behavior-guide.md   # Behavioral Constitution
├── EXAMPLES.md                # Case Studies
├── INTEGRATION.md             # Integration Guide
├── README.md                  # This file (Chinese)
├── README_en.md               # This file (English)
├── blog-post-draft.md         # Blog draft
├── LICENSE                    # MIT License
├── scripts/                   # Automation scripts
│   ├── init-hermes-doc.py
│   └── analyze-project.py
├── skills/                    # Exclusive skills
│   └── project-context/
└── wiki/                      # Knowledge base
    ├── SCHEMA.md
    ├── index.md
    ├── log.md
    └── WIKI_GUIDE.md
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Andrej Karpathy**: For proposing the four efficiency principles, which form the theoretical foundation of this project.
- **Hermes Agent Team**: For building an excellent AI agent framework.
- **Community Contributors**: Every friend who has submitted issues and feedback.

---

## 📬 Contact

- Email: nacoolaby@2925.com
- GitHub Issues: [Open an issue](https://github.com/nacooy-dev/Hermes-Doc/issues)

---

> **A car is just a car; it's how you drive that matters.**
>
> May Hermes become your most capable "dedicated executive car".
