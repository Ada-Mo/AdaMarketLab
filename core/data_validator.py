def validate_price_data(df):
    issues = []

    required_columns = ["timestamp", "open", "high", "low", "close", "volume"]

    for col in required_columns:
        if col not in df.columns:
            issues.append(f"缺少字段: {col}")

    if df.empty:
        issues.append("数据为空")

    if "close" in df.columns and df["close"].isna().any():
        issues.append("close 存在空值")

    if "timestamp" in df.columns:
        if df["timestamp"].duplicated().any():
            issues.append("timestamp 存在重复")

        if not df["timestamp"].is_monotonic_increasing:
            issues.append("timestamp 时间顺序不是递增")

    return issues