import requests


def get_price(symbol="BTC-USDT"):
    url = "https://www.okx.com/api/v5/market/ticker"

    params = {
        "instId": symbol
    }

    res = requests.get(url, params=params)
    data = res.json()

    price = float(data["data"][0]["last"])
    return price