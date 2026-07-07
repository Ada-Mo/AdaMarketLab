from broker.okx import get_price, get_candles


def normalize_symbol(symbol):
    symbol = symbol.strip().upper()

    if "-" not in symbol:
        symbol = f"{symbol}-USDT"

    return symbol


def handle_api_test():
    raw_symbol = input("请输入交易对，例如 BTC 或 BTC-USDT：")
    symbol = normalize_symbol(raw_symbol)

    price = get_price(symbol)

    print("\n===== OKX 行情测试 =====")
    print("交易对：", symbol)
    print("最新价格：", price)

    df = get_candles(symbol=symbol, bar="1H", limit=100)

    print("\n===== OKX K线测试 =====")
    print("K线数量：", len(df))
    print("\n前5行：")
    print(df.head())
    print("\n后5行：")
    print(df.tail())