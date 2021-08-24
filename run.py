from quantitativetrader.event import EventEngine

from quantitativetrader.trader.engine import MainEngine
from quantitativetrader.trader.ui import MainWindow, create_qapp

from quantitativetrader.gateway.binance import BinanceGateway
from quantitativetrader.gateway.binances import BinancesGateway

from quantitativetrader.app.cta_strategy import CtaStrategyApp
from quantitativetrader.app.data_manager import DataManagerApp
from quantitativetrader.app.data_recorder import DataRecorderApp  
from quantitativetrader.app.algo_trading import AlgoTradingApp
from quantitativetrader.app.cta_backtester import CtaBacktesterApp
from quantitativetrader.app.risk_manager import RiskManagerApp
from quantitativetrader.app.spread_trading import SpreadTradingApp
from quantitativetrader.app.chart_wizard import ChartWizardApp
from quantitativetrader.app.paper_account import PaperAccountApp


def main():
    qapp = create_qapp()

    event_engine = EventEngine()
    
    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(BinanceGateway)
    main_engine.add_gateway(BinancesGateway)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(SpreadTradingApp)
    main_engine.add_app(PaperAccountApp)
    main_engine.add_app(ChartWizardApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()