from engine.backtest import backtest
from engine.strategy import ema_strategy
from core.logger import get_logger
from core.data_manager import load_price_data


logger = get_logger()


def print_backtest_report(result):
    print("\n========== Backtest Report ==========")
    print(f"Final Capital: {result['final_capital']:.4f}")
    print(f"Total Return: {result['total_return']:.2%}")
    print(f"Win Rate: {result['win_rate']:.2%}")
    print(f"Trades: {result['trades']}")
    print(f"Max Drawdown: {result['max_drawdown']:.2%}")

    print("\n========== Trades ==========")

    trades = result.get("trades_list", [])

    if not trades:
        print("No trades")
        return

    for idx, trade in enumerate(trades, start=1):
        entry_capital = trade.get("entry_capital", 0)
        exit_capital = trade.get("exit_capital", 0)
        pnl = trade.get("pnl", 0)
        return_rate = trade.get("return_rate", 0)

        print(f"\nTrade {idx}")
        print("------------------------------")
        print(f"Direction: {trade.get('direction')}")
        print(f"Entry Time: {trade.get('entry_time')}")
        print(f"Exit Time: {trade.get('exit_time')}")
        print(f"Entry Price: {trade.get('entry_price')}")
        print(f"Exit Price: {trade.get('exit_price')}")
        print(f"Entry Capital: {entry_capital:.4f}")
        print(f"Exit Capital: {exit_capital:.4f}")
        print(f"PnL: {pnl:.4f}")
        print(f"Return: {return_rate:.2%}")


def handle_backtest():
    df = load_price_data()
    df = ema_strategy(df)

    result = backtest(df)

    print_backtest_report(result)

    logger.info(
        "Backtest finished | "
        "strategy=EMA | "
        f"final_capital={result['final_capital']:.4f} | "
        f"win_rate={result['win_rate']:.2%} | "
        f"max_drawdown={result['max_drawdown']:.2%}"
    )