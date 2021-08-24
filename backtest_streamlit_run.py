from backtest_streamlit import BacktestStreamlit
from quantitativetrader.app.cta_strategy.backtesting import BacktestingEngine


def main():
    backtest_streamlit = BacktestStreamlit(BacktestingEngine())
    backtest_streamlit.set_parameters()
    backtest_streamlit.run_backtesting()


if __name__ == "__main__":

    main()
