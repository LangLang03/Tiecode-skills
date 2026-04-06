# 语法骨架（EBNF + 实际约束）

## 1. 文件级结构
```ebnf
file            = [package_decl], annotation*, class_decl+ ;
package_decl    = "包名", IDENT_DOTTED ;
annotation      = "@", IDENT_DOTTED, ["(", ARG_TEXT, ")"] ;
```

最小可用文件：
```t
类 示例类
结束 类
```

约定：默认不写 `包名`，仅在用户明确要求时添加。

## 2. 类定义
```ebnf
class_decl      = annotation*, "类", IDENT_GENERIC, [":", TYPE_REF],
                  class_member*,
                  "结束", "类" ;
```

示例：
```t
@禁止创建对象
类 工具类 : 对象
结束 类
```

## 3. 成员定义
```ebnf
class_member    = annotation*,
                  (const_decl | var_decl | method_decl | prop_read_decl | prop_write_decl | event_decl) ;

const_decl      = "常量", IDENT, [":", TYPE], ["=", EXPR] ;
var_decl        = "变量", IDENT, [":", TYPE], ["=", EXPR] ;
```

## 4. 方法与属性
```ebnf
method_decl     = "方法", METHOD_NAME, "(", [param_list], ")", [return_clause], body, "结束", "方法" ;
prop_read_decl  = "属性读", IDENT, "(", [param_list], ")", return_clause, body, "结束", "属性" ;
prop_write_decl = "属性写", IDENT, "(", [param_list], ")", [return_clause], body, "结束", "属性" ;
return_clause   = (":" | "为"), TYPE ;
```

返回类型分隔符支持 `:` 和 `为`，但单文件内保持一致。

## 5. 参数
```ebnf
param_list      = param, {",", param} ;
param           = IDENT, (":" | "为"), TYPE, ["=", DEFAULT] ;
```

示例：
```t
方法 查找(关键词 : 文本, 起始索引 : 整数 = 0) : 整数
结束 方法
```

## 6. 事件
```ebnf
event_decl      = ("定义事件" | "事件"), IDENT_EVENT, "(", [param_list], ")", [return_clause] ;
```

- `定义事件`：声明回调点。
- `事件`：实现事件体（例如 `事件 对象:事件名(...)`）。

## 7. 方法名特殊符号
```ebnf
METHOD_NAME     = IDENT | "=" | "[]" | "[]=" | "?" | "+" | "-" | "*" | "/" | "==" | "!=" ;
```

用途：构造语义、索引访问、包含判断、运算符重载。

## 8. 类型
```ebnf
TYPE            = TYPE_REF | TYPE_REF "[]" | TYPE_REF "?" ;
TYPE_REF         = IDENT_GENERIC | IDENT_DOTTED ;
IDENT_GENERIC    = IDENT, ["<", TYPE_REF, {",", TYPE_REF}, ">"] ;
```

- 数组：`文本[]`
- 可空：`对象?`
- 泛型：`集合模板类<模板类型1>`

## 9. 方法体
```ebnf
body            = (结绳_stmt* | inline_code_stmt | inline_code_block) ;
inline_code_stmt = "code", JAVA_SNIPPET ;
inline_code_block = "@code", JAVA_BLOCK, "@end" ;
```

## 9.1 属性访问语义（生成约束）
```ebnf
prop_get_expr    = primary, ".", IDENT ;
prop_set_stmt    = primary, ".", IDENT, "=", EXPR ;
layout_method_key = "@", IDENT, "=", EXPR ;
layout_value      = NUMBER | STRING | BOOL | IDENT | EXPR ;
```

- 仅当存在 `属性读 IDENT() : 类型` 时，`primary.IDENT` 读访问才成立。
- 仅当存在 `属性写 IDENT(值 : 类型)` 时，`primary.IDENT = EXPR` 写访问才成立。
- `属性读/属性写` 可以同名并共同构成可读写属性。
- `@布局配置` 字段可映射到两类来源：属性写入语义（`属性读/属性写`）或 `@布局属性` 注解方法（例如 `位于某组件之下`）。
- `@布局配置` 字段名必须有可验证的属性支持或 `@布局属性` 方法支持。
- `@布局属性` 方法在 `@布局配置` 中必须写成 `@方法名=值`，例如 `@位于某组件之下=1`。
- `@布局属性` 方法签名固定为双参数：`(欲设置组件 : 可视化组件, 参数值 : 类型)`。
- 布局值不只数字：可使用文本/逻辑型/数字等字面量（例如 `内容="猜硬币游戏"`、`字体大小=24`、`@位于布局中间=真`），但必须与目标属性或方法参数类型匹配。
- 多组件布局声明块中，不允许在 `@布局配置` + `变量` 对之间插入空行。
- 布局声明块结束后的空行不受此规则限制。

## 10. 块闭合硬约束
- 类：`结束 类`
- 方法：`结束 方法`
- 属性：`结束 属性`
- 事件：`结束 事件`
- 循环：`结束 循环`
- 条件：`结束 如果`
- 分支：`结束 假如`

任何块缺闭合，优先修复闭合，再看类型和参数。

