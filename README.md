# Ada Market Lab

个人量化交易研究平台。

目标：

- 建立自己的交易数据库
- 研究不同交易策略
- 回测验证
- 风控分析
- 最终连接 OKX API 实盘

---

# 当前功能

✅ 交易记录系统

✅ 盈亏计算

✅ 杠杆计算

✅ 强平价格计算

✅ 风险收益比分析

✅ 推荐杠杆

✅ 资金曲线

✅ 回测系统

✅ EMA策略

✅ RSI策略

✅ Breakout策略

✅ 多策略对比

---

# 项目结构

app/
Controller 层

engine/
交易引擎
策略
回测

modules/
统计
风控
可视化

broker/
交易所接口（OKX）

core/
数据库
菜单

data/
CSV 数据

---

# 当前版本

## V1

项目初始化

---

## V2

交易记录系统

---

## V3

风险控制模块

- 仓位计算
- 手续费
- 强平
- 风险收益比

---

## V4

策略研究平台

### V4.1

资金曲线

### V4.2

回测系统

### V4.3

OKX Broker

### V4.4

多策略系统

- EMA
- RSI
- Breakout

## V4.5 (2026-07-05)

### 新增

- Controller Layer
- app 目录
- Backtest Controller
- Strategy Controller

### 重构

- main.py 从 200+ 行缩减到约 50 行
- Engine 与 Controller 解耦

### 修复

- signal 清洗
- pandas fillna 警告
- backtest 调试输出

---

# 下一步

V5

参数优化

Grid Search

自动寻找最佳 EMA

自动寻找最佳 RSI

自动策略评分

最终目标：

AI 自动生成最优策略。