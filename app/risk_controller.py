from modules.risk import (
    calc_position,
    pnl_simulation,
    fee_calc,
    liquidation_price,
    risk_reward,
    trade_decision,
    recommend_leverage,
)


def handle_risk_calculator():
    price = float(input("BTC开仓价："))
    capital = float(input("保证金："))
    leverage = float(input("杠杆："))
    direction = input("方向(long/short)：").strip().lower()

    position_value, size = calc_position(price, capital, leverage)
    liq_price = liquidation_price(price, leverage, direction)
    fee = fee_calc(position_value)

    print("\n===== 仓位 =====")
    print("仓位价值：", position_value)
    print("BTC数量：", size)

    print("\n===== 风控 =====")
    print("强平价格：", liq_price)

    print("\n===== 成本 =====")
    print("手续费：", fee)

    print("\n===== 盈亏模拟 =====")
    print("+1%：", pnl_simulation(position_value, 1))
    print("-1%：", pnl_simulation(position_value, -1))

    tp = float(input("止盈价："))
    sl = float(input("止损价："))

    rr = risk_reward(price, tp, sl)
    risk_pct = abs(price - sl) / price * 100
    level, advice = trade_decision(leverage, rr, risk_pct)
    rec_lev = recommend_leverage(risk_pct)

    print("\n===== 决策系统 =====")
    print("风险收益比：", rr)
    print("风险百分比：", risk_pct)
    print("交易评级：", level)
    print("建议：", advice)
    print("推荐杠杆：", rec_lev)