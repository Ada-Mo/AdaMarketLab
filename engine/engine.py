from core.database import save_trade, get_next_id
from modules.risk import liquidation_price, risk_reward, trade_score
from broker.okx import get_price


def execute_trade(symbol, direction, entry_price, exit_price, capital, leverage):

    position_value = capital * leverage

    # ⚠️ 标准化收益率（不是绝对值）
    if direction == "long":
        pnl_rate = (exit_price - entry_price) / entry_price
    else:
        pnl_rate = (entry_price - exit_price) / entry_price

    pnl = pnl_rate * position_value

    result = {
        "symbol": symbol,
        "direction": direction,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "capital": capital,
        "leverage": leverage,
        "position_value": position_value,
        "pnl": pnl,
        "pnl_rate": pnl_rate
    }

    return result