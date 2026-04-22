# Project Context Skill

> **功能**：让 Hermes 秒懂当前项目背景，无需每次重复解释。
> **触发**：在新会话开始或切换项目时调用。

## 核心逻辑

1. **自动识别项目类型**：
   - Python: 检测 `requirements.txt`, `pyproject.toml`, `setup.py`
   - Node.js: 检测 `package.json`, `tsconfig.json`
   - Go: 检测 `go.mod`
   - Rust: 检测 `Cargo.toml`

2. **提取关键信息**：
   - 项目名称与描述
   - 主要依赖库
   - 测试框架（pytest, jest, unittest 等）
   - 构建/启动命令

3. **生成项目摘要**：
   - 输出简短的上下文摘要，供 Hermes 在后续对话中参考。

## 使用方法

在 Hermes 对话中：

```
加载 project-context 技能，分析当前项目。
```

或直接运行脚本：

```bash
python scripts/analyze-project.py
```

## 输出示例

```markdown
## 项目上下文摘要

**类型**: Python Web 应用
**框架**: FastAPI
**主要依赖**: pydantic, sqlalchemy, uvicorn
**测试框架**: pytest
**启动命令**: `uvicorn main:app --reload`
**测试命令**: `pytest`

**当前任务**: 实现用户登录功能
```

## 代码实现

见 `scripts/analyze-project.py`
