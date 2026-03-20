# Guided MCP Authoring Run V1 需求与当前状态

## 1. 为什么这份文档有必要

有必要，而且是现在就应该有。

原因很直接：

1. 这次 MCP 案例已经不只是几个零散 tool，而是一条完整 workflow
2. 它涉及 prompt、tool、artifact、状态机、人工确认、datasource intake，多层内容不写清楚很容易失焦
3. 你现在已经开始关心“做到哪一步了、哪些 task 完成了、哪些还没做”，这正说明需要一份正式的需求/状态文档

这份文档的目标是同时解决两件事：

- 固定这次 MCP 案例 V1 的产品需求和边界
- 明确当前完成度，避免误以为“好像做了很多，但不知道现在能不能演示”

## 2. 项目目标

### 2.1 目标

把 `cwtwb` 的 MCP 体验从“自由工具调用”推进到一条可控的、可恢复的、有人类确认节点的 Tableau authoring workflow：

`真实 datasource -> schema intake -> contract -> execution plan -> workbook generation -> validation/analyze`

### 2.2 这个 V1 想证明什么

这个 V1 不是要证明“AI 会生成图表”，而是要证明：

- AI 可以从真实数据源开始工作
- AI 可以先把需求规范化
- 人类可以在关键节点参与确认
- 系统可以持续产出中间 artifact
- 最终可以稳定生成 `.twb`

### 2.3 适合的演示场景

- 给 Matthew 展示 Agentic BI authoring workflow
- 给潜在合作方展示“从需求到 workbook”的受控流程
- 给自己作为后续 live MCP / publish / smoke test 的基础底座

## 3. V1 范围

### 3.1 In Scope

- 本地 `Excel + Hyper` datasource intake
- `run_id` 驱动的 authoring run
- `tmp/agentic_run/{run_id}/` 中间产物
- 3 个关键确认点：
  - `schema`
  - `contract`
  - `execution_plan`
- contract draft / review / finalize
- mechanical execution plan
- workbook generation
- validation / analysis artifact 输出
- MCP prompts for guided orchestration
- `URL Action`
- `Go-To-Sheet Action`
- `Worksheet Caption`

### 3.2 Out of Scope

- SQL / CSV intake
- live MCP runtime backend
- Tableau Server publish workflow
- browser automation smoke test
- multi-table semantic join planning
- 富文本 worksheet caption
- 大规模 CMT merge/dependency engine 复刻

## 4. 核心用户故事

### 4.1 主用户故事

作为一个用户，
我希望给 AI 一个真实的 Excel 或 Hyper 文件，并用自然语言描述想要的 dashboard，
AI 先帮我理解数据结构、形成结构化计划、在关键节点让我确认，
然后再帮我生成最终的 Tableau workbook。

### 4.2 子故事

作为一个用户，
如果会话中断或客户端关闭，我希望能够找回之前的 run 并继续。

作为一个用户，
如果 contract 或 plan 不满意，我希望可以拒绝并重做，而不是只能硬着头皮继续。

作为一个用户，
我希望最终不仅得到 `.twb`，还拿到 validation / analysis 报告，知道结果是否可靠。

## 5. 功能需求

## 5.1 Run 生命周期

系统需要支持：

- `start_authoring_run(datasource_path, output_dir, resume_if_exists=False)`
- `list_authoring_runs(output_dir="tmp/agentic_run")`
- `get_run_status(run_id)`
- `resume_authoring_run(run_id)`

每个 run 必须：

- 拥有唯一 `run_id`
- 拥有独立目录
- 拥有 `manifest.json`
- 能表达当前状态、历史 artifact 和错误信息

## 5.2 Datasource Intake

系统需要支持：

- 从 `manifest` 读取 datasource path
- 对 `Excel` 枚举所有 sheet
- 对 `Hyper` 枚举所有表
- 产出结构化 `schema_summary.json`

`schema_summary.json` 至少应包含：

- datasource metadata
- sheets 或 tables
- selected_primary_object
- fields
- field_candidates
- recommended_profile_matches
- notes

## 5.3 Contract Workflow

系统需要支持：

- `draft_authoring_contract(run_id, human_brief, rewrite=False)`
- `review_authoring_contract_for_run(run_id)`
- `finalize_authoring_contract(run_id, user_answers_json="")`
- `confirm_authoring_stage(run_id, stage, approved, notes="")`

并明确区分：

- `finalize` = 内容定稿
- `confirm` = 人类批准

## 5.4 Execution Plan

系统需要支持：

- `build_execution_plan(run_id)`

并产出一个机械可执行的 `execution_plan.json`，其中：

- `steps` 为 MCP tool 调用序列
- `post_checks` 为生成后检查
- step 工具必须来自白名单

## 5.5 Workbook Generation

系统需要支持：

- `generate_workbook_from_run(run_id, output_twb_path="")`

要求：

- 执行已确认的 execution plan
- 自动保存 workbook
- 自动跑 validation / analysis
- 在失败时写入失败态和错误详情

## 5.6 MCP Prompt 层

系统需要提供并注册：

- `guided_dashboard_authoring`
- `dashboard_brief_to_contract`
- `light_elicitation`
- `authoring_execution_plan`

prompt 的职责是：

- 引导流程
- 提醒在确认点停下
- 把自由需求收束到结构化阶段

tool 的职责是：

- 写文件
- 改状态
- 生成最终结果

## 6. 运行时产物

V1 运行时产物应写入：

```text
tmp/agentic_run/{run_id}/
```

典型文件包括：

- `manifest.json`
- `schema_summary.*.json`
- `contract_draft.*.json`
- `contract_review.*.json`
- `contract_final.*.json`
- `execution_plan.*.json`
- `approvals.json`
- `final_workbook.twb`
- `validation_report.*.json`
- `analysis_report.*.json`

## 7. 当前实现状态

下面是截至今天的真实状态。

### 7.1 已完成

#### A. Guided run 基础骨架

- 已完成 `run_id` 独立目录
- 已完成 `manifest.json`
- 已完成 `list_authoring_runs`
- 已完成 `get_run_status`
- 已完成 `resume_authoring_run`

#### B. Datasource-first intake

- 已完成 Excel schema intake
- 已完成 Hyper schema intake 接口
- 已完成 `schema_summary` 产出
- 已完成 sheet/table 枚举
- 已完成 `preferred_sheet` 支持

#### C. Contract workflow

- 已完成 contract draft
- 已完成 contract review
- 已完成 finalize
- 已完成 3 个确认阶段的状态推进
- 已完成 contract 被拒绝后可 `rewrite=True` 重起草

#### D. Execution / generation

- 已完成 `execution_plan.json` 生成
- 已完成 execution step 白名单
- 已完成 `generate_workbook_from_run`
- 已完成自动保存 workbook
- 已完成自动 validation / analysis artifact 输出
- 已完成 `workbook_generation_failed` 失败态

#### E. MCP orchestration

- 已完成 guided MCP prompts 注册
- 已完成 server instructions 指向 guided workflow
- 已完成 run-based authoring MCP tools 暴露

#### F. Authoring feature 能力

- 已完成 `URL Action`
- 已完成 `Go-To-Sheet Action`
- 已完成 `Worksheet Caption`
- 已完成 `set_excel_connection`

#### G. 文档

- 已完成根 README 更新
- 已完成 CHANGELOG 更新
- 已完成 examples README 更新
- 已完成 tests README 更新
- 已完成今天讨论的归档文档

### 7.2 部分完成

#### A. Hyper 运行环境稳定性

代码路径已经有，但本机/当前环境下 `tableauhyperapi` 可用性会影响真实 Hyper intake 测试。

也就是说：

- 功能设计和代码都在
- 但演示时最好优先走 Excel 路径
- Hyper 目前更适合作为可选增强，而不是主演示路径

#### B. MCP client 端真实体验

server 侧 prompt 与 tool 已经准备好，并且已经补上了一个基于官方 Python `mcp`
client 的真实协议演示脚本，可通过 stdio 连接 `python -m cwtwb.mcp`
跑完整条 Excel guided run。

也就是说：

- server 端功能已具备
- 协议级真实 MCP client 端到端验证已具备
- 仍然建议后续再补一份第三方 GUI MCP client 的录屏/讲解版本

#### C. Workbook generation 质量

workflow 骨架已经具备，但“生成出来的 dashboard 是否足够漂亮、足够像一个 polished demo”这件事还没有打磨到最佳状态。

也就是说：

- 能走通
- 但 demo 美观度和策略质量还有提升空间

### 7.3 未完成

以下内容当前明确还没做：

- SQL intake
- CSV intake
- live MCP / live Tableau session backend
- Tableau Server publish
- browser automation smoke test
- richer semantic modeling for multi-table planning
- standalone low-level `set_excel_connection` XML regression test
- 第三方 GUI MCP client 的完整端到端录屏/讲解记录

## 8. Task 完成情况

把今天这轮最核心的任务拆开看，完成情况如下。

| Task | 状态 |
|---|---|
| 把静态 MCP demo 改成 datasource-first guided workflow | 已完成 |
| 引入 run_id、manifest、artifact 目录 | 已完成 |
| 加入 schema / contract / execution 3 个确认点 | 已完成 |
| 支持 run 恢复与状态查询 | 已完成 |
| 让 execution plan 变成机械可执行 JSON | 已完成 |
| 增加 `workbook_generation_failed` 失败态 | 已完成 |
| 把 prompts 改为 guided orchestration | 已完成 |
| 删除旧的预制案例文件 | 已完成 |
| 增加 `URL Action` | 已完成 |
| 增加 `Go-To-Sheet Action` | 已完成 |
| 增加 `Worksheet Caption` | 已完成 |
| 把 Superstore 从 `src` 里外置成 profile | 已完成 |
| 增加 `set_excel_connection` | 已完成 |
| 用真实 MCP client 跑顺整条演示链 | 已完成（协议级真实 client 脚本已具备，GUI 录屏待补） |
| 把 demo polish 到对外展示级别 | 部分完成 |
| live MCP / publish / smoke test | 未开始 |

## 9. 测试状态

当前已经有针对这次功能的回归测试，主要覆盖：

- prompt 注册
- run lifecycle
- Excel schema intake
- Hyper schema intake（环境可用时）
- contract rewrite after rejection
- end-to-end workbook generation
- failure state handling
- 新 action 类型

已知情况：

- Excel 主链是当前最稳的演示路径
- Hyper 路径受本机 runtime 环境影响，可能 skip

## 10. 现在到底做到哪一步了

如果用一句话描述当前进度：

`现在已经完成了 V1 的 guided authoring 基础设施骨架，并且具备从真实 datasource 开始、经过人工确认、最终生成 workbook 的主链能力；还没有完成的是更高一层的演示 polish、真实 MCP client 全流程验证，以及 live/runtime 扩展。`

换句话说，当前状态不是“还在设计”，而是：

- 核心框架已落地
- 核心 task 大部分已完成
- 已进入“验证、打磨、准备对外演示”的阶段

## 11. 现在最推荐的下一步

如果目标是尽快做出能展示的成果，我建议优先级这样排：

1. 用真实 MCP client 跑一次 Excel 路径的 guided run 演示
2. 调整 contract -> execution -> dashboard 的输出质量
3. 准备一份面向 Matthew 的英文更新
4. 再考虑 publish / smoke test 等下一阶段增强

## 12. 结论

所以，对你最直接的回答是：

### 12.1 需求文档要不要写

要，而且现在写正合适。

### 12.2 现在做到哪一步

已经做到：

- Guided MCP Authoring Run V1 主链落地
- 核心 task 基本完成
- 进入演示验证和打磨阶段

### 12.3 完成 task 的情况

这轮最关键的结构性任务大部分都已经完成；未完成的主要是：

- 真实 MCP client 体验验证
- demo 质量 polish
- V2 扩展项
