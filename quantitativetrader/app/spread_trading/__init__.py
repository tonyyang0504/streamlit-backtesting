from pathlib import Path

from quantitativetrader.trader.app import BaseApp
from quantitativetrader.trader.object import (
    OrderData,
    TradeData,
    TickData,
    BarData
)

from .engine import (
    SpreadEngine,
    APP_NAME,
    SpreadData,
    LegData,
    SpreadStrategyTemplate,
    SpreadAlgoTemplate
)


class SpreadTradingApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "价差交易系统"
    engine_class = SpreadEngine
    widget_name = "SpreadManager"
    icon_name = "spread.ico"
