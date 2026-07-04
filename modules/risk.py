# modules/risk.py

def calc_position(price, capital, leverage):
    position_value = capital * leverage
    size = position_value / price
    return position_value, size


def pnl_simulation(position_value, pct_move):
    return position_value * (pct_move / 100)


def fee_calc(position_value, fee_rate=0.0005):
    return position_value * fee_rate * 2


# ⭐ 新增：强平价格（简化模型）
def liquidation_price(entry_price, leverage, direction):
    """
    近似强平价（不同交易所略有差异）
    """
    if direction in ["long", "buy"]:
        return entry_price * (1 - 1 / leverage)
    else:
        return entry_price * (1 + 1 / leverage)


# ⭐ 新增：风险评分
def risk_score(leverage, stop_distance_pct):
    """
    简单评分模型
    """
    score = 100

    score -= leverage * 5
    score -= stop_distance_pct * 2

    if score >= 80:
        return "A（低风险）"
    elif score >= 60:
        return "B（中等）"
    elif score >= 40:
        return "C（高风险）"
    else:
        return "D（极高风险）"


def trade_decision(leverage, rr_ratio, risk_pct):
    """
    自动交易决策系统
    """

    score = 100

    # 杠杆惩罚
    if leverage > 5:
        score -= (leverage - 5) * 10

    # 风险收益比奖励
    score += rr_ratio * 15

    # 风险惩罚
    score -= risk_pct * 3

    # 输出等级
    if score >= 80:
        return "A（强烈推荐）", "可以开仓"
    elif score >= 60:
        return "B（可交易）", "可以小仓位尝试"
    elif score >= 40:
        return "C（谨慎）", "不建议重仓"
    else:
        return "D（高风险）", "不建议交易"


def recommend_leverage(risk_pct):
    """
    根据风险自动推荐杠杆
    """

    if risk_pct < 1:
        return "5x - 10x"
    elif risk_pct < 3:
        return "3x - 5x"
    else:
        return "1x - 3x"


def liquidation_price(entry_price, leverage, direction):
    if direction in ["long", "buy"]:
        return entry_price * (1 - 1 / leverage)
    else:
        return entry_price * (1 + 1 / leverage)


def risk_reward(entry, tp, sl):
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        return 0
    return reward / risk


def leverage_score(leverage):
    if leverage <= 3:
        return 90
    elif leverage <= 5:
        return 70
    elif leverage <= 10:
        return 50
    else:
        return 20


def trade_score(leverage, rr_ratio, risk_pct):
    score = 100

    if leverage > 5:
        score -= (leverage - 5) * 8

    score += rr_ratio * 10
    score -= risk_pct * 2

    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    else:
        return "D"

