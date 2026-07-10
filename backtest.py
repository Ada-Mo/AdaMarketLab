def backtest(
    df,
    initial_capital=10,
    leverage=1,
    fee_rate=0.0004,
    slip_rate=0.0002,
):
    capital = initial_capital
    peak = initial_capital
    max_drawdown = 0

    position = 0
    entry_price = None
    entry_time = None
    entry_capital = None

    trades = []
    equity_curve = []
    last_equity_timestamp = None

    def trade_cost(current_capital):
        return current_capital * (fee_rate + slip_rate)

    def update_equity(timestamp):
        nonlocal peak, max_drawdown, last_equity_timestamp

        peak = max(peak, capital)

        if peak > 0:
            drawdown = (peak - capital) / peak
            max_drawdown = max(max_drawdown, drawdown)

        record = {
            "timestamp": timestamp,
            "capital": capital,
            "position": position,
        }

        if last_equity_timestamp == timestamp and equity_curve:
            equity_curve[-1] = record
        else:
            equity_curve.append(record)
            last_equity_timestamp = timestamp

    if df is None or len(df) == 0:
        return {
            "final_capital": capital,
            "total_return": 0,
            "win_rate": 0,
            "max_drawdown": 0,
            "trades": 0,
            "trades_list": [],
            "equity_curve": [],
        }

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        price = float(row["close"])
        prev_price = float(prev_row["close"])
        signal = int(row["signal"])

        timestamp = row["timestamp"] if "timestamp" in df.columns else i

        if position == 0:
            if signal == 1:
                capital -= trade_cost(capital)

                position = 1
                entry_price = price
                entry_time = timestamp
                entry_capital = capital

            elif signal == -1:
                capital -= trade_cost(capital)

                position = -1
                entry_price = price
                entry_time = timestamp
                entry_capital = capital

            update_equity(timestamp)
            continue

        change = (price - prev_price) / prev_price
        pnl = capital * leverage * change * position
        capital += pnl

        if signal == 0:
            capital -= trade_cost(capital)

            trades.append({
                "entry_time": entry_time,
                "exit_time": timestamp,
                "direction": "long" if position == 1 else "short",
                "entry_price": entry_price,
                "exit_price": price,
                "entry_capital": entry_capital,
                "exit_capital": capital,
                "pnl": capital - entry_capital,
                "return_rate": (capital - entry_capital) / entry_capital,
            })

            position = 0
            entry_price = None
            entry_time = None
            entry_capital = None

        elif signal != position:
            capital -= trade_cost(capital)

            trades.append({
                "entry_time": entry_time,
                "exit_time": timestamp,
                "direction": "long" if position == 1 else "short",
                "entry_price": entry_price,
                "exit_price": price,
                "entry_capital": entry_capital,
                "exit_capital": capital,
                "pnl": capital - entry_capital,
                "return_rate": (capital - entry_capital) / entry_capital,
            })

            capital -= trade_cost(capital)

            position = signal
            entry_price = price
            entry_time = timestamp
            entry_capital = capital

        update_equity(timestamp)

    if position != 0 and entry_price is not None:
        last_row = df.iloc[-1]
        last_price = float(last_row["close"])
        last_time = last_row["timestamp"] if "timestamp" in df.columns else len(df) - 1

        capital -= trade_cost(capital)

        trades.append({
            "entry_time": entry_time,
            "exit_time": last_time,
            "direction": "long" if position == 1 else "short",
            "entry_price": entry_price,
            "exit_price": last_price,
            "entry_capital": entry_capital,
            "exit_capital": capital,
            "pnl": capital - entry_capital,
            "return_rate": (capital - entry_capital) / entry_capital,
        })

        position = 0
        entry_price = None
        entry_time = None
        entry_capital = None

        update_equity(last_time)

    win_trades = [t for t in trades if t["pnl"] > 0]
    win_rate = len(win_trades) / len(trades) if trades else 0

    return {
        "final_capital": capital,
        "total_return": (capital - initial_capital) / initial_capital,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "trades": len(trades),
        "trades_list": trades,
        "equity_curve": equity_curve,
    }