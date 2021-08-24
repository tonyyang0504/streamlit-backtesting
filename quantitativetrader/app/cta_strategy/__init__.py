from pathlib import Path

from quantitativetrader.trader.app import BaseApp
from quantitativetrader.trader.constant import Direction
from quantitativetrader.trader.object import TickData, BarData, TradeData, OrderData
from quantitativetrader.trader.utility import BarGenerator, ArrayManager

from .base import APP_NAME, StopOrder
from .engine import CtaEngine
from .template import CtaTemplate, CtaSignal, TargetPosTemplate


class CtaStrategyApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA策略机器人"
    engine_class = CtaEngine
    widget_name = "CtaManager"
    icon_name = "cta.ico"
