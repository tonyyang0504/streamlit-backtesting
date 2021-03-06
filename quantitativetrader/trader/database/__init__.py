import os
from typing import TYPE_CHECKING
from .database import DB_TZ

if TYPE_CHECKING:
    from quantitativetrader.trader.database.database import BaseDatabaseManager

if "VNPY_TESTING" not in os.environ:
    from quantitativetrader.trader.setting import get_settings
    from .initialize import init

    settings = get_settings("database.")
    database_manager: "BaseDatabaseManager" = init(settings=settings)
