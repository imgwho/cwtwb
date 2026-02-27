<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Tableau 看板生成 MCP —— 完整方案 v3

## 一句话定位

**输入**：Tableau Server 数据源连接 + 自然语言业务需求
**输出**：可直接打开 / 发布的 `.twb` 文件
**核心能力**：可持续进化——随时注入真实 TWB 案例和计算函数文档来提升生成质量

***

## 核心设计原则

1. **LLM 只做语义决策，不写 XML** —— 输出强类型 JSON，代码负责 XML 组装
2. **知识库驱动生成** —— 真实 TWB 案例库 + 计算函数文档库，是系统持续进化的燃料
3. **可视化优先** —— MVP 阶段重点打通图表生成和 Dashboard 组装，计算字段轻量处理
4. **分层生成，逐层验证** —— 每层有独立验证出口和错误回退
5. **字段引用唯一来源** —— 全局 `FieldRegistry`，杜绝字段名不一致
6. **有状态迭代** —— 保存中间决策 JSON，支持对话式增量修改和版本回滚
7. **错误是一等公民** —— 所有 Tool 返回结构化结果，错误可被 LLM 消费并自动修正

***

## 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      用户 / LLM Host                          │
│                 (Claude / Cursor / GPT)                       │
└───────────────────────────┬──────────────────────────────────┘
                            │ MCP Protocol
┌───────────────────────────▼──────────────────────────────────┐
│                        MCP Server                             │
│                                                               │
│  ┌────────────────────── Tool Layer ──────────────────────┐  │
│  │  profile_datasource      generate_worksheet            │  │
│  │  generate_dashboard      suggest_calculations          │  │
│  │  validate_twb            publish_to_server             │  │
│  │  list_versions           rollback_version              │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────── Core Layer ──────────────────────┐  │
│  │  FieldRegistry    XMLAssembler    LayoutEngine          │  │
│  │  ErrorHandler     VersionStore    PromptBuilder         │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌──────────────── Knowledge Layer ───────────────────────┐  │
│  │  TWBExampleStore         CalcFunctionDocs              │  │
│  │  （真实案例库）            （计算函数文档库）             │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌─────────────── Infrastructure Layer ───────────────────┐  │
│  │  Tableau REST API    lxml validator    tabcmd           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```


***

## 项目目录结构

```
tableau-mcp/
├── .env
├── main.py
│
├── tools/                          # MCP Tool 层
│   ├── profile_datasource.py
│   ├── generate_worksheet.py
│   ├── generate_dashboard.py
│   ├── suggest_calculations.py
│   ├── validate_twb.py
│   ├── publish_to_server.py
│   └── version_tools.py
│
├── core/                           # 核心逻辑层
│   ├── field_registry.py
│   ├── error_handler.py
│   ├── version_store.py
│   ├── prompt_builder.py
│   ├── layout_engine.py
│   └── xml_assembler/
│       ├── worksheet_builder.py
│       ├── dashboard_builder.py
│       ├── calculation_builder.py
│       └── charts/
│           ├── line.py
│           ├── bar.py
│           ├── scatter.py
│           ├── map.py
│           └── text_table.py
│
├── knowledge/                      # 知识库层（可持续扩充）
│   ├── twb_examples/               # 真实 TWB 案例库
│   │   ├── index.json              # 案例索引（标签、场景、图表类型）
│   │   ├── sales_trend/
│   │   │   ├── workbook.twb        # 原始 TWB 文件
│   │   │   └── meta.json           # 案例描述和标签
│   │   ├── region_comparison/
│   │   └── kpi_dashboard/
│   └── calc_functions/             # 计算函数文档库
│       ├── all_functions.md        # 你提供的完整函数文档
│       ├── parsed_functions.json   # 解析后的结构化版本（自动生成）
│       └── recipes/                # 业务配方（基于函数文档提炼）
│           ├── financial.json
│           ├── time_intelligence.json
│           └── statistical.json
│
├── versions/                       # 版本存储
│   └── {session_id}/
│       ├── v1/
│       │   ├── decision.json
│       │   └── workbook.twb
│       └── v2/
│           ├── decision.json
│           └── workbook.twb
│
├── output/                         # 生成文件输出目录
└── tests/
```


***

## 知识库层详解（核心创新点）

这是整个系统"可持续进化"的关键，分两个子库。

### 子库 A：TWB 案例库（twb_examples/）

你可以随时往里面丢真实的 TWB 文件，系统自动学习并在生成时参考。

**案例 meta.json 结构：**

```json
{
  "id": "sales_trend_001",
  "title": "月度销售趋势看板",
  "description": "按月展示销售额趋势，支持地区筛选",
  "tags": ["趋势", "时间序列", "折线图", "筛选器"],
  "chart_types": ["line", "bar"],
  "has_dashboard": true,
  "has_filter_action": true,
  "has_calculated_fields": ["利润率", "同比增长"],
  "datasource_type": "live",
  "added_at": "2026-02-27"
}
```

**案例索引 index.json（自动维护）：**

```json
{
  "examples": [
    {
      "id": "sales_trend_001",
      "tags": ["趋势", "折线图"],
      "chart_types": ["line"],
      "embedding_vector": [...]   // 用于语义检索
    }
  ]
}
```

**案例库如何被使用（RAG 流程）：**

```
用户需求："做一个销售趋势看板"
    ↓
TWBExampleStore.search(query, top_k=3)
    ↓ 语义检索最相关的3个案例
提取这3个案例的 worksheet XML 片段作为 few-shot
    ↓
注入 PromptBuilder → 喂给 LLM
    ↓
LLM 基于真实案例理解 XML 模式，输出更准确的 JSON 决策
```

**TWBExampleStore 核心方法：**

```python
class TWBExampleStore:
    def add_example(self, twb_path: str, meta: dict):
        """
        添加新案例：
        1. 解析 TWB XML，提取 worksheet/dashboard/calculation 片段
        2. 生成 embedding，写入 index.json
        3. 按图表类型分类存储 XML 片段
        """

    def search(self, query: str, top_k: int = 3,
               filter_chart_type: str = None) -> list[Example]:
        """语义检索最相关的案例，返回 XML 片段 + meta"""

    def get_xml_snippet(self, example_id: str,
                        snippet_type: str) -> str:
        """取出特定类型的 XML 片段（worksheet/dashboard/calculation）"""
```


***

### 子库 B：计算函数文档库（calc_functions/）

你提供的 `all_functions.md` 是原始输入，系统自动解析成结构化 JSON 供查询。

**解析后的 parsed_functions.json 结构：**

```json
{
  "functions": [
    {
      "name": "ZN",
      "category": "数字",
      "syntax": "ZN(expression)",
      "description": "如果表达式不为 null 则返回该表达式，否则返回零",
      "example": "ZN(SUM([利润]))",
      "use_cases": ["处理空值", "安全除法分母"]
    },
    {
      "name": "FIXED",
      "category": "LOD",
      "syntax": "{FIXED [dim] : AGG([measure])}",
      "description": "不受视图筛选器影响的固定粒度聚合",
      "example": "{FIXED [客户ID] : MAX([订单日期])}",
      "use_cases": ["客户最后购买日期", "地区基准值"]
    }
  ]
}
```

**函数文档如何被使用：**

```
用户说："帮我计算利润率"
    ↓
suggest_calculations 先查 recipes/（精确配方）
    ↓ 没有匹配
CalcFunctionDocs.search("利润率计算") → 检索相关函数（ZN、SUM、除法）
    ↓
把相关函数的语法和示例注入 Prompt
    ↓
LLM 基于正确的函数语法生成计算表达式，而不是凭记忆瞎写
```


***

## 生成流程详解

### 第一步：数据理解（profile_datasource）

```python
@mcp.tool()
def profile_datasource(datasource_name: str) -> ToolResult:
    """
    1. 连接 Tableau Server（从环境变量读取凭证）
    2. 通过 Metadata API 拉取字段列表
    3. 识别数据源类型（Live / Extract）
    4. 初始化 FieldRegistry
    """
```

**输出给 LLM 的字段摘要：**

```
数据源：超市销售（Live 连接）
维度字段（15个）：
  - 订单日期 [date] 基数:1460
  - 地区 [string] 基数:4 枚举值:["东","西","南","中"]
  - 类别 [string] 基数:3 枚举值:["家具","办公用品","技术"]
  ...
度量字段（8个）：
  - 销售额 [float] 范围:0.44~22638
  - 利润 [float] 范围:-6599~8399
  ...
```


***

### 第二步：可视化生成（generate_worksheet）⭐️ 核心

这是 MVP 阶段最重要的 Tool，详细说明生成流程：

```
用户："做一个月度销售趋势折线图，按地区分色"
    ↓
① PromptBuilder 构造 Prompt
   注入：field_registry + 相关 TWB 案例 XML 片段 + JSON Schema 约束
    ↓
② LLM 输出决策 JSON
   {
     "chart_type": "line",
     "title": "月度销售趋势",
     "columns": [{"field": "订单日期", "granularity": "MONTH"}],
     "rows": [{"field": "销售额", "aggregation": "SUM"}],
     "color": {"field": "地区"},
     "filters": []
   }
    ↓
③ FieldRegistry 校验所有字段名
   → 全部合法，继续
   → 有不合法字段 → ErrorHandler 生成纠错建议 → 返回 LLM 重试
    ↓
④ XMLAssembler 调用 charts/line.py 生成 worksheet XML
   → 从 TWBExampleStore 取真实折线图 XML 作为结构参考
   → 填充字段名、聚合方式、颜色编码
    ↓
⑤ validate_twb 校验 XML 片段合法性
    ↓
⑥ VersionStore 保存 decision.json + 当前 TWB 快照
```

**Prompt 结构（关键设计）：**

```
[System]
你是 Tableau 图表配置专家。严格按 JSON Schema 输出，不要输出 XML。

[可用字段]
{field_registry.to_prompt_context()}

[参考案例XML片段]（从 TWBExampleStore 检索到的真实案例）
{example_xml_snippet}

[输出 JSON Schema]
{worksheet_json_schema}

[Few-shot 示例]
需求：月度销售趋势
输出：{few_shot_example}

[用户需求]
{user_request}

[增量修改基础]（如果是修改操作）
{previous_decision_json}
```


***

### 第三步：轻量计算字段（suggest_calculations）

MVP 阶段的策略：**优先匹配配方库，配方库驱动函数文档，LLM 最后兜底**。

```
用户需求
    ↓
① 精确匹配 recipes/（配方库）→ 命中直接用
    ↓ 未命中
② CalcFunctionDocs.search() 检索相关函数
    ↓
③ 把函数语法注入 Prompt，LLM 生成表达式
    ↓
④ 语法基础校验（括号匹配、函数名合法性）
    ↓ 失败
⑤ ErrorHandler → 结构化错误 → LLM 自动修正（最多3次）
    ↓
⑥ 注册进 FieldRegistry，可在后续图表中直接引用
```


***

### 第四步：Dashboard 组装（generate_dashboard）

```python
@mcp.tool()
def generate_dashboard(
    layout_mode: str,       # "2col" | "grid-2x2" | "top-kpi-bottom-charts"
    worksheet_names: list,
    interactions: list,     # Filter Action / Highlight Action
    session_id: str
) -> ToolResult:
```

**布局预设（LayoutEngine）：**

```
2col（左大右小）:          grid-2x2:           top-kpi-bottom-charts:
┌────────────┬──────┐     ┌──────┬──────┐     ┌──────────────────┐
│            │      │     │      │      │     │   KPI 数字卡片    │
│            │      │     ├──────┼──────┤     ├────────┬─────────┤
│            │      │     │      │      │     │        │         │
└────────────┴──────┘     └──────┴──────┘     └────────┴─────────┘
```

**交互联动注册（最容易出错的地方，代码层统一处理）：**

```python
def register_filter_action(source: str, target: str, field: str, xml_tree):
    """
    同时修改两处 XML，保证一致性：
    1. <actions> 节点写 filter-action
    2. 确认 source worksheet 的对应字段存在
    原子操作：两处都成功才提交，任意失败则回滚
    """
```


***

## 错误处理设计

### 统一返回结构

```python
@dataclass
class ToolResult:
    success: bool
    data: dict | None
    error: ErrorDetail | None

@dataclass
class ErrorDetail:
    code: ErrorCode
    message: str        # 人类可读
    context: dict       # LLM 修正所需上下文
    suggestion: str     # 建议修正方向
    auto_retry: bool    # 是否适合 LLM 自动重试
```


### 错误类型与处理策略

| 错误类型 | 处理策略 | LLM 自动重试 |
| :-- | :-- | :-- |
| `FIELD_NOT_FOUND` | 返回相似字段名 top3 | ✅ |
| `FIELD_TYPE_MISMATCH` | 返回正确类型说明 | ✅ |
| `CALC_SYNTAX_ERROR` | 返回出错位置+相关函数文档 | ✅ |
| `XML_VALIDATION_FAILED` | 返回 lxml 错误详情 | ✅ |
| `DUPLICATE_ZONE_ID` | 代码层自动修复 | 不需要 |
| `SERVER_CONNECTION_FAILED` | 返回用户，检查环境变量 | ❌ |
| `PUBLISH_FAILED` | 返回用户，附带原因 | ❌ |


***

## 版本管理设计

### 版本存储结构

```
versions/
└── sess_abc123/
    ├── v1/
    │   ├── decision.json     # LLM 决策 JSON（可被增量修改）
    │   ├── workbook.twb      # 完整 TWB 文件快照
    │   └── meta.json         # 版本摘要
    ├── v2/
    └── v3/
```


### 版本 meta.json

```json
{
  "version": 3,
  "timestamp": "2026-02-27T11:20:00Z",
  "change_type": "modify",       // "create" | "modify" | "rollback"
  "change_summary": "销售趋势图从折线图改为柱状图",
  "changed_worksheets": ["月度销售趋势"],
  "worksheet_count": 3,
  "has_dashboard": true
}
```


### 增量修改流程

```
用户："把折线图改成柱状图"
    ↓
VersionStore.get_latest(session_id) → 取出上一版 decision.json
    ↓
LLM 收到旧 decision.json + 用户修改指令
    ↓ 只修改 chart_type 字段
XMLAssembler 只重新生成该 worksheet XML
    ↓
Dashboard XML 里对应的 zone 引用自动更新
    ↓
VersionStore.save() → 新版本
```


***

## 环境变量设计

```bash
# .env

# Tableau Server
TABLEAU_SERVER_URL=https://your-tableau-server.com
TABLEAU_SITE_ID=your-site-id
TABLEAU_PAT_NAME=your-token-name
TABLEAU_PAT_SECRET=your-token-secret

# 本地路径
TWB_OUTPUT_DIR=./output
VERSION_STORE_DIR=./versions
TABLEAU_DESKTOP_PATH=/Applications/Tableau Desktop.app

# 知识库
EXAMPLES_DIR=./knowledge/twb_examples
CALC_DOCS_PATH=./knowledge/calc_functions/all_functions.md

# 生成行为
MAX_LLM_RETRY=3               # 错误自动重试最大次数
DEFAULT_CANVAS_WIDTH=1200
DEFAULT_CANVAS_HEIGHT=800
```


***

## 调试工作流

```
生成 TWB
    ↓
validate_twb（程序校验，< 1s）
    ↓ 通过
tabcmd publish → Tableau Server
    ↓
浏览器刷新查看效果（~3-5s）
    ↓ 需要调整
"把XX改成YY"（增量修改，基于上一版 decision.json）
    ↓
重新生成 → 发布 → 浏览器刷新
```


***

## MVP 实施路线图

```
Week 1：基础设施 + 知识库框架
  ├── 环境变量加载 + Tableau Server 连接验证
  ├── FieldRegistry 实现 + 单元测试
  ├── VersionStore 实现 + 单元测试
  ├── TWBExampleStore 框架：add_example + 手动索引（先不做 embedding）
  └── CalcFunctionDocs：解析 all_functions.md → parsed_functions.json

Week 2：数据理解 + 可视化核心
  ├── profile_datasource tool
  ├── PromptBuilder 框架
  ├── XMLAssembler：折线图 + 柱状图
  └── generate_worksheet tool（先不做案例检索，用静态 few-shot）

Week 3：Dashboard + 交互
  ├── LayoutEngine（2col + grid-2x2）
  ├── Filter Action 注册
  ├── generate_dashboard tool
  └── validate_twb tool

Week 4：知识库进化 + 发布
  ├── TWBExampleStore 接入语义检索（embedding）
  ├── generate_worksheet 接入案例检索
  ├── publish_to_server tool
  └── 版本管理 tools

Week 5：闭环测试 + 完善
  ├── 端到端集成测试（从需求到发布）
  ├── 错误重试机制完整验证
  ├── 补充更多图表类型（scatter / map）
  └── 补充更多布局预设
```


***

## 核心风险提前预警

| 风险 | 影响 | 应对 |
| :-- | :-- | :-- |
| 字段名大小写/空格不一致 | TWB 打开报错 | FieldRegistry 严格校验，fuzzy_match 纠错 |
| LOD 表达式逻辑复杂 | LLM 生成错误率高 | 专门维护 LOD 配方，不让 LLM 自由生成 |
| Dashboard zone ID 冲突 | 看板布局错乱 | 代码层统一管理 ID 自增，不经过 LLM |
| 数据源内部引用名称 | 连接失败 | profile_datasource 阶段拿真实内部名存入 FieldRegistry |
| TWB 案例质量参差不齐 | few-shot 引入噪声 | meta.json 打标签，低质量案例不参与检索 |

