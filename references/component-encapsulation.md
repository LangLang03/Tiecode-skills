# 外部 Java 组件封装规范（通用版）

## 1. 适用范围
- 适用于使用 `@外部Java文件` + `@导入Java` 封装 Android 视图组件的场景。
- 本文档为通用规则，不依赖任何固定本地路径或特定示例文件。

## 2. 常见问题模式
- 在 `@导入Java("包名.类型名")` 后，`@code` 内仍混用 `包名.类型名` 与 `类型名`。
- `onCreateView` 返回类型、局部变量类型、`getView` 强转类型不一致。
- `getView()` 返回类型与实际 `view` 对象类型不匹配。

## 3. 强制规则
- `@导入Java` 使用全限定名声明导入：`@导入Java("包名.类型名")`。
- 导入后，在 `@code` 中统一使用简单类型名 `类型名`（返回类型、局部变量、强转保持一致）。
- `onCreateView` 与 `getView` 必须使用同一个目标类型。
- 如果出现同名类型冲突，先消除冲突再生成代码，不允许在同一封装段混写两种类型形态。

## 4. 通用模板
```t
@外部Java文件("./CustomView.java")
@导入Java("demo.widget.CustomView")
类 自定义组件 : 文本框
	@code
	public #<自定义组件>(android.content.Context context) {
		super(context);
	}

	@Override
	public CustomView onCreateView(android.content.Context context) {
		CustomView view = new CustomView(context);
		return view;
	}

	@Override
	public CustomView getView() {
		return (CustomView) view;
	}
	@end
结束 类
```

## 5. 审查清单
- 是否同时声明 `@外部Java文件` 与 `@导入Java("包名.类型名")`。
- `onCreateView` 返回类型是否与创建实例类型一致。
- `getView` 返回与强转类型是否与 `onCreateView` 一致。
- `@code` 内是否仅使用简单类型名，而不是混入 `包名.类型名`。
- 外部 Java 文件中的 `package` 是否与 `@导入Java` 全限定名一致。
