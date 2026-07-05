from core.database import get_next_id, save_trade
from engine.engine import execute_trade


def input_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("请输入数字。")


def handle_add_trade():

    symbol = input("币种(BTC/ETH)：")
    direction = input("方向(long/short)：")

    entry = input_float("开仓价：")
    exit_price = input_float("平仓价：")
    capital = input_float("保证金：")
    leverage = input_float("杠杆：")

    result = execute_trade(
        symbol,
        direction,
        entry,
        exit_price,
        capital,
        leverage
    )

    print("\n===== 交易结果 =====")
    print(result)