
from version import VERSION
from core.database import init_database, get_next_id, save_trade
from modules.statistics import run_statistics
from core.menu import show_menu
from modules.visualization import run_visualization
from modules.risk import calc_position, pnl_simulation, fee_calc,liquidation_price
from engine.engine import execute_trade

def input_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("请输入数字。")


def add_trade():
    print("\n=== 新增交易记录 ===")

    trade = {}
    trade["id"] = get_next_id()
    trade["symbol"] = input("币种：").strip().upper()
    trade["market_type"] = input("类型 spot/futures：").strip().lower()
    trade["direction"] = input("方向 long/short/buy：").strip().lower()

    trade["open_time"] = input("开仓时间：").strip()
    trade["close_time"] = input("平仓时间：").strip()

    entry_price = input_float("开仓价：")
    exit_price = input_float("平仓价：")
    capital = input_float("投入本金/保证金 USDT：")
    leverage = input_float("杠杆倍数，现货填 1：")

    position_value = capital * leverage

    fee_open = input_float("开仓手续费 USDT：")
    fee_close = input_float("平仓手续费 USDT：")
    funding_fee = input_float("资金费 USDT，没有填 0：")

    if trade["direction"] in ["long", "buy"]:
        gross_pnl = position_value * ((exit_price - entry_price) / entry_price)
    elif trade["direction"] == "short":
        gross_pnl = position_value * ((entry_price - exit_price) / entry_price)
    else:
        print("方向输入错误，只能 long / short / buy")
        return

    net_pnl = gross_pnl - fee_open - fee_close - funding_fee
    return_rate = net_pnl / capital if capital != 0 else 0

    trade["entry_price"] = entry_price
    trade["exit_price"] = exit_price
    trade["capital"] = capital
    trade["leverage"] = leverage
    trade["position_value"] = position_value
    trade["fee_open"] = fee_open
    trade["fee_close"] = fee_close
    trade["funding_fee"] = funding_fee
    trade["gross_pnl"] = round(gross_pnl, 4)
    trade["net_pnl"] = round(net_pnl, 4)
    trade["return_rate"] = round(return_rate, 6)

    trade["reason_open"] = input("开仓原因：")
    trade["reason_close"] = input("平仓原因：")
    trade["emotion"] = input("情绪状态：")
    trade["review"] = input("复盘结论：")

    print("\n保存成功 ✅")
    print(f"仓位价值：{position_value:.4f} USDT")
    print(f"毛盈亏：{gross_pnl:.4f} USDT")
    print(f"净盈亏：{net_pnl:.4f} USDT")
    print(f"收益率：{return_rate:.2%}")

    save_trade(trade)

def main():
        init_database()

        while True:
            show_menu()
            choice = input("请选择：")

            if choice == "1":
                symbol = input("币种(BTC/ETH)：")
                direction = input("方向(long/short)：")

                entry = float(input("开仓价："))
                exit = float(input("平仓价："))
                capital = float(input("保证金："))
                leverage = float(input("杠杆："))

                result = execute_trade(
                    symbol,
                    direction,
                    entry,
                    exit,
                    capital,
                    leverage
                )

                print("\n===== 交易结果 =====")
                print(result)

            elif choice == "2":
                run_statistics()

            elif choice == "3":
                run_visualization()


            elif choice == "4":

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

                from modules.risk import (
                    calc_position,
                    pnl_simulation,
                    fee_calc,
                    liquidation_price,
                    risk_reward,
                    trade_decision,
                    recommend_leverage
                )
                tp = float(input("止盈价："))
                sl = float(input("止损价："))
                direction = input("方向(long/short)：")

                rr = risk_reward(price, tp, sl)

                risk_pct = abs(price - sl) / price * 100

                level, advice = trade_decision(leverage, rr, risk_pct)

                rec_lev = recommend_leverage(risk_pct)

                print("\n===== 决策系统 =====")

                print("风险收益比：", rr)
                print("风险百分比：", risk_pct)

                print("\n👉 交易评级：", level)
                print("👉 建议：", advice)

                print("👉 推荐杠杆：", rec_lev)

            elif choice == "5":
                break

if __name__ == "__main__":
        main()