---
title: 我们为什么放弃了 memOS — 记忆工程的幻觉与务实方案
created: 2026-05-05
project: hermes
project_phase: memory-system-critique
status: active
archived: false
blog_origin: 深入分析 memOS 优缺点，对比我们的 Hermes Wiki 方案，形成完整实践记录
sources:
  - MemOS GitHub 源码与文档分析
  - Karpathy LLM Wiki 模式
  - 我们的 Hermes Wiki 系统实践
  - 上篇博客：agent-memory-philosophy
confidence: high
summary: |
  MemOS 的许愿式自动化是工程幻觉：承诺让 AI 自动记住一切，实际上给使用者制造了大量噪音。
  本文拆解 memOS 的设计优点、真实配置成本、以及致命问题。
  给出我们的务实方案：frontmatter + wikilinks + 月度 lint，3 个组件解决 80% 的需求，没有 Node.js 依赖。
tags: [hermes, memory, ai-agent, tooling, critique]
related_blogs:
  - 20260505-hermes-agent-memory-philosophy.md
  - 20260502-hermes-wikilinks-召回机制.md
---

# 我们为什么放弃了 memOS — 记忆工程的幻觉与务实方案

## 结论先行

**好的记忆系统不是让 AI 自动记住一切，而是让人类主动判断什么值得记住。**

这不是技术问题，是工作哲学问题。

MemOS 代表了当前 AI 记忆工程的一个集体幻觉：用技术代替判断，用自动化代替主动思考。Embedding 向量、语义搜索、自动截取……这些技术本身没问题，但当它们被包装成"你不需要想，AI 会帮你记住"的许愿时，工程就变成了噪声生成器。

我们的方案不性感：纯 Markdown 文件，加一个 frontmatter 头，加一个 Python lint 脚本。但它诚实——没有许愿，只有明确的能力边界。

---

## 一、我们评估了 MemOS：承认它的优点

先说客观的。MemOS 有几个设计方向是对的。

### Pyramid Memory 分层框架

MemOS 提出了三层记忆结构：
- **Episodic**：对话片段
- **Semantic**：提取的知识
- **Procedural**：工作流程模式

这个框架的价值不在于代码实现，而在于**迫使使用者思考：不同类型的信息需要不同的记忆策略**。这是对的抽象方向。

### 主动召回意识

MemOS 明确设计为"给 LLM 用的外部记忆"，它尝试解决"存了但找不到"的问题，有向量搜索、时间衰减、自动摘要这些正确的工程思路。

### 与 agent 的集成定位

它不是普通笔记工具，它知道记忆要为 agent 服务。这个定位是对的。

---

## 二、MemOS 的真实配置成本：我们踩过的坑

但是，当我们真的去配置它时，问题是另一回事。

### 坑 1：Node.js 技术栈污染

```
npm install mcp-memory-os
```

然后需要：
- Node.js >= 18
- 向量数据库（Pinecone 或本地 Chroma）
- OpenAI API Key（做 Embeddings）
- MCP server 配置

我们的环境：
- Hermes Agent：Python
- MemOS：Node.js
- 向量数据库：又一套依赖

三个独立系统协同，维护成本远大于收益。不是配置难，是技术栈之间的摩擦成本不可接受。

### 坑 2：自动截取 = 噪音生成器

MemOS 的核心 hook：

```typescript
// agent_end 时自动截取
const endHook = {
  event: "agent_end",
  handler: async (event) => {
    const memory = await extractMemory(event.conversation);
    await vectorStore.upsert(memory.embeddings);
  }
};
```

这个逻辑有一个根本性错误：**假设每次 agent 对话都包含值得记住的内容。**

实际对话中：
- 20% 是有价值的工作结论
- 80% 是确认理解、调试、修正、闲聊

自动截取把这 80% 也存了。向量数据库变成垃圾堆，每次召回要从噪音里找信号。

### 坑 3：Embedding 是统计相似，不是语义理解

MemOS 用 Embedding 做召回。理论上：

> "我想起上次讨论的那个话题" → 语义搜索 → 找到相关片段

**实际上：**

Embedding 是文字统计相似度，不是语义理解：
- "我们决定**不用** memOS" 和 "我们决定**用** memOS" 语义相反，向量距离可能很近
- "项目的技术方案" 和 "项目的管理流程" 在向量空间里可能距离很远，即使它们在同一个项目里

Embedding 召回适合"我有一个模糊关键词"的场景，**不适合"我想起上次讨论的那个判断"**。

MemOS 把 Embedding 当成银弹，实际上它只是匹配文字，不匹配意图。

### 坑 4：许愿式架构承诺

这是最核心的问题。

MemOS 文档：
> "让 AI 自动记住你的所有对话，随时召回，忘掉手动整理的烦恼。"

问题清单：
- 谁来定义"值得记住"？
- 谁来过滤重复信息？
- 谁来管理记忆的失效和更新？
- 谁来判断两个相似记忆是否冲突？

**这些都是工作方式问题，不是工程问题。MemOS 试图用技术绕过工作方式，结果制造了更多问题。**

---

## 三、我们的务实方案

### 怎么想

放弃 MemOS 后，我们重新推倒重建。思考路径：

> **记忆系统真正需要解决的是什么？**
> 在使用者觉得有价值的时候，把信息存下来。在需要的时候，能找到。

就这么简单。不用 AI 自动判断，不用向量搜索，不用 Node.js。

### 怎么干

**方案架构：三个组件**

| 组件 | 作用 | 实现 |
|------|------|------|
| Frontmatter 标准化 | 存储层：让每篇内容有结构、可筛选 | YAML 头 |
| Wikilinks 交叉引用 | 召回层：建立可靠的知识关联 | 手动链接 |
| 月度 lint 检查 | 维护层：定期检查健康度 | Python 脚本 |

---

## 四、在 Hermes 中直接操作

以下是可以直接复制给 AI 的指令，告诉它怎么写、怎么存、怎么检验。

### 告诉 Hermes 怎么写一篇 blog

**把这个指令发给 Hermes：**

```
我写的内容需要存到 blog 文件。请按以下规范帮我整理：

1. 文件名格式：{YYYYMMDD}-{项目}-{主题}.md
   - 日期用今天的日期
   - 项目用全小写连字符，如 ai-colleague / hermes
   - 主题用中文，简洁，如 browser-harness-调研

2. 文件头部必须有这个 frontmatter：

---
title: {标题}
created: {YYYY-MM-DD}
project: {项目名}
project_phase: {当前阶段}  # research / design / development / review
status: active  # active / completed / archived
archived: false  # true / false
blog_origin: |
  3 句话：触发写这篇的原因是什么？为什么现在要写？
sources:
  - {参考来源}
confidence: medium  # low（实验探索）/ medium（调研结论）/ high（确定实践）
summary: |
  3-5 句话的核心内容，用自己的语言总结。
  召回时只看这里，不读正文。
tags: []  # 必须是预定义标签：hermes / memory / ai-agent / tooling / browser / nanobot 等
related_blogs:
  - {相关文件名}  # 至少 1 个
---

3. 正文开头写 ## 背景，简述为什么要做这件事

4. 在正文中主动用 `[[20260502-hermes-wikilinks-召回机制]]` 格式
   链接相关的已有 blog，把文件名替换成实际的

5. 写完后跑 lint 检查：python3 ~/.hermes/skills/wikilinks/scripts/lint.py
   - 确保无错误再结束
```

**这就是全部要告诉 AI 的规则。** 不需要解释为什么，照着做就行。

### 告诉 Hermes 怎么召回 blog

**召回时发这个指令：**

```
我想了解 {主题} 的情况。

请：
1. 先用 wikilinks 工具找到相关的 blog：python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --list
2. 只读 frontmatter 的 summary 部分，快速判断是否相关
3. 相关的话再读正文，不需要全文读，挑相关的段落
4. 读完后总结：这条记录的核心结论是什么，它在当前上下文中的价值是什么
```

**为什么这样设计召回流程？**

因为 frontmatter summary 是人类写的，它已经做了提炼——召回时先读提炼结果，比让 AI 去向量数据库里捞碎片，信号密度高得多。

### 检验工程是否生效

**告诉 Hermes 或手动执行：**

```bash
# 1. 跑 lint 健康检查
python3 ~/.hermes/skills/wikilinks/scripts/lint.py

# 期望输出：✅ 所有检查通过，无问题

# 2. 列出所有 blog
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --list

# 期望：看到带 project / status / confidence 的表格

# 3. 召回某个主题的 blog
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py "memOS"

# 期望：找到标题包含 memOS 的 blog，返回它的 summary

# 4. 查看 frontmatter summary 是否存在且有意义
# 打开任意 blog 文件，确认：
#   - summary 字段有内容（3-5 句话）
#   - 不是空行，不是"暂无"
#   - 读 summary 确实能判断这篇的内容
```

**这三个命令覆盖了完整的数据流：**

| 检验点 | 命令 | 判断标准 |
|--------|------|----------|
| 结构健康 | `lint.py` | 零错误，零警告 |
| 内容存在 | `--list` | 有文件，有摘要 |
| 召回可用 | wikilinks 搜索 | 搜得到，返回 summary |
| Summary 质量 | 手动读文件 | 3-5 句，有实质内容 |

只要这三条全部通过，记忆系统就在正常运作。

### 一键归档过期 blog

超过 90 天没更新的 active blog，lint 会提示归档：

```bash
# 自动将 90 天未更新的 blog 标记为 archived
python3 ~/.hermes/skills/wikilinks/scripts/lint.py --fix

# 然后确认归档结果
python3 ~/.hermes/skills/wikilinks/scripts/wikilinks.py --list
```

---

## 五、关键设计决策：为什么这么干

这些决策不是拍脑袋，每个都有具体原因。

### 决策 1：为什么 frontmatter summary 优于向量搜索？

向量搜索解决"模糊关键词"场景，frontmatter summary 解决"我知道我找什么"场景。

实际工作里：
- "上次我们讨论的那个判断" → 你知道在找什么 → frontmatter summary 精确
- "好像有个类似的想法" → 只有模糊印象 → 浏览器全文搜索足够

我们不需要同时解决两个场景。第一个场景占 80% 的实际需求，frontmatter summary 足够了。

向量搜索能解决第二个场景，但我们不需要为它多搭一套 Node.js + 向量数据库。

### 决策 2：为什么允许自动化的只有"维护检查"？

自动化的边界在于：**自动化不能替使用者做判断**。

| 动作 | 自动化？ | 原因 |
|------|----------|------|
| 触发存储 | ❌ 人类判断 | "感觉有价值才写"，这是主动思考，不是可以外包的行为 |
| 内容提取 | ❌ 人类判断 | summary 是什么，必须由写的人决定 |
| 关联判断 | ❌ 人类判断 | related_blogs 是有意识的关联，不是什么都往里塞 |
| 冲突处理 | ❌ 人类判断 | 两个相似内容谁对谁错，AI 不知道 |
| 健康检查 | ✅ 自动化 | 字段完整性、断链检测，不涉及判断 |

lint 是自动化，但它做的是**合规检查**，不是**价值判断**。这个边界很清楚。

### 决策 3：为什么不用向量数据库，用纯 Markdown？

两个原因：

**第一，零依赖。** MemOS 需要：Node.js + Chroma/Pinecone + Embedding API Key。我们需要：Python（本来就有）+ 任意文本编辑器。

**第二，召回质量更高。** 向量数据库里是算法猜的相关性，Markdown 里是人类的判断。人类的判断更可靠，前提是使用者愿意主动判断。

我们赌的是：愿意主动判断的人，用 frontmatter 会得到更好的结果。不愿意主动判断的人，用 MemOS 只会得到一堆噪音。

---

## 六、与 MemOS 的完整对比

| 维度 | MemOS | 我们的方案 |
|------|-------|-----------|
| 技术栈 | Node.js + 向量数据库 | 纯 Markdown + Python |
| 记忆触发 | `agent_end` 自动截取 | 人类主动判断"感觉有价值" |
| 召回方式 | Embedding 语义搜索 | Frontmatter summary + wikilinks |
| 维护成本 | 高（多套依赖） | 零（无额外依赖） |
| 信号质量 | 低（80% 噪音） | 高（只有主动写的内容） |
| 冲突处理 | 无 | 人类判断 |
| 部署难度 | 复杂 | 零门槛 |
| 设计哲学 | AI 替你想 | 人先想，AI 辅助 |

---

## 七、本次改进：相比哲学篇的具体进化

上篇（[agent-memory-philosophy](20260505-hermes-agent-memory-philosophy.md)）是**哲学层面的思考**，提出了三个层次（存储/召回/推理）和自动化边界的问题。

这篇是**工程层面的落地**，相比上篇具体做了以下改进：

### 1. 精确了"允许自动化的边界"

上篇结论是"全自动记忆是不科学的"。

这篇给出了一个**可操作的精确边界**：

| 动作 | 自动化？ |
|------|----------|
| 触发存储 | ❌ |
| 内容提取 | ❌ |
| 关联判断 | ❌ |
| 冲突处理 | ❌ |
| 健康检查 | ✅ |

不是"尽量少自动化"，而是"只有 lint 检查允许自动化"。这个边界清晰到可以写进团队规范。

### 2. 增加了置信度字段

这次 frontmatter 加了 `confidence: low / medium / high`。

意义：
- `low`：实验性探索，结果不确定
- `medium`：调研结论，有参考价值但未验证
- `high`：确定实践，已验证可用

召回时先看置信度，避免把实验当结论。上篇没有这个区分，这是一个**信息质量标记**的引入。

### 3. 形成了可直接抄的方案

上篇是抽象讨论，这篇给出了**完整的可复用模板**：
- 完整 frontmatter 字段说明
- 三组件架构的决策理由
- 与 MemOS 的 8 维度对比表
- lint 检查的完整检查项清单

任何人都可以照着这个模板搭自己的记忆系统，不需要理解哲学，只需要知道字段怎么填。

### 4. 识别了 MemOS 的四个具体工程问题

上篇说"全自动是不科学的"，这篇拆解了**具体哪里不科学**：
- Node.js 依赖 = 技术栈污染
- `agent_end` hook = 噪音生成器
- Embedding = 统计相似≠语义理解
- 许愿式文档 = 卖愿景不卖产品

这四个判断每个都有具体例子，批判不再停留在"感觉 MemOS 不行"，而是可以说明"哪里不行、为什么不行"。

---

## 八、工程美感

回过头看我们的方案，它有一个优点很少被提及：

**它的能力边界是诚实的。**

我们没有声称"AI 会自动记住一切"。我们说的是：

> 你来判断什么值得记住。我来帮你存好、找准、不生锈。

这不是功能少，这是诚实。

诚实本身是一种工程美感——知道系统能做什么，不能做什么，然后把能做的做到极致。

MemOS 的问题是：它承诺了很多，做了很多，但那些承诺本身就是问题的一部分。

**好的工程不是堆功能，是找到正确的边界，然后把边界内的东西做扎实。**

frontmatter + wikilinks + 月度 lint，三个组件，没有第四个。

这就是我们的记忆系统。

---

*本文为 Hermes Wiki 系统的第二篇实践记录。第一篇讨论哲学基础，本篇给出工程批判和具体方案。*
