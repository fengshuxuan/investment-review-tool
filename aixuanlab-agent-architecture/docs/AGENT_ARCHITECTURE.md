# aixuanlab Excel 学习型 AI Agent 架构规划

## 1. 项目背景

`aixuanlab.com` 当前是一个中文职场 Excel 在线练习网站，已有内容包括：

- 50 道中文职场 Excel 练习题；
- 30 个常用函数和公式说明；
- 40 个可下载办公模板；
- 43 个 Windows Excel 高频快捷键；
- 支持在网页表格里做题、检查公式、解释错误。

现在要新增 AI 助手。这个 AI 助手不应该只是普通客服，而应该成为网站的核心功能之一：

**一个能陪用户练 Excel、分析错题、生成题目、生成文件、修改表格、识别截图的学习型 Agent。**

---

## 2. 总体架构选择

不建议一开始做复杂多 Agent 自治系统。MVP 阶段采用：

```text
工作流 Agent + 工具调用 + 结构化题库 + 用户学习记忆 + Excel 文件处理工具
```

原因：

1. 你的网站任务边界很清晰：Excel 学习、做题、批改、生成文件。
2. 用户操作需要稳定，不适合让模型自由发挥。
3. Excel 文件生成和修改必须由后端工具执行，不能让大模型直接“幻想文件”。
4. 用户画像和做题数据是产品壁垒，应该由数据库维护，不要只存在模型上下文里。

---

## 3. 核心架构图

```text
用户
  ↓
网站前端 AI 助手入口
  ↓
/api/ai/chat
/api/ai/generate-practice
/api/ai/explain-formula-error
/api/ai/upload-image
/api/ai/upload-excel
  ↓
AgentOrchestrator 主控 Agent
  ↓
意图识别 / 上下文整理 / 工具选择 / 结果整合
  ↓
工具服务层：

1. ArkLLMService
   调用火山方舟 doubao-seed-2-1-pro-260628

2. AIContextService
   获取用户画像、最近做题、函数掌握度、学习记忆

3. PracticeService
   检索站内题库，生成新练习题

4. MasteryService
   计算用户函数掌握度

5. MemoryService
   读取、生成、更新学习记忆

6. ExcelService
   生成、读取、修改 xlsx 文件

7. ImageTableService
   图片表格识别，转成结构化数据

8. RecommendationService
   根据薄弱点推荐下一题

  ↓
数据库 / 文件存储
```

---

## 4. Agent 不同能力模块

### 4.1 Chat Agent：聊天答疑

作用：

- 回答 Excel 函数问题；
- 解释练习题；
- 推荐学习路径；
- 根据用户水平调整解释方式。

示例：

```text
用户：VLOOKUP 和 XLOOKUP 有什么区别？
AI：结合网站已有公式库解释，并推荐 2 道对应练习题。
```

上下文需要包含：

- 用户画像；
- 用户最近做题记录；
- 当前题目；
- 相关公式知识；
- 学习记忆摘要。

---

### 4.2 Practice Generator：生成练习题

作用：

- 按岗位、函数、难度、场景生成新题；
- 输出结构化 JSON；
- 前端可以直接渲染为在线练习表；
- 后端也可以根据 JSON 生成 xlsx 文件。

输入示例：

```json
{
  "role": "人事",
  "function_tags": ["IF", "COUNTIFS"],
  "difficulty": "easy",
  "scenario": "考勤统计"
}
```

输出示例：

```json
{
  "title": "按员工统计本月迟到次数",
  "role": "人事",
  "difficulty": "easy",
  "function_tags": ["COUNTIFS"],
  "scenario": "考勤统计",
  "headers": ["员工", "日期", "考勤状态", "统计员工", "迟到次数"],
  "rows": [
    ["张三", "2026-06-01", "迟到", "张三", ""],
    ["李四", "2026-06-01", "正常", "李四", ""],
    ["张三", "2026-06-02", "迟到", "", ""]
  ],
  "target_cell": "E2",
  "answer_formula": "=COUNTIFS(A:A,D2,C:C,\"迟到\")",
  "hints": [
    "需要同时判断员工姓名和考勤状态。",
    "一个条件用 COUNTIF，多个条件用 COUNTIFS。"
  ],
  "common_errors": [
    {
      "error_type": "missing_condition",
      "explanation": "只统计了员工，没有限制考勤状态为迟到。"
    }
  ]
}
```

---

### 4.3 Formula Coach：公式批改 Agent

作用：

- 用户做错题后解释错误；
- 不只是告诉对错，还要说明错因；
- 记录错误类型，用于后续画像和推荐。

输入：

```json
{
  "practice_id": "xxx",
  "user_formula": "=SUMIF(A:A,\"行政\",D:D)",
  "expected_formula": "=SUMIFS(D:D,A:A,\"行政\",B:B,\"6月\")",
  "target_cell": "E2"
}
```

输出：

```json
{
  "is_correct": false,
  "error_type": "missing_condition",
  "explanation": "你的公式只判断了部门，没有判断月份。题目要求按部门和月份两个条件统计报销金额，所以应该使用 SUMIFS。",
  "hint": "先把求和区域放在第一个参数，然后依次写条件区域和条件。",
  "correct_formula": "=SUMIFS(D:D,A:A,\"行政\",B:B,\"6月\")"
}
```

---

### 4.4 Excel File Agent：生成和修改 Excel

作用：

- 根据练习题 JSON 生成 `.xlsx`；
- 用户上传 xlsx 后读取结构；
- 根据用户指令修改表格；
- 返回修改后的文件。

注意：

模型不能直接改 Excel 文件。正确流程是：

```text
用户上传 xlsx
  ↓
ExcelService 解析 workbook 结构
  ↓
AgentOrchestrator 让模型生成修改计划
  ↓
ExcelService 根据结构化计划执行修改
  ↓
保存 generated_files
  ↓
返回下载地址
```

修改计划示例：

```json
{
  "operations": [
    {
      "type": "add_formula_column",
      "sheet": "Sheet1",
      "header": "是否补货",
      "formula_template": "=IF(B{row}<C{row},\"需要补货\",\"正常\")"
    },
    {
      "type": "format_condition",
      "sheet": "Sheet1",
      "range": "D2:D100",
      "condition": "cell_text_equals",
      "value": "需要补货",
      "style": "warning"
    }
  ]
}
```

---

### 4.5 Image Table Agent：图片识别表格

作用：

- 用户上传表格截图；
- 用火山方舟多模态能力识别表头和数据；
- 转成结构化表格；
- 可进一步生成在线练习题或 xlsx 文件。

第一版只做：

1. 图片识别表头和前若干行数据；
2. 返回 JSON；
3. 前端展示“请确认识别结果”；
4. 用户确认后再生成练习题或 Excel。

不要一开始承诺 100% OCR 准确。

---

### 4.6 Learning Memory Agent：学习记忆

作用：

- 从用户画像和做题记录中总结学习记忆；
- 每次 AI 回答时读取相关记忆；
- 用于个性化教学。

学习记忆不是聊天原文，而是压缩后的稳定信息。

示例：

```text
用户最近 SUMIFS 错误较多，主要错误是漏掉第二个条件。
用户偏好先给提示，不希望直接看到答案。
用户更关注人事考勤和工资核算场景。
```

---

## 5. 用户画像、做题数据和记忆的关系

```text
做题数据 = 事实来源
用户画像 = 稳定标签
学习记忆 = 给 AI 使用的摘要
会话历史 = 当前聊天上下文
```

不要把全部聊天记录都塞进模型。每次调用模型时，只取：

1. 最近 6-10 轮对话；
2. 当前题目上下文；
3. 用户画像摘要；
4. 函数掌握度；
5. 与当前问题相关的学习记忆；
6. 必要的站内题库资料。

---

## 6. 多用户与权限原则

这一点必须严格执行。

1. `user_id` 必须来自登录态、JWT、Session 或后端认证中间件。
2. 前端传来的 `user_id` 不可信。
3. 每条做题记录、文件记录、会话记录、生成文件都必须绑定 `user_id`。
4. 文件访问必须校验文件所属用户。
5. 后续如果支持 Coding Agent 或文件操作，每个用户项目必须绑定 `project_id`，并进行目录隔离。

文件隔离建议：

```text
uploads/{user_id}/{file_id}/source.xlsx
generated/{user_id}/{file_id}/result.xlsx
```

不要把所有用户文件混在一个目录。

---

## 7. 推荐开发顺序

### 第 1 阶段：基础后端和模型接入

- FastAPI 项目骨架；
- `.env` 配置；
- `ArkLLMService`；
- `/api/ai/chat`；
- 能正常调用豆包模型返回回答。

### 第 2 阶段：学习上下文

- 用户画像表；
- 做题记录表；
- 函数掌握度表；
- 学习记忆表；
- `AIContextService`。

### 第 3 阶段：公式批改和做题记录

- `/api/ai/explain-formula-error`；
- 保存 `practice_attempts`；
- 更新 `user_function_mastery`；
- 生成错误解释。

### 第 4 阶段：生成练习题

- `/api/ai/generate-practice`；
- 使用结构化 JSON 输出；
- 存入题库或临时生成题表。

### 第 5 阶段：Excel 文件能力

- 根据练习题生成 xlsx；
- 读取上传 xlsx；
- 支持简单修改：新增列、写公式、条件格式、生成 Sheet。

### 第 6 阶段：图片识别表格

- 图片上传；
- 传给 Ark 多模态模型；
- 返回表头和数据 JSON；
- 用户确认后生成 Excel 或练习题。

---

## 8. MVP 验收标准

完成后至少能做到：

1. 用户可以打开 AI 助手聊天。
2. AI 能结合用户画像和最近做题情况回答。
3. 用户做错公式后，AI 能解释错因。
4. 系统能记录做题数据。
5. 系统能统计每个函数的正确率和薄弱点。
6. AI 能根据薄弱点推荐下一道题。
7. AI 能生成一道结构化 Excel 练习题。
8. 后端能根据练习题生成 xlsx 文件。
9. 用户上传图片后，AI 能识别表格大致结构。
10. 所有用户数据和文件都按 `user_id` 隔离。
