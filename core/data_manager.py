import os
import json
import pandas as pd
from datetime import datetime


DATA_DIR = "data"


def save_price_data(
        df,
        filename="price.csv",
        symbol="BTC-USDT",
        timeframe="1H",
        source="OKX"
):

    os.makedirs(DATA_DIR, exist_ok=True)

    path = os.path.join(DATA_DIR, filename)

    df.to_csv(
        path,
        index=False
    )

    metadata = {
        "symbol": symbol,
        "timeframe": timeframe,
        "source": source,
        "rows": len(df),
        "start_time": str(df["timestamp"].iloc[0]),
        "end_time": str(df["timestamp"].iloc[-1]),
        "download_time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    with open(
        os.path.join(DATA_DIR, "metadata.json"),
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=4
        )

    return path


def load_price_data(filename="price.csv"):

    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"数据文件不存在: {path}"
        )

    return pd.read_csv(path)