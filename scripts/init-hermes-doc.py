#!/usr/bin/env python3
"""
init-hermes-doc: 为新项目初始化 Hermes 配置文件
用法：python scripts/init-hermes-doc.py [项目路径]
"""

import os
import sys
import shutil

def init_project(project_path="."):
    """初始化项目配置"""
    
    # 目标路径
    target_dir = os.path.abspath(project_path)
    
    # 1. 创建 .opencode 配置
    opencode_dir = os.path.join(target_dir, ".opencode")
    os.makedirs(opencode_dir, exist_ok=True)
    
    opencode_config = """# OpenCode CLI 配置
# 遵循 Karpathy 效率四原则

system_prompt: |
  你是一个高效的 AI 编程助手，遵循 Karpathy 效率四原则：
  
  1. 编码前思考 — 不假设，不猜测，主动澄清
  2. 简洁优先 — 最少代码解决问题，拒绝过度设计
  3. 精准修改 — 只改必要的，匹配现有风格
  4. 目标驱动执行 — 明确成功标准，验证后再交付
  
  在开始编码前，如果需求不明确，必须先提问确认。
  实现时优先选择最简单的方案。
  修改现有代码时，只改动必要的部分。
  完成后提供验证步骤。

# 默认模型（可根据需要调整）
model: qwen/qwen3.5-397b-a17b

# 工具使用权限
tools:
  - terminal
  - file
  - search_files
  - read_file
  - write_file
  - patch

# 上下文窗口
context_window: 8192
"""
    
    with open(os.path.join(opencode_dir, "config.yaml"), "w", encoding="utf-8") as f:
        f.write(opencode_config)
    
    # 2. 创建 .claude.json 配置
    claude_config = {
        "systemPrompt": "你是一个高效的 AI 编程助手，遵循 Karpathy 效率四原则：\n\n1. 编码前思考 — 不假设，不猜测，主动澄清\n2. 简洁优先 — 最少代码解决问题\n3. 精准修改 — 只改必要的，匹配现有风格\n4. 目标驱动执行 — 明确成功标准，验证后再交付\n\n在开始编码前，如果需求不明确，必须先提问确认。",
        "tools": {
            "enabled": ["terminal", "file", "search", "read", "write", "patch"]
        }
    }
    
    import json
    with open(os.path.join(target_dir, ".claude.json"), "w", encoding="utf-8") as f:
        json.dump(claude_config, f, indent=2, ensure_ascii=False)
    
    # 3. 创建 .gitignore 追加项（如果存在）
    gitignore_path = os.path.join(target_dir, ".gitignore")
    with open(gitignore_path, "a", encoding="utf-8") as f:
        f.write("\n# Hermes & AI Configs\n.opencode/\n.claude.json\n.qwen/\n.hermes/\n")
    
    print(f"✅ 项目配置初始化完成：{target_dir}")
    print("   - 已创建 .opencode/config.yaml")
    print("   - 已创建 .claude.json")
    print("   - 已更新 .gitignore")
    print("\n💡 提示：现在可以启动 OpenCode 或 Claude CLI 开始工作了！")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    init_project(path)
