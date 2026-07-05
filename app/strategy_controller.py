import pandas as pd

from engine.strategy import ema_strategy, rsi_strategy, breakout_strategy
from engine.backtest import backtest


def handle_strategy_compare():

    df = pd.read_csv("data/price.csv")

    strategies = {
        "EMA": ema_strategy,
        "RSI": rsi_strategy,
        "Breakout": breakout_strategy,
    }

    results = {}

    for name, strategy in strategies.items():

        temp_df = strategy(df)

        print("\n===================")
        print(name)
        print("signal分布：")
        print(temp_df["signal"].value_counts())
        print("===================")

        results[name] = backtest(temp_df)

    print("\n===== V4.4 策略对比 =====")

    for name, result in results.items():
        print(f"{name}:")
        print("  最终资金:", result["final_capital"])
        print("  胜率:", result["win_rate"])
        print("  最大回撤:", result["max_drawdown"])
        print("-------------")