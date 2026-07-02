import csv
import os

DATA_FILE = "data/trades.csv"

FIELDS = [
    "id", "symbol", "market_type", "direction",
    "open_time", "close_time",
    "entry_price", "exit_price",
    "capital", "leverage", "position_value",
    "fee_open", "fee_close", "funding_fee",
    "gross_pnl", "net_pnl", "return_rate",
    "reason_open", "reason_close", "emotion", "review"
]


def init_database():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
        print("交易数据库已创建 ✅")
    else:
        print("交易数据库已存在 ✅")


def get_next_id():
    with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        return len(rows) + 1


def save_trade(trade):
    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(trade)