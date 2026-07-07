import os
from core.data_manager import save_price_data
from broker.okx import get_candles
from core.data_validator import validate_price_data


def handle_download_data():

    symbol = input("请输入交易对(BTC)：")

    if "-" not in symbol:
        symbol = symbol.upper() + "-USDT"

    df = get_candles(
        symbol=symbol,
        bar="1H",
        limit=300
    )


    # 数据验证
    issues = validate_price_data(df)

    if issues:
        print("\n===== 数据验证失败 =====")

        for issue in issues:
            print("-", issue)

        return

    path = save_price_data(
        df,
        symbol=symbol,
        timeframe="1H",
        source="OKX"
    )

    print("保存位置：", path)

    print("\n===== 数据下载完成 =====")
    print("交易对：", symbol)
    print("数据数量：", len(df))
    print(df.head())