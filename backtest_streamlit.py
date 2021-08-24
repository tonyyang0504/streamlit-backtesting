import importlib
from logging import INFO
from quantitativetrader.trader.constant import Direction, Offset
from typing import ValuesView
from numpy import index_exp, result_type
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from quantitativetrader.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from quantitativetrader.trader.object import Interval
from quantitativetrader.app.cta_strategy import CtaTemplate
from quantitativetrader.app.cta_strategy.ui.display import NAME_DISPLAY_MAP

KEY_NAME_MAP = {
        "start_date": "首个交易日",
        "end_date": "最后交易日",

        "total_days": "总交易日",
        "profit_days": "盈利交易日",
        "loss_days": "亏损交易日",

        "capital": "起始资金",
        "end_balance": "结束资金",

        "total_return": "总收益率",
        "annual_return": "年化收益",
        "max_drawdown": "最大回撤",
        "max_ddpercent": "百分比最大回撤",
        "max_drawdown_duration": "最大回撤周期",

        "total_net_pnl": "总盈亏",
        "total_commission": "总手续费",
        "total_slippage": "总滑点",
        "total_turnover": "总成交额",
        "total_trade_count": "总成交笔数",

        "daily_net_pnl": "日均盈亏",
        "daily_commission": "日均手续费",
        "daily_slippage": "日均滑点",
        "daily_turnover": "日均成交额",
        "daily_trade_count": "日均成交笔数",

        "daily_return": "日均收益率",
        "return_std": "收益标准差",
        "sharpe_ratio": "夏普比率",
        "return_drawdown_ratio": "收益回撤比"
    }

TARGET_NAME_MAP = {
    "日均盈亏":"daily_return",
    "收益标准差": "return_std",
    "夏普比率": "sharpe_ratio",
    "收益回撤比": "return_drawdown_ratio"}


class BacktestStreamlit:

    def __init__(self, backtesting_engine: BacktestingEngine):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.title("")
        with col2:
            st.title("CTA策略回测系统")
        with col3:
            st.title("")

        self.classes = {}
        self.backtesting_engine = backtesting_engine
        self.optimization_setting = OptimizationSetting()
        self.intervals = [interval.value for interval in Interval]
        self.class_names = NAME_DISPLAY_MAP.values()
        self.strategy_class = None
        self.start_backtesting_button = None
        self.calculate_result = None

    def set_parameters(self):
        st.sidebar.subheader("系统参数设置")
        self.class_name = st.sidebar.selectbox("交易策略", self.class_names)
        self.symbol_line = st.sidebar.text_input("交易币种")
        self.interval = st.sidebar.selectbox("K线周期", self.intervals)
        self.start_date = st.sidebar.date_input("开始日期")
        self.end_date = st.sidebar.date_input("结束日期")
        self.rate_line = st.sidebar.number_input("手续费率(%)") / 100
        self.slippage_line = st.sidebar.number_input("交易滑点")
        self.size_line = st.sidebar.number_input("合约乘数")
        self.pricetick_line = st.sidebar.number_input("价格跳动")
        self.captial_line = st.sidebar.number_input("回测资金")
        self.inverse = st.sidebar.selectbox("合约模式", ["正向", "反向"])

        path = "quantitativetrader.app.cta_strategy.strategies"
        module = importlib.import_module(path)
        importlib.reload(module)

        for name in dir(module):
            value = getattr(module, name)
            if (isinstance(value, type) and issubclass(value, CtaTemplate) and value is not CtaTemplate):
                self.classes[value.__name__] = value

        for key, value in NAME_DISPLAY_MAP.items():
            if value == self.class_name:
                self.strategy_class = self.classes[key]

        self.setting = self.strategy_class.get_class_parameters()

        self.backtesting_engine.set_parameters(
            vt_symbol=self.symbol_line.lower() + '.BINANCE',
            interval=self.interval,
            start=self.start_date,
            end=self.end_date, 
            rate=self.rate_line,
            slippage=self.slippage_line,
            size=self.size_line,
            pricetick=self.pricetick_line,
            capital=self.captial_line
        )

    def run_backtesting(self):
        st.error("策略回测")
        st.subheader("策略参数设置")

        for name in self.setting.keys():
            for key, value in self.strategy_class.parameters_map.items():
                if key == name:
                    self.setting[name] = st.number_input(value)

        self.start_backtesting_button = st.button("开始策略回测")

        if self.start_backtesting_button:
            self.backtesting_engine.add_strategy(self.strategy_class, self.setting)
            self.backtesting_engine.load_data()
            self.backtesting_engine.run_backtesting()

            self.calculate_result = self.backtesting_engine.calculate_result()

            calculate_statistics = self.backtesting_engine.calculate_statistics()
            calculate_statistics = pd.DataFrame.from_dict(calculate_statistics, orient="index").T
            calculate_statistics.rename(columns=KEY_NAME_MAP, inplace=True)

            self.orders = self.backtesting_engine.get_all_orders()
            self.daily_results = self.backtesting_engine.get_all_daily_results()
            
            orderid_list = []
            symbol_list = []
            type_list = []
            direction_list = []
            offset_list = []
            price_list = []
            volume_list = []
            traded_list = []
            status_list = []
            datetime_list = []
            orders = {}

            for order in self.orders:
                orderid_list.append(order.orderid)
                symbol_list.append(order.symbol)
                type_list.append(order.type.value)
                direction_list.append(order.direction.value)
                offset_list.append(order.offset.value)
                price_list.append(order.price)
                volume_list.append(order.volume)
                traded_list.append(order.traded)
                status_list.append(order.status.value)
                datetime_list.append(order.datetime)

            orders["订单号"] = orderid_list
            orders["交易对"] = symbol_list
            orders["订单类型"] = type_list
            orders["订单方向"] = direction_list
            orders["开平仓"] = offset_list
            orders["价格"] = price_list
            orders["开仓订单量"] = volume_list
            orders["成交订单量"] = traded_list
            orders["订单状态"] = status_list
            orders["时间"] = datetime_list

            orders = pd.DataFrame.from_dict(orders, orient="index").T

            date_list = []
            trade_count_list = []
            start_position_list = []
            end_position_list = []
            turnover_list = []
            trading_pnl_list = []
            holding_pnl_list = []
            total_pnl_list = []
            net_pnl_list = []
            commission_list = []
            slippage_list = []
            daily_results = {}

            for result in self.daily_results:
                date_list.append(result.date)
                trade_count_list.append(result.trade_count)
                start_position_list.append(result.start_pos)
                end_position_list.append(result.end_pos)
                turnover_list.append(result.turnover)
                trading_pnl_list.append(result.trading_pnl)
                holding_pnl_list.append(result.holding_pnl)
                total_pnl_list.append(result.total_pnl)
                net_pnl_list.append(result.net_pnl)
                commission_list.append(result.commission)
                slippage_list.append(result.slippage)
            
            daily_results["成交笔数"] = trade_count_list
            daily_results["开盘持仓量"] = start_position_list
            daily_results["收盘持仓量"] = end_position_list
            daily_results["成交额"] = turnover_list
            daily_results["交易盈亏"] = trading_pnl_list
            daily_results["持仓盈亏"] = holding_pnl_list
            daily_results["总盈亏"] = total_pnl_list
            daily_results["净盈亏"] = net_pnl_list
            daily_results["手续费"] = commission_list
            daily_results["滑点"] = slippage_list
            daily_results["日期"] = date_list

            daily_results = pd.DataFrame.from_dict(daily_results, orient="index").T

            calculate_result = self.calculate_result.rename(columns={
                "close_price": "当日收盘价",
                "pre_close": "前日收盘价",
                "trade_count": "成交笔数",
                "start_pos": "开盘持仓量",
                "end_pos": "收盘持仓量",
                "turnover": "成交额",
                "commission": "手续费",
                "slippage": "滑点",
                "trading_pnl": "交易盈亏",
                "holding_pnl": "持仓盈亏",
                "total_pnl": "总盈亏",
                "net_pnl": "净盈亏",
                "balance": "账户余额",
                "highlevel": "高位",
                "drawdown": "回撤",
                "ddpercent": "百分比回撤"})

            calculate_result.drop(["trades", "return"], axis=1, inplace=True)

            st.success("回测记录")
            st.write(calculate_result)

            st.info("回测统计")
            st.dataframe(calculate_statistics)

            st.warning("回测画图")
            st.plotly_chart(self.chart())

            st.error("成交记录")
            with st.expander("点击查看详情"):
                st.table(orders)

            st.success("每日盈亏")
            with st.expander("点击查看详情"):
                st.table(daily_results)

            st.success("策略回测任务完成")

    def run_optimization(self):
        st.error("参数优化")
        st.subheader("优化目标设置")
        target_name = st.selectbox("",  TARGET_NAME_MAP.keys())
        self.optimization_setting.set_target(TARGET_NAME_MAP[target_name])
        st.subheader("策略参数设置")

        self.backtesting_engine.add_strategy(self.strategy_class, self.setting)
        self.backtesting_engine.load_data()

        for name in self.setting.keys():
            for key, Value in self.strategy_class.parameters_map.items():
                if key == name:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        start= st.number_input(f"{Value}(开始)", value=1)
                    with col2:
                        step = st.number_input(f"{Value}(步长)", value=1)
                    with col3:
                        end= st.number_input(f"{Value}(结束)", value=2)
                    self.optimization_setting.add_parameter(
                        name=name,
                        start=start,
                        step=step,
                        end=end
                    )
            
        col1, col2, col3 = st.columns(3)
        with col1:
            optimization_button = st.button("开始枚举算法优化")
        with col2:
            st.write("")
        with col3:
            ga_optimization_button = st.button("开始遗传算法优化")

        if optimization_button:
            optimization_result_details = self.backtesting_engine.run_optimization(self.optimization_setting)
            optimization_result = {}
            paraments = []
            results = {}
            
            for result in optimization_result_details:
                parament = {}
                parament_dict = eval(result[0])
                for key, value in self.strategy_class.parameters_map.items():
                    parament[value] = parament_dict.pop(key)
                parament_str = str(parament)
                for i in ["{", "}", "'"]:
                    parament_str = str(parament_str).replace(i, "")
                paraments.append(parament_str)
                for key, value in result[2].items():
                    results.setdefault(key, []).append(value)

            optimization_result["策略参数"] = paraments
            optimization_result.update(results)
            optimization_result = pd.DataFrame.from_dict(optimization_result, orient="index").T
            optimization_result.rename(columns=KEY_NAME_MAP, inplace=True)
            optimization_result.drop(columns=["首个交易日", "最后交易日"], inplace=True)

            if target_name == "收益标准差":
                optimization_result.sort_values(by=target_name, ascending=True, inplace=True, ignore_index=True)
            else:
                optimization_result.sort_values(by=target_name, ascending=False, inplace=True, ignore_index=True)

            st.warning("参数优化结果")
            st.write(optimization_result)

            st.info("优化目标排名")
            st.table(optimization_result[["策略参数", target_name]])

            st.success("参数优化任务完成")
        elif ga_optimization_button:
            optimization_result_details = self.backtesting_engine.run_ga_optimization(self.optimization_setting)

            optimization_result = {}
            paraments = []
            results = {}
            parament = {}

            parament_dict = optimization_result_details[0][0]
            for key, value in self.strategy_class.parameters_map.items():
                parament[value] = parament_dict.pop(key)
            parament_str = str(parament)
            for i in ["{", "}", "'"]:
                parament_str = str(parament_str).replace(i, "")
                
            optimization_result["策略参数"] = parament_str
            optimization_result[target_name] = optimization_result_details[0][1]
            optimization_result = pd.DataFrame.from_dict(optimization_result, orient="index").T

            if target_name == "收益标准差":
                optimization_result.sort_values(by=target_name, ascending=True, inplace=True, ignore_index=True)
            else:
                optimization_result.sort_values(by=target_name, ascending=False, inplace=True, ignore_index=True)

            st.warning("参数优化结果")
            st.table(optimization_result)

            st.success("参数优化任务完成")

    def chart(self):
        fig = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["Balance", "Drawdown", "Daily Pnl", "Pnl Distribution"],
            vertical_spacing=0.06
        )

        balance_line = go.Scatter(
            x=self.calculate_result.index,
            y=self.calculate_result["balance"],
            mode="lines",
            name="Balance"
        )

        drawdown_scatter = go.Scatter(
            x=self.calculate_result.index,
            y=self.calculate_result["drawdown"],
            fillcolor="red",
            fill='tozeroy',
            mode="lines",
            name="Drawdown"
        )

        pnl_bar = go.Bar(y=self.calculate_result["net_pnl"], name="Daily Pnl")
        pnl_histogram = go.Histogram(x=self.calculate_result["net_pnl"], nbinsx=100, name="Days")

        fig.add_trace(balance_line, row=1, col=1)
        fig.add_trace(drawdown_scatter, row=2, col=1)
        fig.add_trace(pnl_bar, row=3, col=1)
        fig.add_trace(pnl_histogram, row=4, col=1)

        fig.update_layout(height=1000, width=1000)

        return fig
