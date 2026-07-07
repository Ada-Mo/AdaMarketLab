import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from core.data_manager import load_price_data
from engine.strategy import ema_strategy

BASE_DIR = Path(__file__).resolve().parent.parent
TRADE_FILE = BASE_DIR / "data" / "trades.csv"


def load_trades():
    return pd.read_csv(TRADE_FILE)


def draw_equity_curve():
    df = load_trades()

    if df.empty:
        print("暂无交易记录")
        return

    df["net_pnl"] = df["net_pnl"].astype(float)
    df["equity"] = df["net_pnl"].cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(df["id"], df["equity"], marker="o")
    plt.title("Equity Curve")
    plt.xlabel("Trade ID")
    plt.ylabel("Cumulative PnL")
    plt.grid(True)
    plt.show()


def draw_price_curve():

    df = load_price_data()

    if df.empty:
        print("暂无价格数据，请先使用菜单9下载OKX数据")
        return


    df["timestamp"] = pd.to_datetime(df["timestamp"])


    # 使用策略模块计算
    df = ema_strategy(df)


    plt.figure(figsize=(12, 6))


    # 价格
    plt.plot(
        df["timestamp"],
        df["close"],
        label="Close"
    )


    # EMA
    plt.plot(
        df["timestamp"],
        df["ema_short"],
        label="EMA 5"
    )

    plt.plot(
        df["timestamp"],
        df["ema_long"],
        label="EMA 20"
    )


    # 买入信号
    buy = df[
        (df["signal"] == 1) &
        (df["signal"].shift(1) != 1)
        ]

    plt.scatter(
        buy["timestamp"],
        buy["close"],
        marker="^",
        s=80,
        label="BUY"
    )


    # 卖出信号
    sell = df[
        (df["signal"] == -1) &
        (df["signal"].shift(1) != -1)
        ]

    plt.scatter(
        sell["timestamp"],
        sell["close"],
        marker="v",
        s=80,
        label="SELL"
    )


    plt.title("BTC-USDT EMA Strategy Signal")

    plt.xlabel("Time")
    plt.ylabel("Price")

    plt.gcf().autofmt_xdate()

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    plt.show()


def run_visualization():
    print("1. 交易资金曲线")
    print("2. OKX价格曲线")

    choice = input("请选择图表：")

    if choice == "1":
        draw_equity_curve()

    elif choice == "2":
        draw_price_curve()

    else:
        print("无效选择")