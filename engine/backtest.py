def backtest(df, initial_capital=10, leverage=1, fee_rate=0.0004, slip_rate=0.0002):
    capital = float(initial_capital)
    peak = capital
    max_drawdown = 0
    wins = 0
    trades = 0

    for i in range(1, len(df)):
        price = float(df.iloc[i]["close"])
        prev_price = float(df.iloc[i - 1]["close"])
        direction = int(df.iloc[i]["signal"])

        if direction == 0:
            pnl = 0
            print(
                f"{i} "
                f"price={price:.2f} "
                f"dir={direction} "
                f"pnl={pnl:.4f} "
                f"capital={capital:.4f}"
            )
            continue

        change = (price - prev_price) / prev_price
        pnl = capital * leverage * change * direction
        fee_cost = capital * leverage * fee_rate
        slip_cost = capital * leverage * slip_rate
        capital += pnl - fee_cost - slip_cost

        trades += 1
        if pnl > fee_cost + slip_cost:
            wins += 1

        peak = max(peak, capital)
        drawdown = (peak - capital) / peak if peak else 0
        max_drawdown = max(max_drawdown, drawdown)

        print(
            f"{i} "
            f"price={price:.2f} "
            f"dir={direction} "
            f"pnl={pnl:.4f} "
            f"capital={capital:.4f}"
        )

    win_rate = wins / trades if trades else 0
    return {
        "final_capital": capital,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "trades": trades,
    }
