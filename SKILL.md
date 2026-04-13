***

name: tiecode-tlang
description: Write, refactor, review, and repair Tiecode `.t` 结绳代码 with strict syntax-first guidance. Use when tasks mention `.t` files, Tiecode/结绳 language grammar, annotations, OOP wrappers, embedded Java blocks (`code` or `@code/@end`), event-driven component patterns, naming/style normalization, compile-error repair, project conventions (`源代码` and `绳包`), layout annotation patterns, object reference semantics (`本对象` and `父对象`), and annotation-based dependency/resource loading.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Tiecode T-Lang

## Top-Level Hard Review Requirement (Blocking)

- **Built-in API Retrieval Rule (Highest Priority)**:
  - In IDE, CLI, and other environments with file read/write support, must prioritize checking built-in APIs under `{项目路径}/绳包/安卓基本库` directory to find available classes, methods, properties, etc.
  - In chat environments (such as mobile, web, App, etc. where file read/write is not supported), can request the user to provide `t_lang_api_index.json` file to obtain built-in API index.
  - This rule has higher priority than all other rules, ensuring built-in API retrieval and verification is completed before any code generation.
- **Basic-Library Function Priority Rule (Hard Requirement / Blocking)**:
  - When handling any functional requirement (for example array-to-text conversion, text processing, numeric conversion, etc.), must first search the basic library for existing functions or methods that can be used directly.
  - Search scope includes `绳包/安卓基本库/源代码/**/*.t` and utility methods already defined in project `源代码/**/*.t`.
  - Only implement custom logic when the corresponding functionality does not exist in the basic library; it is strictly forbidden to skip the search and re-implement existing functionality.
  - This rule applies to all code generation scenarios, including but not limited to data conversion, string processing, collection operations, file operations, etc.
- No assumptions: during review and code generation, do not approve based on guesses like "probably exists" or "usually works."
- If there is any error/diagnostic/fix task, check the issue checklists first: `references/error-fix-rules.md` and `references/ai-generation-checklist.md`.
- Mandatory verification: in every round, verify that referenced layout properties, classes, and methods truly exist and are usable.
- Any uncertainty must be verified first; if verification cannot be completed successfully, explicitly inform the user and immediately terminate the current generation/review flow.
- All document viewing and editing must use UTF-8 without BOM.
- Layout numeric values in `@布局配置` support both `px` and `dp` for normal numeric layout keys: default to `px` when unit is omitted, and prefer `dp` unless there is an explicit reason to use `px`. For `@布局属性` method keys (`@方法名=值`), `dp` suffix is not supported.
- Tiecode layout is Java-backed at runtime: when designing/writing layout, you may follow Java-style implementation if a corresponding implementation class exists, or encapsulate it yourself via `@code`.
- For layout/component work, use a strict pre-reference flow: inspect underlying implementation first, simulate the generated Java mapping of current Tiecode declarations, and only then use internet-findable Java/Android layout patterns as reference.
- External layout references are advisory only: before emission, re-verify local mapping/implementations exist (class, method, property, signature). If local evidence is missing, stop and report uncertainty.
- In this workflow, do not create/edit local `.java` files; complete implementation in Tiecode (`.t`) + `@code` bridge only, unless the user explicitly requests Java-file changes.
- Java-block language boundary is strict: inside `code` / `@code...@end`, do not use Tiecode literals/keywords directly (for example `真`/`假`/`空`/`返回`); use Java forms (`true`/`false`/`null`/`return`) and use `#变量` only for Tiecode symbol bridging.
- Do not assume software users will always operate correctly: enforce strict and comprehensive checks (input/state/boundary/error-path) to prevent crashes before approval or code emission.
- Java-style comment requirement (top priority): unless the user explicitly requests no comments, add concise Java-style comments on class and method definitions to clarify intent/usage/constraints.
- Global annotation constraint: `@全局基础类` is reserved exclusively for class `对象类`, and this global base slot is already occupied; do not generate or add `@全局基础类` anywhere else.

## Objective

Generate and edit `.t` code that is syntactically valid first, style-consistent second, and API-complete third.
Prefer grammar and template correctness over broad API enumeration.

## Syntax & Logic Focus (No Business Injection)

Use this section as a strict generation lens: prioritize grammar correctness, call semantics, and control-flow validity before introducing any feature code.

### Logic Constraints (Project-Derived, Syntax-Level)

- Condition discipline:
  - `=` is assignment only.
  - `==` / `!=` must be used for comparisons.
- Call-shape discipline:
  - Instance member: `对象.方法(...)`
  - Static member: `类型.方法(...)`
  - Forbid pseudo-global calls when member call is required.
- Construction discipline:
  - Normal typed declaration may auto-create: `变量 名称 : 类型`
  - For `@禁止创建对象` classes, forbid all instance construction forms.
  - Use static access or declaration-only reference: `变量 名称 : 类型?`
- Loop and branch discipline:
  - Use `循环(条件)` (must include parentheses).
  - Multi-branch must use `否则 条件`, not `否则如果`.
  - Guarded branch must not use `否则 条件 则`.
- Layout-key discipline:
  - Built-in structural keys: `父布局` / `根布局`.
  - Other keys must map to `属性读/属性写` or `@布局属性` methods.
  - `@布局属性` keys in `@布局配置` must use `@key=value` form.
- Event/lifecycle discipline:
  - Window event wiring should start in `事件 <窗口>:创建完毕()`.
  - Keep event subscriptions centralized (`订阅事件()` first, then side effects).
- Async/UI discipline:
  - UI mutation should happen on main thread callbacks.
  - Always provide explicit failure path for async request logic.

### Minimal Syntax Examples (Abstract)

Comparison:

```t
// 正确
如果 计数 == 0 则
结束 如果

// 错误
如果 计数 = 0 则
结束 如果
```

Loop condition:

```t
// 正确
循环(索引 < 长度)
	索引 = 索引 + 1
结束 循环

// 错误
循环 索引 < 长度
	索引 = 索引 + 1
结束 循环
```

Static vs instance call:

```t
// 正确 实例调用
变量 文本值 : 文本 = 数值.到文本()

// 正确 静态调用
变量 时间戳 : 长整数 = 系统工具.当前时间毫秒()
```

Non-instantiable class usage:

**When to use `@禁止创建对象`**: Only use this annotation when external instantiation must be prevented, such as: utility classes (pure static method collections), singleton patterns, factory classes, etc. Regular business classes generally do not need this annotation.

```t
@禁止创建对象
类 工具类
	@静态
	方法 校验() : 逻辑型
		返回 真
	结束 方法
结束 类

// 正确
变量 结果 : 逻辑型 = 工具类.校验()

// 正确（仅声明，不创建）
变量 延迟引用 : 工具类?
```

## Absolute Rules (Load First)

- Encoding Redline (Top-Most Priority / Blocking, Above All Rules):
  - All file reads/writes must use UTF-8 without BOM.
  - Do not rely on system-default ANSI/locale codepage for decoding `.t`, `.md`, `.json`, or `.java`.
  - Any generated or modified file must be persisted as UTF-8 (no BOM).
  - If decoded text appears garbled, stop and re-read with explicit UTF-8 before analysis or edits.
- Rule-Evidence Corpus Redline (Highest Priority for policy expansion):
  - When expanding SKILL rules/conventions/requirements, use `绳包/安卓基本库/源代码/**/*.t` as primary evidence source.
  - Evidence lookup is read-only; never write into the above reference corpus.
- Object-Creation Ban Redline (Hard Requirement / Blocking):
  - For any class annotated with `@禁止创建对象`, instance construction is strictly forbidden.
  - Forbidden forms include both auto-creation declaration `变量 名称 : 类型` and explicit creation `变量 名称 : 类型 = 创建 类型()`.
  - Violation handling is blocking: report error and stop generation/repair flow until the violation is removed.
  - Before using such class, inspect class definition and use only allowed static members (for example `类型.方法(...)`).
- Agent Redline (Highest Priority):
  - If Agent is available and the user has not explicitly forbidden Agent, Agent participation is mandatory.
  - Agent must cover all three phases: document scan, project understanding, and generated-code review.
  - Generated-code review is required on every generation turn/round; do not reuse first-turn or previous-turn review as a substitute.
  - This rule has higher priority than optimization/convenience rules; do not skip Agent phases.
- Android Runtime Redline (Highest Priority):
  - Target runtime is Android (ART), not Java SE/JRE.
  - Before generating/importing/calling any Java API, verify Android availability first.
  - Availability evidence must come from at least one source: existing project/`绳包` code, Android framework API import path, or declared dependency.
  - Do not generate unverified or Java-SE-only APIs (for example `java.awt.*`, `javax.swing.*`, `java.applet.*`).
- AndroidX Redline (Highest Priority):
  - Unless the user explicitly requests AndroidX, do not generate/import/call AndroidX APIs or dependencies.
  - Forbidden by default includes `androidx.*` packages, AndroidX AAR dependencies, and AndroidX-specific wrappers.
  - Only when user-specified may AndroidX be introduced, and it still must pass availability verification.
- Skill Scope Redline (Highest):
  - Always resolve docs from the currently loaded skill root, not from random workspace folders.
  - Global Skill Mode: if loaded path is under `~/.codex/skills/` or `~/.trae-cn/skills/`, read docs only from `<active-skill-root>/references/`; do not scan `<workspace>/skills/**` for docs.
  - Project Skill Mode: if loaded path is under `<workspace>/skills/`, read docs only from that project skill's `references/`.
  - Cross-skill/workspace doc scanning is forbidden unless user explicitly asks.
- Doc Path Rule (Preferred):
  - If Python is available, run `python <active-skill-root>/scrpits/list_doc_absolute_paths.py` first.
  - Use the script output absolute paths as the primary doc loading paths.
  - If Python is unavailable, fall back to the original relative paths in this file's Mandatory Read Set.
- Index JSON Ops Rule (Preferred):
  - If the task involves index lookup/stat/search/consistency checks, run `python <active-skill-root>/scrpits/index_json_ops.py` instead of ad-hoc manual JSON parsing.
  - Prefer subcommands: `list`, `stats`, `search`, `validate`.
  - Use `--indexes` to limit scan scope and `--json` when structured machine-readable output is needed.
  - If Python is unavailable, fall back to direct read of `references/indexes/*.json`.
- Full-Read Rule (Strict): before any coding, read the full Mandatory Read Set in this file (covers all active docs/json/schema/indexes). Skipping is not allowed.
- Formatting Redline (Highest): do not introduce unintended spaces in layout blocks or UI literals. Examples: use `猜正面` (not `猜 正面`), `总次数:0|胜利:0|失败:0` (no auto-added separator spaces unless user asks).
- Layout Key Redline: use canonical Chinese layout keys only (`高度`, not `height`; `宽度`, not `width`).
- Zero Rule 0: 结绳 uses Java-style comments (`//` or `/* */`) instead of `'`-prefixed comments.
- Zero Rule +1: read as many relevant references as possible to improve accuracy, and deduplicate findings to avoid repeated scans.
- Write and edit business code only under `源代码/`; do not write code in any path under `绳包/`.
- Zero Rule +2: property semantics are mandatory. `属性读 XXX() : 类型` enables `对象.XXX` read access; `属性写 XXX(值 : 类型)` enables `对象.XXX = 值` write access; same-name `属性读/属性写` pairs are allowed.
- Zero Rule +3: for every `@布局配置([[...]] )` key (such as `宽度/高度`), verify corresponding accessor support exists before using it. Built-in structural keys `父布局/根布局` are allowed without basic-library member lookup. Treat non-built-in layout keys as property accessors, never as undocumented magic fields.
- Zero Rule +4: methods annotated as layout properties (for example `@布局属性` methods such as `位于某组件之下`) are also valid layout keys in `@布局配置`; verify annotation and callable signature from source/index before use.
- Zero Rule +5: `@布局属性` method signatures are fixed to two parameters only: `(欲设置组件 : 可视化组件, 参数值 : 类型)`; do not generate extra parameters.
- Zero Rule +6: when using a layout-property method in `@布局配置`, the key must be prefixed with `@` (for example `@位于某组件之下=1`).
- Zero Rule +6.1: `@位于某组件之下` / `@位于某组件之上` describe 2D planar relative position (higher/lower placement). They do not change view hierarchy, parent-child relation, or z-order/layer.
- Zero Rule +7: for multi-component layout declaration blocks, keep exactly one blank line after class declaration before the first layout pair, then keep declarations contiguous: no blank line between each `@布局配置` + `变量` pair. After the layout block ends, trailing blank lines are not constrained by this rule.
- Zero Rule +8: layout values are not numeric-only. `@布局配置` supports typed values (number/text/bool/etc.) as long as type matches the target property or `@布局属性` method second parameter. Example keys: `内容="猜硬币游戏"`, `字体大小=24`, `@位于布局中间=真`.
- Zero Rule +9（第0标识）: inheritance-chain analysis is mandatory for all classes and objects (not only `窗口` classes). Before emitting member calls/parameter passing, determine current type, parent chain, and whether upcast is valid.
- Zero Rule +10: in classes inheriting `窗口` (including indirect inheritance), `本对象` is already Android `Context` (`安卓环境`). Pass `本对象` directly when APIs need `安卓环境`.
- Zero Rule +11: in `窗口` inheritance classes, do not generate `本对象.取安卓环境()`; only use `取安卓环境()` when the current object is not already `安卓环境` and conversion is actually needed.
- Zero Rule +12: logical-symbol discipline is mandatory. In conditions, `=` is assignment only; comparisons must use `==` / `!=`. Reject patterns like `如果 硬币结果 = 0 则`.
- Zero Rule +13: color values in `@布局配置` (for example `背景颜色`) must use signed decimal integers, not hex literals (`0x...`/`0X...`). Example: `0xfff5f5f5 -> -657931`, `0xff2c3e50 -> -13877680`.
- Zero Rule +14: inside a multi-component layout declaration block, no blank line is allowed between consecutive layout definitions (`@布局配置` + `变量` pairs). Keep pairs strictly contiguous.
- Zero Rule +15: object variables are auto-created by typed declaration. Use `变量 对象名 : 类型` directly; do not generate `变量 对象名 : 类型 = 创建 类型()`.
- Zero Rule +16: keyword `创建` is internal-only and must not be emitted in business/source code generation.
- Zero Rule +17: multi-branch condition syntax uses `否则 条件` (without `否则如果`). Do not generate `否则如果`.
- Zero Rule +18: conditional-loop syntax must use parentheses: `循环(条件)`; do not generate `循环 条件`.
- Zero Rule +19: function-call signatures are strict. Verify parameter count/types against existing definitions; do not invent overloads (for example forbid `到小数(文本)` when only zero-arg `到小数()` exists).
- Zero Rule +20: function-call form is strict. Instance methods must be called by instance receiver (`对象.方法(...)`); static methods must be called by type/class receiver (`类型.方法(...)`). Forbid global-call misuse such as `到文本(变量名)` when correct form is `变量名.到文本()`.
- Zero Rule +21: guarded-else branch syntax is strict: use `否则 条件` only (no trailing `则`). Forbid both `否则如果` and `否则 条件 则`.
- Zero Rule +22: file/class structure is strict. A file may contain multiple top-level classes, but nested/inner class declarations inside a class are unsupported and must not be generated.
- Zero Rule +23: `@导入Java` scope is class-local and independent. Do not assume imports declared for one class apply to other classes in the same file.
- Zero Rule +24: annotation explanation output is mandatory. For every emitted key annotation, explain target, purpose, and critical parameters. Annotations not attached to valid targets and not consumed by compile stage are treated as ineffective and may be cleared during compilation.
- Zero Rule +25: global-class annotations must not be abused. Use `@全局类` / `@全局基础类` only when cross-module global entry is explicitly required by the task or existing design.
- Zero Rule +26: for `@附加可变清单` placeholder completion, define a separate dedicated class containing exactly one empty parameter-carrier method. This method must be used only for compile-time template parameter mapping (for example `方法 XXX(输入法类名:文本,输入法名称:文本,输入法配置:文本) ...` with no runtime logic).
- Zero Rule +27（Top Priority / Hard Requirement）: for classes annotated `@禁止创建对象`, inspect the class definition first and confirm usable members. Treat these classes as non-instantiable utility/meta classes. Note: use this pattern only when truly needed (utility classes, singletons, factories); regular business classes generally do not require this annotation.
- Zero Rule +28（Top Priority / Hard Requirement）: for `@禁止创建对象` classes, forbid all instance construction forms, including auto-creation declaration (`变量 名称 : 类型`) and explicit creation (`变量 名称 : 类型 = 创建 类型()`). Violation is blocking and must be fixed before continuing.
- Zero Rule +29（Top Priority）: `变量 名称 : 类型?` is declaration-only (no auto-creation). Use it for deferred assignment or nullable references when object creation must not happen.
- Zero Rule +30（Top Priority）: do not use language keywords as identifiers (class names, method names, variable names, parameter names, constant names, event names, etc.).
- Zero Rule +31（Top Priority）: array types use suffix brackets and support multi-dimension: `类型[]`, `类型[][]`, `类型[][][]` ... Arrays can be initialized with braces, for example `变量 数组 : 整数[] = {1,2,3}`.
- Zero Rule +32（Top Priority）: direct conversion from `小数` to `单精小数` is not supported. Only when conversion is strictly necessary, use `到文本().到单精小数()` (or project-defined equivalent method name) or use an `@code` block.
- Zero Rule +33（Top Priority）: use keyword `退出循环` to exit loop blocks in 结绳 layer. Do not generate Java `break` outside `@code`.
- Zero Rule +34（Top Priority）: for external Java component wrappers (`@外部Java文件` + `@导入Java("包名.类型名")`), use simple imported type name in wrapper `@code` signatures/locals/casts (`类型名`), not package-prefixed names.
- Do not generate `包名 ...` by default.
- Main window must be `类 启动窗口 : 窗口`.
- Page classes must inherit `窗口` (do not use `组件容器` as page base class).
- Prefer annotation-driven layout (`@布局配置`) with parent-child declaration order.
- If no embedded Java (`code` / `@code...@end`) is used, do not add `@导入Java`.
- Zero Rule: before adding constructor boilerplate, check whether the class already defines it; if already defined, do not duplicate; if missing and required, add exactly one constructor boilerplate block.
- Top Rule: before calling any function, search `源代码/` and `绳包/` to confirm it exists, then verify whether it is instance or static and use the correct call form.
- Treat all unverified functions as unavailable; there are no undocumented built-in functions（不存在任何未公开内置函数）.
- Do not start coding after reading only a few files; complete the mandatory read set first and report what was read.
- Use `@code` only when 结绳语句 cannot express the logic.

## Execution Workflow

1. Detect target domain from file path and surrounding existing code style (`结绳.JVM`, `结绳.安卓`, `结绳.Meng`, `结绳.基本`) and whether the task is syntax generation or syntax profiling.
2. Determine current skill mode first (Global Skill Mode vs Project Skill Mode) and lock doc root to active skill `references/` only.
3. For SKILL policy update tasks, collect evidence from mandatory docs and `绳包/安卓基本库/源代码/**/*.t` before writing.
4. Before writing code, read the full mandatory set (all listed `references/` docs + required project files). If Agent is available and not forbidden by user, run Agent to review docs and project and deduplicate evidence. If index evidence is needed, prefer `scrpits/index_json_ops.py` for query/validation. If Java API is involved, complete Android-availability check before writing imports/calls.
5. Select nearest template and instantiate with minimal edits in `源代码/`.
6. Add annotations and embedded Java only when necessary.
7. Run post-generation checklist and fix violations.
8. If Agent is available and not forbidden by user, run Agent review on generated code for this round and apply required fixes. This step is mandatory every round.

## Absolute Path Discovery (Preferred)

- Script path: `scrpits/list_doc_absolute_paths.py`
- Command:
  - `python <active-skill-root>/scrpits/list_doc_absolute_paths.py`
  - Optional: `python <active-skill-root>/scrpits/list_doc_absolute_paths.py --workspace-root <workspace-root>`
- Output usage:
  - Read docs by the emitted absolute paths first.
  - Keep skill scope locked to the active skill root.
- No-Python fallback:
  - Use the original relative paths in Mandatory Read Set (unchanged fallback behavior).

## Index JSON Operations (Preferred)

- Script path: `scrpits/index_json_ops.py`
- Commands:
  - `python <active-skill-root>/scrpits/index_json_ops.py list`
  - `python <active-skill-root>/scrpits/index_json_ops.py stats --indexes api structured annotation`
  - `python <active-skill-root>/scrpits/index_json_ops.py search <关键词> --indexes api structured --sections methods members --limit 20`
  - `python <active-skill-root>/scrpits/index_json_ops.py validate --fail-on-warning`
- Usage rule:
  - For `references/indexes/*.json` operations, prefer this script over manual parsing to keep output and checks consistent.

Parameter explanation (must follow):

- Common:
  - `command`: required subcommand; one of `list` / `stats` / `search` / `validate`.
- `list`:
  - `--json`: optional; emit JSON output instead of plain text list.
- `stats`:
  - `--indexes`: optional; choose from `annotation api structured manifest manifest_v2`; default is all indexes.
  - `--json`: optional; emit JSON output.
- `search`:
  - `keyword`: required positional argument; plain keyword by default, or regex when `--regex` is enabled.
  - `--indexes`: optional; choose search scope from `annotation api structured manifest manifest_v2`; default is `annotation api structured`.
  - `--sections`: optional; section filter (for example `classes methods members annotations`).
  - `--limit`: optional integer; max returned items; default `50`.
  - `--ignore-case`: optional flag; case-insensitive search.
  - `--regex`: optional flag; treat `keyword` as regular expression.
  - `--show-raw`: optional flag; include `raw` field in text output.
  - `--json`: optional; emit JSON output.
- `validate`:
  - `--indexes`: optional; choose validation scope from `annotation api structured manifest manifest_v2`; default is all indexes.
  - `--fail-on-warning`: optional flag; return non-zero exit code when warnings exist.
  - `--json`: optional; emit JSON output.

## Mandatory Read Set (Must Load Before Coding)

Always load these before writing test pages or production code (paths are relative to the active skill root; this list is authoritative; do not rely on `references/README.md`):

- `references/overview.md`
- `references/grammar-ebnf.md`
- `references/grammar-strict.schema.json`
- `references/grammar-strict-example.json`
- `references/declaration-patterns.md`
- `references/control-flow-async.md`
- `references/oop-annotations.md`
- `references/embedded-java.md`
- `references/template-recipes.md`
- `references/component-encapsulation.md`
- `references/naming-style.md`
- `references/error-fix-rules.md`
- `references/ai-generation-checklist.md`
- `references/syntax-feature-matrix.md`
- `references/evidence-index.md`
- `references/project-conventions.md`
- `references/indexes/t_lang_annotation_index_v2.json`
- `references/indexes/t_lang_api_index.json`
- `references/indexes/t_lang_manifest.json`
- `references/indexes/t_lang_manifest_v2.json`
- `references/indexes/t_lang_structured_members.json`
- When querying index records/counts, use `scrpits/index_json_ops.py` as first choice.
- Project source structure and peer code under `源代码/**/*.t` (read nearby same-domain files first).
- 必读 `绳包/安卓基本库/源代码/安卓_可视化组件.t` 用于组件能力确认（只读检索）。
- Use files under `绳包/**/源代码/*.t` only for lookup/verification (for example `绳包/安卓基本库/源代码/安卓_可视化组件.t`), not as write targets.
- For SKILL policy expansion tasks, additionally sample and compare patterns from:
  - `绳包/安卓基本库/源代码/**/*.t`
- Do not write into the above reference corpora; use them as evidence only.
- Verify property read/write support in the above files before emitting property access or non-built-in layout keys.
- For every layout key, verify it maps to either a property accessor (`属性读/属性写`) or a `@布局属性` method; built-in structural keys `父布局/根布局` are exempt from this lookup.
- For every `@布局属性` method used as layout key, verify two-parameter signature and `@key=value` usage form.
- For relative-position layout keys such as `@位于某组件之下` / `@位于某组件之上`, treat them as planar positioning only (up/down in 2D). Do not infer hierarchy/z-order changes.
- For every layout key-value pair, verify value type compatibility (for example `内容` uses text, `字体大小` uses number, `@位于布局中间` uses bool).
- Inheritance-chain analysis is mandatory before generation: resolve current class/object parent chain first, then decide member access and parameter passing.
- In classes inheriting `窗口`, treat `本对象` as `安卓环境` directly and forbid `本对象.取安卓环境()` generation.
- In conditions, use `==` / `!=` for comparison and reserve `=` for assignment/default values only.
- For layout color keys (for example `背景颜色`), use signed decimal integer literals only; do not use `0x...`/`0X...`.
- In layout declaration blocks, keep `@布局配置` definitions contiguous with no blank lines between adjacent definition pairs.
- For normal object instance declaration, use auto-creation form `变量 名称 : 类型`; forbid `= 创建 类型()` generation.
- For classes with `@禁止创建对象`, forbid auto-creation declaration (`变量 名称 : 类型`) and explicit creation; use class-level static calls or declaration-only reference `变量 名称 : 类型?`.
- Treat `变量 名称 : 类型?` as declaration-only (no auto-creation); assign later when needed.
- Do not use language keywords as any identifier.
- For arrays, use suffix bracket form `类型[]` and support multi-dimension `类型[][][]`. Brace initialization is allowed: `变量 名称 : 类型[] = {值1,值2,值3}`.
- For `小数 -> 单精小数`, do not generate direct conversion. Only generate conversion when strictly required, via `到文本().到单精小数()` (or project-defined equivalent) or an `@code` block.
- For loop early-exit in 结绳 layer, use `退出循环` only. `break` is Java-only and may appear only inside `@code`.
- In multi-branch conditions, use `否则 条件` syntax; do not emit `否则如果`.
- In multi-branch guarded else branch, do not append `则` after `否则 条件`.
- Use `循环(条件)` for conditional loops.
- Validate call arity/type against real function signatures before generation.
- Validate call kind and receiver form before generation: instance method -> `对象.方法(...)`, static method -> `类型.方法(...)`; forbid `到文本(变量名)`-style global misuse.
- Respect class-structure constraints: allow multiple top-level classes in one file, but do not generate nested/inner classes.
- Treat `@导入Java` as class-local independent declarations; do not reuse import scope across classes implicitly.
- For annotation-heavy generation (for example `@附加权限`/`@附加清单`/`@附加清单.全局属性`/`@附加清单.组件属性`/`@附加可变清单`/`@编译时处理参数`), output concise annotation explanations and verify target validity.
- For `@附加可变清单`, use a standalone class + single empty method template-parameter carrier pattern; do not mix extra methods or runtime logic in that carrier class.
- For any Java API/class used in `@导入Java` or embedded Java, verify Android availability first; do not use Java-SE-only APIs, and do not use AndroidX unless user explicitly requests it.
- If Agent is available and not forbidden by user, Agent must participate in all three phases: document scan, project understanding, and generated-code review on every round.

Execution gate:

- Do not start from only 2-3 files.
- Before code output, print a full "已读取文件清单" that covers every file in this mandatory set.
- If Agent is available and user has not forbidden Agent, do not bypass mandatory Agent phases.
- Do not treat first-round review as sufficient; code review must be executed again for each new generation round.

## Reference Loading Map

After the mandatory set is loaded, load request-specific references:

- Grammar and declarations:
  - `references/grammar-ebnf.md`
  - `references/grammar-strict.schema.json`
  - `references/grammar-strict-example.json`
  - `references/declaration-patterns.md`
- Control flow or async/thread logic:
  - `references/control-flow-async.md`
- OOP, generic, operator, annotation semantics:
  - `references/oop-annotations.md`
- Embedded Java bridging:
  - `references/embedded-java.md`
- External Java component wrapper patterns:
  - `references/component-encapsulation.md`
- Fast scaffold generation:
  - `references/template-recipes.md`
- Naming/style normalization:
  - `references/naming-style.md`
- Repair pass:
  - `references/error-fix-rules.md`
  - `references/ai-generation-checklist.md`
- Project conventions and dependency/resource annotations:
  - `references/project-conventions.md`

## Hard Constraints

- Close every opened block (`结束 类/方法/属性/事件/循环/如果/假如`).
- Keep return-style consistent per file (`:` or `为`).
- Keep parameter typing explicit; default values at the tail.
- Use `@运算符重载` for operator methods.
- Keep `@code` and `@end` paired.
- Use `#参数名` / `#this` macros in Java-embedded code.
- Read and write all files in UTF-8 without BOM.
- Use `==` / `!=` (not `=`) in condition comparisons.
- In guarded else branches, never generate `否则 条件 则`; correct form is `否则 条件`.
- Treat Android API compatibility as highest-priority gating for all Java API imports/calls.
- Unless user explicitly requests AndroidX, do not generate any AndroidX import/dependency/API usage.
- Do not bypass the highest-priority Agent rule unless user explicitly forbids Agent.
- Do not skip code review in later turns; per-round review is mandatory when Agent is available and not forbidden.
- Do not invent unseen annotation names unless explicitly requested.
- Do not generate nested/inner class declarations.
- Do not assume `@导入Java` scope is shared between classes.
- For external Java component wrappers, do not use package-prefixed type names inside wrapper `@code` signatures/locals/casts when the type is already imported by `@导入Java`.
- When extending a Java class, use `@后缀代码("extends JavaClassName")` instead of `@前缀代码`. `@前缀代码` is only for class modifiers (like `abstract`).
- Do not instantiate classes annotated with `@禁止创建对象` by any syntax form; treat this as a blocking hard requirement.
- Treat `变量 名称 : 类型?` as declaration-only (no auto-creation).
- Do not use language keywords as identifiers.
- Use array type syntax with one or more `[]` suffixes (`类型[]`, `类型[][]`, `类型[][][]`). Array literals may use brace initialization (`变量 名称 : 类型[] = {值1,值2,值3}`).
- Treat `小数 -> 单精小数` as non-direct-convertible in 结绳 layer; when unavoidable, convert via `到文本().到单精小数()` or use `@code`.
- Use `退出循环` keyword for loop exits in 结绳 statements; do not emit `break` unless inside `@code`.

## Built-In Navigation (Migrated From README)

Core navigation:

- `references/grammar-ebnf.md`: 核心语法骨架（声明/块/参数/返回/表达式入口）
- `references/grammar-strict.schema.json`: 严格 JSON Schema（校验结绳 AST 结构）
- `references/grammar-strict-example.json`: 严格 Schema 最小合法示例
- `references/declaration-patterns.md`: 类、方法、属性、事件、变量、常量声明模板
- `references/control-flow-async.md`: `如果/否则`、`循环`、`假如/是`、容错、线程语法
- `references/oop-annotations.md`: OOP 规则、泛型、运算符重载、注解语义
- `references/embedded-java.md`: `code` 与 `@code/@end` 的嵌入规则与约束
- `references/component-encapsulation.md`: 外部 Java 组件封装规则（导入、`onCreateView/getView`、类型签名）
- `references/template-recipes.md`: 可直接复用的场景模板（组件、适配器、工具类等）
- `references/naming-style.md`: 命名、编码风格、组织规范
- `references/error-fix-rules.md`: 高频错误与自动修复规则
- `references/ai-generation-checklist.md`: 生成前后检查单（硬约束）
- `references/syntax-feature-matrix.md`: 语法特性矩阵（是否必需、典型坑）
- `references/evidence-index.md`: 语法证据（源码路径+行号）
- `references/project-conventions.md`: 项目约定（源代码/绳包、注解引入依赖、布局模式、本对象/父对象）
- `references/error-handling-debug.md`: 错误处理与调试（异常,日志）
- `references/design-patterns.md`: 设计模式（单例、工厂、策略等）
- `references/business-scenarios.md`: 业务场景（登录、注册、支付等）
- `references/indexes/t_lang_api_index.json`: 机器索引（Java API）

Recommended reading order:

1. `references/grammar-ebnf.md` + `references/declaration-patterns.md`
2. `references/oop-annotations.md`
3. `references/embedded-java.md`
4. `references/template-recipes.md` + `references/naming-style.md`
5. `references/ai-generation-checklist.md` + `references/error-fix-rules.md`

Corpus summary:

- 源文件总数：50 (`源代码/**/*.t`)
- 统计摘要：类 368、方法 1856、属性读 540、属性写 467、常量 552、事件定义 167
- 证据索引：`references/evidence-index.md`
- 机器索引：`references/indexes/t_lang_api_index.json`, `references/indexes/t_lang_structured_members.json`

## Authoring Strategy

- Start from smallest compilable skeleton.
- Add properties/events/overrides incrementally.
- Prefer 结绳语句 for simple logic.
- Switch to `@code` for complex Java control/anonymous class/override logic.
- Maintain local style of adjacent `.t` files.

## Deliverable Format

When producing code for users:

1. Output final `.t` code first.
2. Briefly list syntax-critical decisions (annotation, return style, block closure).
3. Mention unresolved assumptions explicitly.

