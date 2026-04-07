# 外部 Java 组件封装（对比总结）

## 1. 对比来源
- AI 生成文件：`C:\Users\Administrator\Documents\Tiecode-AndroidLib-master\测试\源代码\初始代码.t`
- 手工修复文件：`C:\Users\Administrator\Music\源代码\初始代码.t`
- 对照结论：`TimeTextView.java` 两侧内容一致；差异集中在 `.t` 封装代码。

## 2. 差异摘要（核心问题）
- `onCreateView` 返回类型：
  - 错误：`public rn_1.TimeTextView onCreateView(...)`
  - 修复：`public TimeTextView onCreateView(...)`
- `onCreateView` 局部变量与创建：
  - 错误：`rn_1.TimeTextView view = new rn_1.TimeTextView(context);`
  - 修复：`TimeTextView view = new TimeTextView(context);`
- `getView` 返回与强转：
  - 错误：`public rn_1.TimeTextView getView() { return (rn_1.TimeTextView) view; }`
  - 修复：`public TimeTextView getView() { return (TimeTextView) view; }`

结论：`@导入Java("rn_1.TimeTextView")` 已完成类型导入后，封装组件的 `@code` 里应统一使用简单类型名 `TimeTextView`，不要在签名/变量/强转里继续写 `rn_1.` 前缀。

## 3. 封装规则（强制）
- `@导入Java` 负责声明全限定名（`包名.类型名`）。
- 在 `@code` 中，`onCreateView/getView` 的返回类型、局部变量、强转统一用简单类型名（`类型名`）。
- `onCreateView` 与 `getView` 必须保持同一类型，不得一处简单名、一处全限定名混写。
- 若出现同名类型冲突，优先精简导入并保持目标类型唯一；不要在同一封装段里混搭两种类型写法。

## 4. 推荐模板
```t
@外部Java文件("./TimeTextView.java")
@导入Java("rn_1.TimeTextView")
类 时间显示框 : 文本框
	@code
	public #<时间显示框>(android.content.Context context) {
		super(context);
	}

	@Override
	public TimeTextView onCreateView(android.content.Context context) {
		TimeTextView view = new TimeTextView(context);
		return view;
	}

	@Override
	public TimeTextView getView() {
		return (TimeTextView) view;
	}
	@end
结束 类
```

## 5. 快速审查点
- 是否同时存在 `@外部Java文件` 与 `@导入Java("包名.类型名")`。
- 是否在 `@code` 的 `onCreateView/getView` 中统一使用简单类型名。
- 是否出现 `包名.类型名` 与 `类型名` 混写。
- `getView` 强转类型是否与 `onCreateView` 返回类型一致。
- 外部 Java 文件的包名与 `@导入Java` 全限定名是否一致。
