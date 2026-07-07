import logging
import os
from datetime import datetime

LOG_DIR = "logs"

_logger = None


def get_logger():
    global _logger

    if _logger:
        return _logger

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger("AdaMarketLab")
    logger.setLevel(logging.INFO)

    # 防止重复 handler
    if not logger.handlers:

        try:
            log_file = os.path.join(
                LOG_DIR,
                f"{datetime.now().strftime('%Y-%m-%d')}.log"
            )

            file_handler = logging.FileHandler(log_file, encoding="utf-8")

        except Exception:
            # 🔥 fallback：只输出控制台，不写文件
            file_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger