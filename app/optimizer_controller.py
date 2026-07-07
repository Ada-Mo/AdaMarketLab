import json
import os
from datetime import datetime

from core.data_manager import load_price_data
from engine.optimizer import (
    optimize_ema,
    optimize_rsi,
    optimize_breakout
)


def save_optimizer_report(results):
    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "reports/optimizer_%Y%m%d_%H%M%S.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=4
        )

    return filename


def handle_optimizer():

    df = load_price_data()

    results = []

    results.extend(optimize_ema(df))
    results.extend(optimize_rsi(df))
    results.extend(optimize_breakout(df))

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print("\n===== V5.3 多策略优化结果 =====")

    for r in results[:10]:
        print(r)

    report = save_optimizer_report(results[:50])

    print("\n优化报告保存：", report)