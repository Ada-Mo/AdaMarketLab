import pandas as pd

from engine.backtest import backtest
from engine.strategy import ema_strategy


def handle_backtest():
    df = pd.read_csv("data/price.csv")
    df = ema_strategy(df)

    result = backtest(df)

    print("\n===== V4.2 回测结果 =====")
    print("最终资金：", result["final_capital"])
    print("胜率：", result["win_rate"])
    print("最大回撤：", result["max_drawdown"])