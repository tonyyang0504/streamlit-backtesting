from pathlib import Path

from quantitativetrader.trader.app import BaseApp
from .engine import APP_NAME, ManagerEngine


class DataManagerApp(BaseApp):
    """"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "数据管理系统"
    engine_class = ManagerEngine
    widget_name = "ManagerWidget"
    icon_name = "manager.ico"
