from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from broker.okx import get_candles, get_price
from core.data_manager import load_price_data, save_price_data
from core.data_validator import validate_price_data
from engine.backtest import backtest
from engine.optimizer import (
    optimize_breakout,
    optimize_ema,
    optimize_rsi,
)
from engine.strategy import (
    breakout_strategy,
    ema_strategy,
    rsi_strategy,
)


app = FastAPI(
    title="AdaMarketLab API",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()

    if not symbol:
        return "BTC-USDT"

    if "-" not in symbol:
        return f"{symbol}-USDT"

    return symbol


def dataframe_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    result = df.copy()

    if "timestamp" in result.columns:
        result["timestamp"] = result["timestamp"].astype(str)

    return result.to_dict(orient="records")


def normalize_result_value(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()

    return value


def normalize_result_dict(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: normalize_result_value(value)
        for key, value in result.items()
    }


def apply_strategy(
    df: pd.DataFrame,
    strategy: str,
    short_window: int = 5,
    long_window: int = 20,
    rsi_period: int = 14,
    overbought: int = 70,
    oversold: int = 30,
    breakout_window: int = 10,
) -> pd.DataFrame:
    strategy = strategy.lower()

    if strategy == "ema":
        if short_window >= long_window:
            raise HTTPException(
                status_code=400,
                detail="EMA short_window must be smaller than long_window.",
            )

        return ema_strategy(
            df,
            short_window=short_window,
            long_window=long_window,
        )

    if strategy == "rsi":
        if oversold >= overbought:
            raise HTTPException(
                status_code=400,
                detail="RSI oversold must be smaller than overbought.",
            )

        return rsi_strategy(
            df,
            period=rsi_period,
            overbought=overbought,
            oversold=oversold,
        )

    if strategy == "breakout":
        if breakout_window < 2:
            raise HTTPException(
                status_code=400,
                detail="Breakout window must be at least 2.",
            )

        return breakout_strategy(
            df,
            window=breakout_window,
        )

    raise HTTPException(
        status_code=404,
        detail=f"Unknown strategy: {strategy}",
    )


@app.get("/")
def root():
    return {
        "system": "AdaMarketLab",
        "status": "online",
        "version": "0.2.0",
    }


@app.get("/api/status")
def api_status():
    return {
        "api": "online",
        "backend": "FastAPI",
        "system": "AdaMarketLab",
        "version": "0.2.0",
        "exchange": "OKX",
        "mode": "public-read-only",
    }


# =========================================================
# Market Data
# =========================================================

@app.get("/api/market/price")
def market_price(symbol: str = "BTC-USDT"):
    normalized_symbol = normalize_symbol(symbol)

    price = get_price(normalized_symbol)

    return {
        "symbol": normalized_symbol,
        "price": price,
        "source": "OKX",
    }


@app.get("/api/market/candles")
def market_candles(
    symbol: str = "BTC-USDT",
    bar: str = "1H",
    limit: int = 100,
):
    normalized_symbol = normalize_symbol(symbol)
    limit = max(1, min(limit, 300))

    df = get_candles(
        symbol=normalized_symbol,
        bar=bar,
        limit=limit,
    )

    issues = validate_price_data(df)

    return {
        "symbol": normalized_symbol,
        "bar": bar,
        "limit": limit,
        "source": "OKX",
        "rows": len(df),
        "issues": issues,
        "candles": dataframe_records(df),
    }


@app.post("/api/market/download")
def download_market_data(
    symbol: str = "BTC-USDT",
    bar: str = "1H",
    limit: int = 300,
):
    normalized_symbol = normalize_symbol(symbol)
    limit = max(1, min(limit, 300))

    df = get_candles(
        symbol=normalized_symbol,
        bar=bar,
        limit=limit,
    )

    issues = validate_price_data(df)

    if issues:
        return {
            "success": False,
            "symbol": normalized_symbol,
            "bar": bar,
            "rows": len(df),
            "issues": issues,
        }

    path = save_price_data(
        df,
        symbol=normalized_symbol,
        timeframe=bar,
        source="OKX",
    )

    return {
        "success": True,
        "symbol": normalized_symbol,
        "bar": bar,
        "rows": len(df),
        "path": str(path),
        "source": "OKX",
        "issues": [],
    }


# =========================================================
# Strategy
# =========================================================

@app.get("/api/strategy/list")
def strategy_list():
    return {
        "strategies": [
            {
                "id": "ema",
                "name": "EMA Crossover",
                "type": "Trend Following",
                "description": (
                    "Compares a fast EMA with a slow EMA and changes "
                    "position when their relationship changes."
                ),
                "parameters": {
                    "short_window": 5,
                    "long_window": 20,
                },
            },
            {
                "id": "rsi",
                "name": "RSI Mean Reversion",
                "type": "Mean Reversion",
                "description": (
                    "Opens long positions in oversold zones and short "
                    "positions in overbought zones."
                ),
                "parameters": {
                    "rsi_period": 14,
                    "overbought": 70,
                    "oversold": 30,
                },
            },
            {
                "id": "breakout",
                "name": "Breakout",
                "type": "Trend Following",
                "description": (
                    "Uses previous rolling highs and lows to detect "
                    "price breakouts."
                ),
                "parameters": {
                    "breakout_window": 10,
                },
            },
        ]
    }


@app.get("/api/strategy/signals")
def strategy_signals(
    strategy: str = "ema",
    short_window: int = 5,
    long_window: int = 20,
    rsi_period: int = 14,
    overbought: int = 70,
    oversold: int = 30,
    breakout_window: int = 10,
):
    df = load_price_data()

    strategy_df = apply_strategy(
        df=df,
        strategy=strategy,
        short_window=short_window,
        long_window=long_window,
        rsi_period=rsi_period,
        overbought=overbought,
        oversold=oversold,
        breakout_window=breakout_window,
    )

    signal_counts = strategy_df["signal"].value_counts().to_dict()

    signal_columns = [
        column
        for column in [
            "timestamp",
            "close",
            "signal",
            "ema_short",
            "ema_long",
            "rsi",
            "breakout_high",
            "breakout_low",
        ]
        if column in strategy_df.columns
    ]

    return {
        "success": True,
        "strategy": strategy.lower(),
        "rows": len(strategy_df),
        "long_signals": int(signal_counts.get(1, 0)),
        "short_signals": int(signal_counts.get(-1, 0)),
        "flat_signals": int(signal_counts.get(0, 0)),
        "signals": dataframe_records(
            strategy_df[signal_columns].tail(120)
        ),
    }


# =========================================================
# Backtest
# =========================================================

@app.get("/api/backtest")
def default_backtest():
    df = load_price_data()
    strategy_df = ema_strategy(df)

    result = backtest(strategy_df)

    return result


@app.get("/api/backtest/run")
def run_backtest(
    strategy: str = "ema",
    initial_capital: float = 10,
    leverage: float = 1,
    fee_rate: float = 0.0004,
    slip_rate: float = 0.0002,
    short_window: int = 5,
    long_window: int = 20,
    rsi_period: int = 14,
    overbought: int = 70,
    oversold: int = 30,
    breakout_window: int = 10,
):
    if initial_capital <= 0:
        raise HTTPException(
            status_code=400,
            detail="initial_capital must be greater than 0.",
        )

    if leverage <= 0:
        raise HTTPException(
            status_code=400,
            detail="leverage must be greater than 0.",
        )

    if fee_rate < 0 or slip_rate < 0:
        raise HTTPException(
            status_code=400,
            detail="fee_rate and slip_rate cannot be negative.",
        )

    df = load_price_data()

    strategy_df = apply_strategy(
        df=df,
        strategy=strategy,
        short_window=short_window,
        long_window=long_window,
        rsi_period=rsi_period,
        overbought=overbought,
        oversold=oversold,
        breakout_window=breakout_window,
    )

    result = backtest(
        strategy_df,
        initial_capital=initial_capital,
        leverage=leverage,
        fee_rate=fee_rate,
        slip_rate=slip_rate,
    )

    return {
        **result,
        "strategy": strategy.lower(),
        "configuration": {
            "initial_capital": initial_capital,
            "leverage": leverage,
            "fee_rate": fee_rate,
            "slip_rate": slip_rate,
            "short_window": short_window,
            "long_window": long_window,
            "rsi_period": rsi_period,
            "overbought": overbought,
            "oversold": oversold,
            "breakout_window": breakout_window,
        },
    }


# =========================================================
# Optimizer
# =========================================================

@app.get("/api/optimizer/run")
def run_optimizer(
    strategy: str = "all",
    top_n: int = 20,
):
    strategy = strategy.lower()
    top_n = max(1, min(top_n, 100))

    df = load_price_data()
    results: list[dict[str, Any]] = []

    if strategy in ["all", "ema"]:
        results.extend(optimize_ema(df))

    if strategy in ["all", "rsi"]:
        results.extend(optimize_rsi(df))

    if strategy in ["all", "breakout"]:
        results.extend(optimize_breakout(df))

    if strategy not in ["all", "ema", "rsi", "breakout"]:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown optimizer strategy: {strategy}",
        )

    results = [
        normalize_result_dict(result)
        for result in results
    ]

    results.sort(
        key=lambda item: float(item.get("score", 0)),
        reverse=True,
    )

    return {
        "success": True,
        "strategy": strategy,
        "total_results": len(results),
        "returned_results": min(top_n, len(results)),
        "best_result": results[0] if results else None,
        "results": results[:top_n],
    }