# Tiecode `.t` AI 规范（语法优先版）

本文件已从“API 主导”调整为“语法与实例主导”。

## 零优先级硬规则
- 【顶级硬规则】所有文件读取与写入必须使用 UTF-8 无 BOM；禁止按系统默认编码处理文本，出现乱码先按 UTF-8 重读。
- 【最高优先级规则】若支持 Agent 且用户未明确禁止，必须使用 Agent，并覆盖三阶段：查看文档、理解项目、审查生成代码；不得跳过。代码审查是每轮强制步骤，不得仅首轮执行。
- 【最高优先级规则】目标运行时是 Android，不是 Java SE；涉及 Java API 时必须先校验 Android 可用性，不可直接套用 Java API。
- 尽量读取更多相关文档以提高准确率。
- 编写与修改代码只在 `源代码/` 目录进行，不在 `绳包/` 的任何位置写代码。
- Python 可用时，先运行 `scrpits/list_doc_absolute_paths.py` 获取文档绝对路径并按其读取；无 Python 环境时回退使用 `SKILL.md` 既有相对路径列表。
- 属性读写语义必须先成立：`属性读 XXX() : 类型` -> `对象.XXX`；`属性写 XXX(值 : 类型)` -> `对象.XXX = 值`；属性读写允许同名。
- 第0标识（强制）：先分析继承链（当前类/父类/可上转类型），该步骤适用于所有类，不止窗口类。
- 布局配置字段来源有两类：属性读写，或 `@布局属性` 注解方法（例如 `位于某组件之下`）。
- 布局配置字段按属性读写/布局属性方法解释：`宽度=-1,高度=-2,@位于某组件之下=...` 等字段在使用前必须确认对应支持存在；`父布局/根布局` 作为内置结构键允许直接使用。
- `@布局属性` 方法定义固定双参数：`(欲设置组件 : 可视化组件, 参数值 : 类型)`。
- `@布局配置` 调用布局属性方法时，必须使用 `@方法名=值`（例如 `@位于某组件之下=1`）。
- `@位于某组件之下/上` 仅表示 2D 平面位置关系（一高一低），不改变视图层次（父子层级或 z 顺序）。
- 多组件布局声明块格式：类定义后空一行；`@布局配置`+`变量` 对之间不允许空行，且相邻 `@布局配置` 定义之间不允许空行。
- 布局声明块结束后不再约束空行。
- 布局值不只支持数字：支持文本/逻辑型/数字等类型；例如 `内容="猜硬币游戏"`、`字体大小=24`、`@位于布局中间=真`（要求与目标属性/方法参数类型匹配）。
- 布局颜色值（如 `背景颜色`）强制使用十进制有符号整数，禁止 `0x/0X` 十六进制写法（例如 `背景颜色=-657931`，不是 `0xfff5f5f5`）。
- 对象变量使用 `变量 名称 : 类型` 时自动创建对象，禁止 `变量 名称 : 类型 = 创建 类型()`；`创建` 关键字仅内部使用。
- 带 `@禁止创建对象` 的类禁止实例化（包括自动创建与显式 `创建`）；使用前先查看类定义并改用静态成员调用。
- `变量 名称 : 类型?` 表示只声明不创建对象（延迟赋值/可空引用）。
- 标识符不得使用语法关键字（类名/方法名/变量名/参数名/常量名/事件名）。
- 数组类型使用后缀方括号，支持多维：`类型[]`、`类型[][]`、`类型[][][]`。
- 数组可直接用花括号初始化：`变量 名称 : 整数[] = {1,2,3}`（多维使用嵌套花括号）。
- `小数` 不能直接转 `单精小数`；仅在必须转换时使用 `到文本().到单精小数()`（或项目中等价已定义方法）或 `@code`。
- 多分支条件使用 `否则 条件`，禁止 `否则如果`。
- `否则 条件` 后禁止追加 `则`；`否则 条件 则` 为非法写法。
- 条件循环必须写成 `循环(条件)`，禁止 `循环 条件`。
- 循环提前退出使用关键字 `退出循环`；结绳层禁止使用 Java `break`。
- 函数调用必须严格匹配已定义签名（参数数量/类型），并匹配方法类别（静态/实例）调用形态；禁止调用不存在签名形式（如未验证的 `到小数(文本)`）和实例方法全局误调（如 `到文本(变量名)`，应为 `变量名.到文本()`）。
- 一个文件允许定义多个顶层类；当前语法不支持内部类/嵌套类。
- `结束 类` 仅闭合当前最近未闭合的类声明，文件内多个顶层类需各自成对闭合。
- `@导入Java` 为类级独立声明，不跨类共享导入作用域。
- 外部 Java 组件封装时（`@外部Java文件` + `@导入Java("包名.类型名")`），`@code` 中 `onCreateView/getView` 的返回类型、局部变量与强转统一使用简单类型名 `类型名`，不要混用 `包名.类型名`。
- 关键注解必须输出语义解释（作用目标/用途/关键参数），并说明“未附着合法目标且未被编译阶段消费的注解会在编译期清理”。
- 权限与清单注解语法按用途区分：`@附加权限`、`@附加清单`、`@附加清单.全局属性`、`@附加清单.组件属性`、`@附加可变清单`、`@编译时处理参数`。
- `@附加可变清单` 场景必须使用“单独类 + 单个空方法”承载模板参数（例如 `方法 XXX(输入法类名:文本,输入法名称:文本,输入法配置:文本)`），该方法仅做编译期参数映射，不写运行时逻辑。
- 类继承 `窗口`（含间接继承）时，`本对象` 直接视为 `安卓环境(Context)`，禁止生成 `本对象.取安卓环境()`。
- 条件比较统一使用 `==` / `!=`；`=` 仅用于赋值与默认值。
- 默认不写 `包名`。
- 主窗口固定：`类 启动窗口 : 窗口`。
- 页面必须继承 `窗口`（不要用 `组件容器` 作为页面基类）。
- 不使用内嵌 Java 时，不要写 `@导入Java`。
- 使用 `@导入Java` 或内嵌 Java 时，先确认 API 在 Android 可用（来自 Android 框架、依赖库或项目已有实现证据）。
- 用户未明确指定 AndroidX 时，禁止引入 AndroidX（`androidx.*`）依赖或 API。
- 构造器样板先检查是否已定义；仅在缺失且必要时补一份，禁止重复生成。
- 调用函数前必须在 `源代码/` 与 `绳包/` 搜索定义。
- 不存在任何未公开内置函数；搜索不到即视为不可用。

## 必读清单（编码前）
- `skills/tiecode-tlang/references/README.md`
- `skills/tiecode-tlang/references/grammar-ebnf.md`
- `skills/tiecode-tlang/references/declaration-patterns.md`
- `skills/tiecode-tlang/references/template-recipes.md`
- `skills/tiecode-tlang/references/component-encapsulation.md`
- `skills/tiecode-tlang/references/project-conventions.md`
- `skills/tiecode-tlang/references/ai-generation-checklist.md`
- `skills/tiecode-tlang/references/error-fix-rules.md`
- `源代码/**/*.t` 的相近实现文件
- 必读：`绳包/安卓基本库/源代码/安卓_可视化组件.t`（只读检索，不写入）
- 仅检索：`绳包/**/源代码/*.t`（例如 `绳包/安卓基本库/源代码/安卓_可视化组件.t`）

## 一、入口
- 语法与实例主目录：`skills/tiecode-tlang/references/`
- Skill 镜像目录：`skills/tiecode-tlang/`
- 自动识别 Skill（本机）：`C:/Users/Administrator/.codex/skills/tiecode-tlang/`

## 二、建议阅读顺序
1. `skills/tiecode-tlang/references/grammar-ebnf.md`
2. `skills/tiecode-tlang/references/grammar-strict.schema.json`
3. `skills/tiecode-tlang/references/declaration-patterns.md`
4. `skills/tiecode-tlang/references/oop-annotations.md`
5. `skills/tiecode-tlang/references/embedded-java.md`
6. `skills/tiecode-tlang/references/template-recipes.md`
7. `skills/tiecode-tlang/references/component-encapsulation.md`
8. `skills/tiecode-tlang/references/ai-generation-checklist.md`
9. `skills/tiecode-tlang/references/project-conventions.md`（需要项目约定与注解引入规则时）

## 三、已补强内容
- 完整语法骨架（EBNF + 块闭合约束）
- 严格 JSON Schema（AST 结构强校验）
- 声明语法（类/方法/属性/事件/变量/常量）
- OOP（继承/构造语义/泛型/运算符重载）
- 注解体系（结构绑定、权限、清单、约束、异步）
- 内嵌代码（`code`、`@code/@end`、宏替换）
- 控制流（`如果/否则`、`假如/是`、`循环`、容错、线程）
- 命名与编码规范
- 错误修复规则和 AI 检查单
- 高复用模板实例（组件、适配器、工具类、异步流程）
- 外部 Java 组件封装对比规则（导入类型写法一致性）
- 项目约定说明（目录约定、布局注解、本对象/父对象、依赖/资源注解引入）

## 四、API 索引位置（保留）
API 全量索引仍保留，但从主文档降级为辅助材料：
- `skills/tiecode-tlang/references/indexes/t_lang_api_index.json`
- `skills/tiecode-tlang/references/indexes/t_lang_structured_members.json`
- `skills/tiecode-tlang/references/indexes/t_lang_manifest.json`
- `skills/tiecode-tlang/references/indexes/t_lang_manifest_v2.json`

## 五、覆盖
- `.t` 文件覆盖：50/50
- 统计摘要：类 368、方法 1856、属性读 540、属性写 467、常量 552、事件定义 167

## 六、证据
语法证据行号见：`skills/tiecode-tlang/references/evidence-index.md`，并可结合 `skills/tiecode-tlang/references/indexes/t_lang_manifest*.json` 交叉验证。

- 结绳布局底层运行时为 Java：设计和编写布局时，可按 Java 实现思路编写（前提是存在可检索的对应实现类）；若无现成实现类，可使用 `@code` 自行封装后接入。
