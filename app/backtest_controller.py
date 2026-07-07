import pandas as pd

from engine.backtest import backtest
from engine.strategy import ema_strategy
from core.logger import get_logger
from core.data_manager import load_price_data


logger = get_logger()


def handle_backtest():

    df = load_price_data()

    df = ema_strategy(df)

    result = backtest(df)

    print("\n===== V4.2 回测结果 =====")
    print("最终资金：", result["final_capital"])
    print("胜率：", result["win_rate"])
    print("最大回撤：", result["max_drawdown"])

    logger.info(
        "Backtest finished | "
        "strategy=EMA | "
        f"final_capital={result['final_capital']:.4f} | "
        f"win_rate={result['win_rate']:.2%} | "
        f"max_drawdown={result['max_drawdown']:.2%}"
    )