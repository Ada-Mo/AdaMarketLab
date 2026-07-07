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

    def trade_cost(current_capital):
        return current_capital * (fee_rate + slip_rate)

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        price = float(row["close"])
        prev_price = float(prev_row["close"])
        signal = int(row["signal"])

        timestamp = row["timestamp"] if "timestamp" in df.columns else i

        equity_curve.append({
            "timestamp": timestamp,
            "capital": capital,
            "position": position,
        })

        # 空仓状态
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

            continue

        # 持仓状态：逐 K 线计算浮动收益
        change = (price - prev_price) / prev_price
        pnl = capital * leverage * change * position

        capital += pnl
        # 更新最大回撤
        peak = max(peak, capital)
        drawdown = (peak - capital) / peak
        max_drawdown = max(max_drawdown, drawdown)

        # 平仓：signal 变成 0
        # 平仓：signal 变成 0
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

        # 多转空 / 空转多：反手
        elif signal != position:

            # ① 平掉旧仓，扣除平仓交易成本
            capital -= trade_cost(capital)

            # ② 记录旧仓交易
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

            # ③ 建立新仓，扣除开仓交易成本
            capital -= trade_cost(capital)

            # ④ 记录新仓信息
            position = signal
            entry_price = price
            entry_time = timestamp
            entry_capital = capital

    # 最后一根 K 线强制平仓
    # 最后一根 K 线强制平仓
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