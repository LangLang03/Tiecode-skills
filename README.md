# tiecode-tlang

Tiecode `.t` 语法与生成规范 Skill。

## 目录
- `SKILL.md`：Skill 触发规则与执行流程
- `agents/openai.yaml`：Skill UI 元数据
- `references/`：语法、实例、规范、证据、Schema
- `references/indexes/`：API 与结构化索引 JSON

总览入口：
- `references/overview.md`

## Scripts
- `scrpits/list_doc_absolute_paths.py`：输出文档绝对路径清单
- `scrpits/index_json_ops.py`：`references/indexes/*.json` 操作工具

示例：
```bash
python scrpits/index_json_ops.py list
python scrpits/index_json_ops.py stats --indexes api structured
python scrpits/index_json_ops.py search 到文本 --indexes api structured --sections methods members --limit 20
python scrpits/index_json_ops.py validate --fail-on-warning
```

## License
- 代码（例如 `SKILL.md`、`agents/**`、`scrpits/**`、工具脚本）采用 [Apache License 2.0](./LICENSE)
- 文档内容（例如 `references/**`、`README.md`）采用 [CC BY 4.0](./LICENSE-CC-BY-4.0)

如需在同一文件中混合代码与文档，请按文件主内容类型适配上述许可证。
