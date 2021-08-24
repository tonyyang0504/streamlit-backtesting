from pathlib import Path

from quantitativetrader.trader.app import BaseApp
from quantitativetrader.trader.constant import Direction
from quantitativetrader.trader.object import TickData, BarData, TradeData, OrderData
from quantitativetrader.trader.utility import BarGenerator, ArrayManager

from .engine import RecorderEngine, APP_NAME


class DataRecorderApp(BaseApp):
    """"""
    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "行情记录系统"
    engine_class = RecorderEngine
    widget_name = "RecorderManager"
    icon_name = "recorder.ico"
