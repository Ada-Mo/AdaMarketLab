import pandas as pd

from engine.backtest import backtest
from engine.strategy import ema_strategy, rsi_strategy, breakout_strategy

def strategy_score(final_capital, win_rate, max_drawdown):
    return (
        final_capital * 10
        + win_rate * 20
        - max_drawdown * 50
    )
def optimize_ema(df):

    results = []

    for short in range(3, 11):
        for long in range(15, 41, 5):

            if short >= long:
                continue

            temp_df = ema_strategy(
                df,
                short_window=short,
                long_window=long
            )

            result = backtest(temp_df)
            score = strategy_score(
                result["final_capital"],
                result["win_rate"],
                result["max_drawdown"]
            )
            results.append({
                "strategy": "EMA",
                "short": short,
                "long": long,
                "final_capital": result["final_capital"],
                "win_rate": result["win_rate"],
                "max_drawdown": result["max_drawdown"],
                "score": score,
            })
    return results
    results.sort(key=lambda x: x["score"], reverse=True)


def optimize_rsi(df):

    results = []

    for period in range(7, 21):
        for overbought in range(65, 85, 5):
            for oversold in range(15, 40, 5):

                temp_df = rsi_strategy(
                    df,
                    period=period,
                    overbought=overbought,
                    oversold=oversold
                )

                result = backtest(temp_df)

                results.append({
                    "strategy": "RSI",
                    "period": period,
                    "overbought": overbought,
                    "oversold": oversold,
                    "final_capital": result["final_capital"],
                    "win_rate": result["win_rate"],
                    "max_drawdown": result["max_drawdown"],
                })
    return results
    results.sort(key=lambda x: x["final_capital"], reverse=True)

def optimize_breakout(df):
        results = []

        for window in range(5, 31, 5):
            temp_df = breakout_strategy(df, window=window)
            result = backtest(temp_df)

            score = strategy_score(
                result["final_capital"],
                result["win_rate"],
                result["max_drawdown"]
            )

            results.append({
                "strategy": "Breakout",
                "window": window,
                "final_capital": result["final_capital"],
                "win_rate": result["win_rate"],
                "max_drawdown": result["max_drawdown"],
                "score": score,
            })
        return results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
