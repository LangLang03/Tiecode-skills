---
name: tiecode-tlang
description: Write, refactor, review, and repair Tiecode `.t` 缁撶怀浠ｇ爜 with strict syntax-first guidance. Use when tasks mention `.t` files, Tiecode/缁撶怀 language grammar, annotations, OOP wrappers, embedded Java blocks (`code` or `@code/@end`), event-driven component patterns, naming/style normalization, compile-error repair, project conventions (`婧愪唬鐮乣 and `缁冲寘`), layout annotation patterns, object reference semantics (`鏈璞 and `鐖跺璞), and annotation-based dependency/resource loading.
---

# Tiecode T-Lang

## Top-Level Hard Review Requirement (Blocking)

- No assumptions: during review and code generation, do not approve based on guesses like "probably exists" or "usually works."
- If there is any error/diagnostic/fix task, check the issue checklists first: `references/error-fix-rules.md` and `references/ai-generation-checklist.md`.
- Mandatory verification: in every round, verify that referenced layout properties, classes, and methods truly exist and are usable.
- Minimum verification scope:
  - Layout property keys must be valid and resolvable in the current layout/config context.
  - Classes/types must resolve to real definitions within project or dependency scope.
  - Method/member calls must resolve to real callable targets, with matching receiver and signature context.
- Any uncertainty must be verified first; if verification cannot be completed successfully, explicitly inform the user and immediately terminate the current generation/review flow.
- All document viewing and editing must use UTF-8 without BOM.
- This rule has the highest priority, above speed and convenience, and must never be skipped in any round.

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
  - Instance member: `瀵硅薄.鏂规硶(...)`
  - Static member: `绫诲瀷.鏂规硶(...)`
  - Forbid pseudo-global calls when member call is required.
- Construction discipline:
  - Normal typed declaration may auto-create: `鍙橀噺 鍚嶇О : 绫诲瀷`
  - For `@绂佹鍒涘缓瀵硅薄` classes, forbid all instance construction forms.
  - Use static access or declaration-only reference: `鍙橀噺 鍚嶇О : 绫诲瀷?`
- Loop and branch discipline:
  - Use `寰幆(鏉′欢)` (must include parentheses).
  - Multi-branch must use `鍚﹀垯 鏉′欢`, not `鍚﹀垯濡傛灉`.
  - Guarded branch must not use `鍚﹀垯 鏉′欢 鍒檂.
- Layout-key discipline:
  - Built-in structural keys: `鐖跺竷灞€` / `鏍瑰竷灞€`.
  - Other keys must map to `灞炴€ц/灞炴€у啓` or `@甯冨眬灞炴€ methods.
  - `@甯冨眬灞炴€ keys in `@甯冨眬閰嶇疆` must use `@key=value` form.
- Event/lifecycle discipline:
  - Window event wiring should start in `浜嬩欢 <绐楀彛>:鍒涘缓瀹屾瘯()`.
  - Keep event subscriptions centralized (`璁㈤槄浜嬩欢()` first, then side effects).
- Async/UI discipline:
  - UI mutation should happen on main thread callbacks.
  - Always provide explicit failure path for async request logic.

### Java `#` Macro Rules (Hard Requirement)

- Before generating any `code` / `@code...@end`, must inspect **all** lines containing `#` in basic-library corpus `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t` (read-only evidence pass).
- If this evidence pass is skipped, Java-block generation is blocked.
- Only use proven macro forms from corpus evidence:
  - Value/identifier reference: `#鍙傛暟鍚峘 / `#鍙橀噺鍚峘 / `#瀵硅薄`
  - Current wrapped object: `#this`
  - Class literal: `#绫诲瀷.class`
  - Type/member bridge: `#<绫诲瀷>`, `#<@娉ㄨВ绫诲瀷>`, `#<绫诲瀷.鎴愬憳>`, `#<瀵硅薄.鏂规硶>`
- Keep macro token strict:
  - No whitespace between `#` and token.
  - No invented or guessed macro grammar.
  - If uncertain, search evidence first, then emit.
- `#` macros are for Java-embedded context only (`code` or `@code...@end`); do not generate standalone `#` expressions in non-Java statement context.

Typical usage patterns:

```t
@code
// 1) 褰撳墠鍖呰瀵硅薄
return #this.getView();

// 2) 缁戝畾缁撶怀鍙傛暟/鍙橀噺
view.setTag(#鏍囪鍊?;

// 3) 绫诲瀷妗ユ帴涓庢瀯閫犵鍚?public #<绐楀彛缁勪欢>(#<@瀹夊崜鐜> context) { ... }

// 4) 绫诲瓧闈㈤噺
Class<?> clazz = #鐩爣绫诲瀷.class;

// 5) 璋冪敤妗ユ帴鎴愬憳
int px = #<鍍忕礌鎿嶄綔.DP鍒癙X>(#杈硅窛);
#<甯冨眬.甯冨眬琚姞杞?();
@end
```

### Minimal Syntax Examples (Abstract)

Comparison:

```t
// 姝ｇ‘
濡傛灉 璁℃暟 == 0 鍒?缁撴潫 濡傛灉

// 閿欒
濡傛灉 璁℃暟 = 0 鍒?缁撴潫 濡傛灉
```

Loop condition:

```t
// 姝ｇ‘
寰幆(绱㈠紩 < 闀垮害)
	绱㈠紩 = 绱㈠紩 + 1
缁撴潫 寰幆

// 閿欒
寰幆 绱㈠紩 < 闀垮害
	绱㈠紩 = 绱㈠紩 + 1
缁撴潫 寰幆
```

Static vs instance call:

```t
// 姝ｇ‘ 瀹炰緥璋冪敤
鍙橀噺 鏂囨湰鍊?: 鏂囨湰 = 鏁板€?鍒版枃鏈?)

// 姝ｇ‘ 闈欐€佽皟鐢?鍙橀噺 鏃堕棿鎴?: 闀挎暣鏁?= 绯荤粺宸ュ叿.褰撳墠鏃堕棿姣()
```

Non-instantiable class usage:

```t
@绂佹鍒涘缓瀵硅薄
绫?宸ュ叿绫?	@闈欐€?	鏂规硶 鏍￠獙() : 閫昏緫鍨?		杩斿洖 鐪?	缁撴潫 鏂规硶
缁撴潫 绫?
// 姝ｇ‘
鍙橀噺 缁撴灉 : 閫昏緫鍨?= 宸ュ叿绫?鏍￠獙()

// 姝ｇ‘锛堜粎澹版槑锛屼笉鍒涘缓锛?鍙橀噺 寤惰繜寮曠敤 : 宸ュ叿绫?
```

## Absolute Rules (Load First)

- Encoding Redline (Top-Most Priority / Blocking, Above All Rules):
  - All file reads/writes must use UTF-8 without BOM.
  - Do not rely on system-default ANSI/locale codepage for decoding `.t`, `.md`, `.json`, or `.java`.
  - Any generated or modified file must be persisted as UTF-8 (no BOM).
  - If decoded text appears garbled, stop and re-read with explicit UTF-8 before analysis or edits.
- Rule-Evidence Corpus Redline (Highest Priority for policy expansion):
  - When expanding SKILL rules/conventions/requirements, use `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t` as primary evidence source.
  - Evidence lookup is read-only; never write into the above reference corpus.
- Java-`#` Macro Evidence Redline (Top Priority / Blocking):
  - Before writing any Java block (`code` / `@code...@end`), perform a full evidence scan of `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t` lines that contain `#`.
  - Only emit `#` forms already evidenced by the corpus (for example `#this`, `#鍙傛暟鍚峘, `#绫诲瀷.class`, `#<绫诲瀷>`, `#<@娉ㄨВ绫诲瀷>`, `#<绫诲瀷.鎴愬憳>`).
  - Do not invent undocumented `#` syntaxes; violation is blocking and must be fixed before continuing.
- Object-Creation Ban Redline (Hard Requirement / Blocking):
  - For any class annotated with `@绂佹鍒涘缓瀵硅薄`, instance construction is strictly forbidden.
  - Forbidden forms include both auto-creation declaration `鍙橀噺 鍚嶇О : 绫诲瀷` and explicit creation `鍙橀噺 鍚嶇О : 绫诲瀷 = 鍒涘缓 绫诲瀷()`.
  - Violation handling is blocking: report error and stop generation/repair flow until the violation is removed.
  - Before using such class, inspect class definition and use only allowed static members (for example `绫诲瀷.鏂规硶(...)`).
- Agent Redline (Highest Priority):
  - If Agent is available and the user has not explicitly forbidden Agent, Agent participation is mandatory.
  - Agent must cover all three phases: document scan, project understanding, and generated-code review.
  - Generated-code review is required on every generation turn/round; do not reuse first-turn or previous-turn review as a substitute.
  - This rule has higher priority than optimization/convenience rules; do not skip Agent phases.
- Android Runtime Redline (Highest Priority):
  - Target runtime is Android (ART), not Java SE/JRE.
  - Before generating/importing/calling any Java API, verify Android availability first.
  - Availability evidence must come from at least one source: existing project/`缁冲寘` code, Android framework API import path, or declared dependency.
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
- Formatting Redline (Highest): do not introduce unintended spaces in layout blocks or UI literals. Examples: use `鐚滄闈 (not `鐚?姝ｉ潰`), `鎬绘鏁?0|鑳滃埄:0|澶辫触:0` (no auto-added separator spaces unless user asks).
- Layout Key Redline: use canonical Chinese layout keys only (`楂樺害`, not `height`; `瀹藉害`, not `width`).
- Zero Rule +1: read as many relevant references as possible to improve accuracy, and deduplicate findings to avoid repeated scans.
- Write and edit business code only under `婧愪唬鐮?`; do not write code in any path under `缁冲寘/`.
- Zero Rule +2: property semantics are mandatory. `灞炴€ц XXX() : 绫诲瀷` enables `瀵硅薄.XXX` read access; `灞炴€у啓 XXX(鍊?: 绫诲瀷)` enables `瀵硅薄.XXX = 鍊糮 write access; same-name `灞炴€ц/灞炴€у啓` pairs are allowed.
- Zero Rule +3: for every `@甯冨眬閰嶇疆([[...]] )` key (such as `瀹藉害/楂樺害`), verify corresponding accessor support exists before using it. Built-in structural keys `鐖跺竷灞€/鏍瑰竷灞€` are allowed without basic-library member lookup. Treat non-built-in layout keys as property accessors, never as undocumented magic fields.
- Zero Rule +4: methods annotated as layout properties (for example `@甯冨眬灞炴€ methods such as `浣嶄簬鏌愮粍浠朵箣涓媊) are also valid layout keys in `@甯冨眬閰嶇疆`; verify annotation and callable signature from source/index before use.
- Zero Rule +5: `@甯冨眬灞炴€ method signatures are fixed to two parameters only: `(娆茶缃粍浠?: 鍙鍖栫粍浠? 鍙傛暟鍊?: 绫诲瀷)`; do not generate extra parameters.
- Zero Rule +6: when using a layout-property method in `@甯冨眬閰嶇疆`, the key must be prefixed with `@` (for example `@浣嶄簬鏌愮粍浠朵箣涓?1`).
- Zero Rule +6.1: `@浣嶄簬鏌愮粍浠朵箣涓媊 / `@浣嶄簬鏌愮粍浠朵箣涓奰 describe 2D planar relative position (higher/lower placement). They do not change view hierarchy, parent-child relation, or z-order/layer.
- Zero Rule +7: for multi-component layout declaration blocks, keep exactly one blank line after class declaration before the first layout pair, then keep declarations contiguous: no blank line between each `@甯冨眬閰嶇疆` + `鍙橀噺` pair. After the layout block ends, trailing blank lines are not constrained by this rule.
- Zero Rule +8: layout values are not numeric-only. `@甯冨眬閰嶇疆` supports typed values (number/text/bool/etc.) as long as type matches the target property or `@甯冨眬灞炴€ method second parameter. Example keys: `鍐呭="鐚滅‖甯佹父鎴?`, `瀛椾綋澶у皬=24`, `@浣嶄簬甯冨眬涓棿=鐪焋.
- Zero Rule +9锛堢0鏍囪瘑锛? inheritance-chain analysis is mandatory for all classes and objects (not only `绐楀彛` classes). Before emitting member calls/parameter passing, determine current type, parent chain, and whether upcast is valid.
- Zero Rule +10: in classes inheriting `绐楀彛` (including indirect inheritance), `鏈璞 is already Android `Context` (`瀹夊崜鐜`). Pass `鏈璞 directly when APIs need `瀹夊崜鐜`.
- Zero Rule +11: in `绐楀彛` inheritance classes, do not generate `鏈璞?鍙栧畨鍗撶幆澧?)`; only use `鍙栧畨鍗撶幆澧?)` when the current object is not already `瀹夊崜鐜` and conversion is actually needed.
- Zero Rule +12: logical-symbol discipline is mandatory. In conditions, `=` is assignment only; comparisons must use `==` / `!=`. Reject patterns like `濡傛灉 纭竵缁撴灉 = 0 鍒檂.
- Zero Rule +13: color values in `@甯冨眬閰嶇疆` (for example `鑳屾櫙棰滆壊`) must use signed decimal integers, not hex literals (`0x...`/`0X...`). Example: `0xfff5f5f5 -> -657931`, `0xff2c3e50 -> -13877680`.
- Zero Rule +14: inside a multi-component layout declaration block, no blank line is allowed between consecutive layout definitions (`@甯冨眬閰嶇疆` + `鍙橀噺` pairs). Keep pairs strictly contiguous.
- Zero Rule +15: object variables are auto-created by typed declaration. Use `鍙橀噺 瀵硅薄鍚?: 绫诲瀷` directly; do not generate `鍙橀噺 瀵硅薄鍚?: 绫诲瀷 = 鍒涘缓 绫诲瀷()`.
- Zero Rule +16: keyword `鍒涘缓` is internal-only and must not be emitted in business/source code generation.
- Zero Rule +17: multi-branch condition syntax uses `鍚﹀垯 鏉′欢` (without `鍚﹀垯濡傛灉`). Do not generate `鍚﹀垯濡傛灉`.
- Zero Rule +18: conditional-loop syntax must use parentheses: `寰幆(鏉′欢)`; do not generate `寰幆 鏉′欢`.
- Zero Rule +19: function-call signatures are strict. Verify parameter count/types against existing definitions; do not invent overloads (for example forbid `鍒板皬鏁?鏂囨湰)` when only zero-arg `鍒板皬鏁?)` exists).
- Zero Rule +20: function-call form is strict. Instance methods must be called by instance receiver (`瀵硅薄.鏂规硶(...)`); static methods must be called by type/class receiver (`绫诲瀷.鏂规硶(...)`). Forbid global-call misuse such as `鍒版枃鏈?鍙橀噺鍚?` when correct form is `鍙橀噺鍚?鍒版枃鏈?)`.
- Zero Rule +21: guarded-else branch syntax is strict: use `鍚﹀垯 鏉′欢` only (no trailing `鍒檂). Forbid both `鍚﹀垯濡傛灉` and `鍚﹀垯 鏉′欢 鍒檂.
- Zero Rule +22: file/class structure is strict. A file may contain multiple top-level classes, but nested/inner class declarations inside a class are unsupported and must not be generated.
- Zero Rule +23: `@瀵煎叆Java` scope is class-local and independent. Do not assume imports declared for one class apply to other classes in the same file.
- Zero Rule +24: annotation explanation output is mandatory. For every emitted key annotation, explain target, purpose, and critical parameters. Annotations not attached to valid targets and not consumed by compile stage are treated as ineffective and may be cleared during compilation.
- Zero Rule +25: global-class annotations must not be abused. Use `@鍏ㄥ眬绫籤 / `@鍏ㄥ眬鍩虹绫籤 only when cross-module global entry is explicitly required by the task or existing design.
- Zero Rule +26: for `@闄勫姞鍙彉娓呭崟` placeholder completion, define a separate dedicated class containing exactly one empty parameter-carrier method. This method must be used only for compile-time template parameter mapping (for example `鏂规硶 XXX(杈撳叆娉曠被鍚?鏂囨湰,杈撳叆娉曞悕绉?鏂囨湰,杈撳叆娉曢厤缃?鏂囨湰) ...` with no runtime logic).
- Zero Rule +27锛圱op Priority / Hard Requirement锛? for classes annotated `@绂佹鍒涘缓瀵硅薄`, inspect the class definition first and confirm usable members. Treat these classes as non-instantiable utility/meta classes.
- Zero Rule +28锛圱op Priority / Hard Requirement锛? for `@绂佹鍒涘缓瀵硅薄` classes, forbid all instance construction forms, including auto-creation declaration (`鍙橀噺 鍚嶇О : 绫诲瀷`) and explicit creation (`鍙橀噺 鍚嶇О : 绫诲瀷 = 鍒涘缓 绫诲瀷()`). Violation is blocking and must be fixed before continuing.
- Zero Rule +29锛圱op Priority锛? `鍙橀噺 鍚嶇О : 绫诲瀷?` is declaration-only (no auto-creation). Use it for deferred assignment or nullable references when object creation must not happen.
- Zero Rule +30锛圱op Priority锛? do not use language keywords as identifiers (class names, method names, variable names, parameter names, constant names, event names, etc.).
- Zero Rule +31锛圱op Priority锛? array types use suffix brackets and support multi-dimension: `绫诲瀷[]`, `绫诲瀷[][]`, `绫诲瀷[][][]` ... Arrays can be initialized with braces, for example `鍙橀噺 鏁扮粍 : 鏁存暟[] = {1,2,3}`.
- Zero Rule +32锛圱op Priority锛? direct conversion from `灏忔暟` to `鍗曠簿灏忔暟` is not supported. Only when conversion is strictly necessary, use `鍒版枃鏈?).鍒板崟绮惧皬鏁?)` (or project-defined equivalent method name) or use an `@code` block.
- Zero Rule +33锛圱op Priority锛? use keyword `閫€鍑哄惊鐜痐 to exit loop blocks in 缁撶怀 layer. Do not generate Java `break` outside `@code`.
- Zero Rule +34锛圱op Priority锛? for external Java component wrappers (`@澶栭儴Java鏂囦欢` + `@瀵煎叆Java("鍖呭悕.绫诲瀷鍚?)`), use simple imported type name in wrapper `@code` signatures/locals/casts (`绫诲瀷鍚峘), not package-prefixed names.
- Do not generate `鍖呭悕 ...` by default.
- Main window must be `绫?鍚姩绐楀彛 : 绐楀彛`.
- Page classes must inherit `绐楀彛` (do not use `缁勪欢瀹瑰櫒` as page base class).
- Prefer annotation-driven layout (`@甯冨眬閰嶇疆`) with parent-child declaration order.
- If no embedded Java (`code` / `@code...@end`) is used, do not add `@瀵煎叆Java`.
- Zero Rule: before adding constructor boilerplate, check whether the class already defines it; if already defined, do not duplicate; if missing and required, add exactly one constructor boilerplate block.
- Top Rule: before calling any function, search `婧愪唬鐮?` and `缁冲寘/` to confirm it exists, then verify whether it is instance or static and use the correct call form.
- Treat all unverified functions as unavailable; there are no undocumented built-in functions锛堜笉瀛樺湪浠讳綍鏈叕寮€鍐呯疆鍑芥暟锛?
- Do not start coding after reading only a few files; complete the mandatory read set first and report what was read.
- Use `@code` only when 缁撶怀璇彞 cannot express the logic.

## Execution Workflow

1. Detect target domain from file path and surrounding existing code style (`缁撶怀.JVM`, `缁撶怀.瀹夊崜`, `缁撶怀.Meng`, `缁撶怀.鍩烘湰`) and whether the task is syntax generation or syntax profiling.
2. Determine current skill mode first (Global Skill Mode vs Project Skill Mode) and lock doc root to active skill `references/` only.
3. For SKILL policy update tasks, collect evidence from mandatory docs and `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t` before writing.
4. Before writing code, read the full mandatory set (all listed `references/` docs + required project files). If Agent is available and not forbidden by user, run Agent to review docs and project and deduplicate evidence. If index evidence is needed, prefer `scrpits/index_json_ops.py` for query/validation. If Java API is involved, complete Android-availability check before writing imports/calls.
5. Select nearest template and instantiate with minimal edits in `婧愪唬鐮?`.
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
  - `python <active-skill-root>/scrpits/index_json_ops.py search <鍏抽敭璇? --indexes api structured --sections methods members --limit 20`
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
- Project source structure and peer code under `婧愪唬鐮?**/*.t` (read nearby same-domain files first).
- Hard requirement for Java macro generation: read and verify **all** `#` lines under `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t` before emitting any `code` / `@code...@end`.
- 蹇呰 `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?瀹夊崜_鍙鍖栫粍浠?t` 鐢ㄤ簬缁勪欢鑳藉姏纭锛堝彧璇绘绱級銆?- Use files under `缁冲寘/**/婧愪唬鐮?*.t` only for lookup/verification (for example `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?瀹夊崜_鍙鍖栫粍浠?t`), not as write targets.
- For SKILL policy expansion tasks, additionally sample and compare patterns from:
  - `缁冲寘/瀹夊崜鍩烘湰搴?婧愪唬鐮?**/*.t`
- Do not write into the above reference corpora; use them as evidence only.
- Verify property read/write support in the above files before emitting property access or non-built-in layout keys.
- For every layout key, verify it maps to either a property accessor (`灞炴€ц/灞炴€у啓`) or a `@甯冨眬灞炴€ method; built-in structural keys `鐖跺竷灞€/鏍瑰竷灞€` are exempt from this lookup.
- For every `@甯冨眬灞炴€ method used as layout key, verify two-parameter signature and `@key=value` usage form.
- For relative-position layout keys such as `@浣嶄簬鏌愮粍浠朵箣涓媊 / `@浣嶄簬鏌愮粍浠朵箣涓奰, treat them as planar positioning only (up/down in 2D). Do not infer hierarchy/z-order changes.
- For every layout key-value pair, verify value type compatibility (for example `鍐呭` uses text, `瀛椾綋澶у皬` uses number, `@浣嶄簬甯冨眬涓棿` uses bool).
- Inheritance-chain analysis is mandatory before generation: resolve current class/object parent chain first, then decide member access and parameter passing.
- In classes inheriting `绐楀彛`, treat `鏈璞 as `瀹夊崜鐜` directly and forbid `鏈璞?鍙栧畨鍗撶幆澧?)` generation.
- In conditions, use `==` / `!=` for comparison and reserve `=` for assignment/default values only.
- For layout color keys (for example `鑳屾櫙棰滆壊`), use signed decimal integer literals only; do not use `0x...`/`0X...`.
- In layout declaration blocks, keep `@甯冨眬閰嶇疆` definitions contiguous with no blank lines between adjacent definition pairs.
- For normal object instance declaration, use auto-creation form `鍙橀噺 鍚嶇О : 绫诲瀷`; forbid `= 鍒涘缓 绫诲瀷()` generation.
- For classes with `@绂佹鍒涘缓瀵硅薄`, forbid auto-creation declaration (`鍙橀噺 鍚嶇О : 绫诲瀷`) and explicit creation; use class-level static calls or declaration-only reference `鍙橀噺 鍚嶇О : 绫诲瀷?`.
- Treat `鍙橀噺 鍚嶇О : 绫诲瀷?` as declaration-only (no auto-creation); assign later when needed.
- Do not use language keywords as any identifier.
- For arrays, use suffix bracket form `绫诲瀷[]` and support multi-dimension `绫诲瀷[][][]`. Brace initialization is allowed: `鍙橀噺 鍚嶇О : 绫诲瀷[] = {鍊?,鍊?,鍊?}`.
- For `灏忔暟 -> 鍗曠簿灏忔暟`, do not generate direct conversion. Only generate conversion when strictly required, via `鍒版枃鏈?).鍒板崟绮惧皬鏁?)` (or project-defined equivalent) or an `@code` block.
- For loop early-exit in 缁撶怀 layer, use `閫€鍑哄惊鐜痐 only. `break` is Java-only and may appear only inside `@code`.
- In multi-branch conditions, use `鍚﹀垯 鏉′欢` syntax; do not emit `鍚﹀垯濡傛灉`.
- In multi-branch guarded else branch, do not append `鍒檂 after `鍚﹀垯 鏉′欢`.
- Use `寰幆(鏉′欢)` for conditional loops.
- Validate call arity/type against real function signatures before generation.
- Validate call kind and receiver form before generation: instance method -> `瀵硅薄.鏂规硶(...)`, static method -> `绫诲瀷.鏂规硶(...)`; forbid `鍒版枃鏈?鍙橀噺鍚?`-style global misuse.
- Respect class-structure constraints: allow multiple top-level classes in one file, but do not generate nested/inner classes.
- Treat `@瀵煎叆Java` as class-local independent declarations; do not reuse import scope across classes implicitly.
- For annotation-heavy generation (for example `@闄勫姞鏉冮檺`/`@闄勫姞娓呭崟`/`@闄勫姞娓呭崟.鍏ㄥ眬灞炴€/`@闄勫姞娓呭崟.缁勪欢灞炴€/`@闄勫姞鍙彉娓呭崟`/`@缂栬瘧鏃跺鐞嗗弬鏁癭), output concise annotation explanations and verify target validity.
- For `@闄勫姞鍙彉娓呭崟`, use a standalone class + single empty method template-parameter carrier pattern; do not mix extra methods or runtime logic in that carrier class.
- For any Java API/class used in `@瀵煎叆Java` or embedded Java, verify Android availability first; do not use Java-SE-only APIs, and do not use AndroidX unless user explicitly requests it.
- If Agent is available and not forbidden by user, Agent must participate in all three phases: document scan, project understanding, and generated-code review on every round.

Execution gate:
- Do not start from only 2-3 files.
- Before code output, print a full "宸茶鍙栨枃浠舵竻鍗? that covers every file in this mandatory set.
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

- Close every opened block (`缁撴潫 绫?鏂规硶/灞炴€?浜嬩欢/寰幆/濡傛灉/鍋囧`).
- Keep return-style consistent per file (`:` or `涓篳).
- Keep parameter typing explicit; default values at the tail.
- Use `@杩愮畻绗﹂噸杞絗 for operator methods.
- Keep `@code` and `@end` paired.
- Use only evidenced Java `#` macro forms in Java-embedded code (`#鍙傛暟鍚峘 / `#this` / `#绫诲瀷.class` / `#<...>`); do not invent new forms.
- Read and write all files in UTF-8 without BOM.
- Use `==` / `!=` (not `=`) in condition comparisons.
- In guarded else branches, never generate `鍚﹀垯 鏉′欢 鍒檂; correct form is `鍚﹀垯 鏉′欢`.
- Treat Android API compatibility as highest-priority gating for all Java API imports/calls.
- Unless user explicitly requests AndroidX, do not generate any AndroidX import/dependency/API usage.
- Do not bypass the highest-priority Agent rule unless user explicitly forbids Agent.
- Do not skip code review in later turns; per-round review is mandatory when Agent is available and not forbidden.
- Do not invent unseen annotation names unless explicitly requested.
- Do not generate nested/inner class declarations.
- Do not assume `@瀵煎叆Java` scope is shared between classes.
- For external Java component wrappers, do not use package-prefixed type names inside wrapper `@code` signatures/locals/casts when the type is already imported by `@瀵煎叆Java`.
- Do not instantiate classes annotated with `@绂佹鍒涘缓瀵硅薄` by any syntax form; treat this as a blocking hard requirement.
- Treat `鍙橀噺 鍚嶇О : 绫诲瀷?` as declaration-only (no auto-creation).
- Do not use language keywords as identifiers.
- Use array type syntax with one or more `[]` suffixes (`绫诲瀷[]`, `绫诲瀷[][]`, `绫诲瀷[][][]`). Array literals may use brace initialization (`鍙橀噺 鍚嶇О : 绫诲瀷[] = {鍊?,鍊?,鍊?}`).
- Treat `灏忔暟 -> 鍗曠簿灏忔暟` as non-direct-convertible in 缁撶怀 layer; when unavoidable, convert via `鍒版枃鏈?).鍒板崟绮惧皬鏁?)` or use `@code`.
- Use `閫€鍑哄惊鐜痐 keyword for loop exits in 缁撶怀 statements; do not emit `break` unless inside `@code`.

## Built-In Navigation (Migrated From README)

Core navigation:

- `references/grammar-ebnf.md`: 鏍稿績璇硶楠ㄦ灦锛堝０鏄?鍧?鍙傛暟/杩斿洖/琛ㄨ揪寮忓叆鍙ｏ級
- `references/grammar-strict.schema.json`: 涓ユ牸 JSON Schema锛堟牎楠岀粨缁?AST 缁撴瀯锛?- `references/grammar-strict-example.json`: 涓ユ牸 Schema 鏈€灏忓悎娉曠ず渚?- `references/declaration-patterns.md`: 绫汇€佹柟娉曘€佸睘鎬с€佷簨浠躲€佸彉閲忋€佸父閲忓０鏄庢ā鏉?- `references/control-flow-async.md`: `濡傛灉/鍚﹀垯`銆乣寰幆`銆乣鍋囧/鏄痐銆佸閿欍€佺嚎绋嬭娉?- `references/oop-annotations.md`: OOP 瑙勫垯銆佹硾鍨嬨€佽繍绠楃閲嶈浇銆佹敞瑙ｈ涔?- `references/embedded-java.md`: `code` 涓?`@code/@end` 鐨勫祵鍏ヨ鍒欎笌绾︽潫
- `references/component-encapsulation.md`: 澶栭儴 Java 缁勪欢灏佽瑙勫垯锛堝鍏ャ€乣onCreateView/getView`銆佺被鍨嬬鍚嶏級
- `references/template-recipes.md`: 鍙洿鎺ュ鐢ㄧ殑鍦烘櫙妯℃澘锛堢粍浠躲€侀€傞厤鍣ㄣ€佸伐鍏风被绛夛級
- `references/naming-style.md`: 鍛藉悕銆佺紪鐮侀鏍笺€佺粍缁囪鑼?- `references/error-fix-rules.md`: 楂橀閿欒涓庤嚜鍔ㄤ慨澶嶈鍒?- `references/ai-generation-checklist.md`: 鐢熸垚鍓嶅悗妫€鏌ュ崟锛堢‖绾︽潫锛?- `references/syntax-feature-matrix.md`: 璇硶鐗规€х煩闃碉紙鏄惁蹇呴渶銆佸吀鍨嬪潙锛?- `references/evidence-index.md`: 璇硶璇佹嵁锛堟簮鐮佽矾寰?琛屽彿锛?- `references/project-conventions.md`: 椤圭洰绾﹀畾锛堟簮浠ｇ爜/缁冲寘銆佹敞瑙ｅ紩鍏ヤ緷璧栥€佸竷灞€妯″紡銆佹湰瀵硅薄/鐖跺璞★級

Recommended reading order:

1. `references/grammar-ebnf.md` + `references/declaration-patterns.md`
2. `references/oop-annotations.md`
3. `references/embedded-java.md`
4. `references/template-recipes.md` + `references/naming-style.md`
5. `references/ai-generation-checklist.md` + `references/error-fix-rules.md`

Corpus summary:

- 婧愭枃浠舵€绘暟锛?0 (`婧愪唬鐮?**/*.t`)
- 缁熻鎽樿锛氱被 368銆佹柟娉?1856銆佸睘鎬ц 540銆佸睘鎬у啓 467銆佸父閲?552銆佷簨浠跺畾涔?167
- 璇佹嵁绱㈠紩锛歚references/evidence-index.md`
- 鏈哄櫒绱㈠紩锛歚references/indexes/t_lang_api_index.json`, `references/indexes/t_lang_structured_members.json`

## Authoring Strategy

- Start from smallest compilable skeleton.
- Add properties/events/overrides incrementally.
- Prefer 缁撶怀璇彞 for simple logic.
- Switch to `@code` for complex Java control/anonymous class/override logic.
- Maintain local style of adjacent `.t` files.

## Deliverable Format

When producing code for users:

1. Output final `.t` code first.
2. Briefly list syntax-critical decisions (annotation, return style, block closure).
3. Mention unresolved assumptions explicitly.


