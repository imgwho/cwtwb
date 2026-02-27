# Tableau 看板生成 MCP —— 新方案 v4

## 一句话定位

**输入**：TWB 模板文件 + 数据源文件 + MCP Tool 调用指令
**输出**：可直接用 Tableau Desktop 打开的 `.twb` 文件
**核心策略**：**模板驱动 + XML 注入** —— 不让 LLM 写 XML，而是通过确定性代码操作 TWB XML 树

---

## 与 v3 方案的核心区别

| 维度 | v3 方案 | v4 方案（本方案） |
|:--|:--|:--|
| **LLM 角色** | LLM 做语义决策，输出 JSON | LLM 是 MCP 调用者，直接调用 Tool |
| **XML 生成** | 完全从零生成 | 基于真实 TWB 模板，lxml 操作 XML 树 |
| **知识库** | 需要 embedding + RAG | 不需要，直接用模板 TWB 学习结构 |
| **MVP 范围** | 全链路（Server连接+生成+发布） | 聚焦三件事：计算字段、可视化、仪表板 |
| **数据源** | Tableau Server Live | 本地文件（Excel/CSV），模板自带 |
| **复杂度** | 非常高 | 可控，逐步构建 |

---

## 核心设计原则

1. **模板驱动** —— 从真实 TWB 文件中提取 XML 结构作为骨架，保证 Tableau 兼容性
2. **确定性代码** —— 所有 XML 操作由 Python lxml 完成，不依赖 LLM 生成 XML
3. **MCP Tool = 原子操作** —— 每个 Tool 做一件事，LLM 负责编排调用顺序
4. **渐进式构建** —— 从空模板开始，逐步注入 datasource → calculated field → worksheet → dashboard
5. **字段引用一致性** —— 全局 FieldRegistry 维护字段名到 TWB 内部引用名的映射

---

## 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      LLM Host（Claude / Cursor）              │
│                    通过 MCP 协议调用下列 Tools                  │
└───────────────────────────┬──────────────────────────────────┘
                            │ MCP Protocol (stdio)
┌───────────────────────────▼──────────────────────────────────┐
│                     cwtwb MCP Server                          │
│                                                               │
│  ┌────────────────────── Tool Layer ──────────────────────┐  │
│  │                                                          │  │
│  │  ── 基础工具 ──                                          │  │
│  │  create_workbook        从模板创建新工作簿                │  │
│  │  list_fields            列出数据源中所有可用字段          │  │
│  │                                                          │  │
│  │  ── 计算字段 ──                                          │  │
│  │  add_calculated_field   添加计算字段到数据源              │  │
│  │  remove_calculated_field 移除计算字段                     │  │
│  │                                                          │  │
│  │  ── 可视化 ──                                            │  │
│  │  add_worksheet          添加空白工作表                    │  │
│  │  configure_chart        配置图表类型和编码通道            │  │
│  │                                                          │  │
│  │  ── 仪表板 ──                                            │  │
│  │  add_dashboard          创建仪表板，排列工作表            │  │
│  │                                                          │  │
│  │  ── 输出 ──                                              │  │
│  │  save_workbook          保存 TWB 到指定路径               │  │
│  │                                                          │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌────────────────────── Core Layer ──────────────────────┐  │
│  │  TWBEditor        基于 lxml 的 TWB XML 编辑器            │  │
│  │  FieldRegistry    字段名 → TWB 内部引用名映射            │  │
│  │  ChartConfigs     图表类型对应的 XML 模板片段            │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## TWB XML 结构解析（基于 template.twb 逆向分析）

一个 TWB 文件是纯 XML，结构如下：

```xml
<workbook version="18.1">
  ├── <document-format-change-manifest>  <!-- 版本兼容标记，直接复制 -->
  ├── <preferences>                      <!-- UI偏好，直接复制 -->
  ├── <datasources>                      <!-- ⭐ 数据源定义 -->
  │   └── <datasource>
  │       ├── <connection class="federated">
  │       │   ├── <named-connections>     <!-- 物理连接（Excel路径等） -->
  │       │   ├── <relation>             <!-- 表/Sheet 引用 -->
  │       │   ├── <cols>                 <!-- ⭐ 字段映射（key→value） -->
  │       │   └── <metadata-records>     <!-- 字段元数据（类型、聚合） -->
  │       ├── <column>                   <!-- ⭐ 计算字段定义在这里 -->
  │       └── <object-graph>             <!-- 数据模型 -->
  │
  ├── <worksheets>                       <!-- ⭐ 工作表列表 -->
  │   └── <worksheet name="xxx">
  │       └── <table>
  │           ├── <view>
  │           │   ├── <datasource-dependencies>  <!-- ⭐ 引用的字段声明 -->
  │           │   │   ├── <column>               <!-- 字段定义 -->
  │           │   │   └── <column-instance>      <!-- 字段实例(聚合方式等) -->
  │           │   └── <aggregation>
  │           ├── <style>                <!-- 样式规则 -->
  │           ├── <panes>
  │           │   └── <pane>
  │           │       ├── <mark class="...">     <!-- ⭐ 图表类型 -->
  │           │       ├── <encodings>            <!-- ⭐ 编码通道(color/size/label) -->
  │           │       └── <style>
  │           ├── <rows>                 <!-- ⭐ 行架（维度/度量） -->
  │           └── <cols>                 <!-- ⭐ 列架（维度/度量） -->
  │
  ├── <windows>                          <!-- 窗口布局，直接复制 -->
  └── <thumbnails>                       <!-- 缩略图（base64），可忽略 -->
```

### 关键发现

1. **字段引用格式**：`[datasource_name].[derivation:FieldName:type_suffix]`
   - 例：`[federated.xxx].[sum:Sales (Orders):qk]`
   - 其中 `derivation` = `None/Sum/Year/...`, `type_suffix` = `nk`(nominal key) / `qk`(quantitative key)

2. **计算字段**：作为 `<column>` 添加到 `<datasource>` 下，带 `<calculation>` 子元素

3. **图表类型**由 `<mark class="...">` 控制：
   - `Automatic` = 自动
   - `Pie` = 饼图
   - `Bar` = 柱状图
   - `Line` = 折线图
   - `Area` = 面积图
   - `Circle` = 圆形

4. **编码通道**在 `<encodings>` 中：
   - `<color column="...">` = 颜色编码
   - `<wedge-size column="...">` = 饼图扇区大小
   - `<size column="...">` = 大小编码
   - `<text column="...">` = 标签编码

5. **饼图 vs 柱状图的核心差异**：
   - 柱状图：字段放在 `<rows>` 和 `<cols>` 中
   - 饼图：字段放在 `<encodings>` 的 `<color>` 和 `<wedge-size>` 中，`<rows>` 和 `<cols>` 为空

---

## MCP Tool 详细设计

### Tool 1: `create_workbook`

**用途**：基于模板 TWB 创建新工作簿，解析数据源字段

```python
@server.tool()
def create_workbook(
    template_path: str,       # TWB 模板路径
    workbook_name: str        # 新工作簿名称
) -> str:
    """
    1. 读取模板 TWB XML
    2. 解析 <datasource> 中的字段信息，初始化 FieldRegistry
    3. 清空 <worksheets>（移除模板中的示例 worksheet）
    4. 返回字段列表摘要
    """
```

**返回示例**：
```
已创建工作簿「销售分析」
数据源：Sample _ Superstore 数据提取
可用字段（21个）：
  维度：Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID,
        Customer Name, Segment, Country/Region, City, State/Province,
        Postal Code, Region, Product ID, Category, Sub-Category, Product Name
  度量：Sales, Quantity, Discount, Profit
```

---

### Tool 2: `list_fields`

**用途**：列出当前数据源的所有字段（含计算字段）

```python
@server.tool()
def list_fields() -> str:
    """
    返回 FieldRegistry 中所有字段，标注类型和来源（原始/计算）
    """
```

---

### Tool 3: `add_calculated_field`

**用途**：向数据源添加计算字段

```python
@server.tool()
def add_calculated_field(
    field_name: str,          # 字段名，如 "利润率"
    formula: str,             # Tableau 计算表达式
    datatype: str = "real"    # 数据类型：real/string/integer/date/boolean
) -> str:
    """
    在 <datasource> 下添加：
    <column caption='利润率'
            datatype='real'
            name='[Calculation_利润率]'
            role='measure'
            type='quantitative'>
      <calculation class='tableau' formula='SUM([Profit (Orders)])/SUM([Sales (Orders)])' />
    </column>
    
    同时注册到 FieldRegistry
    """
```

**实现要点**：
- `name` 属性用 `[Calculation_{field_name}]` 格式，避免与原始字段冲突
- `formula` 中的字段名需要通过 FieldRegistry 转换为 TWB 内部引用名
  - 用户输入 `SUM([Profit])` → 转换为 `SUM([Profit (Orders)])`
- `role` 根据 `datatype` 自动判断：`real/integer` → `measure`，其他 → `dimension`
- `type` 同理：`real/integer` → `quantitative`，其他 → `nominal`

---

### Tool 4: `add_worksheet`

**用途**：添加一个新的空白工作表

```python
@server.tool()
def add_worksheet(
    worksheet_name: str       # 工作表名称
) -> str:
    """
    在 <worksheets> 下添加一个带基本结构的空 worksheet
    同时在 <windows> 中注册窗口配置
    """
```

---

### Tool 5: `configure_chart` ⭐ 核心

**用途**：配置工作表的图表类型和字段映射

```python
@server.tool()
def configure_chart(
    worksheet_name: str,      # 目标工作表
    mark_type: str,           # 图表标记类型：Bar/Line/Pie/Area/Circle/Automatic
    columns: list[str] = [],  # 列架字段，如 ["SUM(Sales)"]
    rows: list[str] = [],     # 行架字段，如 ["Category"]
    color: str = None,        # 颜色编码字段
    size: str = None,         # 大小编码字段
    label: str = None,        # 标签编码字段
    detail: str = None,       # 详细信息字段
    tooltip: str = None       # 工具提示字段
) -> str:
    """
    配置要素：
    1. <mark class="Bar/Line/Pie/..."> 设置图表类型
    2. <rows> / <cols> 设置行列架
    3. <encodings> 设置编码通道
    4. <datasource-dependencies> 声明引用的字段
    """
```

**字段表达式语法设计**（用户输入 → TWB 内部表示）：

| 用户输入 | 解析结果 | TWB column-instance |
|:--|:--|:--|
| `SUM(Sales)` | field=Sales, derivation=Sum | `[sum:Sales (Orders):qk]` |
| `Category` | field=Category, derivation=None | `[none:Category (Orders):nk]` |
| `YEAR(Order Date)` | field=Order Date, derivation=Year | `[yr:Order Date (Orders):ok]` |
| `MONTH(Order Date)` | field=Order Date, derivation=Month | `[mn:Order Date (Orders):ok]` |
| `COUNT(Order ID)` | field=Order ID, derivation=Count | `[cnt:Order ID (Orders):qk]` |
| `AVG(Discount)` | field=Discount, derivation=Avg | `[avg:Discount (Orders):qk]` |

---

### Tool 6: `add_dashboard`

**用途**：创建仪表板，组合多个工作表

```python
@server.tool()
def add_dashboard(
    dashboard_name: str,          # 仪表板名称
    width: int = 1200,            # 画布宽度
    height: int = 800,            # 画布高度
    layout: str = "vertical",     # 布局：vertical/horizontal/grid-2x2
    worksheet_names: list[str] = []  # 包含的工作表
) -> str:
    """
    在 TWB 中创建 dashboard：
    1. 在 <dashboards> 下添加 <dashboard> 节点
    2. 通过 <zones> 排列工作表
    3. Zone ID 由代码自增管理，杜绝冲突
    """
```

**Dashboard XML 结构**（从 Tableau Desktop 实际输出逆向）：
```xml
<dashboards>
  <dashboard name='仪表板 1'>
    <style />
    <size maxheight='800' maxwidth='1200' minheight='800' minwidth='1200' />
    <zones>
      <zone h='100000' id='2' type-v2='layout-basic' w='100000' x='0' y='0'>
        <zone h='98000' id='3' name='工作表1' w='49000' x='800' y='800'
              type-v2='viz' />
        <zone h='98000' id='4' name='工作表2' w='49000' x='50200' y='800'
              type-v2='viz' />
      </zone>
    </zones>
  </dashboard>
</dashboards>
```

---

### Tool 7: `save_workbook`

**用途**：将当前工作簿保存为 TWB 文件

```python
@server.tool()
def save_workbook(
    output_path: str          # 输出路径
) -> str:
    """
    使用 lxml 序列化 XML 树并写入文件
    """
```

---

## 项目目录结构

```
cwtwb/
├── pyproject.toml              # 项目配置
├── README.md
│
├── src/
│   └── cwtwb/
│       ├── __init__.py
│       ├── server.py           # MCP Server 主入口
│       ├── twb_editor.py       # TWB XML 编辑核心类
│       ├── field_registry.py   # 字段注册与引用名映射
│       └── chart_configs.py    # 图表类型的 XML 模板配置
│
├── templates/                  # TWB 模板文件
│   └── superstore_base.twb     # 基于 template.twb 清理后的基础模板
│
├── vizs/                       # 可视化参考 & 数据
│   ├── Sample - Superstore.xls
│   └── pie_chart.twb
│
├── output/                     # 生成的 TWB 输出目录
│
└── tests/
    ├── test_twb_editor.py
    ├── test_field_registry.py
    └── test_chart_configs.py
```

---

## 核心类设计

### TWBEditor

```python
class TWBEditor:
    """基于 lxml 的 TWB XML 编辑器"""
    
    def __init__(self, template_path: str):
        self.tree = etree.parse(template_path)
        self.root = self.tree.getroot()
        self.field_registry = FieldRegistry()
        self._zone_id_counter = 10  # zone id 自增计数器
        self._init_fields()         # 解析模板中的字段
    
    def _init_fields(self):
        """从 <datasource> 解析所有字段，注册到 FieldRegistry"""
        
    def add_calculated_field(self, name, formula, datatype):
        """在 <datasource> 下添加 <column> + <calculation>"""
        
    def add_worksheet(self, name):
        """在 <worksheets> 下添加空 worksheet 骨架"""
        
    def configure_chart(self, ws_name, mark_type, columns, rows, **encodings):
        """配置 worksheet 的图表类型和字段绑定"""
        
    def add_dashboard(self, name, width, height, layout, ws_names):
        """在 <dashboards> 下添加 dashboard"""
        
    def save(self, output_path):
        """序列化并保存 TWB 文件"""
```

### FieldRegistry

```python
class FieldRegistry:
    """字段名 → TWB 内部引用名的映射"""
    
    def __init__(self, datasource_name: str):
        self.datasource_name = datasource_name
        self.fields = {}  # {display_name: FieldInfo}
        
    def register(self, display_name, local_name, datatype, role, field_type):
        """注册一个字段"""
        
    def resolve(self, user_expr: str) -> str:
        """
        将用户表达式解析为 TWB 内部引用
        "SUM(Sales)" → "[federated.xxx].[sum:Sales (Orders):qk]"
        """
        
    def get_column_instance(self, user_expr: str) -> dict:
        """
        解析表达式，返回 column-instance 属性
        {column, derivation, name, pivot, type}
        """
```

---

## 字段表达式解析器

用户在 `configure_chart` 中输入的字段表达式需要解析为 TWB XML 格式。

### 解析规则

```
输入格式：AGGREGATION(FieldName) 或 FieldName
     
解析流程：
1. 正则匹配 ^(SUM|AVG|COUNT|MIN|MAX|YEAR|MONTH|DAY|QUARTER)?\\(?(.+?)\\)?$
2. aggregation = 匹配的聚合函数，默认 None
3. field_name = 括号内的字段名
4. 从 FieldRegistry 查找 field_name 对应的 local_name
5. 生成 derivation 缩写：Sum→sum, None→none, Year→yr, Month→mn ...
6. 生成 type_suffix：measure→qk, dimension→nk, date+聚合→ok
7. 拼接为 [derivation:local_name:type_suffix]
```

### 聚合函数到 TWB derivation 的映射

| 聚合函数 | TWB derivation | type_suffix |
|:--|:--|:--|
| (无) | `None` | `nk` |
| `SUM` | `Sum` | `qk` |
| `AVG` | `Avg` | `qk` |
| `COUNT` | `Count` | `qk` |
| `COUNTD` | `CountD` | `qk` |
| `MIN` | `Min` | `qk` |
| `MAX` | `Max` | `qk` |
| `YEAR` | `Year` | `ok` |
| `MONTH` | `Month` | `ok` |
| `QUARTER` | `Quarter` | `ok` |
| `DAY` | `Day` | `ok` |

---

## 典型使用场景（MCP 调用流程）

### 场景：创建一个销售分析仪表板

LLM 会依次调用以下 MCP Tools：

```
1. create_workbook(
     template_path="templates/superstore_base.twb",
     workbook_name="销售分析"
   )

2. add_calculated_field(
     field_name="利润率",
     formula="SUM([Profit])/SUM([Sales])",
     datatype="real"
   )

3. add_worksheet(worksheet_name="按类别销售额")

4. configure_chart(
     worksheet_name="按类别销售额",
     mark_type="Bar",
     rows=["Category"],
     columns=["SUM(Sales)"]
   )

5. add_worksheet(worksheet_name="类别占比")

6. configure_chart(
     worksheet_name="类别占比",
     mark_type="Pie",
     color="Segment",
     size="SUM(Sales)"
   )

7. add_dashboard(
     dashboard_name="销售概览",
     layout="horizontal",
     worksheet_names=["按类别销售额", "类别占比"]
   )

8. save_workbook(output_path="output/销售分析.twb")
```

---

## 实施路线图（3 个阶段）

### 阶段 1：基础框架（核心可用）
- [ ] 项目初始化（pyproject.toml, MCP Server 骨架）
- [ ] `TWBEditor` 类：读取模板、解析字段、保存文件
- [ ] `FieldRegistry` 类：字段注册、名称解析
- [ ] `create_workbook` Tool
- [ ] `list_fields` Tool
- [ ] `save_workbook` Tool
- [ ] 单元测试

### 阶段 2：计算字段与可视化
- [ ] `add_calculated_field` Tool（含公式中字段名转换）
- [ ] `remove_calculated_field` Tool
- [ ] `add_worksheet` Tool
- [ ] `configure_chart` Tool（支持 Bar/Line/Pie/Area）
- [ ] 字段表达式解析器
- [ ] 集成测试：生成 TWB，Tableau Desktop 打开验证

### 阶段 3：仪表板
- [ ] `add_dashboard` Tool（支持 vertical/horizontal/grid 布局）
- [ ] Zone ID 管理器
- [ ] 端到端测试：从创建到保存完整仪表板

---

## 验证方案

### 自动化测试
```bash
pytest tests/ -v
```
- `test_field_registry.py`：字段解析、名称映射、表达式转换
- `test_twb_editor.py`：XML 操作、计算字段注入、worksheet 添加
- `test_chart_configs.py`：各图表类型的 XML 模板正确性

### 手动验证
1. 使用 MCP Server 生成 TWB 文件
2. 用 Tableau Desktop 打开，验证：
   - 数据源连接正常
   - 计算字段正确计算
   - 图表显示正常
   - 仪表板布局正确

---

## 核心风险与应对

| 风险 | 影响 | 应对 |
|:--|:--|:--|
| 字段内部引用名格式错误 | TWB 打开报错 | 从模板中逆向所有引用名模式，严格按模式生成 |
| Zone ID 冲突 | Dashboard 布局错乱 | 代码层自增管理，不经过 LLM |
| 计算字段公式语法不兼容 | 字段计算失败 | 只做字段名替换，不验证公式逻辑，交给 Tableau 校验 |
| XML namespace/编码问题 | TWB 无法解析 | 使用 lxml 的 `tostring(xml_declaration=True, encoding='utf-8')` |
| 模板 TWB 版本兼容 | 新版 Tableau 结构变化 | 锁定 TWB version='18.1'，与 Tableau 2025.3 对齐 |
