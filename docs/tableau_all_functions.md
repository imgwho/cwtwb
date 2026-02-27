Title: 所有函数（按字母顺序）

URL Source: https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm

Published Time: Thu, 26 Feb 2026 23:40:26 GMT

Markdown Content:
[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)本参考中的 Tableau 函数按字母顺序进行组织。单击某个字母可跳转到列表中的该位置。您也可以使用 Ctrl+F（在 Mac 上为 Command-F）打开一个搜索框，用于查找特定函数。

[A](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#A)[B](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#B)[C](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#C)[D](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#D)[E](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#E)[F](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#F)[G](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#G)[H](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#H)[I](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#I)[J](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#J)[K](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#K)[L](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#L)[M](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#M)[N](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#N)[O](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#O)[P](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#P)[Q](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#Q)[R](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#R)[S](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#S)[T](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#T)[U](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#U)[V](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#V)[W](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#W)[X](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#X)[Y](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#Y)[Z](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#Z)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)A
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ABS

语法`ABS(number)`
输出 数字（正数）
定义 返回给定 `<number>` 的绝对值。
示例 ABS(-7) = 7

ABS([Budget Variance])
第二个示例返回“Budget Variance”（预算差异）字段中包含的所有数字的绝对值。
说明 另请参见 `SIGN`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ACOS

语法`ACOS(number)`
输出 数字（以弧度表示的角度）
定义 返回给定 `<number>` 的反余弦（角度）。
示例 ACOS(-1) = 3.14159265358979
说明 反函数 `COS` 以弧度为单位的角度作为参数，并返回余弦值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)AND

语法`<expr1> AND <expr2>`
定义 对两个表达式执行逻辑合取运算。（如果两边都为 true，则逻辑测试返回 true。）
输出 布尔值
示例 IF [Season] = "Spring" AND "[Season] = "Fall" 

THEN "It's the apocalypse and footwear doesn't matter" 

END
_“如果（Season = Spring）和（Season = Fall）同时为 true，则返回“It's the apocalypse and footwear doesn't matter。”_
说明 通常与 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [IIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IIF) 一起使用。另请参见 [NOT](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#NOT) 和 [或者](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#OR)。

如果两个表达式都为 `TRUE`（即不为 `FALSE` 或 `NULL`），则结果为 `TRUE`。如果任一表达式为 `NULL`，则结果为 `NULL`。在所有其他情况下，结果都为 `FALSE`。

如果所创建的计算中的 `AND` 比较结果显示在工作表上，则 Tableau 显示 `TRUE` 和 `FALSE`。如果要更改此情况，请使用设置格式对话框中的“设置格式”区域。

**注意**：`AND` 运算符使用 _短路计算_。这表示如果第一个表达式计算为 `FALSE`，则根本不会计算第二个表达式。如果第二个表达式在第一个表达式为 `FALSE` 时产生错误，则这可能十分有用，因为在这种情况下从不计算第二个表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)AREA

语法`AREA(Spatial Polygon, 'units')`
输出 数字
定义 返回 `<spatial polygon>` 的总表面积。
示例 AREA([Geometry], 'feet')
说明 支持的单位名称（计算时必须用引号括起来，例如`'miles'`）：

*   _米_：meters、metres、m
*   _公里_：kilometers、kilometres、km
*   _英里_：miles、mi
*   _英尺_：feet、ft

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ASCII

语法`ASCII(string)`
输出 数字
定义 返回 `<string>` 的第一个字符的 ASCII 码。
示例 ASCII('A') = 65
说明 这是 `CHAR` 函数的反函数。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ASIN

语法`ASIN(number)`
输出 数字（以弧度表示的角度）
定义 返回给定 `<number>` 的反正弦（角度）。
示例 ASIN(1) = 1.5707963267949
说明 反函数 `SIN` 以弧度为单位的角度作为参数，并返回正弦值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ATAN

语法`ATAN(number)`
输出 数字（以弧度表示的角度）
定义 返回给定 `<number>` 的反正切（角度）。
示例 ATAN(180) = 1.5652408283942
说明 反函数 `TAN` 以弧度为单位的角度作为参数，并返回正切值。

另请参见 `ATAN2` 和 `COT`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ATAN2

语法`ATAN2(y number, x number)`
输出 数字（以弧度表示的角度）
定义 返回两个数字（`<y number>` 和 `<x number>`）之间的反正切（角度）。结果以弧度表示。
示例 ATAN2(2, 1) = 1.10714871779409
说明 另请参见 `ATAN`、`TAN` 和 `COT`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ATTR

语法`ATTR(expression)`
定义 如果它的所有行都有一个值，则返回 `<expression>` 的值。否则返回星号。会忽略 Null 值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)AVG

语法`AVG(expression)`
定义 返回 `<expression>` 中所有值的平均值。会忽略 Null 值。
说明`AVG` 只能用于数字字段。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)B
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)BUFFER

语法`BUFFER(Spatial Point, distance, 'units')`
输出 几何图形
定义 返回以 `<spatial point>` 为中心的多边形形状，半径由 `<distance>` 和 `<unit>` 值确定。
示例 BUFFER([Spatial Point Geometry], 25, 'mi')BUFFER(MAKEPOINT(47.59, -122.32), 3, 'km')
说明 支持的单位名称（计算时必须用引号括起来，例如`'miles'`）：

*   _米_：meters、metres、m
*   _公里_：kilometers、kilometres、km
*   _英里_：miles、mi
*   _英尺_：feet、ft

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)C
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)CASE

语法
```
CASE <expression> 
							WHEN <value1> THEN <then1> 
							WHEN <value2> THEN <then2> 
							...
						[ELSE <default>]END
```


输出 取决于 `<then>` 值的数据类型。
定义 对 `expression` 进行求值，并将其与指定选项（`<value1>`、`<value2>` 等）进行比较。遇到一个与表达式匹配的 `value` 时，CASE 返回相应的 `return`。如果未找到匹配值，则返回（可选）默认值。如果不存在默认值并且没有任何值匹配，则会返回 Null。
示例`CASE [Season] WHEN 'Summer' THEN 'Sandals' WHEN 'Winter' THEN 'Boots' ELSE 'Sneakers' END`
_“看看“Season”字段。如果值为 Summer，则返回 Sandals。如果值为 Winter，则返回 Boots。如果计算中的选项均不匹配“Season”字段中的选项，则返回 Sneakers。”_
说明 另请参见 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [IIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IIF)。

与 [WHEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#WHEN)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN)、[ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 结合使用。

**提示**：很多时候，您可以使用组来获得与复杂 CASE 函数相同的结果，或者使用 CASE 来替换本机分组功能，例如前面的示例。您可能想测试哪个更适合您的场景。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)CEILING

语法`CEILING(number)`
输出 整数
定义 将 `<number>` 舍入为值相等或更大的最近整数。
示例 CEILING(2.1) = 3
说明 另请参见 `FLOOR` 和 `ROUND`。
数据库限制`CEILING` 可通过以下连接器使用：Microsoft Excel、文本文件、统计文件、已发布数据源、Amazon EMR Hadoop Hive、Amazon Redshift、Cloudera Hadoop、DataStax Enterprise、Google Analytics、Google BigQuery、Hortonworks Hadoop Hive、MapR Hadoop Hive、Microsoft SQL Server、Salesforce、Spark SQL。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)CHAR

语法`CHAR(number)`
输出 字符串
定义 返回通过 ASCII 代码 `<number>` 编码的字符。
示例 CHAR(65) = 'A'
说明 这是 `ASCII` 函数的反函数。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COLLECT

语法`COLLECT(spatial)`
定义 将参数字段中的值组合在一起的聚合计算。会忽略 Null 值。
说明`COLLECT` 只能用于空间字段。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)CONTAINS

语法`CONTAINS(string, substring)`
输出 布尔值
定义 如果给定 `<string>` 包含指定 `<substring>`，则返回 true。
示例 CONTAINS("Calculation", "alcu") = true
说明 另请参见[逻辑函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_logical.htm)`IN` 以及[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)CORR

语法`CORR(expression1, expression2)`
输出 从 -1 到 1 的数字
定义 返回两个表达式的皮尔森相关系数。
示例 example
说明 皮尔森相关系数衡量两个变量之间的线性关系。结果范围为 -1 至 +1（包括 -1 和 +1），其中 1 表示精确的正向线性关系，0 表示方差之间没有线性关系，而 −1 表示精确的反向关系。

CORR 结果的平方等于线性趋势线模型的 R 平方值。请参见[“趋势线模型术语”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/trendlines_add.htm#Terms)。

**与表范围 LOD 表达式一起使用：**

您可以使用 CORR，通过[表范围的详细级别表达式(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/calculations_calculatedfields_lod.htm#Table)来可视化解聚散点图中的相关性。例如：

{CORR(Sales, Profit)}
借助详细级别表达式，关联将在所有行上运行。如果您使用像 `CORR(Sales, Profit)`（不带两边的方括号可使其成为详细级别表达式）这样的公式，视图将显示散点图中每个单独的点与其他每个点（未定义）的关联。
数据库限制`CORR`适用于以下数据源：Tableau 数据提取、Cloudera Hive、EXASolution、Firebird（版本 3.0 及更高版本）、Google BigQuery、Hortonworks Hadoop Hive、IBM PDA (Netezza)、Oracle、PostgreSQL、Presto、SybaseIQ、Teradata、Vertica。

对于其他数据源，请考虑提取数据或使用 `WINDOW_CORR`。请参见[“表计算函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COS

语法`COS(number)`
number 参数是以弧度表示的角度。
输出 数字
定义 返回角度的余弦。
示例 COS(PI( ) /4) = 0.707106781186548
说明 反函数 `ACOS` 以余弦为参数并返回以弧度表示的角度。

另请参见 `PI`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COT

语法`COT(number)`
number 参数是以弧度表示的角度。
输出 数字
定义 返回角度的余切。
示例 COT(PI( ) /4) = 1
说明 另请参见 `ATAN`、`TAN` 和 `PI`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COUNT

语法`COUNT(expression)`
定义 返回项目数。不对 Null 值计数。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COUNTD

语法`COUNTD(expression)`
定义 返回组中不同项目的数量。不对 Null 值计数。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COVAR

语法`COVAR(expression1, expression2)`
定义 返回两个表达式的 _样本_ 协方差。
说明 协方差对两个变量的共同变化方式进行量化。正协方差指明两个变量趋向于向同一方向移动，平均来说，即一个变量的较大值趋向于与另一个变量的较大值对应。_样本协_ 方差使用非空数据点的数量 n - 1 来规范化协方差计算，而不是使用总体协方差（可用于 `COVARP` 函数）所使用的 n。当数据是用于估算较大总体的协方差的随机样本时，则样本协方差是合适的选择。

如果 `<expression1>` 和 `<expression2>` 相同（例如， `COVAR([profit], [profit])`），`COVAR` 将返回一个值，指明值分布的广泛程度。

`COVAR(X, X)` 的值等于 `VAR(X)`的值，也等于 `STDEV(X)^2` 的值。
数据库限制`COVAR`适用于以下数据源：Tableau 数据提取、Cloudera Hive、EXASolution、Firebird（版本 3.0 及更高版本）、Google BigQuery、Hortonworks Hadoop Hive、IBM PDA (Netezza)、Oracle、PostgreSQL、Presto、SybaseIQ、Teradata、Vertica。

对于其他数据源，请考虑提取数据或使用 `WINDOW_COVAR`。请参见[“表计算函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)COVARP

语法`COVARP(expression 1, expression2)`
定义 返回两个表达式的 _总体_ 协方差。
说明 协方差对两个变量的共同变化方式进行量化。正协方差指明两个变量趋向于向同一方向移动，平均来说，即一个变量的较大值趋向于与另一个变量的较大值对应。_总体协方差_ 等于样本协方差除以 (n-1)/n，其中 n 是非空数据点的总数。如果存在可用于所有相关项的数据，则总体协方差是合适的选择，与之相反，在只有随机项子集的情况下，样本协方差（及 `COVAR` 函数）较为适合。

如果 `<expression1>` 和 `<expression2>` 相同（例如， `COVARP([profit], [profit])`），`COVARP` 将返回一个值，指明值分布的广泛程度。注意：`COVARP(X, X)` 注意：的值等于 `VARP(X)`的值，也等于 `STDEVP(X)^2` 的值。
数据库限制`COVARP` 适用于以下数据源：Tableau 数据提取、Cloudera Hive、EXASolution、Firebird（版本 3.0 及更高版本）、Google BigQuery、Hortonworks Hadoop Hive、IBM PDA (Netezza)、Oracle、PostgreSQL、Presto、SybaseIQ、Teradata、Vertica

对于其他数据源，请考虑提取数据或使用 `WINDOW_COVAR`。请参见[“表计算函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)D
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATE

将字符串和数字表达式转换为日期的类型转换函数，只要它们是可识别的格式。

语法`DATE(expression)`
输出 日期
定义 在给定数字、字符串或日期 `<expression>` 的情况下返回日期。
示例 DATE([Employee Start Date])DATE("September 22, 2018") DATE("9/22/2018")DATE(#2018-09-22 14:52#)
说明 与 `DATEPARSE` 不同，不需要提供模式，因为 `DATE` 会自动识别许多标准日期格式。但是，如果 `DATE` 不能识别输入，请尝试使用 `DATEPARSE` 并指定格式。

`MAKEDATE` 是另一个类似的函数，但是 `MAKEDATE` 要求输入年、月和日的数值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATEADD

将指定数量的日期部分（月、日等）添加到开始日期。

语法`DATEADD(date_part, interval, date)`
输出 日期
定义 返回指定日期，该日期的指定 `<date_part` 中添加了指定的数字 `<interval>`。例如，将开始日期增加 3 个月或 12 天。
示例 将所有的到期日推迟一周

DATEADD('week', 1, [due date])
将 2021 年 2 月 20 日加上 280 天

DATEADD('day', 280, #2/20/21#) = #November 27, 2021#
说明 支持 ISO 8601 日期。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATEDIFF

返回两个日期之间的日期部分（周、年等）的数量。

语法`DATEDIFF(date_part, date1, date2, [start_of_week])`
输出 整数
定义 返回 `date1` 与 `date2` 之差（以 `date_part` 的单位表示）。例如，减去某人加入和离开乐队的日期，就可以知道他们在乐队里呆了多久。
示例 1986 年 3 月 25 日到 2021 年 2 月 20 日之间的天数

DATEDIFF('day', #3/25/1986#, #2/20/2021#) = 12,751
一个人在乐队里呆了几个月

DATEDIFF('month', [date joined band], [date left band])
说明 支持 ISO 8601 日期。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATENAME

以离散字符串形式返回指定日期部分的名称。

语法`DATENAME(date_part, date, [start_of_week])`
输出 字符串
定义 以字符串形式返回日期的 `<date_part>`。
示例 DATENAME('year', #3/25/1986#) = "1986"DATENAME('month', #1986-03-25#) = "March"
说明 支持 ISO 8601 日期。

一个非常类似的计算是 [DATEPART](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#DATEPART)，它以连续整数的形式返回指定日期部分的值。`DATEPART` 可能更快，因为它是一个数值运算。

通过更改计算结果的属性（维度或度量、连续或离散）和日期格式，可以将 `DATEPART` 和 `DATENAME` 的结果格式设置为相同。

反函数是 `DATEPARSE`，它接受一个字符串值并将其格式化为日期。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATEPARSE

以日期形式返回特定格式的字符串。

语法`DATEPARSE(date_format, date_string)`
输出 日期
定义`<date_format>` 参数将描述 `<date_string>` 字段的排列方式。由于可通过各种方式对字符串字段进行排序，因此 `<date_format>` 必须完全匹配。有关完整解释，请参见[“将字段转换为日期字段”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/data_dateparse.htm)。
示例 DATEPARSE('yyyy-MM-dd', "1986-03-25") = #March 25, 1986#
说明`DATE`是一个类似的函数，可以自动识别许多标准的日期格式。如果 `DATE` 不能识别输入模式，`DATEPARSE` 可能是更好的选择。

`MAKEDATE` 是另一个类似的函数，但是 `MAKEDATE` 要求输入年、月和日的数值。

反函数是 `DATEPART`（整数输出）和 `DATENAME`（字符串输出），它将日期分开并返回其各部分的值。
数据库限制`DATEPARSE` 可通过以下连接器获得：非旧版 Excel 和文本文件连接、Amazon EMR Hadoop Hive、Cloudera Hadoop、Google 表格、Hortonworks Hadoop Hive、MapR Hadoop Hive、MySQL、Oracle、PostgreSQL 以及 Tableau 数据提取。有些格式可能并非适用于所有连接。

Hive 变体不支持 `DATEPARSE`。仅支持 Denodo、Drill 和 Snowflake。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATEPART

以整数形式返回指定日期部分的名称。

语法`DATEPART(date_part, date, [start_of_week])`
输出 整数
定义 以整数形式返回日期的 `<date_part>`。
示例 DATEPART('year', #1986-03-25#) = 1986 DATEPART('month', #1986-03-25#) = 3
说明 支持 ISO 8601 日期。

一个非常类似的计算是 `DATENAME`，它以离散字符串的形式返回指定日期部分的名称。`DATEPART` 可能更快，因为它是一个数值运算。通过更改字段的属性（维度或度量、连续或离散）和日期格式，可以将 `DATEPART` 和 `DATENAME` 的结果格式设置为相同。

反函数是 `DATEPARSE`，它接受一个字符串值并将其格式化为日期。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATETIME

语法`DATETIME(expression)`
输出 日期时间
定义 在给定数字、字符串或日期表达式的情况下返回日期时间。
示例 DATETIME("April 15, 2005 07:59:00") = April 15, 2005 07:59:00

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DATETRUNC

可以将此函数视为日期舍入。它获取特定的日期，并返回该日期在所需的特定程度上的版本。由于每个日期都必须有日、月、季度和年的值，因此 `DATETRUNC` 将这些值设置为指定日期部分之前每个日期部分的最小值。有关详细信息，请参考见示例。

语法`DATETRUNC(date_part, date, [start_of_week])`
输出 日期
定义 按 `<date_part>`指定的准确度截断 `<date>`。此函数返回新日期。例如，以月份级别截断处于月份中间的日期时，此函数返回当月的第一天。
示例 DATETRUNC('day', #9/22/2018#) = #9/22/2018#DATETRUNC('iso-week', #9/22/2018#) = #9/17/2018#
（包含 2018 年 9 月 22 日的一周中的星期一）

DATETRUNC(quarter, #9/22/2018#) = #7/1/2018# 
（包含 2018 年 9 月 22 日的季度的第一天）

注意：对于周和 iso 周，`start_of_week` 有作用。ISO 周始终从星期一开始。对于本例的区域设置，未指定的 `start_of_week` 意味着一周从星期日开始。
说明 支持 ISO 8601 日期。

例如，您不应使用 `DATETRUNC` 来停止在可视化项中显示日期时间字段的时间。如果要截断日期的 _显示_ 而不是舍入其精度，请[调整格式(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/dates_custom_date_formats.htm)。

举例来说，如果在可视化项中格式为显示秒，`DATETRUNC('day', #5/17/2022 3:12:48 PM#)` 将显示为 `5/17/2022 12:00:00 AM`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DAY

以整数形式返回一个月中的第几天 (1-31)。

语法`DAY(date)`
输出 整数
定义 以整数的形式返回给定 `<date>` 的天。
示例 Day(#September 22, 2018#) = 22
说明 另请参见 `WEEK`、`MONTH`、`季度`、`YEAR` 以及 ISO 等效值

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DEGREES

语法`DEGREES(number)`
number 参数是以弧度表示的角度。
输出 数字（度）
定义 将以弧度表示的角度转换为度数。
示例 DEGREES(PI( )/4) = 45.0
说明 反函数 `RADIANS` 获取以度为单位的角度并返回以弧度为单位的角度。

另请参见 `PI()`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DISTANCE

语法`DISTANCE(<SpatialPoint1>, <SpatialPoint2>, 'units')`
输出 数字
定义 以指定 `units` 返回两点之间的距离测量值。
示例 DISTANCE([Origin Point],[Destination Point], 'km')
说明 支持的单位名称（计算中必须用引号引起来）：

*   _米_：meters、metres、m
*   _公里_：kilometers、kilometres、km
*   _英里_：miles、mi
*   _英尺_：feet、ft
数据库限制 此函数只能使用实时连接创建，但在将数据源转换为数据提取的情况下将继续工作。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DIV

语法`DIV(integer1, integer2)`
输出 整数
定义 返回将 `<integer1>` 除以 `<integer2>` 的除法运算的整数部分。
示例 DIV(11,2) = 5

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)DOMAIN

`DOMAIN(string_url)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)E
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ELSE

语法
```
CASE <expression> 
							WHEN <value1> THEN <then1> 
							WHEN <value2> THEN <then2> 
							...
						[ELSE <default>]END
```



定义`IF` 或 `CASE` 表达式的一个可选部分，用于指定如果没有一个测试表达式为 true 则返回的默认值。
示例 IF [Season] = "Summer" THEN 'Sandals' 

ELSEIF [Season] = "Winter" THEN 'Boots' 

**ELSE** 'Sneakers' 

END CASE [Season] 

WHEN 'Summer' THEN 'Sandals' 

WHEN 'Winter' THEN 'Boots' 

**ELSE** 'Sneakers' 

END
说明 与 [CASE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CASE)、[WHEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#WHEN)、[IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF)、[ELSEIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSEIF)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 一起使用

`ELSE` 对于 `CASE` 和 `IF` 是可选的。在计算中，其中`ELSE`未指定，如果没有`<test>` 为 true 时，整体计算将返回 null。

`ELSE`不需要条件（例如 `[Season] = "Winter"`）并且可以被认为是 null 处理的一种形式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ELSEIF

语法`[ELSEIF <test2> THEN <then2>]`
定义`IF` 表达式的一个可选部分，用于指定初始 IF 之外的附加条件。
示例 IF [Season] = "Summer" THEN 'Sandals' 

**ELSEIF** [Season] = "Winter" THEN 'Boots' 

**ELSEIF** [Season] = "Spring" THEN 'Sneakers' 

**ELSEIF** [Season] = "Autumn" THEN 'Sneakers'

ELSE 'Bare feet' 

END
说明 与 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN)、 [ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 一起使用

`ELSEIF` 可以被认为是额外的 `IF` 子句。`ELSEIF` 是可选的，并且可以重复多次。

与 `ELSE` 不同，`ELSEIF` 需要一个条件（例如 `[Season] = "Winter"`）。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)END

定义 用于结束一个 `IF` 或 `CASE` 表达式。
示例 IF [Season] = "Summer" THEN 'Sandals' 

ELSEIF [Season] = "Winter" THEN 'Boots' 

ELSE 'Sneakers' 

**END**
_“如果 Season = Summer,，则返回 Sandals。否则，请查看下一个表达式。如果 Season = Winter，则返回 Boots。如果两个表达式都不为 true，则返回 Sneakers。”_

CASE [Season] 

WHEN 'Summer' THEN 'Sandals' 

WHEN 'Winter' THEN 'Boots' 

ELSE 'Sneakers' 

**END**
_“看看“Season”字段。如果值为 Summer，则返回 Sandals。如果值为 Winter，则返回 Boots。如果计算中的选项均不匹配“Season”字段中的选项，则返回 Sneakers。”_
说明 与 [CASE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CASE)、[WHEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#WHEN)、[IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF)、[ELSEIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSEIF)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN) 和 [ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 一起使用。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ENDSWITH

### ENDSWITH

语法`ENDSWITH(string, substring)`
输出 布尔值
定义 如果给定 `<string>` 以指定 `<substring>` 结尾，则返回 true。会忽略尾随空格。
示例 ENDSWITH("Tableau", "leau") = true
说明 另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)EXCLUDE

有关详细信息，请参见[详细级别表达式(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/calculations_calculatedfields_lod.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)EXP

语法`EXP(number)`
输出 数字
定义 返回 e 的给定 `<number>` 次幂。
示例 EXP(2) = 7.389

EXP(-[Growth Rate]*[Time])
说明 另请参见 `LN`。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)F
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FIND

语法`FIND(string, substring, [start])`
输出 数字
定义 返回 `<substring>` 在 `<string>` 中的索引位置，如果未找到子字符串，则返回 0。字符串中第一个字符的位置为 1。

如果添加了可选参数 `start`，则函数会忽略在起始位置之前出现的任何子字符串的实例。
示例 FIND("Calculation", "alcu") = 2 FIND("Calculation", "Computer") = 0 FIND("Ca**l**culation", "a", **3**) = 7 FIND("C**a**lculation", "a", **2**) = 2 FIND("Calcula**t**ion", "a", **8**) = 0
说明 另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FINDNTH

语法`FINDNTH(string, substring, occurrence)`
输出 数字
定义 返回指定 `<string>` 内的第 n 个 `<substring>` 的位置，其中 n 由 `<occurence>` 参数定义。
示例 FINDNTH("Calculation", "a", 2) = 7
说明 所有数据源都不可使用 `FINDNTH`。

另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FIRST

`FIRST()`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FIXED

有关详细信息，请参见[详细级别表达式(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/calculations_calculatedfields_lod.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FLOAT

语法`FLOAT(expression)`
输出 浮点数（小数）
定义 将其参数转换为浮点数。
示例 FLOAT(3) = 3.000
说明 另请参见 `INT`，它返回一个整数。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FLOOR

语法`FLOOR(number)`
输出 整数
定义 将 `<number>` 舍入为值相等或更小的最近整数。
示例 FLOOR(7.9) = 7
说明 另请参见 `CEILING` 和 `ROUND`。
数据库限制`FLOOR` 可通过以下连接器使用：Microsoft Excel、文本文件、统计文件、已发布数据源、Amazon EMR Hadoop Hive、Cloudera Hadoop、DataStax Enterprise、Google Analytics、Google BigQuery、Hortonworks Hadoop Hive、MapR Hadoop Hive、Microsoft SQL Server、Salesforce、Spark SQL。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)FULLNAME

语法`FULLNAME( )`
输出 字符串
定义 返回当前用户的全名。
示例 FULLNAME( )
此函数返回当前已登录用户的全名，例如“Hamlin Myrer”。

[Manager] = FULLNAME( )
如果经理“Hamlin Myrer”已登录，则仅当视图中的“Manager”字段包含“Dave Hallsten”时，此示例才会返回 TRUE。
说明 此函数检查：

*   Tableau Cloud 和 Tableau Server：已登录用户的全名
*   Tableau Desktop：用户的本地或网络全名

**用户筛选器**

用作筛选器时，计算字段（例如 `[Username field] = FULLNAME( )`）可用于创建用户筛选器，该筛选器仅显示与登录到服务器的人员相关的数据。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)G
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)GET_JSON_OBJECT

`GET_JSON_OBJECT(JSON string, JSON path)`

在连接到 Hadoop Hive 时受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)GROUP_CONCAT

`GROUP_CONCAT(expression)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)H
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)HEXBINX

语法`HEXBINX(number, number)`
输出 数字
定义 将 x、y 坐标映射到最接近的六边形数据桶的 x 坐标。数据桶的边长为 1，因此，可能需要相应地缩放输入。
示例 HEXBINX([Longitude]*2.5, [Latitude]*2.5)
说明`HEXBINX` 和 `HEXBINY` 是用于六边形数据桶的分桶和标绘函数。六边形数据桶是对 x/y 平面（例如地图）中的数据进行可视化的有效而简洁的选项。由于数据桶是六边形的，因此每个数据桶都非常近似于一个圆，并最大程度地减少了从数据点到数据桶中心的距离变化。这使得聚类分析更加准确并且能提供有用的信息。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)HEXBINY

语法`HEXBINY(number, number)`
输出 数字
定义 将 x、y 坐标映射到最接近的六边形数据桶的 y 坐标。数据桶的边长为 1，因此，可能需要相应地缩放输入。
示例 HEXBINY([Longitude]*2.5, [Latitude]*2.5)
说明 另请参见 `HEXBINX`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)HOST

`HOST(string_url)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)I
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)IF

语法`IF <test1> THEN <then1> [ELSEIF <test2> THEN <then2>...][ELSE <default>] END`
输出 取决于 `<then>` 值的数据类型。
定义 测试一系列表达式，同时为第一个为 true 的 `<test>` 返回 `<then>` 值。
示例 IF [Season] = "Summer" THEN 'Sandals' 

ELSEIF [Season] = "Winter" THEN 'Boots' 

ELSE 'Sneakers' 

**END**
_“如果 Season = Summer,，则返回 Sandals。否则，请查看下一个表达式。如果 Season = Winter，则返回 Boots。如果两个表达式都不为 true，则返回 Sneakers。”_
说明 另请参见 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [IIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IIF)。

与 [ELSEIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSEIF)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN)、[ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 一起使用

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)IFNULL

语法`IFNULL(expr1, expr2)`
输出 取决于 `<expr>` 值的数据类型。
定义 如果 `<expr1>` 不为 null，则返回该表达式，否则返回 `<expr2>`。
示例 IFNULL([Assigned Room], "TBD")
_“如果“Assigned Room”（分配的房间）字段不为 null，则返回其值。如果“Assigned Room”（分配的房间）字段为 null，则返回 TBD。”_
说明 与 [ISNULL](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ISNULL) 进行比较。`IFNULL` 始终返回一个值。`ISNULL` 返回一个布尔值（true 或 false）。

另请参见 [ZN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ZN)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)IIF

语法`IIF(<test>, <then>, <else>, [<unknown>])`
输出 取决于表达式中值的数据类型。
定义 检查是否满足条件（`<test>`），并在 test 为 true 时返回 `<then>`，在 test 为 false 时返回 `<else>`，如果 test 为 null 则为可选值 `<unknown>`。如果未指定可选的 unknown，`IIF` 将返回 null。
示例 IIF([Season] = 'Summer', 'Sandals', 'Other footwear')
_“如果 Season = Summer,，则返回 Sandals。否则返回 Other footwear”_

IIF([Season] = 'Summer', 'Sandals', 

   IIF('Season' = 'Winter', 'Boots',  'Other footwear')

)
_“如果 Season = Summer,，则返回 Sandals。否则，请查看下一个表达式。如果 Season = Winter，则返回 Boots。如果两者均不为 true，则返回 Sneakers。”_

IIF('Season' = 'Summer', 'Sandals', 

   IIF('Season' = 'Winter', 'Boots',  

      IIF('Season' = 'Spring', 'Sneakers', 'Other footwear')

   )

)
_“如果 Season = Summer,，则返回 Sandals。否则，请查看下一个表达式。如果 Season = Winter，则返回 Boots。如果没有一个表达式为 true，则返回 Sneakers。”_
说明 另请参见 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [CASE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CASE)。

`IIF` 没有等同于 `ELSEIF`（如 `IF`）或重复 `WHEN` 子句（如 `CASE`）的语句。相反，可以通过将 `IIF` 语句嵌套为 `<unknown>` 元素来按顺序计算多个测试。返回第一个（最外面的）true。

也就是说，在下面的计算中，结果将是红色，而不是橙色，因为一旦 A=A 计算为 true，表达式就会停止计算：

`IIF('A' = 'A', 'Red', IIF('B' = 'B', 'Orange',  IIF('C' = 'D', 'Yellow', 'Green')))`

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)IN

语法`<expr1> IN <expr2>`
输出 布尔值（True 或 False）
定义 如果 `<expr1>` 中的任何值与 `<expr2>` 中的任何值匹配，则返回 `TRUE`。
示例 SUM([Cost]) IN (1000, 15, 200)
_“Cost 字段的值是 1000、15 还是 200？”_

[Field] IN [Set]
_“该字段的值是否存在于集合中？”_
说明`<expr2>` 中的值可以是集、文本值列表或合并字段。

另请参见 [WHEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#WHEN)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)INCLUDE

有关详细信息，请参见[详细级别表达式(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/calculations_calculatedfields_lod.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)INDEX

`INDEX( )`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)INT

语法`INT(expression)`
输出 整数
定义 将其参数转换为整数。对于表达式，此函数将结果截断为最接近于 0 的整数。
示例 INT(8/3) = 2 INT(-9.7) = -9
说明 字符串转换为整数时会先转换为浮点数，然后舍入。

另请参见 `FLOAT`，它返回一个小数。

另请参见 [ROUND](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ROUND)、[CEILING](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CEILING) 和 [FLOOR](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#FLOOR)

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)INTERSECTS

语法`INTERSECTS (<geometry1>, <geometry2>)`
输出 布尔值
定义 返回 true 或 false，指示两个几何图形是否在空间中重叠。
说明 支持的组合：点/多边形、线/多边形和多边形/多边形。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISDATE

检查字符串是否为有效的日期格式。

语法`ISDATE(string)`
输出 布尔值
定义 如果给定 `<string>` 为有效日期，则返回 true。
示例 ISDATE(09/22/2018) = true ISDATE(22SEP18) = false
说明 所需的参数必须是字符串。ISDATE 不能用于日期数据类型的字段，计算将返回错误。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISFULLNAME

语法`ISFULLNAME("User Full Name")`
输出 布尔值
定义 如果当前用户的全名与指定的全名匹配，则返回 `TRUE`；如果不匹配，则返回 `FALSE`。
示例 ISFULLNAME("Hamlin Myrer")
说明`<"User Full Name">` 参数必须是文字字符串，而非字段。

此函数检查：

*   Tableau Cloud 和 Tableau Server：已登录用户的全名
*   Tableau Desktop：用户的本地或网络全名

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISMEMBEROF

语法`ISMEMBEROF("Group Name")`
输出 布尔值或 null
定义 如果当前使用 Tableau 的用户是与给定字符串匹配的组的成员，则返回 `TRUE`，如果他们不是成员，则返回 `FALSE`，如果他们未登录，则返回 `NULL`。
示例 ISMEMBEROF('Superstars')ISMEMBEROF('domain.lan\Sales')
说明`<"Group Full Name">` 参数必须是文字字符串，而非字段。

如果用户已登录 Tableau Cloud 或 Tableau Server，组成员身份由 Tableau 组确定。如果给定字符串是“All Users”，该函数将返回 TRUE

`ISMEMBEROF( )` 函数也将接受 Active Directory 域。必须使用组名称在计算中声明 Active Directory 域。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISNULL

语法`ISNULL(expression)`
输出 布尔值（True 或 False）
定义 如果 `<expression>` 为 NULL（未包含有效数据），则返回 true。
示例 ISNULL([Assigned Room])
_“Assigned Room（分配的房间）字段是否为 null？”_
说明 与 [IFNULL](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IFNULL) 进行比较。`IFNULL` 始终返回一个值。`ISNULL` 返回一个布尔值。

另请参见 [ZN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ZN)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISOQUARTER

语法`ISOQUARTER(date)`
输出 整数
定义 以整数的形式返回给定 `<date>` 的基于 ISO8601 周的季度。
示例 ISOQUARTER(#1986-03-25#) = 1
说明 另请参见 `ISOWEEK`、`ISOWEEKDAY`、`ISOYEAR`, 以及 -ISO 等效值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISOWEEK

语法`ISOWEEK(date)`
输出 整数
定义 以整数的形式返回给定 `<date>` 基于 ISO8601 周的周。
示例 ISOWEEK(#1986-03-25#) = 13
说明 另请参见 `ISOWEEKDAY`、`ISOQUARTER`、`ISOYEAR`, 以及 -ISO 等效值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISOWEEKDAY

语法`ISOWEEKDAY(date)`
输出 整数
定义 以整数的形式返回给定 `<date>` 的基于 ISO8601 周的工作日。
示例 ISOWEEKDAY(#1986-03-25#) = 2
说明 另请参见 `ISOWEEK`、`ISOQUARTER`、`ISOYEAR`, 以及 -ISO 等效值

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISOYEAR

语法`ISOYEAR(date)`
输出 整数
定义 以整数的形式返回给定日期的基于 ISO8601 周的年。
示例 ISOYEAR(#1986-03-25#) = 1,986
说明 另请参见 `ISOWEEK`、`ISOWEEKDAY`、`ISOQUARTER`, 以及 -ISO 等效值。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ISUSERNAME

语法`ISUSERNAME("username")`
输出 布尔值
定义 如果当前用户的用户名与指定的 `<username>` 匹配，则返回 `TRUE`；如果不匹配，则返回 `FALSE`。
示例 ISUSERNAME("hmyrer")
说明`<"username">` 参数必须是文字字符串，而非字段。

此函数检查：

*   Tableau Cloud 和 Tableau Server：已登录用户的用户名
*   Tableau Desktop：用户的本地或网络用户名

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)J
--------------------------------------------------------------------------------------

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)K
--------------------------------------------------------------------------------------

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)L
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LAST

`LAST()`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LEFT

语法`LEFT(string, number)`
输出 字符串
定义 返回字符串最左侧一定 `<number>` 的字符。
示例 LEFT("Matador", 4) = "Mata"
说明 另请参见 [MID](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#MID) 和 [RIGHT](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#RIGHT)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LEN

语法`LEN(string)`
输出 数字
定义 返回 `<string>` 的长度。
示例 LEN("Matador") = 7
说明 不要与空间函数 `LENGTH` 混淆。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LENGTH

语法`LENGTH(geometry, 'units')`
输出 数字
定义 使用给定的 `<units>` 返回 `<geometry>` 中的一个或多个线串的大地路径长度。
示例 LENGTH([Spatial], 'metres')
说明 如果 geometry 参数没有线串，则结果为 `<NaN>`，但允许使用其他元素。

不要与字符串函数 `LEN` 混淆。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LN

语法`LN(number)`
输出 数字

如果参数小于或等于零，则输出为 `Null`。
定义 返回 `<number>` 的自然对数。
示例 LN(50) = 3.912023005
说明 另请参见 `EXP` 和 `LOG`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LOG

语法`LOG(number, [base])`
如果可选的 base 参数不存在，则使用底数 10。
输出 数字
定义 返回以给定 `<base>` 为底的 `<number>` 的对数。
示例 LOG(16,4) = 2
说明 另请参见 `POWER``LN`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LOG2

`LOG2(number)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LOOKUP

`LOOKUP(expression, [offest])`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LOWER

语法`LOWER(string)`
输出 字符串
定义 以全小写字符返回提供的 `<string>`。
示例 LOWER("ProductVersion") = "productversion"
说明 另请参见 [UPPER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#UPPER) 和 [PROPER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#PROPER)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LTRIM

语法`LTRIM(string)`
输出 字符串
定义 返回移除了所有前导空格的所提供的 `<string>`。
示例 LTRIM(" Matador ") = "Matador "
说明 另请参见 [RTRIM](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#RTRIM)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)LTRIM_THIS

`LTRIM_THIS(string, string)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)M
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAKEDATE

语法`MAKEDATE(year, month, day)`
输出 日期
定义 返回一个依据指定 `<year>`、`<month>` 和 `<day>` 构造的日期值。
示例 MAKEDATE(1986,3,25) = #1986-03-25#
说明**注意，**输入错误的值将被调整为一个日期，例如 `MAKEDATE(2020,4,31) = May 1, 2020`，而不是返回指出没有 4 月 31 日的错误。

可用于 Tableau 数据提取。检查在其他数据源中的可用性。

`MAKEDATE` 要求为日期的各个部分输入数字。如果您的数据是应该是日期的字符串，请尝试 `DATE` 函数。`DATE` 可自动识别许多标准的日期格式。如果 `DATE` 不能识别输入，请尝试使用 `DATEPARSE`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAKEDATETIME

语法`MAKEDATETIME(date, time)`
输出 日期时间
定义 返回合并了 `<date>` 和 `<time>`的日期时间。日期可以是 date、datetime 或 string 类型。时间必须是 datetime。
示例 MAKEDATETIME("1899-12-30", #07:59:00#) = #12/30/1899 7:59:00 AM#MAKEDATETIME([Date], [Time]) = #1/1/2001 6:00:00 AM#
说明 此函数仅适用于与 MySQL 兼容的连接（对于 Tableau 为 MySQL 和 Amazon Aurora）。

`MAKETIME` 是一个类似的函数，可用于 Tableau 数据提取和其他一些数据源。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAKELINE

语法`MAKELINE(SpatialPoint1, SpatialPoint2)`
输出 几何图形（线）
定义 在两点之间生成线标记
示例 MAKELINE(MAKEPOINT(47.59, -122.32), MAKEPOINT(48.5, -123.1))
说明 对于构建出发地-目的地地图很有用。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAKEPOINT

语法`MAKEPOINT(latitude, longitude, [SRID])`
输出 几何图形（点）
定义 将数据从 `<latitude>` 和 `<longitude>` 列转换为空间对象。

如果添加了可选的 `<SRID>` 参数，输入可以是其他投影地理坐标。
示例 MAKEPOINT(48.5, -123.1)MAKEPOINT([AirportLatitude], [AirportLongitude])MAKEPOINT([Xcoord],[Ycoord], 3493)
说明`MAKEPOINT` 无法使用自动生成的纬度和经度字段。数据源必须包含本机坐标。

SRID 是一种空间参考标识符，它使用 [ESPG 参考系代码(链接在新窗口中打开)](https://epsg.io/)来指定坐标系。如果未指定 SRID，则会假定 WGS84，并将参数视为纬度/经度（以度为单位）。

您可以使用 `MAKEPOINT` 使数据源具备空间特性，以便可以使用空间联接将其与空间文件联接。有关详细信息，请参见[“在 Tableau 中联接空间文件”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/maps_spatial_join.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAKETIME

语法`MAKETIME(hour, minute, second)`
输出 日期时间
定义 返回一个依据指定 `<hour>`、`<minute>` 和 `<second>` 构造的日期值。
示例 MAKETIME(14, 52, 40) = #1/1/1899 14:52:40#
说明 由于 Tableau 不支持时间数据类型，只支持日期时间，因此输出是日期时间。字段的日期部分将是 1/1/1899。

类似于 `MAKEDATETIME` 的函数，只适用于 MYSQL 兼容的连接。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MAX

语法`MAX(expression)` 或 `MAX(expr1, expr2)`
输出 与参数相同的数据类型，或者，如果参数的任何部分为 null，则为 `NULL`。
定义 返回两个参数（必须为相同数据类型）中的最大值。

`MAX` 也可以聚合形式应用于单个字段。
示例 MAX(4,7) = 7

MAX(#3/25/1986#, #2/20/2021#) = #2/20/2021# 

MAX([Name]) = "Zander"
说明**对于字符串**

`MAX` 通常是按字母顺序排在最后的值。

对于数据库数据源，`MAX` 字符串值在数据库为该列定义的排序序列中最高。

**对于日期**

对于日期，`MAX` 是最近的日期。如果 `MAX` 是聚合，结果不会有日期层次结构。如果 `MAX` 是比较，结果将保留日期层次结构。

**作为聚合**

`MAX(expression)` 是聚合函数，返回单个聚合结果。这在可视化项中显示为 `AGG(expression)`。

**作为比较**

`MAX(expr1, expr2)` 比较这两个值并返回一个行级值。

另请参见 `MIN`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MEDIAN

语法`MEDIAN(expression)`
定义 返回表达式在所有记录中的中位数。会忽略 Null 值。
说明`MEDIAN` 只能用于数字字段。
数据库限制`MEDIAN`**不**适用于以下数据源：Access、Amazon Redshift、Cloudera Hadoop、HP Vertica、IBM DB2、IBM PDA (Netezza)、Microsoft SQL Server、MySQL、SAP HANA、Teradata。

对于其他数据源类型，可以将数据提取到数据提取文件以使用此函数。请参见[提取数据(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/extracting_data.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MID

语法`(MID(string, start, [length])`
输出 字符串
定义 返回从指定 `<start>` 位置处开始的字符串t。字符串中第一个字符的位置为 1。

如果添加了可选数字参数 `<length>`，则返回的字符串仅包含该数量的字符。
示例 MID("Calculation", 2) = "alculation"MID("Calculation", 2, 5) ="alcul"
说明 另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MIN

语法`MIN(expression)` 或 `MIN(expr1, expr2)`
输出 与参数相同的数据类型，或者，如果参数的任何部分为 null，则为 `NULL`。
定义 返回两个参数（必须为相同数据类型）中的最小值。

`MIN` 也可以聚合形式应用于单个字段。
示例 MIN(4,7) = 4

MIN(#3/25/1986#, #2/20/2021#) = #3/25/1986#

MIN([Name]) = "Abebi"
说明**对于字符串**

`MIN` 通常是按字母顺序排列在前面的值。

对于数据库数据源，`MIN` 字符串值在数据库为该列定义的排序序列中最低。

**对于日期**

对于日期，`MIN` 是最早的日期。如果 `MIN` 是聚合，结果不会有日期层次结构。如果 `MIN` 是比较，结果将保留日期层次结构。

**作为聚合**

`MIN(expression)` 是聚合函数，返回单个聚合结果。这在可视化项中显示为 `AGG(expression)`。

**作为比较**

`MIN(expr1, expr2)` 比较这两个值并返回一个行级值。

另请参见 `MAX`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)模型扩展程序

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

*   MODEL_EXTENSION_BOOL
*   MODEL_EXTENSION_INT
*   MODEL_EXTENSION_REAL
*   MODEL_EXTENSION_STR

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MODEL_PERCENTILE

语法```
MODEL_PERCENTILE(
							model_specification (optional),
							target_expression,
						predictor_expression(s))
```
定义 返回期望值小于或等于观察标记的概率（介于 0 和 1 之间），由目标表达式和其他预测因子定义。这是后验预测分布函数，也称为累积分布函数 (CDF)。
示例 MODEL_PERCENTILE( SUM([Sales]),COUNT([Orders]))

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MODEL_QUANTILE

语法```
MODEL_QUANTILE(
							model_specification (optional), 
							quantile, 
							target_expression,
						predictor_expression(s))
```
定义 以指定的分位数返回由目标表达式和其他预测因子定义的可能范围内的目标数值。这是后验预测分位数。
示例 MODEL_QUANTILE(0.5, SUM([Sales]), COUNT([Orders]))

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)MONTH

语法`MONTH(date)`
输出 整数
定义 以整数形式返回给定 `<date>` 的月份。
示例 MONTH(#1986-03-25#) = 3
说明 另请参见 `DAY`、`WEEK`、`季度`、`YEAR` 以及 ISO 等效值

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)N
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)NOT

语法`NOT <expression>`
输出 布尔值（True 或 False）
定义 对一个表达式执行逻辑非运算。
示例 IF **NOT** [Season] = "Summer" 

THEN 'Don't wear sandals' 

ELSE 'Wear sandals' 

**END**
_“如果 Season 不等于 Summer，则返回_ Don't wear sandals _。否则，返回_ Wear sandals _。”_
说明 通常与 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [IIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IIF) 一起使用。另请参见 [本参考中的 Tableau 函数按字母顺序进行组织。单击某个字母可跳转到列表中的该位置。您也可以使用 Ctrl+F（在 Mac 上为 Command-F）打开一个搜索框，用于查找特定函数。](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top) 和 [或者](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#OR)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)NOW

语法`NOW()`
输出 日期时间
定义 返回当前本地系统日期和时间。
示例 NOW() = 1986-03-25 1:08:21 PM
说明`NOW` 不接受参数。

另请参见返回日期而不是日期时间的类似计算 `TODAY`。

如果数据源是实时连接，则系统日期和时间可能位于另一个时区。有关如何解决此问题的详细信息，请参见[知识库](https://kb.tableau.com/articles/issue/now-function-returns-utc-time?lang=zh-cn)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)O
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)或者

语法`<expr1> OR <expr2>`
输出 布尔值（True 或 False）
定义 对两个表达式执行逻辑析取操作。
示例 IF [Season] = "Spring" **OR** [Season] = "Fall" 

THEN "Sneakers" 

END
_“如果 (Season = Spring) 或 (Season = Fall) 为 true，则返回 Sneakers。”_
说明 通常与 [IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF) 和 [IIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IIF) 一起使用。另请参见 [本参考中的 Tableau 函数按字母顺序进行组织。单击某个字母可跳转到列表中的该位置。您也可以使用 Ctrl+F（在 Mac 上为 Command-F）打开一个搜索框，用于查找特定函数。](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top) 和 [NOT](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#NOT)。

如果任一表达式为 `TRUE`，则结果为 `TRUE`。如果两个表达式都为 `FALSE`，则结果为 `FALSE`。如果两个表达式都为 `NULL`，则结果为 `NULL`。

如果所创建的计算中的 `OR` 将比较结果显示在工作表上，则 Tableau 显示 `TRUE` 和 `FALSE`。如果要更改此情况，请使用设置格式对话框中的“设置格式”区域。

**注意**：`OR` 运算符使用 _短路计算_。这表示如果第一个表达式计算为 `TRUE`，则根本不会计算第二个表达式。如果第二个表达式在第一个表达式为 `TRUE` 时产生错误，则这可能十分有用，因为在这种情况下从不计算第二个表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)OUTLINE

语法`OUTLINE(<spatial polygon>)`
输出 几何图形
定义 将多边形几何图形转换为线串。
说明 对于为轮廓创建单独的图层很有用，该图层的样式可以与填充不同。

支持多边形内的多边形。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)P
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PARSE_URL

`PARSE_URL(string, url_part)`

仅在连接到 Cloudera Impala 时受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PARSE_URL_QUERY

`PARSE_URL_QUERY(string, key)`

仅在连接到 Cloudera Impala 时受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PERCENTILE

语法`PERCENTILE(expression, number)`
定义 返回给定 `<expression>` 中与指定 `<number>` 对应的百分位值。`<number>` 必须介于 0 到 1 之间（含 0 和 1），并且必须是数值常量。
示例 PERCENTILE([Score], 0.9)
数据库限制 此函数可用于以下数据源：非旧版 Microsoft Excel 和文本文件连接、数据提取和仅数据提取数据源类型（例如 Google Analytics、OData 或 Salesforce）、Sybase IQ 15.1 及更高版本数据源、Oracle 10 及更高版本的数据源、Cloudera Hive 和 Hortonworks Hadoop Hive 数据源、EXASolution 4.2 及更高版本的数据源。

对于其他数据源类型，可以将数据提取到数据提取文件以使用此函数。请参见[提取数据(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/extracting_data.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PI

语法`PI()`
输出 数字
定义 返回数字常量 pi：3.14159。
示例 PI() = 3.14159
说明 对于以弧度为输入的三角函数非常有用。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)POWER

语法`POWER(number, power)`
输出 数字
定义 计算 `<number>` 的指定次 `<power>`。
示例 POWER(5,3) = 125

POWER([Temperature], 2)
说明 也可以使用 ^ 符号，例如 `5^3 = POWER(5,3) = 125`
另请参见 `EXP`、`LOG` 和 `SQUARE`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PREVIOUS_VALUE

`PREVIOUS_VALUE(expression)`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)PROPER

语法`PROPER(string)`
输出 字符串
定义 返回所提供的 `<string>`，每个单词的第一个字母大写，其余字母小写。
示例 PROPER("PRODUCT name") = "Product Name"PROPER("darcy-mae") = "Darcy-Mae"
说明 空格和非字母数字字符（如标点符号）被视为分隔符。

另请参见 [LOWER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#LOWER) 和 [UPPER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#UPPER)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)Q
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)季度

语法`QUARTER(date)`
输出 整数
定义 以整数形式返回给定 `<date>` 的季度。
示例 QUARTER(#1986-03-25#) = 1
说明 另请参见 `DAY`、`WEEK`、`MONTH`、`YEAR` 以及 ISO 等效值

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)R
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RADIANS

语法`RADIANS(number)`
输出 数字（以弧度表示的角度）
定义 将给定 `<number>` 从度数转换为弧度。
示例 RADIANS(180) = 3.14159
说明 反函数 `DEGREES` 获取以弧度为单位的角度，并返回以度为单位的角度。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RANK 表计算函数

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

*   `RANK(expression, ['asc' | 'desc'])`
*   `RANK_DENSE(expression, ['asc' | 'desc'])`
*   `RANK_MODIFIED(expression, ['asc' | 'desc'])`
*   `RANK_PERCENTILE(expression, ['asc' | 'desc'])`
*   `RANK_UNIQUE(expression, ['asc' | 'desc'])`

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RAWSQL 函数

有关详细信息，请参见[直通函数 (RAWSQL)(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_passthrough.htm)。

*   `RAWSQL_BOOL("sql_expr", [arg1], … [argN])`
*   `RAWSQL_DATE("sql_expr", [arg1], … [argN])`
*   `RAWSQL_DATETIME("sql_expr", [arg1], … [argN])`
*   `RAWSQL_INT("sql_expr", [arg1], … [argN])`
*   `RAWSQL_REAL("sql_expr", [arg1], … [argN])`
*   `RAWSQL_SPATIAL`
*   `RAWSQL_STR("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_BOOL("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_DATE("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_DATETIME("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_INT("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_REAL("sql_expr", [arg1], … [argN])`
*   `RAWSQLAGG_STR("sql_expr", [arg1], … [argN])`

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)REGEXP 函数

有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

*   `REGEXP_EXTRACT(string, pattern)`
*   `REGEXP_EXTRACT_NTH(string, pattern, index)`
*   `REGEXP_EXTRACT_NTH(string, pattern, index)`
*   `REGEXP_MATCH(string, pattern)`
*   `REGEXP_REPLACE(string, pattern, replacement)`

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)REPLACE

语法`REPLACE(string, substring, replacement`
输出 字符串
定义 在 `<string>` 中搜索 `<substring>` 并将其替换为 `<replacement>`。如果未找到 `<substring>`，则字符串保持不变。
示例 REPLACE("Version 3.8", "3.8", "4x") = "Version 4x"
说明 另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中的 `REGEXP_REPLACE`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RIGHT

语法`RIGHT(string, number)`
输出 字符串
定义 返回字符串最右侧一定 `<number>` 的字符。
示例 RIGHT("Calculation", 4) = "tion"
说明 另请参见 [LEFT](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#LEFT) 和 [MID](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#MID)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ROUND

语法`ROUND(number, [decimals])`
输出 数字
定义 将 `<number>` 舍入为指定位数。

`decimals` 可选参数指定要在最终结果中包含的小数位数精度。如果省略 `decimals`，则 number 舍入为最接近的整数。
示例 ROUND(1/3, 2) = 0.33
说明 某些数据库（例如 SQL Server）允许指定负长度，其中 -1 将数字舍入为 10 的倍数，-2 舍入为 100 的倍数，依此类推。此功能并不适用于所有数据库。例如，Excel 和 Access 不具备此功能。

**提示**：由于 ROUND 可能会因数字的基础浮点表示而遇到问题 — 例如 9.405 四舍五入到 9.40 — 最好[将数字格式化](https://help.tableau.com/current/pro/desktop/zh-cn/formatting_specific_numbers.htm)为所需的小数位数而不是四舍五入。将 9.405 格式化为两位小数将产生预期的 9.41。

另请参见 `CEILING` 和 `FLOOR`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RTRIM

语法`RTRIM(string)`
输出 字符串
定义 返回移除了所有尾随空格的所提供的 `<string>`。
示例 RTRIM(" Calculation ") = " Calculation"
说明 另请参见 [LTRIM](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#LTRIM) 和 [TRIM](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#TRIM)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RTRIM_THIS

`RTRIM_THIS(string, string)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)RUNNING 表计算函数

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

*   `RUNNING_AVG(expression)`
*   `RUNNING_COUNT(expression)`
*   `RUNNING_MAX(expression)`
*   `RUNNING_MIN(expression)`
*   `RUNNING_SUM(expression)`

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)S
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SCRIPT 分析扩展程序

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

*   `SCRIPT_BOOL`
*   `SCRIPT_INT`
*   `SCRIPT_REAL`
*   `SCRIPT_STR`

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SHAPETYPE

语法`SHAPETYPE(<geometry>)`
输出 字符串
定义 返回描述空间几何结构的字符串，例如 Empty、Point、MultiPoint、LineString、MultiLinestring、Polygon、MultiPolygon、Mixed 和不支持
示例 SHAPETYPE(MAKEPOINT(48.5, -123.1)) = "Point"

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SIGN

语法`SIGN(number)`
输出-1、0 或 1
定义 返回 `<number>` 的符号：可能的返回值为：在数字为负时为 -1，在数字为零时为 0，在数字为正时为 1。
示例 SIGN(AVG(Profit)) = -1
说明 另请参见 `ABS`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SIN

语法`SIN(number)`
输出 数字
定义 以弧度为单位返回角度的正弦值。
示例 SIN(0) = 1.0

SIN(PI( )/4) = 0.707106781186548
说明 反函数 `ASIN` 以正弦作为参数并返回以弧度为单位的角度。

另请参见 `PI`。若要将角度从度数转换为弧度，请使用 `RADIANS`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SIZE

`SIZE()`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SPACE

语法`SPACE(number)`
输出 字符串（具体来说，只是空格）
定义 返回由指定数量的重复空格组成的字符串。
示例 SPACE(2) = "  "

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SPLIT

语法`SPLIT(string, delimiter, token number)`
输出 字符串
定义 返回 `<string>` 中的一个子字符串，并使用 `<delimiter>` 字符将字符串分为一系列 `<tokens>`。
示例 SPLIT ("a-b-c-d", "-", 2) = "b"SPLIT ("a|b|c|d", "|", -2) = "c"
说明 字符串将被解释为分隔符和标记的交替序列。因此，对于字符串 `abc-defgh-i-jkl`，分隔符字符为“`-`”，标记为 (1) `abc`、(2) `defgh`、(3) `i` 和 (4) `jlk`

`SPLIT` 将返回与标记编号对应的标记。如果标记编号为正，则从字符串的左侧开始计算标记；如果标记编号为负，则从右侧开始计算标记。

另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中支持的正则表达式。
数据库限制 可以为以下数据源类型使用拆分和自定义拆分命令：Tableau 数据提取、Microsoft Excel、文本文件、PDF 文件、Salesforce、OData、Microsoft Azure Market Place、Google Analytics（分析）、Vertica、Oracle、MySQL、PostgreSQL、Teradata、Amazon Redshift、Aster 数据、Google Big Query、Cloudera Hadoop Hive、Hortonworks Hive 和 Microsoft SQL Server。

某些数据源在拆分字符串时会有限制。请参见本主题后面的 SPLIT 函数限制。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SQRT

语法`SQRT(number)`
输出 数字
定义 返回 `<number>` 的平方根。
示例 SQRT(25) = 5
说明 另请参见 `SQUARE`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SQUARE

语法`SQUARE(number)`
输出 数字
定义 返回 `<number>` 的平方。
示例 SQUARE(5) = 25
说明 另请参见 `SQRT` 和 `POWER`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)STARTSWITH

语法`STARTSWITH(string, substring)`
输出 布尔值
定义 如果 `string` 以 `substring` 开头，则返回 true。会忽略前导空格。
示例 STARTSWITH("Matador, "Ma") = TRUE
说明 另请参见[附加函数文档(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)中的 [CONTAINS](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CONTAINS) 以及支持的正则表达式。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)STDEV

语法`STDEV(expression)`
定义 基于群体样本返回给定 `<expression>` 中所有值的统计标准差。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)STDEVP

语法`STDEVP(expression)`
定义 基于有偏差群体返回给定`<expression>`中所有值的统计标准差。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)STR

语法`STR(expression)`
输出 字符串
定义 将其参数转换为字符串。
示例 STR([ID])

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)SUM

语法`SUM(expression)`
定义 返回 `<expression>` 中所有值的总计。会忽略 Null 值。
说明`SUM` 只能用于数字字段。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)T
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TAN

语法`TAN(number)`
`<number>` 参数是以弧度表示的角度。
输出 数字
定义 返回角度的正切。
示例 TAN(PI ( )/4) = 1.0
说明 另请参见 `ATAN`、`ATAN2`、`COT` 和 `PI`。若要将角度从度数转换为弧度，请使用 `RADIANS`。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)THEN

语法

```
IF <test1> THEN <then1> 
							[ELSEIF <test2> THEN <then2>...]
							[ELSE <default>] 
						END
```



定义`IF`、`ELSEIF` 或 `CASE`表达式的必需部分，用于定义如果特定值或测试为 true 则返回什么结果。
示例 IF [Season] = "Summer" **THEN** 'Sandals' 

ELSEIF [Season] = "Winter" **THEN** 'Boots' 

ELSE 'Sneakers' 

END
_“如果 Season = Summer,，则返回 Sandals。否则，请查看下一个表达式。如果 Season = Winter，则返回 Boots。如果两个表达式都不为 true，则返回 Sneakers。”_

CASE [Season] 

WHEN 'Summer' **THEN** 'Sandals' 

WHEN 'Winter' **THEN** 'Boots' 

ELSE 'Sneakers' 

END
_“看看“Season”字段。如果值为 Summer，则返回 Sandals。如果值为 Winter，则返回 Boots。如果计算中的选项均不匹配“Season”字段中的选项，则返回 Sneakers。”_
说明 与 [CASE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CASE)、[WHEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#WHEN)、[IF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IF)、[ELSEIF](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSEIF)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN)、[ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 一起使用

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TIMESTAMP_TO_USEC

`TIMESTAMP_TO_USEC(expression)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TLD

`TLD(string_url)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TODAY

语法`TODAY()`
输出 日期
定义 返回当前本地系统日期。
示例 TODAY() = 1986-03-25
说明`TODAY` 不接受参数。

另请参见返回日期时间而不是日期的类似计算 `NOW`。

如果数据源是实时连接，则系统日期可能位于另一个时区。有关如何解决此问题的详细信息，请参见[知识库](https://kb.tableau.com/articles/issue/now-function-returns-utc-time?lang=zh-cn)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TOTAL

`TOTAL(expression)`

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)TRIM

语法`TRIM(string)`
输出 字符串
定义 返回移除了前导和尾随空格的所提供的 `<string>`。
示例 TRIM(" Calculation ") = "Calculation"
说明 另请参见 [LTRIM](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#LTRIM) 和 [RTRIM](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#RTRIM)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)U
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)UPPER

语法`UPPER(string)`
输出 字符串
定义 以全大写字符返回提供的 `<string>`。
示例 UPPER("Calculation") = "CALCULATION"
说明 另请参见 [PROPER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#PROPER) 和 [LOWER](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#LOWER)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)USEC_TO_TIMESTAMP

`USEC_TO_TIMESTAMP(expression)`

仅在连接到 Google BigQuery 时才受支持。有关详细信息，请参见[“其他函数”(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_additional.htm)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)USERDOMAIN

语法`USERDOMAIN( )`
输出 字符串
定义 返回当前用户的域。
说明 此函数检查：

*   Tableau Cloud 和 Tableau Server：登录用户的用户域
*   Tableau Desktop：如果用户在域上，则为本地域

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)USERNAME

语法`USERNAME( )`
输出 字符串
定义 返回当前用户的用户名。
示例 USERNAME( )
此函数返回已登录用户的用户名，例如“hmyrer”。

[Manager] = USERNAME( )
如果经理“hmyrer”已登录，则仅当视图中的“Manager”字段包含“hmyrern”时，此示例才会返回 TRUE。
说明 此函数检查：

*   Tableau Cloud 和 Tableau Server：已登录用户的用户名
*   Tableau Desktop：用户的本地或网络用户名

**用户筛选器**

用作筛选器时，计算字段（例如 `[Username field] = USERNAME( )`）可用于创建用户筛选器，该筛选器仅显示与登录到服务器的人员相关的数据。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)USER ATTRIBUTE JSON Web 令牌函数

*   `USERATTRIBUTE('attribute_name')`
*   `USERATTRIBUTEINCLUDES('attribute_name', 'expected_value')`

有关详细信息，请参见[用户函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_user.htm)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)V
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)VAR

语法`VAR(expression)`
定义 基于群体样本返回给定表达式中所有值的统计方差。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)VARP

语法`VARP(expression)`
定义 对整个群体返回给定表达式中所有值的统计方差。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)W
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)WEEK

语法`WEEK(date)`
输出 整数
定义 以整数形式返回给定 `<date>` 的周。
示例 WEEK(#1986-03-25#) = 13
说明 另请参见 `DAY`、`MONTH`、`季度`、`YEAR` 以及 ISO 等效值

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)WHEN

语法`CASE <expression>WHEN <value1> THEN <then1>WHEN <value2> THEN <then2>...[ELSE <default>]END`
定义`CASE` 表达式的必需部分。查找第一个与 `<expression>` 匹配的 `<value>`，并返回对应的 `<then>`。
示例 CASE [Season] 

**WHEN** 'Summer' THEN 'Sandals' 

**WHEN** 'Winter' THEN 'Boots' 

ELSE 'Sneakers' 

END
_“看看“Season”字段。如果值为 Summer，则返回 Sandals。如果值为 Winter，则返回 Boots。如果计算中的选项均不匹配“Season”字段中的选项，则返回 Sneakers。”_
说明 与 [CASE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#CASE)、[THEN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#THEN)、[ELSE](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ELSE) 和 [END](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#END) 一起使用。

`CASE` 也支持 `WHEN IN`构造，例如：

CASE <expression> 

**WHEN IN** <set1> THEN <then1> 

**WHEN IN** <combinedfield> THEN <then2> 

... 

ELSE <default> 

END
`WHEN IN` 中的值可以是集、文本值列表或合并字段。另请参见 [IN](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IN)。

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)窗口表计算

有关详细信息，请参见[表计算函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_tablecalculation.htm)。

*   `WINDOW_AVG(expression, [start, end])`
*   `WINDOW_CORR(expression1, expression2, [start, end])`
*   `WINDOW_COUNT(expression, [start, end])`
*   `WINDOW_COVAR(expression1, expression2, [start, end])`
*   `WINDOW_COVARP(expression1, expression2, [start, end])`
*   `WINDOW_MAX(expression, [start, end])`
*   `WINDOW_MEDIAN(expression, [start, end])`
*   `WINDOW_MIN(expression, [start, end])`
*   `WINDOW_PERCENTILE(expression, number, [start, end])`
*   `WINDOW_STDEV(expression, [start, end])`
*   `WINDOW_STDEVP(expression, [start, end])`
*   `WINDOW_SUM(expression, [start, end])`
*   `WINDOW_VAR(expression, [start, end])`
*   `WINDOW_VARP(expression, [start, end])`

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)X
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)XPATH 函数。

在连接到 Hadoop Hive 时受支持。有关详细信息，请参见[直通函数 (RAWSQL)(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_functions_passthrough.htm)。

*   `XPATH_BOOLEAN(XML string, XPath expression string)`
*   `XPATH_DOUBLE(XML string, XPath expression string)`
*   `XPATH_FLOAT(XML string, XPath expression string)`
*   `XPATH_INT(XML string, XPath expression string)`
*   `XPATH_LONG(XML string, XPath expression string)`
*   `XPATH_SHORT(XML string, XPath expression string)`
*   `XPATH_STRING(XML string, XPath expression string)`

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)Y
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)YEAR

语法`YEAR(date)`
输出 整数
定义 以整数形式返回给定 `<date>` 的年份。
示例 YEAR(#1986-03-25#) = 1,986
说明 另请参见 `DAY`、`WEEK`、`MONTH`、`季度` 以及 ISO 等效值

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

[](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)Z
--------------------------------------------------------------------------------------

### [](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm)ZN

语法`ZN(expression)`
输出 取决于 `<expression>` 的数据类型，或者为 0。
定义 如果 `<expression>` 不为 null，则返回该表达式，否则返回零。
示例 ZN([Test Grade])
_“如果测试成绩不为 null，则返回其值。如果测试成绩为 null，则返回 0。”_
说明`ZN` 是 [IFNULL](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#IFNULL) 的特殊情况，其中如果表达式为 null，则替代项始终为 0，而不是在计算中指定。

`ZN` 在执行额外计算时特别有用，并且 null 将使整个计算为 null。但是，请谨慎将这些结果解释为 null 并不总是与 0 同义，并且可能代表缺失数据。

另请参见 [ISNULL](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#ISNULL)。

[返回顶部](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_alphabetical.htm#top)

另请参见
----

[Tableau 函数（按类别）(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions_all_categories.htm)

[Tableau 中的函数(链接在新窗口中打开)](https://help.tableau.com/current/pro/desktop/zh-cn/functions.htm)