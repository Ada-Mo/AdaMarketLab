import pandas as pd


def _clean_signal(df):
    df["signal"] = df["signal"].fillna(0)
    df["signal"] = df["signal"].astype(int)
    df.loc[~df["signal"].isin([1, -1, 0]), "signal"] = 0
    return df


def ema_strategy(df, short_window=5, long_window=20):
    df = df.copy()
    df["ema_short"] = df["close"].ewm(span=short_window, adjust=False).mean()
    df["ema_long"] = df["close"].ewm(span=long_window, adjust=False).mean()
    df["signal"] = 0
    df.loc[df["ema_short"] > df["ema_long"], "signal"] = 1
    df.loc[df["ema_short"] < df["ema_long"], "signal"] = -1
    return _clean_signal(df)


def rsi_strategy(df, period=14, overbought=70, oversold=30):
    df = df.copy()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss.where(loss != 0, pd.NA)
    df["rsi"] = 100 - (100 / (1 + rs))
    df["signal"] = 0
    df.loc[df["rsi"] < oversold, "signal"] = 1
    df.loc[df["rsi"] > overbought, "signal"] = -1
    return _clean_signal(df)


def breakout_strategy(df, window=10):
    df = df.copy()
    prev_high = df["close"].rolling(window=window).max().shift(1)
    prev_low = df["close"].rolling(window=window).min().shift(1)
    df["breakout_high"] = prev_high
    df["breakout_low"] = prev_low
    df["signal"] = 0
    df.loc[df["close"] > prev_high, "signal"] = 1
    df.loc[df["close"] < prev_low, "signal"] = -1
    return _clean_signal(df)
