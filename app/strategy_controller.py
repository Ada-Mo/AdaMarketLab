from core.data_manager import load_price_data
from core.logger import get_logger
from engine.backtest import backtest
from engine.strategy import ema_strategy, rsi_strategy, breakout_strategy


logger = get_logger()


def handle_strategy_compare():
    df = load_price_data()

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

        logger.info(
            "Strategy compare result | "
            f"strategy={name} | "
            f"final_capital={result['final_capital']:.4f} | "
            f"win_rate={result['win_rate']:.2%} | "
            f"max_drawdown={result['max_drawdown']:.2%}"
        )