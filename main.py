import pandas as pd

from core.database import init_database
from core.menu import show_menu

from modules.statistics import run_statistics
from engine.engine import execute_trade
from app.trade_controller import handle_add_trade
from app.statistics_controller import handle_statistics
from app.visualization_controller import handle_visualization
from app.risk_controller import handle_risk_calculator
from app.backtest_controller import handle_backtest
from app.strategy_controller import handle_strategy_compare


def main():
    init_database()

    while True:
        show_menu()
        choice = input("请选择：")

        if choice == "1":
            handle_add_trade()
        elif choice == "2":
            handle_statistics()
        elif choice == "3":
            handle_visualization()
        elif choice == "4":
            handle_risk_calculator()
        elif choice == "5":
            handle_backtest()
        elif choice == "6":
            handle_strategy_compare()
        elif choice == "10":
            break

        else:
            print("无效选项，请重新输入。")


if __name__ == "__main__":
    main()