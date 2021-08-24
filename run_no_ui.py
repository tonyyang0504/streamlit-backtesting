from time import sleep
from logging import INFO

from quantitativetrader.event import EventEngine
from quantitativetrader.trader.setting import SETTINGS
from quantitativetrader.trader.engine import MainEngine

from quantitativetrader.gateway.binance import BinanceGateway
from quantitativetrader.app.cta_strategy import CtaStrategyApp
from quantitativetrader.app.cta_strategy.base import EVENT_CTA_LOG


SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True


binance_setting = {
        "key": "3sYQvGCszRfJsAqWaCTxbsMCnVJEE7aGUeG0HRjfTvJfmqQKG1BFFTEFvFFCFw43",
        "secret": "Qp2Y7R0iPbjz3yTLjG9dKsS3a9O1SkvltZahjvN9em2dksw50kFPkuOoqoN6LEih",
        "session_number": 3,
        "proxy_host": "",
        "proxy_port": 0,
    }


def run():
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(BinanceGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log("注册日志事件监听")

    main_engine.connect(binance_setting, "BINANCE")
    main_engine.write_log("连接BINANCE接口")

    sleep(10)

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(60)  # Leave enough time to complete strategy initialization.
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")

    while True:
        sleep(10)


if __name__ == "__main__":
    run()