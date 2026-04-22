#!/usr/bin/env python3
"""
analyze-project: 分析当前项目结构，生成上下文摘要
用法：python scripts/analyze-project.py [项目路径]
"""

import os
import sys
import json

def analyze_project(project_path="."):
    """分析项目并生成摘要"""
    
    target_dir = os.path.abspath(project_path)
    
    # 检测文件
    files = os.listdir(target_dir)
    
    project_type = "Unknown"
    framework = "Unknown"
    dependencies = []
    test_framework = "Unknown"
    start_cmd = "Unknown"
    test_cmd = "Unknown"
    
    # Python 检测
    if "requirements.txt" in files or "pyproject.toml" in files or "setup.py" in files:
        project_type = "Python"
        
        # 读取 requirements.txt
        if "requirements.txt" in files:
            with open(os.path.join(target_dir, "requirements.txt"), "r", encoding="utf-8") as f:
                deps = f.read().splitlines()
                dependencies = [d.split("==")[0].split(">=")[0].split("<")[0].strip() for d in deps if d.strip() and not d.startswith("#")]
        
        # 检测框架
        if any("fastapi" in d.lower() for d in dependencies):
            framework = "FastAPI"
            start_cmd = "uvicorn main:app --reload"
        elif any("django" in d.lower() for d in dependencies):
            framework = "Django"
            start_cmd = "python manage.py runserver"
        elif any("flask" in d.lower() for d in dependencies):
            framework = "Flask"
            start_cmd = "python app.py"
        else:
            framework = "Python Script"
        
        # 检测测试框架
        if any("pytest" in d.lower() for d in dependencies):
            test_framework = "pytest"
            test_cmd = "pytest"
        elif any("unittest" in d.lower() for d in dependencies):
            test_framework = "unittest"
            test_cmd = "python -m unittest"
    
    # Node.js 检测
    if "package.json" in files:
        project_type = "Node.js"
        with open(os.path.join(target_dir, "package.json"), "r", encoding="utf-8") as f:
            pkg = json.load(f)
            dependencies = list(pkg.get("dependencies", {}).keys())
            dev_deps = list(pkg.get("devDependencies", {}).keys())
            
            # 检测框架
            if "express" in dependencies:
                framework = "Express"
            elif "next" in dependencies:
                framework = "Next.js"
            elif "react" in dependencies:
                framework = "React"
            elif "vue" in dependencies:
                framework = "Vue"
            
            # 检测测试
            if "jest" in dev_deps or "jest" in dependencies:
                test_framework = "Jest"
                test_cmd = "npm test"
            elif "mocha" in dev_deps or "mocha" in dependencies:
                test_framework = "Mocha"
                test_cmd = "npm test"
            
            # 启动命令
            scripts = pkg.get("scripts", {})
            if "dev" in scripts:
                start_cmd = f"npm run dev"
            elif "start" in scripts:
                start_cmd = f"npm start"
    
    # 生成摘要
    summary = f"""## 项目上下文摘要

**类型**: {project_type}
**框架**: {framework}
**主要依赖**: {', '.join(dependencies[:5]) if dependencies else '无'}
**测试框架**: {test_framework}
**启动命令**: `{start_cmd}`
**测试命令**: `{test_cmd}`

---
*由 Hermes-Doc analyze-project 脚本生成*
"""
    
    print(summary)
    
    # 保存到 .hermes-context.md (如果存在 .hermes 目录)
    hermes_dir = os.path.join(target_dir, ".hermes")
    if os.path.exists(hermes_dir):
        context_file = os.path.join(hermes_dir, "project-context.md")
        with open(context_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"\n💾 已保存至：{context_file}")
    
    return summary

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    analyze_project(path)
