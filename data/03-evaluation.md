# 评估
测试覆盖正常冲突调整、信息缺失、规则风险、无可用时段、保存失败。运行 `python -m unittest discover -s tests -v`。`examples/normal.json` 与 `examples/normal.trace.json` 展示 18:00 被占用后建议 19:00；Mock 仅证明流程，不证明真实模型决策质量。
