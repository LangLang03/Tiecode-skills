# 内嵌 Java 规则（`code` / `@code...@end`）

## 1. 两种内嵌方式

单行内嵌：
```t
方法 到文本() : 文本
	code return String.valueOf(#this);
结束 方法
```

块内嵌：
```t
方法 置标题(标题 : 文本)
	@code
	getView().setTitle(#标题);
	@end
结束 方法
```

## 2. 宏替换
- `#this`：当前对象
- `#参数名`：参数注入
- `#<类名>`：类映射入口
- `#<@模板类型1>`：模板类型映射

## 3. Java 注解与语法
`@code` 块中允许 Java 注解，例如：
- `@Override`
- `@SuppressLint`
- `@TargetApi`
- `@JavascriptInterface`

## 4. 典型嵌入模板

覆写视图创建：
```t
@导入Java("rn_1.TimeTextView")
@code
@Override
public TimeTextView onCreateView(android.content.Context context) {
	return new TimeTextView(context);
}
@end
```

事件桥接：
```t
@code
view.setOnClickListener(new View.OnClickListener(){
	@Override
	public void onClick(View v){
		#被单击();
	}
});
@end
```

## 5. 约束与坑
- `@code` 必须和 `@end` 成对。
- 不在 `code` 单行中写多行 Java 结构。
- 结绳标识符引用必须带 `#`，否则编译后会变成未定义 Java 变量。
- 不把 结绳 `返回` 写进 Java 块；Java 块里用 `return`。
- Java 块中禁止直接写结绳字面量/关键字（如 `真/假/空/返回`）；应使用 Java 形式 `true/false/null/return`。
- 目标运行时是 Android，不是 Java SE；`@导入Java` 与 `@code` 中所有 Java API 需先校验 Android 可用性。
- 禁止直接使用 Java SE 专属 API（如 `java.awt.*`、`javax.swing.*`、`java.applet.*`），应改用 Android 框架或项目依赖中可用 API。
- 默认禁止引入 AndroidX；仅在用户明确指定 AndroidX 时才可使用 `androidx.*` 或 AndroidX 依赖。
- 同文件多类场景下，`@导入Java` 按类独立声明；不可假设前一类导入自动作用于后一类。
- 外部 Java 组件封装时，若已使用 `@导入Java("包名.类型名")`，则 `@code` 中 `onCreateView/getView` 的返回类型、局部变量与强转统一使用简单类型名 `类型名`，不要混入 `包名.类型名`。

## 6. 何时选哪种
- 一句表达式：`code ...`
- 多行、匿名类、try/catch、override：`@code ... @end`

## 7. 方法级 `@嵌入式代码` 说明
- `@嵌入式代码` 放在方法上方，用于声明该方法采用嵌入式 Java 展开语义。
- 使用该注解时，方法体可以只保留一个 `@code ... @end` 块；这是合法且常见的写法。
- 典型场景是桥接已有实现类；如果没有对应实现类，可在 `@code` 中自行封装。
- `@code` 块内出现 `});` 这类匿名类/监听器闭合片段属于正常 Java 语法，不应误判为结绳语法错误。
- 规则证据必须按“全库”检索，不得只扫单一目录：至少包含 `源代码/` 与 `测试/绳包/安卓基本库/源代码/`。
- 已整理的全量使用明细见 `references/indexes/embedded_code_annotation_usage.md`（当前为全库检索结果）。

示例（方法体仅 `@code` 块）：
```t
@嵌入式代码
方法 绑定监听()
	@code
	view.setOnClickListener(new View.OnClickListener() {
		@Override
		public void onClick(View v) {
			#被单击();
		}
	});
	@end
结束 方法
```
