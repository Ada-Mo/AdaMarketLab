import { useEffect, useMemo, useState } from "react";
import "./App.css";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = "http://127.0.0.1:8000";

const DEFAULT_BACKTEST_FORM = {
  strategy: "ema",
  initialCapital: 10,
  leverage: 1,
  feeRate: 0.0004,
  slipRate: 0.0002,
  shortWindow: 5,
  longWindow: 20,
  rsiPeriod: 14,
  overbought: 70,
  oversold: 30,
  breakoutWindow: 10,
};

const DEFAULT_STRATEGY_FORM = {
  strategy: "ema",
  shortWindow: 5,
  longWindow: 20,
  rsiPeriod: 14,
  overbought: 70,
  oversold: 30,
  breakoutWindow: 10,
};

function App() {
  const [activePage, setActivePage] = useState("dashboard");

  const [apiStatus, setApiStatus] = useState(null);
  const [globalError, setGlobalError] = useState("");

  const [backtestData, setBacktestData] = useState(null);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [backtestForm, setBacktestForm] = useState(
    DEFAULT_BACKTEST_FORM
  );

  const [marketData, setMarketData] = useState(null);
  const [marketLoading, setMarketLoading] = useState(false);

  const [downloadForm, setDownloadForm] = useState({
    symbol: "BTC-USDT",
    bar: "1H",
    limit: 300,
  });
  const [downloadResult, setDownloadResult] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const [exchangeSymbol, setExchangeSymbol] = useState("BTC-USDT");
  const [exchangeTestResult, setExchangeTestResult] =
    useState(null);
  const [exchangeTesting, setExchangeTesting] = useState(false);

  const [strategyList, setStrategyList] = useState([]);
  const [strategyForm, setStrategyForm] = useState(
    DEFAULT_STRATEGY_FORM
  );
  const [strategyResult, setStrategyResult] = useState(null);
  const [strategyLoading, setStrategyLoading] = useState(false);

  const [optimizerStrategy, setOptimizerStrategy] =
    useState("all");
  const [optimizerTopN, setOptimizerTopN] = useState(20);
  const [optimizerResult, setOptimizerResult] = useState(null);
  const [optimizerLoading, setOptimizerLoading] =
    useState(false);

  function formatNumber(value, digits = 4) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "--";
    }

    return number.toFixed(digits);
  }

  function formatPercent(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "--";
    }

    return `${(number * 100).toFixed(2)}%`;
  }

  function normalizeSymbol(symbol) {
    const normalized = String(symbol || "")
      .trim()
      .toUpperCase();

    if (!normalized) {
      return "BTC-USDT";
    }

    if (!normalized.includes("-")) {
      return `${normalized}-USDT`;
    }

    return normalized;
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
      let message = `HTTP ${response.status}`;

      try {
        const body = await response.json();
        message = body.detail || body.error || message;
      } catch {
        // 保留 HTTP 状态信息
      }

      throw new Error(message);
    }

    return response.json();
  }

  async function loadApiStatus() {
    try {
      const result = await requestJson(`${API_BASE}/api/status`);
      setApiStatus(result);
    } catch (error) {
      console.error(error);
      setApiStatus(null);
    }
  }

  async function runDefaultBacktest() {
    setBacktestLoading(true);
    setGlobalError("");

    try {
      const result = await requestJson(
        `${API_BASE}/api/backtest`
      );

      setBacktestData({
        ...result,
        strategy: result.strategy || "ema",
        updated_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);
      setGlobalError(`Backtest Error: ${error.message}`);
    } finally {
      setBacktestLoading(false);
    }
  }

  async function runConfiguredBacktest() {
    setBacktestLoading(true);
    setGlobalError("");

    try {
      const params = new URLSearchParams({
        strategy: backtestForm.strategy,
        initial_capital: String(backtestForm.initialCapital),
        leverage: String(backtestForm.leverage),
        fee_rate: String(backtestForm.feeRate),
        slip_rate: String(backtestForm.slipRate),
        short_window: String(backtestForm.shortWindow),
        long_window: String(backtestForm.longWindow),
        rsi_period: String(backtestForm.rsiPeriod),
        overbought: String(backtestForm.overbought),
        oversold: String(backtestForm.oversold),
        breakout_window: String(
          backtestForm.breakoutWindow
        ),
      });

      const result = await requestJson(
        `${API_BASE}/api/backtest/run?${params.toString()}`
      );

      setBacktestData({
        ...result,
        updated_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);
      setGlobalError(`Backtest Error: ${error.message}`);
    } finally {
      setBacktestLoading(false);
    }
  }

  async function loadMarketData(
    symbol = "BTC-USDT",
    bar = "1H",
    limit = 100
  ) {
    setMarketLoading(true);
    setGlobalError("");

    const normalizedSymbol = normalizeSymbol(symbol);

    try {
      const priceParams = new URLSearchParams({
        symbol: normalizedSymbol,
      });

      const candleParams = new URLSearchParams({
        symbol: normalizedSymbol,
        bar,
        limit: String(limit),
      });

      const [priceResult, candleResult] = await Promise.all([
        requestJson(
          `${API_BASE}/api/market/price?${priceParams.toString()}`
        ),
        requestJson(
          `${API_BASE}/api/market/candles?${candleParams.toString()}`
        ),
      ]);

      setMarketData({
        symbol: priceResult.symbol,
        price: priceResult.price,
        source: priceResult.source,
        bar: candleResult.bar,
        rows: candleResult.rows,
        candles: candleResult.candles || [],
        issues: candleResult.issues || [],
        updated_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);
      setGlobalError(`Market Error: ${error.message}`);
    } finally {
      setMarketLoading(false);
    }
  }

  async function downloadMarketData() {
    setDownloadLoading(true);
    setDownloadResult(null);

    const symbol = normalizeSymbol(downloadForm.symbol);
    const limit = Math.max(
      1,
      Math.min(Number(downloadForm.limit) || 300, 300)
    );

    try {
      const params = new URLSearchParams({
        symbol,
        bar: downloadForm.bar,
        limit: String(limit),
      });

      const result = await requestJson(
        `${API_BASE}/api/market/download?${params.toString()}`,
        {
          method: "POST",
        }
      );

      setDownloadResult({
        ...result,
        requested_at: new Date().toLocaleString(),
      });

      setDownloadForm((previous) => ({
        ...previous,
        symbol,
        limit,
      }));

      if (result.success) {
        await loadMarketData(
          symbol,
          downloadForm.bar,
          Math.min(limit, 100)
        );
      }
    } catch (error) {
      console.error(error);

      setDownloadResult({
        success: false,
        issues: [error.message],
        requested_at: new Date().toLocaleString(),
      });
    } finally {
      setDownloadLoading(false);
    }
  }

  async function testExchangeConnection() {
    setExchangeTesting(true);
    setExchangeTestResult(null);

    const symbol = normalizeSymbol(exchangeSymbol);

    try {
      const params = new URLSearchParams({ symbol });

      const result = await requestJson(
        `${API_BASE}/api/market/price?${params.toString()}`
      );

      setExchangeSymbol(result.symbol);

      setExchangeTestResult({
        success: true,
        symbol: result.symbol,
        price: result.price,
        source: result.source,
        message: "OKX Public API connection succeeded.",
        tested_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);

      setExchangeTestResult({
        success: false,
        message: `Connection failed: ${error.message}`,
        tested_at: new Date().toLocaleString(),
      });
    } finally {
      setExchangeTesting(false);
    }
  }

  async function loadStrategyList() {
    try {
      const result = await requestJson(
        `${API_BASE}/api/strategy/list`
      );

      setStrategyList(result.strategies || []);
    } catch (error) {
      console.error(error);
      setGlobalError(`Strategy Error: ${error.message}`);
    }
  }

  async function runStrategySignals() {
    setStrategyLoading(true);
    setGlobalError("");

    try {
      const params = new URLSearchParams({
        strategy: strategyForm.strategy,
        short_window: String(strategyForm.shortWindow),
        long_window: String(strategyForm.longWindow),
        rsi_period: String(strategyForm.rsiPeriod),
        overbought: String(strategyForm.overbought),
        oversold: String(strategyForm.oversold),
        breakout_window: String(
          strategyForm.breakoutWindow
        ),
      });

      const result = await requestJson(
        `${API_BASE}/api/strategy/signals?${params.toString()}`
      );

      setStrategyResult({
        ...result,
        updated_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);
      setGlobalError(`Strategy Error: ${error.message}`);
    } finally {
      setStrategyLoading(false);
    }
  }

  async function runOptimizer() {
    setOptimizerLoading(true);
    setOptimizerResult(null);
    setGlobalError("");

    try {
      const params = new URLSearchParams({
        strategy: optimizerStrategy,
        top_n: String(optimizerTopN),
      });

      const result = await requestJson(
        `${API_BASE}/api/optimizer/run?${params.toString()}`
      );

      setOptimizerResult({
        ...result,
        updated_at: new Date().toLocaleString(),
      });
    } catch (error) {
      console.error(error);
      setGlobalError(`Optimizer Error: ${error.message}`);
    } finally {
      setOptimizerLoading(false);
    }
  }

  useEffect(() => {
    loadApiStatus();
    runDefaultBacktest();
    loadMarketData();
    loadStrategyList();
  }, []);

  const trades = backtestData?.trades_list || [];
  const equityCurve = backtestData?.equity_curve || [];
  const candles = marketData?.candles || [];

  const strategySignals = strategyResult?.signals || [];
  const optimizerRows = optimizerResult?.results || [];

  const winningTrades = trades.filter(
    (trade) => Number(trade.pnl) > 0
  ).length;

  const losingTrades = trades.filter(
    (trade) => Number(trade.pnl) < 0
  ).length;

  const averageReturn =
    trades.length > 0
      ? trades.reduce(
          (total, trade) =>
            total + Number(trade.return_rate || 0),
          0
        ) / trades.length
      : 0;

  const lastEquity = equityCurve[equityCurve.length - 1];

  const currentPosition =
    lastEquity?.position === 1
      ? "LONG"
      : lastEquity?.position === -1
        ? "SHORT"
        : "FLAT";

  const selectedStrategy = useMemo(
    () =>
      strategyList.find(
        (item) => item.id === strategyForm.strategy
      ),
    [strategyList, strategyForm.strategy]
  );

  const pageTitles = {
    dashboard: "Dashboard",
    market: "Market Data",
    dataCenter: "Data Center",
    exchange: "Exchange",
    backtest: "Backtest",
    strategy: "Strategy",
    optimizer: "Optimizer",
  };

  function renderNavigationButton(page, label) {
    return (
      <button
        className={
          activePage === page
            ? "nav-item active"
            : "nav-item"
        }
        onClick={() => {
          setActivePage(page);
          setGlobalError("");

          if (page === "market") {
            loadMarketData(
              downloadForm.symbol,
              downloadForm.bar,
              100
            );
          }

          if (page === "strategy" && !strategyResult) {
            runStrategySignals();
          }

          if (page === "exchange") {
            loadApiStatus();
          }
        }}
      >
        {label}
      </button>
    );
  }

  function renderEquityChart() {
    return (
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={equityCurve}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#20242c"
              vertical={false}
            />

            <XAxis dataKey="timestamp" hide />

            <YAxis
              dataKey="capital"
              stroke="#555b65"
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={48}
              domain={["auto", "auto"]}
            />

            <Tooltip
              contentStyle={{
                background: "#0f1218",
                border:
                  "1px solid rgba(85, 214, 194, 0.28)",
                borderRadius: "8px",
                color: "#f5f7fb",
                fontSize: "12px",
              }}
              labelStyle={{
                color: "#55d6c2",
              }}
              formatter={(value) => [
                `$${formatNumber(value, 4)}`,
                "Capital",
              ]}
            />

            <Line
              type="monotone"
              dataKey="capital"
              stroke="#55d6c2"
              strokeWidth={2}
              dot={false}
              activeDot={{
                r: 4,
                fill: "#55d6c2",
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  function renderTradeTable(limit = 8) {
    const visibleTrades =
      limit === null ? trades : trades.slice(0, limit);

    return (
      <div className="trade-table">
        <div className="trade-row trade-header">
          <span>Direction</span>
          <span>Entry</span>
          <span>Exit</span>
          <span>PnL</span>
          <span>Return</span>
        </div>

        {visibleTrades.length === 0 && (
          <div className="empty-state">
            No trades available.
          </div>
        )}

        {visibleTrades.map((trade, index) => (
          <div
            className="trade-row"
            key={`${trade.entry_time}-${index}`}
          >
            <span
              className={
                trade.direction === "long"
                  ? "long"
                  : "short"
              }
            >
              {String(
                trade.direction || "--"
              ).toUpperCase()}
            </span>

            <span>
              {formatNumber(trade.entry_price, 2)}
            </span>

            <span>
              {formatNumber(trade.exit_price, 2)}
            </span>

            <span
              className={
                Number(trade.pnl) >= 0
                  ? "profit"
                  : "loss"
              }
            >
              {Number(trade.pnl) >= 0 ? "+" : ""}
              {formatNumber(trade.pnl, 4)}
            </span>

            <span
              className={
                Number(trade.return_rate) >= 0
                  ? "profit"
                  : "loss"
              }
            >
              {formatPercent(trade.return_rate)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  function renderStrategyParameters() {
    if (strategyForm.strategy === "ema") {
      return (
        <>
          <label className="form-field">
            <span>Fast EMA</span>

            <input
              type="number"
              min="1"
              value={strategyForm.shortWindow}
              onChange={(event) =>
                setStrategyForm((previous) => ({
                  ...previous,
                  shortWindow: Number(event.target.value),
                }))
              }
            />
          </label>

          <label className="form-field">
            <span>Slow EMA</span>

            <input
              type="number"
              min="2"
              value={strategyForm.longWindow}
              onChange={(event) =>
                setStrategyForm((previous) => ({
                  ...previous,
                  longWindow: Number(event.target.value),
                }))
              }
            />
          </label>
        </>
      );
    }

    if (strategyForm.strategy === "rsi") {
      return (
        <>
          <label className="form-field">
            <span>RSI Period</span>

            <input
              type="number"
              min="2"
              value={strategyForm.rsiPeriod}
              onChange={(event) =>
                setStrategyForm((previous) => ({
                  ...previous,
                  rsiPeriod: Number(event.target.value),
                }))
              }
            />
          </label>

          <label className="form-field">
            <span>Overbought</span>

            <input
              type="number"
              value={strategyForm.overbought}
              onChange={(event) =>
                setStrategyForm((previous) => ({
                  ...previous,
                  overbought: Number(event.target.value),
                }))
              }
            />
          </label>

          <label className="form-field">
            <span>Oversold</span>

            <input
              type="number"
              value={strategyForm.oversold}
              onChange={(event) =>
                setStrategyForm((previous) => ({
                  ...previous,
                  oversold: Number(event.target.value),
                }))
              }
            />
          </label>
        </>
      );
    }

    return (
      <label className="form-field">
        <span>Breakout Window</span>

        <input
          type="number"
          min="2"
          value={strategyForm.breakoutWindow}
          onChange={(event) =>
            setStrategyForm((previous) => ({
              ...previous,
              breakoutWindow: Number(event.target.value),
            }))
          }
        />
      </label>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <h1>AdaMarketLab</h1>
          <span>Quant Research System</span>
        </div>

        <nav className="nav">
          {renderNavigationButton("dashboard", "Dashboard")}
          {renderNavigationButton("market", "Market Data")}
          {renderNavigationButton(
            "dataCenter",
            "Data Center"
          )}
          {renderNavigationButton("exchange", "Exchange")}
          {renderNavigationButton("backtest", "Backtest")}
          {renderNavigationButton("strategy", "Strategy")}
          {renderNavigationButton("optimizer", "Optimizer")}
        </nav>

        <div className="system-status">
          <span
            className={
              apiStatus
                ? "status-dot"
                : "status-dot error"
            }
          ></span>

          {apiStatus ? "System Online" : "System Offline"}
        </div>
      </aside>

      <main className="main-content">
        <header className="header">
          <div>
            <p className="eyebrow">ADA QUANT RESEARCH</p>
            <h2>{pageTitles[activePage]}</h2>
          </div>

          <div className="header-actions">
            <div className="market-status">
              <span
                className={
                  apiStatus
                    ? "status-dot"
                    : "status-dot error"
                }
              ></span>

              {apiStatus ? "API Connected" : "API Offline"}
            </div>

            {activePage === "dashboard" && (
              <button
                className="run-button"
                onClick={runDefaultBacktest}
                disabled={backtestLoading}
              >
                {backtestLoading
                  ? "Running..."
                  : "Run Backtest"}
              </button>
            )}

            {activePage === "market" && (
              <button
                className="run-button"
                onClick={() =>
                  loadMarketData(
                    downloadForm.symbol,
                    downloadForm.bar,
                    100
                  )
                }
                disabled={marketLoading}
              >
                {marketLoading
                  ? "Refreshing..."
                  : "Refresh Market"}
              </button>
            )}

            {activePage === "dataCenter" && (
              <button
                className="run-button"
                onClick={downloadMarketData}
                disabled={downloadLoading}
              >
                {downloadLoading
                  ? "Downloading..."
                  : "Download Data"}
              </button>
            )}

            {activePage === "exchange" && (
              <button
                className="run-button"
                onClick={testExchangeConnection}
                disabled={exchangeTesting}
              >
                {exchangeTesting
                  ? "Testing..."
                  : "Test Connection"}
              </button>
            )}

            {activePage === "backtest" && (
              <button
                className="run-button"
                onClick={runConfiguredBacktest}
                disabled={backtestLoading}
              >
                {backtestLoading
                  ? "Running..."
                  : "Run Backtest"}
              </button>
            )}

            {activePage === "strategy" && (
              <button
                className="run-button"
                onClick={runStrategySignals}
                disabled={strategyLoading}
              >
                {strategyLoading
                  ? "Calculating..."
                  : "Generate Signals"}
              </button>
            )}

            {activePage === "optimizer" && (
              <button
                className="run-button"
                onClick={runOptimizer}
                disabled={optimizerLoading}
              >
                {optimizerLoading
                  ? "Optimizing..."
                  : "Run Optimizer"}
              </button>
            )}
          </div>
        </header>

        {globalError && (
          <div className="error-panel">
            {globalError}
          </div>
        )}

        {activePage === "dashboard" && (
          <>
            {!backtestData && (
              <div className="loading-panel">
                Loading backtest data...
              </div>
            )}

            {backtestData && (
              <>
                <section className="metrics-grid">
                  <div className="metric-card">
                    <span>Final Capital</span>
                    <strong>
                      $
                      {formatNumber(
                        backtestData.final_capital,
                        4
                      )}
                    </strong>
                    <small>Backtest Result</small>
                  </div>

                  <div className="metric-card">
                    <span>Total Return</span>
                    <strong>
                      {formatPercent(
                        backtestData.total_return
                      )}
                    </strong>
                    <small>Strategy Performance</small>
                  </div>

                  <div className="metric-card">
                    <span>Win Rate</span>
                    <strong>
                      {formatPercent(backtestData.win_rate)}
                    </strong>
                    <small>
                      {backtestData.trades} Completed Trades
                    </small>
                  </div>

                  <div className="metric-card">
                    <span>Max Drawdown</span>
                    <strong>
                      {formatPercent(
                        backtestData.max_drawdown
                      )}
                    </strong>
                    <small>Risk Measurement</small>
                  </div>
                </section>

                <div className="update-time">
                  Last Updated:{" "}
                  {backtestData.updated_at || "Just now"}
                </div>

                <section className="metrics-grid secondary">
                  <div className="metric-card small-card">
                    <span>Total Trades</span>
                    <strong>{backtestData.trades}</strong>
                    <small>Completed Positions</small>
                  </div>

                  <div className="metric-card small-card">
                    <span>Winning Trades</span>
                    <strong className="profit">
                      {winningTrades}
                    </strong>
                    <small>Positive Return</small>
                  </div>

                  <div className="metric-card small-card">
                    <span>Losing Trades</span>
                    <strong className="loss">
                      {losingTrades}
                    </strong>
                    <small>Negative Return</small>
                  </div>

                  <div className="metric-card small-card">
                    <span>Avg Return</span>
                    <strong>
                      {(averageReturn * 100).toFixed(2)}%
                    </strong>
                    <small>Per Trade</small>
                  </div>
                </section>

                <section className="dashboard-grid">
                  <div className="panel">
                    <div className="panel-header">
                      <div>
                        <span>PERFORMANCE</span>
                        <h3>Equity Curve</h3>
                      </div>

                      <button>
                        {equityCurve.length} Points
                      </button>
                    </div>

                    {renderEquityChart()}
                  </div>

                  <div className="panel">
                    <div className="panel-header">
                      <div>
                        <span>ACTIVE MODEL</span>
                        <h3>Strategy</h3>
                      </div>
                    </div>

                    <div className="strategy-info">
                      <strong>
                        {String(
                          backtestData.strategy || "EMA"
                        ).toUpperCase()}
                      </strong>

                      <div>
                        <span>Market</span>
                        <b>BTC-USDT</b>
                      </div>

                      <div>
                        <span>Timeframe</span>
                        <b>1H</b>
                      </div>

                      <div>
                        <span>Trades</span>
                        <b>{backtestData.trades}</b>
                      </div>
                    </div>

                    <div className="position-status">
                      <span>Current Position</span>

                      <strong
                        className={currentPosition.toLowerCase()}
                      >
                        {currentPosition}
                      </strong>
                    </div>
                  </div>
                </section>

                <section className="panel trades-panel">
                  <div className="panel-header">
                    <div>
                      <span>BACKTEST HISTORY</span>
                      <h3>Recent Trades</h3>
                    </div>

                    <button>
                      {backtestData.trades} Trades
                    </button>
                  </div>

                  {renderTradeTable(8)}
                </section>
              </>
            )}
          </>
        )}

        {activePage === "market" && (
          <>
            <section className="metrics-grid">
              <div className="metric-card">
                <span>Symbol</span>
                <strong>
                  {marketData?.symbol || "BTC-USDT"}
                </strong>
                <small>Trading Pair</small>
              </div>

              <div className="metric-card">
                <span>Current Price</span>
                <strong>
                  ${formatNumber(marketData?.price, 2)}
                </strong>
                <small>Latest OKX Price</small>
              </div>

              <div className="metric-card">
                <span>Timeframe</span>
                <strong>{marketData?.bar || "1H"}</strong>
                <small>Candle Interval</small>
              </div>

              <div className="metric-card">
                <span>Rows</span>
                <strong>{marketData?.rows ?? "--"}</strong>
                <small>Loaded Candles</small>
              </div>
            </section>

            <div className="update-time">
              Last Updated:{" "}
              {marketData?.updated_at || "Loading..."}
            </div>

            <section className="panel trades-panel">
              <div className="panel-header">
                <div>
                  <span>MARKET DATA</span>
                  <h3>Recent Candles</h3>
                </div>

                <button>
                  {marketData?.source || "OKX"}
                </button>
              </div>

              <div className="trade-table">
                <div className="trade-row market-header">
                  <span>Time</span>
                  <span>Open</span>
                  <span>High</span>
                  <span>Low</span>
                  <span>Close</span>
                  <span>Volume</span>
                </div>

                {candles
                  .slice(-12)
                  .reverse()
                  .map((candle, index) => (
                    <div
                      className="trade-row market-row"
                      key={`${candle.timestamp}-${index}`}
                    >
                      <span>
                        {String(candle.timestamp).slice(
                          0,
                          16
                        )}
                      </span>
                      <span>
                        {formatNumber(candle.open, 2)}
                      </span>
                      <span>
                        {formatNumber(candle.high, 2)}
                      </span>
                      <span>
                        {formatNumber(candle.low, 2)}
                      </span>
                      <span>
                        {formatNumber(candle.close, 2)}
                      </span>
                      <span>
                        {formatNumber(candle.volume, 2)}
                      </span>
                    </div>
                  ))}
              </div>
            </section>
          </>
        )}

        {activePage === "dataCenter" && (
          <>
            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>DATA COLLECTION</span>
                    <h3>Download Market Data</h3>
                  </div>

                  <button>OKX Public API</button>
                </div>

                <div className="form-grid">
                  <label className="form-field">
                    <span>Trading Pair</span>

                    <input
                      value={downloadForm.symbol}
                      onChange={(event) =>
                        setDownloadForm((previous) => ({
                          ...previous,
                          symbol: event.target.value,
                        }))
                      }
                    />
                  </label>

                  <label className="form-field">
                    <span>Timeframe</span>

                    <select
                      value={downloadForm.bar}
                      onChange={(event) =>
                        setDownloadForm((previous) => ({
                          ...previous,
                          bar: event.target.value,
                        }))
                      }
                    >
                      <option value="1m">1 Minute</option>
                      <option value="5m">5 Minutes</option>
                      <option value="15m">
                        15 Minutes
                      </option>
                      <option value="30m">
                        30 Minutes
                      </option>
                      <option value="1H">1 Hour</option>
                      <option value="4H">4 Hours</option>
                      <option value="1D">1 Day</option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Candle Limit</span>

                    <input
                      type="number"
                      min="1"
                      max="300"
                      value={downloadForm.limit}
                      onChange={(event) =>
                        setDownloadForm((previous) => ({
                          ...previous,
                          limit: event.target.value,
                        }))
                      }
                    />
                  </label>
                </div>

                <button
                  className="run-button form-action"
                  onClick={downloadMarketData}
                  disabled={downloadLoading}
                >
                  {downloadLoading
                    ? "Downloading..."
                    : "Download and Save"}
                </button>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>DATA STATUS</span>
                    <h3>Collection Result</h3>
                  </div>
                </div>

                {!downloadResult && (
                  <div className="empty-state">
                    Configure the request and download data.
                  </div>
                )}

                {downloadResult && (
                  <div className="strategy-info">
                    <strong
                      className={
                        downloadResult.success
                          ? "profit"
                          : "loss"
                      }
                    >
                      {downloadResult.success
                        ? "Download Successful"
                        : "Download Failed"}
                    </strong>

                    <div>
                      <span>Symbol</span>
                      <b>
                        {downloadResult.symbol ||
                          normalizeSymbol(
                            downloadForm.symbol
                          )}
                      </b>
                    </div>

                    <div>
                      <span>Timeframe</span>
                      <b>
                        {downloadResult.bar ||
                          downloadForm.bar}
                      </b>
                    </div>

                    <div>
                      <span>Rows</span>
                      <b>{downloadResult.rows ?? "--"}</b>
                    </div>

                    <div>
                      <span>Saved Path</span>
                      <b>{downloadResult.path || "--"}</b>
                    </div>
                  </div>
                )}
              </div>
            </section>
          </>
        )}

        {activePage === "exchange" && (
          <>
            <section className="metrics-grid">
              <div className="metric-card">
                <span>Exchange</span>
                <strong>OKX</strong>
                <small>Primary Data Provider</small>
              </div>

              <div className="metric-card">
                <span>Public API</span>
                <strong
                  className={apiStatus ? "profit" : "loss"}
                >
                  {apiStatus ? "ONLINE" : "OFFLINE"}
                </strong>
                <small>Market Read Access</small>
              </div>

              <div className="metric-card">
                <span>Private API</span>
                <strong>NOT CONFIGURED</strong>
                <small>Account Access Disabled</small>
              </div>

              <div className="metric-card">
                <span>Trading Mode</span>
                <strong>READ ONLY</strong>
                <small>No Order Permission</small>
              </div>
            </section>

            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>CONNECTION TEST</span>
                    <h3>OKX Public API</h3>
                  </div>
                </div>

                <div className="form-grid">
                  <label className="form-field">
                    <span>Test Symbol</span>

                    <input
                      value={exchangeSymbol}
                      onChange={(event) =>
                        setExchangeSymbol(event.target.value)
                      }
                    />
                  </label>
                </div>

                <button
                  className="run-button form-action"
                  onClick={testExchangeConnection}
                  disabled={exchangeTesting}
                >
                  {exchangeTesting
                    ? "Testing..."
                    : "Test Public Connection"}
                </button>

                {exchangeTestResult && (
                  <div
                    className={
                      exchangeTestResult.success
                        ? "connection-result success"
                        : "connection-result failed"
                    }
                  >
                    <strong>
                      {exchangeTestResult.success
                        ? "Connection Successful"
                        : "Connection Failed"}
                    </strong>

                    <p>{exchangeTestResult.message}</p>
                  </div>
                )}
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>EXCHANGE DETAILS</span>
                    <h3>Connection Information</h3>
                  </div>
                </div>

                <div className="strategy-info">
                  <strong>OKX Exchange</strong>

                  <div>
                    <span>API Type</span>
                    <b>Public REST API</b>
                  </div>

                  <div>
                    <span>Data Permission</span>
                    <b>Market Read</b>
                  </div>

                  <div>
                    <span>Order Permission</span>
                    <b>Disabled</b>
                  </div>

                  <div>
                    <span>Last Test</span>
                    <b>
                      {exchangeTestResult?.tested_at ||
                        "Not Tested"}
                    </b>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}

        {activePage === "backtest" && (
          <>
            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>BACKTEST CONFIGURATION</span>
                    <h3>Research Parameters</h3>
                  </div>
                </div>

                <div className="form-grid">
                  <label className="form-field">
                    <span>Strategy</span>

                    <select
                      value={backtestForm.strategy}
                      onChange={(event) =>
                        setBacktestForm((previous) => ({
                          ...previous,
                          strategy: event.target.value,
                        }))
                      }
                    >
                      <option value="ema">
                        EMA Crossover
                      </option>
                      <option value="rsi">
                        RSI Mean Reversion
                      </option>
                      <option value="breakout">
                        Breakout
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Initial Capital</span>

                    <input
                      type="number"
                      value={backtestForm.initialCapital}
                      onChange={(event) =>
                        setBacktestForm((previous) => ({
                          ...previous,
                          initialCapital: Number(
                            event.target.value
                          ),
                        }))
                      }
                    />
                  </label>

                  <label className="form-field">
                    <span>Leverage</span>

                    <input
                      type="number"
                      value={backtestForm.leverage}
                      onChange={(event) =>
                        setBacktestForm((previous) => ({
                          ...previous,
                          leverage: Number(
                            event.target.value
                          ),
                        }))
                      }
                    />
                  </label>

                  <label className="form-field">
                    <span>Fee Rate</span>

                    <input
                      type="number"
                      step="0.0001"
                      value={backtestForm.feeRate}
                      onChange={(event) =>
                        setBacktestForm((previous) => ({
                          ...previous,
                          feeRate: Number(
                            event.target.value
                          ),
                        }))
                      }
                    />
                  </label>

                  <label className="form-field">
                    <span>Slippage</span>

                    <input
                      type="number"
                      step="0.0001"
                      value={backtestForm.slipRate}
                      onChange={(event) =>
                        setBacktestForm((previous) => ({
                          ...previous,
                          slipRate: Number(
                            event.target.value
                          ),
                        }))
                      }
                    />
                  </label>
                </div>

                <button
                  className="run-button form-action"
                  onClick={runConfiguredBacktest}
                  disabled={backtestLoading}
                >
                  {backtestLoading
                    ? "Running..."
                    : "Run Configured Backtest"}
                </button>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>RESULT SUMMARY</span>
                    <h3>Backtest Performance</h3>
                  </div>
                </div>

                <div className="strategy-info">
                  <div>
                    <span>Final Capital</span>
                    <b>
                      $
                      {formatNumber(
                        backtestData?.final_capital,
                        4
                      )}
                    </b>
                  </div>

                  <div>
                    <span>Total Return</span>
                    <b>
                      {formatPercent(
                        backtestData?.total_return
                      )}
                    </b>
                  </div>

                  <div>
                    <span>Win Rate</span>
                    <b>
                      {formatPercent(
                        backtestData?.win_rate
                      )}
                    </b>
                  </div>

                  <div>
                    <span>Max Drawdown</span>
                    <b>
                      {formatPercent(
                        backtestData?.max_drawdown
                      )}
                    </b>
                  </div>

                  <div>
                    <span>Trades</span>
                    <b>{backtestData?.trades ?? "--"}</b>
                  </div>
                </div>
              </div>
            </section>

            <section className="panel trades-panel">
              <div className="panel-header">
                <div>
                  <span>BACKTEST ENGINE</span>
                  <h3>Equity Curve</h3>
                </div>
              </div>

              {renderEquityChart()}
            </section>

            <section className="panel trades-panel">
              <div className="panel-header">
                <div>
                  <span>TRADE DETAILS</span>
                  <h3>Backtest Trades</h3>
                </div>

                <button>
                  {backtestData?.trades ?? 0} Trades
                </button>
              </div>

              {renderTradeTable(null)}
            </section>
          </>
        )}

        {activePage === "strategy" && (
          <>
            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>STRATEGY CONFIGURATION</span>
                    <h3>Signal Generator</h3>
                  </div>
                </div>

                <div className="form-grid">
                  <label className="form-field">
                    <span>Strategy Model</span>

                    <select
                      value={strategyForm.strategy}
                      onChange={(event) =>
                        setStrategyForm((previous) => ({
                          ...previous,
                          strategy: event.target.value,
                        }))
                      }
                    >
                      <option value="ema">
                        EMA Crossover
                      </option>
                      <option value="rsi">
                        RSI Mean Reversion
                      </option>
                      <option value="breakout">
                        Breakout
                      </option>
                    </select>
                  </label>

                  {renderStrategyParameters()}
                </div>

                <button
                  className="run-button form-action"
                  onClick={runStrategySignals}
                  disabled={strategyLoading}
                >
                  {strategyLoading
                    ? "Calculating..."
                    : "Generate Strategy Signals"}
                </button>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>MODEL INFORMATION</span>
                    <h3>
                      {selectedStrategy?.name ||
                        "Strategy Model"}
                    </h3>
                  </div>
                </div>

                <p className="page-desc">
                  {selectedStrategy?.description ||
                    "Select a strategy and generate signals."}
                </p>

                <div className="strategy-info">
                  <div>
                    <span>Type</span>
                    <b>
                      {selectedStrategy?.type || "--"}
                    </b>
                  </div>

                  <div>
                    <span>Data Rows</span>
                    <b>{strategyResult?.rows ?? "--"}</b>
                  </div>

                  <div>
                    <span>Updated</span>
                    <b>
                      {strategyResult?.updated_at ||
                        "Not Calculated"}
                    </b>
                  </div>
                </div>
              </div>
            </section>

            <section className="metrics-grid secondary">
              <div className="metric-card small-card">
                <span>Long Signals</span>
                <strong className="profit">
                  {strategyResult?.long_signals ?? "--"}
                </strong>
                <small>Position = 1</small>
              </div>

              <div className="metric-card small-card">
                <span>Short Signals</span>
                <strong className="short">
                  {strategyResult?.short_signals ?? "--"}
                </strong>
                <small>Position = -1</small>
              </div>

              <div className="metric-card small-card">
                <span>Flat Signals</span>
                <strong>
                  {strategyResult?.flat_signals ?? "--"}
                </strong>
                <small>Position = 0</small>
              </div>

              <div className="metric-card small-card">
                <span>Total Rows</span>
                <strong>
                  {strategyResult?.rows ?? "--"}
                </strong>
                <small>Processed Candles</small>
              </div>
            </section>

            <section className="panel trades-panel">
              <div className="panel-header">
                <div>
                  <span>SIGNAL HISTORY</span>
                  <h3>Recent Strategy Signals</h3>
                </div>

                <button>
                  {String(
                    strategyResult?.strategy ||
                      strategyForm.strategy
                  ).toUpperCase()}
                </button>
              </div>

              <div className="trade-table">
                <div className="trade-row signal-header">
                  <span>Time</span>
                  <span>Close</span>
                  <span>Signal</span>
                  <span>Indicator A</span>
                  <span>Indicator B</span>
                </div>

                {strategySignals
                  .slice(-20)
                  .reverse()
                  .map((signal, index) => {
                    const indicatorA =
                      signal.ema_short ??
                      signal.rsi ??
                      signal.breakout_high;

                    const indicatorB =
                      signal.ema_long ??
                      signal.breakout_low;

                    return (
                      <div
                        className="trade-row signal-row"
                        key={`${signal.timestamp}-${index}`}
                      >
                        <span>
                          {String(signal.timestamp).slice(
                            0,
                            16
                          )}
                        </span>

                        <span>
                          {formatNumber(signal.close, 2)}
                        </span>

                        <span
                          className={
                            signal.signal === 1
                              ? "profit"
                              : signal.signal === -1
                                ? "short"
                                : ""
                          }
                        >
                          {signal.signal === 1
                            ? "LONG"
                            : signal.signal === -1
                              ? "SHORT"
                              : "FLAT"}
                        </span>

                        <span>
                          {formatNumber(indicatorA, 2)}
                        </span>

                        <span>
                          {formatNumber(indicatorB, 2)}
                        </span>
                      </div>
                    );
                  })}
              </div>
            </section>
          </>
        )}

        {activePage === "optimizer" && (
          <>
            <section className="dashboard-grid">
              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>OPTIMIZER CONFIGURATION</span>
                    <h3>Parameter Search</h3>
                  </div>
                </div>

                <div className="form-grid">
                  <label className="form-field">
                    <span>Strategy</span>

                    <select
                      value={optimizerStrategy}
                      onChange={(event) =>
                        setOptimizerStrategy(
                          event.target.value
                        )
                      }
                    >
                      <option value="all">
                        All Strategies
                      </option>
                      <option value="ema">EMA</option>
                      <option value="rsi">RSI</option>
                      <option value="breakout">
                        Breakout
                      </option>
                    </select>
                  </label>

                  <label className="form-field">
                    <span>Result Limit</span>

                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={optimizerTopN}
                      onChange={(event) =>
                        setOptimizerTopN(
                          Number(event.target.value)
                        )
                      }
                    />
                  </label>
                </div>

                <button
                  className="run-button form-action"
                  onClick={runOptimizer}
                  disabled={optimizerLoading}
                >
                  {optimizerLoading
                    ? "Running Optimization..."
                    : "Run Parameter Optimizer"}
                </button>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>BEST RESULT</span>
                    <h3>Top Parameter Set</h3>
                  </div>
                </div>

                {!optimizerResult?.best_result && (
                  <div className="empty-state">
                    Run the optimizer to generate ranked
                    parameter combinations.
                  </div>
                )}

                {optimizerResult?.best_result && (
                  <div className="strategy-info">
                    <strong className="profit">
                      {
                        optimizerResult.best_result
                          .strategy
                      }
                    </strong>

                    <div>
                      <span>Score</span>
                      <b>
                        {formatNumber(
                          optimizerResult.best_result
                            .score,
                          4
                        )}
                      </b>
                    </div>

                    <div>
                      <span>Final Capital</span>
                      <b>
                        $
                        {formatNumber(
                          optimizerResult.best_result
                            .final_capital,
                          4
                        )}
                      </b>
                    </div>

                    <div>
                      <span>Win Rate</span>
                      <b>
                        {formatPercent(
                          optimizerResult.best_result
                            .win_rate
                        )}
                      </b>
                    </div>

                    <div>
                      <span>Max Drawdown</span>
                      <b>
                        {formatPercent(
                          optimizerResult.best_result
                            .max_drawdown
                        )}
                      </b>
                    </div>
                  </div>
                )}
              </div>
            </section>

            <section className="metrics-grid secondary">
              <div className="metric-card small-card">
                <span>Total Combinations</span>
                <strong>
                  {optimizerResult?.total_results ?? "--"}
                </strong>
                <small>Evaluated Results</small>
              </div>

              <div className="metric-card small-card">
                <span>Displayed Results</span>
                <strong>
                  {optimizerResult?.returned_results ??
                    "--"}
                </strong>
                <small>Ranked Rows</small>
              </div>

              <div className="metric-card small-card">
                <span>Strategy Scope</span>
                <strong>
                  {String(
                    optimizerResult?.strategy ||
                      optimizerStrategy
                  ).toUpperCase()}
                </strong>
                <small>Optimization Target</small>
              </div>

              <div className="metric-card small-card">
                <span>Status</span>
                <strong
                  className={
                    optimizerResult ? "profit" : ""
                  }
                >
                  {optimizerLoading
                    ? "RUNNING"
                    : optimizerResult
                      ? "COMPLETE"
                      : "READY"}
                </strong>
                <small>Optimizer State</small>
              </div>
            </section>

            <section className="panel trades-panel">
              <div className="panel-header">
                <div>
                  <span>OPTIMIZATION RANKING</span>
                  <h3>Top Strategy Parameters</h3>
                </div>

                <button>
                  {optimizerRows.length} Results
                </button>
              </div>

              <div className="trade-table">
                <div className="trade-row optimizer-header">
                  <span>Rank</span>
                  <span>Strategy</span>
                  <span>Parameters</span>
                  <span>Capital</span>
                  <span>Score</span>
                  <span>Drawdown</span>
                </div>

                {optimizerRows.length === 0 && (
                  <div className="empty-state">
                    No optimization results available.
                  </div>
                )}

                {optimizerRows.map((result, index) => {
                  const parameters =
                    result.strategy === "EMA"
                      ? `S:${result.short} / L:${result.long}`
                      : result.strategy === "RSI"
                        ? `P:${result.period} / ${result.oversold}-${result.overbought}`
                        : `W:${result.window}`;

                  return (
                    <div
                      className="trade-row optimizer-row"
                      key={`${result.strategy}-${index}`}
                    >
                      <span>#{index + 1}</span>
                      <span>{result.strategy}</span>
                      <span>{parameters}</span>
                      <span>
                        $
                        {formatNumber(
                          result.final_capital,
                          4
                        )}
                      </span>
                      <span className="profit">
                        {formatNumber(result.score, 4)}
                      </span>
                      <span>
                        {formatPercent(
                          result.max_drawdown
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;