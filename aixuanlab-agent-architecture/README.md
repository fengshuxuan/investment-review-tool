# aixuanlab AI Agent 架构项目文件

这个目录是给 Codex 使用的项目骨架，用来为 `aixuanlab.com` 增加一个 Excel 学习型 AI Agent。

> 说明：当前 GitHub 可访问仓库里没有找到 `aixuanlab` 仓库，所以本次文件被放在独立目录 `aixuanlab-agent-architecture/` 和独立分支 `aixuanlab-agent-architecture` 中，便于后续复制到真正的网站仓库。

## 产品定位

`aixuanlab.com` 不是普通聊天机器人场景，而是一个中文职场 Excel 在线练习网站。AI 助手应定位为：

**Excel 学习教练 Agent**

它要做到：

1. 能聊天，解释 Excel 公式和练习题。
2. 能基于站内题库生成新的 Excel 练习题。
3. 能根据练习题生成 `.xlsx` 文件。
4. 能读取和修改用户上传的 Excel 文件。
5. 能识别用户上传的表格截图。
6. 能结合用户画像、做题数据、错题记录和学习记忆，推荐下一步练什么。

## 推荐技术路线

```text
前端网站 / AI 聊天窗口
  ↓
后端 API 层 FastAPI
  ↓
AgentOrchestrator 主控调度器
  ↓
工具服务层：
- ArkLLMService：调用火山方舟豆包模型
- PracticeService：题库检索与练习题生成
- ExcelService：生成 / 读取 / 修改 xlsx
- ImageTableService：图片表格识别
- ContextService：拼接用户画像、做题数据和当前上下文
- MemoryService：学习记忆读取和更新
- MasteryService：函数掌握度计算
  ↓
数据库：用户画像、做题记录、函数掌握度、会话历史、学习记忆、文件记录
```

## 火山方舟模型

默认使用你提供的接入方式：

```python
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv("ARK_API_KEY"),
)

response = client.responses.create(
    model="doubao-seed-2-1-pro-260628",
    input=[...],
)
```

## 目录说明

```text
aixuanlab-agent-architecture/
  README.md
  .env.example
  docs/
    AGENT_ARCHITECTURE.md
    CODEX_IMPLEMENTATION_PLAN.md
  backend/
    requirements.txt
    app/
      main.py
      api/
        ai_routes.py
      core/
        config.py
      db/
        schema.sql
      prompts/
        excel_coach_system_prompt.md
      schemas/
        ai.py
      services/
        agent_orchestrator.py
        ark_llm_service.py
        ai_context_service.py
        memory_service.py
        mastery_service.py
        practice_service.py
        excel_service.py
        image_table_service.py
```

## 给 Codex 的第一句指令

把下面这段发给 Codex：

```text
请阅读 aixuanlab-agent-architecture/docs/AGENT_ARCHITECTURE.md 和 CODEX_IMPLEMENTATION_PLAN.md，按照文档要求为 aixuanlab.com 实现 Excel 学习型 AI Agent。先不要重构现有网站，只新增后端服务、数据库表、API 和最小前端入口。模型接入使用火山方舟 Ark，环境变量为 ARK_API_KEY，模型为 doubao-seed-2-1-pro-260628。
```
