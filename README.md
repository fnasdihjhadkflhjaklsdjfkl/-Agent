# 素材审核与发布排期 Agent

一个可离线运行的 CLI 示例：读取素材、检查审核规则、查询时段、动态调整排期并保存草稿。只保存草稿，不执行真实发布。

## 环境与运行

需要 Python 3.10+，无第三方依赖。运行：

```powershell
python -m src.agent --input examples/normal.json
python -m unittest discover -s tests -v
```

`--input` 可传 JSON 文件；未提供时读取 stdin。每次执行最多 8 次工具调用，超限会返回 `incomplete`。

## 评审入口

- 设计与边界：[docs/02-solution.md](docs/02-solution.md)
- 测试结果：[docs/03-evaluation.md](docs/03-evaluation.md)
- 示例 Trace：`examples/*.json`、`examples/*.trace.json`

## 项目结构

`src/agent.py` 为 CLI、工具和离线决策循环；`tests/` 为可执行测试；`data/` 为合成规则与时段资料。

