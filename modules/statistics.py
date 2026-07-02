import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "trades.csv"

def load_trades():
    return pd.read_csv(DATA_FILE)


def analyze_trades(df):
    if df.empty:
        print("暂无交易记录")
        return

    df["net_pnl"] = df["net_pnl"].astype(float)
    df["gross_pnl"] = df["gross_pnl"].astype(float)
    df["capital"] = df["capital"].astype(float)
    df["fee_open"] = df["fee_open"].astype(float)
    df["fee_close"] = df["fee_close"].astype(float)
    df["funding_fee"] = df["funding_fee"].astype(float)

    df["total_fee"] = df["fee_open"] + df["fee_close"] + df["funding_fee"]

    total_trades = len(df)
    win_trades = len(df[df["net_pnl"] > 0])
    loss_trades = len(df[df["net_pnl"] < 0])

    win_rate = win_trades / total_trades
    total_net_pnl = df["net_pnl"].sum()
    total_fee = df["total_fee"].sum()
    total_capital = df["capital"].sum()

    print("=" * 50)
    print("Ada Market Lab V0.4 统计报告")
    print("=" * 50)

    print(f"总交易次数：{total_trades}")
    print(f"盈利次数：{win_trades}")
    print(f"亏损次数：{loss_trades}")
    print(f"胜率：{win_rate:.2%}")
    print("-" * 50)
    print(f"总净盈亏：{total_net_pnl:.4f} USDT")
    print(f"总手续费：{total_fee:.4f} USDT")
    print(f"手续费 / 总投入本金：{total_fee / total_capital:.2%}")
    print("-" * 50)
    print(f"平均每笔净盈亏：{df['net_pnl'].mean():.4f} USDT")
    print(f"最大单笔盈利：{df['net_pnl'].max():.4f} USDT")
    print(f"最大单笔亏损：{df['net_pnl'].min():.4f} USDT")

def run_statistics():
    df = load_trades()
    analyze_trades(df)

if __name__ == "__main__":
    run_statistics()