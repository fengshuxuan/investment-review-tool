# Codex 实施计划

## 目标

请在现有 aixuanlab.com 项目中新增一个 Excel 学习型 AI Agent。不要大规模重构现有网站，优先以“新增模块”的方式接入。

模型供应商：火山方舟 Ark  
模型：`doubao-seed-2-1-pro-260628`  
环境变量：`ARK_API_KEY`

---

## Codex 开发原则

1. 先跑通最小闭环，再扩展功能。
2. 所有 AI 调用必须在服务端完成，不允许前端暴露 `ARK_API_KEY`。
3. `user_id` 必须来自认证中间件，不能信任前端传入。
4. Excel 文件处理必须由代码执行，不要让大模型直接生成虚构文件地址。
5. 所有模型输出如果要入库，必须先经过 schema 校验。
6. 做题数据是事实来源，学习记忆只是摘要，不能反过来覆盖事实。

---

## 第一步：创建后端服务骨架

如果现有项目已有后端，则把 `backend/app` 中的模块合并进去。

如果现有项目没有后端，可以新增 FastAPI 服务：

```bash
cd aixuanlab-agent-architecture/backend
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 第二步：配置环境变量

复制：

```bash
cp .env.example .env
```

然后设置：

```env
ARK_API_KEY=你的火山方舟 API Key
ARK_MODEL=doubao-seed-2-1-pro-260628
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

---

## 第三步：实现 ArkLLMService

文件：

```text
backend/app/services/ark_llm_service.py
```

要求：

1. 封装普通文本对话。
2. 封装图片 + 文本多模态调用。
3. 后续支持 JSON 输出解析。
4. 统一异常处理，避免 Ark 报错直接暴露给前端。

---

## 第四步：实现 AgentOrchestrator

文件：

```text
backend/app/services/agent_orchestrator.py
```

职责：

1. 判断用户意图；
2. 获取用户学习上下文；
3. 选择调用哪个服务；
4. 拼接 prompt；
5. 调用 Ark 模型；
6. 返回统一响应格式。

第一版不用做复杂自主规划，直接用明确的 endpoint 分流：

```text
/api/ai/chat                  普通聊天
/api/ai/generate-practice     生成练习题
/api/ai/explain-formula-error 解释公式错误
/api/ai/image-to-table        图片识别表格
/api/ai/excel/generate        生成 Excel 文件
```

---

## 第五步：实现数据库

先用 SQLite 或现有数据库。MVP 表结构参考：

```text
user_profiles
practice_questions
practice_attempts
user_function_mastery
learning_memories
ai_conversations
ai_messages
uploaded_files
generated_files
```

数据库 SQL 在：

```text
backend/app/db/schema.sql
```

如果现有项目使用 Prisma / Drizzle / Supabase / Django ORM，请把这些表迁移成对应写法。

---

## 第六步：实现做题数据闭环

当用户提交公式后：

```text
前端提交：practice_id + target_cell + user_formula
  ↓
后端读取标准答案 expected_formula
  ↓
判断对错
  ↓
保存 practice_attempts
  ↓
更新 user_function_mastery
  ↓
需要解释时调用 AI 生成解释
```

错误类型要结构化：

```text
wrong_function
wrong_range
wrong_condition
syntax_error
absolute_ref_error
missing_condition
logic_reversed
unknown
```

---

## 第七步：实现学习记忆

学习记忆由系统根据做题数据生成，不要完全相信聊天内容。

保存规则：

1. 同一个函数连续多次错，生成 weakness 记忆。
2. 用户明确表达偏好，生成 preference 记忆。
3. 用户正确率提升，生成 progress 记忆。
4. 低置信度记忆不用于强推荐。

示例：

```json
{
  "memory_type": "weakness",
  "content": "用户在 SUMIFS 题目中经常遗漏第二个条件。",
  "confidence": 0.91,
  "source": "practice_data"
}
```

---

## 第八步：实现练习题生成

接口：

```http
POST /api/ai/generate-practice
```

输入：

```json
{
  "role": "人事",
  "function_tags": ["COUNTIFS"],
  "difficulty": "easy",
  "scenario": "考勤统计"
}
```

输出必须是结构化 JSON，字段参考 `PracticeQuestion` schema。

---

## 第九步：实现 Excel 文件能力

MVP 支持：

1. 练习题 JSON -> xlsx；
2. 上传 xlsx -> 解析 workbook 摘要；
3. 简单修改：新增列、写公式、加条件格式；
4. 返回下载地址。

不要一开始做复杂 VBA、数据透视表或宏。

---

## 第十步：实现图片表格识别

接口：

```http
POST /api/ai/image-to-table
```

流程：

1. 用户上传图片；
2. 后端保存图片；
3. 调用 Ark 多模态模型；
4. 返回识别出的表头和数据；
5. 前端提示用户确认。

---

## 第十一步：前端最小入口

在网站右下角增加：

```text
💬 Excel AI 助手
```

面板里放 4 个快捷入口：

1. 问 Excel 问题；
2. 生成练习题；
3. 解释我的公式错误；
4. 上传图片识别表格。

练习题页面增加：

```text
问 AI：为什么我这题错了？
问 AI：给我一个提示，不要直接给答案
问 AI：生成一道类似题
下载这道题的 Excel 文件
```

---

## 最终验收

Codex 完成后，请确认：

- [ ] `uvicorn app.main:app --reload` 能启动；
- [ ] `/health` 返回 ok；
- [ ] `/api/ai/chat` 能调用 Ark；
- [ ] `/api/ai/generate-practice` 返回结构化题目；
- [ ] `/api/ai/explain-formula-error` 能解释错因；
- [ ] 做题记录能写入数据库；
- [ ] 函数掌握度能更新；
- [ ] 学习记忆能读取并进入 AI 上下文；
- [ ] 能根据练习题生成 xlsx；
- [ ] 图片识别接口能返回表格 JSON；
- [ ] 不暴露 `ARK_API_KEY`；
- [ ] 所有用户数据都按 `user_id` 隔离。
