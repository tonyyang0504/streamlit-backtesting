from pathlib import Path

from quantitativetrader.trader.app import BaseApp
from quantitativetrader.trader.constant import Direction
from quantitativetrader.trader.object import TickData, BarData, TradeData, OrderData
from quantitativetrader.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME
from .engine import StrategyEngine
from .template import StrategyTemplate
from .backtesting import BacktestingEngine


class PortfolioStrategyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "组合策略系统"
    engine_class = StrategyEngine
    widget_name = "PortfolioStrategyManager"
    icon_name = "strategy.ico"
