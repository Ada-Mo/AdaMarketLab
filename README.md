
# AdaMarketLab

AdaMarketLab 是一个面向个人研究的量化交易研究平台。

项目最初是一个本地 Python CLI 工具，目前正在逐步升级为由 **Python Engine、FastAPI 和 React** 组成的 Web 化量化研究系统。

项目目标不是快速生成某个单一策略，而是建立一个长期可扩展的个人量化研究生态，覆盖：

- 行情数据获取
- 数据验证与管理
- 交易记录
- 风险计算
- 策略研究
- 回测
- 参数优化
- 可视化
- 模拟交易
- 未来交易所账户接入

> 当前版本仅接入 OKX 公共行情 API，不涉及账户、资金或真实下单。

---

## 当前版本

```text
v8.0.0
Web Dashboard & FastAPI Integration