import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "trades.csv"

def load_trades():
    return pd.read_csv(DATA_FILE)

def draw_equity_curve():

    df = load_trades()

    if df.empty:
        print("暂无交易记录")
        return

    df["net_pnl"] = df["net_pnl"].astype(float)

    df["equity"] = df["net_pnl"].cumsum()

    plt.figure(figsize=(10,5))

    plt.plot(
        df["id"],
        df["equity"],
        marker="o"
    )

    plt.title("Equity Curve")
    plt.xlabel("Trade ID")
    plt.ylabel("Cumulative PnL")

    plt.grid(True)

    plt.show()

def run_visualization():
    draw_equity_curve()


if __name__ == "__main__":
    run_visualization()