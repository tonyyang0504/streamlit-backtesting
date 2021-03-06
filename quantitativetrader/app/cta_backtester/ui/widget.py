import csv
from datetime import datetime, timedelta
from tzlocal import get_localzone
from copy import copy

import numpy as np
import pyqtgraph as pg

from quantitativetrader.trader.constant import Interval, Direction, Exchange
from quantitativetrader.trader.engine import MainEngine
from quantitativetrader.trader.ui import QtCore, QtWidgets, QtGui
from quantitativetrader.trader.ui.widget import BaseMonitor, BaseCell, DirectionCell, EnumCell
from quantitativetrader.trader.ui.editor import CodeEditor
from quantitativetrader.event import Event, EventEngine
from quantitativetrader.chart import ChartWidget, CandleItem, VolumeItem
from quantitativetrader.trader.utility import load_json, save_json
from quantitativetrader.trader.database import DB_TZ

from ..engine import (
    APP_NAME,
    EVENT_BACKTESTER_LOG,
    EVENT_BACKTESTER_BACKTESTING_FINISHED,
    EVENT_BACKTESTER_OPTIMIZATION_FINISHED,
    OptimizationSetting
)


class BacktesterManager(QtWidgets.QWidget):
    """"""

    setting_filename = "cta_backtester_setting.json"

    signal_log = QtCore.pyqtSignal(Event)
    signal_backtesting_finished = QtCore.pyqtSignal(Event)
    signal_optimization_finished = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.backtester_engine = main_engine.get_engine(APP_NAME)
        self.class_names = []
        self.settings = {}

        self.target_display = ""

        self.init_ui()
        self.register_event()
        self.backtester_engine.init_engine()
        self.init_strategy_settings()
        self.load_backtesting_setting()

    def init_strategy_settings(self):
        """"""
        self.class_names = self.backtester_engine.get_strategy_class_names()

        for class_name in self.class_names:
            setting = self.backtester_engine.get_default_setting(class_name)
            self.settings[class_name] = setting

        self.class_combo.addItems(self.class_names)

    def init_ui(self):
        """"""
        self.setWindowTitle("CTA??????????????????")

        # Setting Part
        self.class_combo = QtWidgets.QComboBox()
        self.class_combo.setStyleSheet(
                        '''QComboBox{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

        self.symbol_line = QtWidgets.QLineEdit("btcusdt.BINANCE")
        self.symbol_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

        self.interval_combo = QtWidgets.QComboBox()
        self.interval_combo.setStyleSheet(
                        '''QComboBox{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        for interval in Interval:
            # if interval != Interval.TICK:
                self.interval_combo.addItem(interval.value)

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3 * 365)

        self.start_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate(
                start_dt.year,
                start_dt.month,
                start_dt.day
            )
        )
        self.start_date_edit.setStyleSheet(
                        '''QDateEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.end_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate.currentDate()
        )
        self.end_date_edit.setStyleSheet(
                        '''QDateEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

        self.rate_line = QtWidgets.QLineEdit("0.000025")
        self.rate_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.slippage_line = QtWidgets.QLineEdit("0.2")
        self.slippage_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.size_line = QtWidgets.QLineEdit("300")
        self.size_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.pricetick_line = QtWidgets.QLineEdit("0.2")
        self.pricetick_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.capital_line = QtWidgets.QLineEdit("1000000")
        self.capital_line.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

        self.inverse_combo = QtWidgets.QComboBox()
        self.inverse_combo.setStyleSheet(
                        '''QComboBox{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.inverse_combo.addItems(["??????", "??????"])

        backtesting_button = QtWidgets.QPushButton("????????????")
        backtesting_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(52, 168, 83)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}")
        backtesting_button.clicked.connect(self.start_backtesting)

        optimization_button = QtWidgets.QPushButton("????????????")
        optimization_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        optimization_button.clicked.connect(self.start_optimization)

        self.result_button = QtWidgets.QPushButton("????????????")
        self.result_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(66, 133, 244)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        self.result_button.clicked.connect(self.show_optimization_result)
        self.result_button.setEnabled(False)

        downloading_button = QtWidgets.QPushButton("????????????")
        downloading_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(66, 133, 244)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        downloading_button.clicked.connect(self.start_downloading)

        self.order_button = QtWidgets.QPushButton("????????????")
        self.order_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(234, 67, 53)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        self.order_button.clicked.connect(self.show_backtesting_orders)
        self.order_button.setEnabled(False)

        self.trade_button = QtWidgets.QPushButton("????????????")
        self.trade_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        self.trade_button.clicked.connect(self.show_backtesting_trades)
        self.trade_button.setEnabled(False)

        self.daily_button = QtWidgets.QPushButton("????????????")
        self.daily_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(66, 133, 244)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        self.daily_button.clicked.connect(self.show_daily_results)
        self.daily_button.setEnabled(False)

        self.candle_button = QtWidgets.QPushButton("K?????????")
        self.candle_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(52, 168, 83)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        self.candle_button.clicked.connect(self.show_candle_chart)
        self.candle_button.setEnabled(False)

        edit_button = QtWidgets.QPushButton("????????????")
        edit_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        edit_button.clicked.connect(self.edit_strategy_code)

        reload_button = QtWidgets.QPushButton("????????????")
        reload_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(234, 67, 53)}"
                                       "QPushButton{border:20px}"
                                       "QPushButton{border-radius:20px}"
                                       "QPushButton{padding:2px 4px}")
        reload_button.clicked.connect(self.reload_strategy_class)

        for button in [
            backtesting_button,
            optimization_button,
            downloading_button,
            self.result_button,
            self.order_button,
            self.trade_button,
            self.daily_button,
            self.candle_button,
            edit_button,
            reload_button
        ]:
            button.setFixedHeight(button.sizeHint().height() * 2)

        form = QtWidgets.QFormLayout()
        form.addRow("????????????", self.class_combo)
        form.addRow("????????????", self.symbol_line)
        form.addRow("K?????????", self.interval_combo)
        form.addRow("????????????", self.start_date_edit)
        form.addRow("????????????", self.end_date_edit)
        form.addRow("????????????", self.rate_line)
        form.addRow("????????????", self.slippage_line)
        form.addRow("????????????", self.size_line)
        form.addRow("????????????", self.pricetick_line)
        form.addRow("????????????", self.capital_line)
        form.addRow("????????????", self.inverse_combo)

        result_grid = QtWidgets.QGridLayout()     
        result_grid.addWidget(self.trade_button, 0, 0)
        result_grid.addWidget(self.order_button, 0, 1)
        result_grid.addWidget(self.daily_button, 1, 0)
        result_grid.addWidget(self.candle_button, 1, 1)

        left_vbox = QtWidgets.QVBoxLayout()    
        left_vbox.addLayout(form)
        left_vbox.addWidget(backtesting_button)
        left_vbox.addWidget(downloading_button)
        left_vbox.addStretch()
        left_vbox.addLayout(result_grid)
        left_vbox.addStretch()
        left_vbox.addWidget(optimization_button)
        left_vbox.addWidget(self.result_button)
        left_vbox.addStretch()
        left_vbox.addWidget(edit_button)
        left_vbox.addWidget(reload_button)

        # Result part
        self.statistics_monitor = StatisticsMonitor()

        self.log_monitor = QtWidgets.QTextEdit()
        self.log_monitor.setStyleSheet(
                        '''QTextEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')   
        self.log_monitor.setMaximumHeight(400)

        self.chart = BacktesterChart()
        self.chart.setMinimumWidth(1000)

        self.trade_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "??????????????????",
            BacktestingTradeMonitor
        )
        self.order_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "??????????????????",
            BacktestingOrderMonitor
        )
        self.daily_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "??????????????????",
            DailyResultMonitor
        )

        # Candle Chart
        self.candle_dialog = CandleChartDialog()

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.statistics_monitor)
        vbox.addWidget(self.log_monitor)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(vbox)
        hbox.addWidget(self.chart)
        self.setLayout(hbox)

        # Code Editor
        self.editor = CodeEditor(self.main_engine, self.event_engine)

    def load_backtesting_setting(self):
        """"""
        setting = load_json(self.setting_filename)
        if not setting:
            return

        self.class_combo.setCurrentIndex(
            self.class_combo.findText(setting["class_name"])
        )

        self.symbol_line.setText(setting["vt_symbol"])

        self.interval_combo.setCurrentIndex(
            self.interval_combo.findText(setting["interval"])
        )

        start_str = setting.get("start", "")
        if start_str:
            start_dt = QtCore.QDate.fromString(start_str, "yyyy-MM-dd")
            self.start_date_edit.setDate(start_dt)

        self.rate_line.setText(str(setting["rate"]))
        self.slippage_line.setText(str(setting["slippage"]))
        self.size_line.setText(str(setting["size"]))
        self.pricetick_line.setText(str(setting["pricetick"]))
        self.capital_line.setText(str(setting["capital"]))

        if not setting["inverse"]:
            self.inverse_combo.setCurrentIndex(0)
        else:
            self.inverse_combo.setCurrentIndex(1)

    def register_event(self):
        """"""
        self.signal_log.connect(self.process_log_event)
        self.signal_backtesting_finished.connect(
            self.process_backtesting_finished_event)
        self.signal_optimization_finished.connect(
            self.process_optimization_finished_event)

        self.event_engine.register(EVENT_BACKTESTER_LOG, self.signal_log.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_BACKTESTING_FINISHED, self.signal_backtesting_finished.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_OPTIMIZATION_FINISHED, self.signal_optimization_finished.emit)

    def process_log_event(self, event: Event):
        """"""
        msg = event.data
        self.write_log(msg)

    def write_log(self, msg):
        """"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"{timestamp}\t{msg}"
        self.log_monitor.append(msg)

    def process_backtesting_finished_event(self, event: Event):
        """"""
        statistics = self.backtester_engine.get_result_statistics()
        self.statistics_monitor.set_data(statistics)

        df = self.backtester_engine.get_result_df()
        self.chart.set_data(df)

        self.trade_button.setEnabled(True)
        self.order_button.setEnabled(True)
        self.daily_button.setEnabled(True)
        self.candle_button.setEnabled(True)

        # Tick data can not be displayed using candle chart
        interval = self.interval_combo.currentText()
        if interval != Interval.TICK.value:
            self.candle_button.setEnabled(True)
            

    def process_optimization_finished_event(self, event: Event):
        """"""
        self.write_log("?????????[????????????]????????????")
        self.result_button.setEnabled(True)

    def start_backtesting(self):
        """"""
        class_name = self.class_combo.currentText()
        vt_symbol = self.symbol_line.text()
        interval = self.interval_combo.currentText()
        start = self.start_date_edit.dateTime().toPyDateTime()
        end = self.end_date_edit.dateTime().toPyDateTime()
        rate = float(self.rate_line.text())
        slippage = float(self.slippage_line.text())
        size = float(self.size_line.text())
        pricetick = float(self.pricetick_line.text())
        capital = float(self.capital_line.text())

        if self.inverse_combo.currentText() == "??????":
            inverse = False
        else:
            inverse = True

        # Check validity of vt_symbol
        if "." not in vt_symbol:
            self.write_log("?????????????????????????????????????????????")
            return

        _, exchange_str = vt_symbol.split(".")
        if exchange_str not in Exchange.__members__:
            self.write_log("???????????????????????????????????????????????????")
            return

        # Save backtesting parameters
        backtesting_setting = {
            "class_name": class_name,
            "vt_symbol": vt_symbol,
            "interval": interval,
            "start": start.isoformat(),
            "rate": rate,
            "slippage": slippage,
            "size": size,
            "pricetick": pricetick,
            "capital": capital,
            "inverse": inverse,
        }
        save_json(self.setting_filename, backtesting_setting)

        # Get strategy setting
        old_setting = self.settings[class_name]
        dialog = BacktestingSettingEditor(class_name, old_setting)
        i = dialog.exec()
        if i != dialog.Accepted:
            return

        new_setting = dialog.get_setting()
        self.settings[class_name] = new_setting

        result = self.backtester_engine.start_backtesting(
            class_name,
            vt_symbol,
            interval,
            start,
            end,
            rate,
            slippage,
            size,
            pricetick,
            capital,
            inverse,
            new_setting
        )

        if result:
            self.statistics_monitor.clear_data()
            self.chart.clear_data()

            self.trade_button.setEnabled(False)
            self.order_button.setEnabled(False)
            self.daily_button.setEnabled(False)
            self.candle_button.setEnabled(False)

            self.trade_dialog.clear_data()
            self.order_dialog.clear_data()
            self.daily_dialog.clear_data()
            self.candle_dialog.clear_data()

    def start_optimization(self):
        """"""
        class_name = self.class_combo.currentText()
        vt_symbol = self.symbol_line.text()
        interval = self.interval_combo.currentText()
        start = self.start_date_edit.dateTime().toPyDateTime()
        end = self.end_date_edit.dateTime().toPyDateTime()
        rate = float(self.rate_line.text())
        slippage = float(self.slippage_line.text())
        size = float(self.size_line.text())
        pricetick = float(self.pricetick_line.text())
        capital = float(self.capital_line.text())

        if self.inverse_combo.currentText() == "??????":
            inverse = False
        else:
            inverse = True

        parameters = self.settings[class_name]
        dialog = OptimizationSettingEditor(class_name, parameters)
        i = dialog.exec()
        if i != dialog.Accepted:
            return

        optimization_setting, use_ga = dialog.get_setting()
        self.target_display = dialog.target_display

        self.backtester_engine.start_optimization(
            class_name,
            vt_symbol,
            interval,
            start,
            end,
            rate,
            slippage,
            size,
            pricetick,
            capital,
            inverse,
            optimization_setting,
            use_ga
        )

        self.result_button.setEnabled(False)

    def start_downloading(self):
        """"""
        vt_symbol = self.symbol_line.text()
        interval = self.interval_combo.currentText()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        start = datetime(
            start_date.year(),
            start_date.month(),
            start_date.day(),
            tzinfo=get_localzone()
        )
        start = DB_TZ.localize(start)

        end = datetime(
            end_date.year(),
            end_date.month(),
            end_date.day(),
            23,
            59,
            59,
            tzinfo=get_localzone()
        )
        end = DB_TZ.localize(end)

        self.backtester_engine.start_downloading(
            vt_symbol,
            interval,
            start,
            end
        )

    def show_optimization_result(self):
        """"""
        result_values = self.backtester_engine.get_result_values()

        dialog = OptimizationResultMonitor(
            result_values,
            self.target_display
        )
        dialog.exec_()

    def show_backtesting_trades(self):
        """"""
        if not self.trade_dialog.is_updated():
            trades = self.backtester_engine.get_all_trades()
            self.trade_dialog.update_data(trades)

        self.trade_dialog.exec_()

    def show_backtesting_orders(self):
        """"""
        if not self.order_dialog.is_updated():
            orders = self.backtester_engine.get_all_orders()
            self.order_dialog.update_data(orders)

        self.order_dialog.exec_()

    def show_daily_results(self):
        """"""
        if not self.daily_dialog.is_updated():
            results = self.backtester_engine.get_all_daily_results()
            self.daily_dialog.update_data(results)

        self.daily_dialog.exec_()

    def show_candle_chart(self):
        """"""
        if not self.candle_dialog.is_updated():
            history = self.backtester_engine.get_history_data()
            self.candle_dialog.update_history(history)

            trades = self.backtester_engine.get_all_trades()
            self.candle_dialog.update_trades(trades)

        self.candle_dialog.exec_()

    def edit_strategy_code(self):
        """"""
        class_name = self.class_combo.currentText()
        file_path = self.backtester_engine.get_strategy_class_file(class_name)

        self.editor.open_editor(file_path)
        self.editor.show()

    def reload_strategy_class(self):
        """"""
        self.backtester_engine.reload_strategy_class()

        current_strategy_name = self.class_combo.currentText()

        self.class_combo.clear()
        self.init_strategy_settings()

        ix = self.class_combo.findText(current_strategy_name)
        self.class_combo.setCurrentIndex(ix)

    def show(self):
        """"""
        self.showMaximized()


class StatisticsMonitor(QtWidgets.QTableWidget):
    """"""
    KEY_NAME_MAP = {
        "start_date": "???????????????",
        "end_date": "???????????????",

        "total_days": "????????????",
        "profit_days": "???????????????",
        "loss_days": "???????????????",

        "capital": "????????????",
        "end_balance": "????????????",

        "total_return": "????????????",
        "annual_return": "????????????",
        "max_drawdown": "????????????",
        "max_ddpercent": "?????????????????????",

        "total_net_pnl": "?????????",
        "total_commission": "????????????",
        "total_slippage": "?????????",
        "total_turnover": "????????????",
        "total_trade_count": "???????????????",

        "daily_net_pnl": "????????????",
        "daily_commission": "???????????????",
        "daily_slippage": "????????????",
        "daily_turnover": "???????????????",
        "daily_trade_count": "??????????????????",

        "daily_return": "???????????????",
        "return_std": "???????????????",
        "sharpe_ratio": "????????????",
        "return_drawdown_ratio": "???????????????"
    }

    def __init__(self):
        """"""
        super().__init__()

        self.cells = {}

        self.init_ui()

    def init_ui(self):
        """"""
        self.setRowCount(len(self.KEY_NAME_MAP))
        self.setVerticalHeaderLabels(list(self.KEY_NAME_MAP.values()))

        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.setEditTriggers(self.NoEditTriggers)

        for row, key in enumerate(self.KEY_NAME_MAP.keys()):
            cell = QtWidgets.QTableWidgetItem()
            self.setItem(row, 0, cell)
            self.cells[key] = cell

    def clear_data(self):
        """"""
        for cell in self.cells.values():
            cell.setText("")

    def set_data(self, data: dict):
        """"""
        data["capital"] = f"{data['capital']:,.2f}"
        data["end_balance"] = f"{data['end_balance']:,.2f}"
        data["total_return"] = f"{data['total_return']:,.2f}%"
        data["annual_return"] = f"{data['annual_return']:,.2f}%"
        data["max_drawdown"] = f"{data['max_drawdown']:,.2f}"
        data["max_ddpercent"] = f"{data['max_ddpercent']:,.2f}%"
        data["total_net_pnl"] = f"{data['total_net_pnl']:,.2f}"
        data["total_commission"] = f"{data['total_commission']:,.2f}"
        data["total_slippage"] = f"{data['total_slippage']:,.2f}"
        data["total_turnover"] = f"{data['total_turnover']:,.2f}"
        data["daily_net_pnl"] = f"{data['daily_net_pnl']:,.2f}"
        data["daily_commission"] = f"{data['daily_commission']:,.2f}"
        data["daily_slippage"] = f"{data['daily_slippage']:,.2f}"
        data["daily_turnover"] = f"{data['daily_turnover']:,.2f}"
        data["daily_trade_count"] = f"{data['daily_trade_count']:,.2f}"
        data["daily_return"] = f"{data['daily_return']:,.2f}%"
        data["return_std"] = f"{data['return_std']:,.2f}%"
        data["sharpe_ratio"] = f"{data['sharpe_ratio']:,.2f}"
        data["return_drawdown_ratio"] = f"{data['return_drawdown_ratio']:,.2f}"

        for key, cell in self.cells.items():
            value = data.get(key, "")
            cell.setText(str(value))


class BacktestingSettingEditor(QtWidgets.QDialog):
    """
    For creating new strategy and editing strategy parameters.
    """

    def __init__(
        self, class_name: str, parameters: dict
    ):
        """"""
        super(BacktestingSettingEditor, self).__init__()

        self.class_name = class_name
        self.parameters = parameters
        self.edits = {}

        self.init_ui()

    def init_ui(self):
        """"""
        form = QtWidgets.QFormLayout()

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"?????????????????????{self.class_name}")
        button_text = "??????"
        parameters = self.parameters

        for name, value in parameters.items():
            type_ = type(value)

            edit = QtWidgets.QLineEdit(str(value))
            edit.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
            if type_ is int:
                validator = QtGui.QIntValidator()
                edit.setValidator(validator)
            elif type_ is float:
                validator = QtGui.QDoubleValidator()
                edit.setValidator(validator)

            form.addRow(f"{name} {type_}", edit)

            self.edits[name] = (edit, type_)

        button = QtWidgets.QPushButton(button_text)
        button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:2px}"
                                       "QPushButton{border-radius:10px}"
                                       "QPushButton{padding:2px 4px}")
        button.clicked.connect(self.accept)
        form.addRow(button)

        widget = QtWidgets.QWidget()
        widget.setLayout(form)

        scroll = QtWidgets.QScrollArea()
        scroll.setStyleSheet(
                        '''QScrollArea{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)

    def get_setting(self):
        """"""
        setting = {}

        for name, tp in self.edits.items():
            edit, type_ = tp
            value_text = edit.text()

            if type_ == bool:
                if value_text == "True":
                    value = True
                else:
                    value = False
            else:
                value = type_(value_text)

            setting[name] = value

        return setting


class BacktesterChart(pg.GraphicsWindow):
    """"""

    def __init__(self):
        """"""
        super().__init__(title="Backtester Chart")

        self.dates = {}

        self.init_ui()

    def init_ui(self):
        """"""
        pg.setConfigOptions(antialias=True)

        # Create plot widgets
        self.balance_plot = self.addPlot(
            title="????????????",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.drawdown_plot = self.addPlot(
            title="????????????",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.pnl_plot = self.addPlot(
            title="????????????",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.distribution_plot = self.addPlot(title="????????????")

        # Add curves and bars on plot widgets
        self.balance_curve = self.balance_plot.plot(
            pen=pg.mkPen((66, 133, 244), width=3)
        )

        dd_color = (251, 188, 5)
        self.drawdown_curve = self.drawdown_plot.plot(
            fillLevel=-0.3, brush=dd_color, pen=dd_color
        )

        profit_color = (52, 168, 83)
        loss_color = (234, 67, 53)
        self.profit_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=profit_color, pen=profit_color
        )
        self.loss_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=loss_color, pen=loss_color
        )
        self.pnl_plot.addItem(self.profit_pnl_bar)
        self.pnl_plot.addItem(self.loss_pnl_bar)

        distribution_color = (66, 133, 244)
        self.distribution_curve = self.distribution_plot.plot(
            fillLevel=-0.3, brush=distribution_color, pen=distribution_color
        )

    def clear_data(self):
        """"""
        self.balance_curve.setData([], [])
        self.drawdown_curve.setData([], [])
        self.profit_pnl_bar.setOpts(x=[], height=[])
        self.loss_pnl_bar.setOpts(x=[], height=[])
        self.distribution_curve.setData([], [])

    def set_data(self, df):
        """"""
        if df is None:
            return

        count = len(df)

        self.dates.clear()
        for n, date in enumerate(df.index):
            self.dates[n] = date

        # Set data for curve of balance and drawdown
        self.balance_curve.setData(df["balance"])
        self.drawdown_curve.setData(df["drawdown"])

        # Set data for daily pnl bar
        profit_pnl_x = []
        profit_pnl_height = []
        loss_pnl_x = []
        loss_pnl_height = []

        for count, pnl in enumerate(df["net_pnl"]):
            if pnl >= 0:
                profit_pnl_height.append(pnl)
                profit_pnl_x.append(count)
            else:
                loss_pnl_height.append(pnl)
                loss_pnl_x.append(count)

        self.profit_pnl_bar.setOpts(x=profit_pnl_x, height=profit_pnl_height)
        self.loss_pnl_bar.setOpts(x=loss_pnl_x, height=loss_pnl_height)

        # Set data for pnl distribution
        hist, x = np.histogram(df["net_pnl"], bins="auto")
        x = x[:-1]
        self.distribution_curve.setData(x, hist)


class DateAxis(pg.AxisItem):
    """Axis for showing date data"""

    def __init__(self, dates: dict, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.dates = dates

    def tickStrings(self, values, scale, spacing):
        """"""
        strings = []
        for v in values:
            dt = self.dates.get(v, "")
            strings.append(str(dt))
        return strings


class OptimizationSettingEditor(QtWidgets.QDialog):
    """
    For setting up parameters for optimization.
    """
    DISPLAY_NAME_MAP = {
        "????????????": "total_return",
        "????????????": "sharpe_ratio",
        "???????????????": "return_drawdown_ratio",
        "????????????": "daily_net_pnl"
    }

    def __init__(
        self, class_name: str, parameters: dict
    ):
        """"""
        super().__init__()

        self.class_name = class_name
        self.parameters = parameters
        self.edits = {}

        self.optimization_setting = None
        self.use_ga = False

        self.init_ui()

    def init_ui(self):
        """"""
        QLabel = QtWidgets.QLabel

        self.target_combo = QtWidgets.QComboBox()
        self.target_combo.setStyleSheet(
                        '''QComboBox{
                        border:1px solid grey;
                        width:300px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        self.target_combo.addItems(list(self.DISPLAY_NAME_MAP.keys()))

        grid = QtWidgets.QGridLayout()
        grid.addWidget(QLabel("??????"), 0, 0)
        grid.addWidget(self.target_combo, 0, 1, 1, 3)
        grid.addWidget(QLabel("??????"), 1, 0)
        grid.addWidget(QLabel("??????"), 1, 1)
        grid.addWidget(QLabel("??????"), 1, 2)
        grid.addWidget(QLabel("??????"), 1, 3)

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"?????????????????????{self.class_name}")

        validator = QtGui.QDoubleValidator()
        row = 2

        for name, value in self.parameters.items():
            type_ = type(value)
            if type_ not in [int, float]:
                continue

            start_edit = QtWidgets.QLineEdit(str(value))
            start_edit.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:30px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
            step_edit = QtWidgets.QLineEdit(str(1))
            step_edit.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:30px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
            end_edit = QtWidgets.QLineEdit(str(value))
            end_edit.setStyleSheet(
                        '''QLineEdit{
                        border:1px solid grey;
                        width:30px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

            for edit in [start_edit, step_edit, end_edit]:
                edit.setValidator(validator)

            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(start_edit, row, 1)
            grid.addWidget(step_edit, row, 2)
            grid.addWidget(end_edit, row, 3)

            self.edits[name] = {
                "type": type_,
                "start": start_edit,
                "step": step_edit,
                "end": end_edit
            }

            row += 1

        parallel_button = QtWidgets.QPushButton("???????????????")
        parallel_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:2px}"
                                       "QPushButton{border-radius:10px}"
                                       "QPushButton{padding:2px 4px}")
        parallel_button.clicked.connect(self.generate_parallel_setting)
        grid.addWidget(parallel_button, row, 0, 1, 4)

        row += 1
        ga_button = QtWidgets.QPushButton("??????????????????")
        ga_button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:2px}"
                                       "QPushButton{border-radius:10px}"
                                       "QPushButton{padding:2px 4px}")
        ga_button.clicked.connect(self.generate_ga_setting)
        grid.addWidget(ga_button, row, 0, 1, 4)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)

        scroll = QtWidgets.QScrollArea()
        scroll.setStyleSheet(
                        '''QScrollArea{
                        border:1px solid grey;
                        width:30px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)

    def generate_ga_setting(self):
        """"""
        self.use_ga = True
        self.generate_setting()

    def generate_parallel_setting(self):
        """"""
        self.use_ga = False
        self.generate_setting()

    def generate_setting(self):
        """"""
        self.optimization_setting = OptimizationSetting()

        self.target_display = self.target_combo.currentText()
        target_name = self.DISPLAY_NAME_MAP[self.target_display]
        self.optimization_setting.set_target(target_name)

        for name, d in self.edits.items():
            type_ = d["type"]
            start_value = type_(d["start"].text())
            step_value = type_(d["step"].text())
            end_value = type_(d["end"].text())

            if start_value == end_value:
                self.optimization_setting.add_parameter(name, start_value)
            else:
                self.optimization_setting.add_parameter(
                    name,
                    start_value,
                    end_value,
                    step_value
                )

        self.accept()

    def get_setting(self):
        """"""
        return self.optimization_setting, self.use_ga


class OptimizationResultMonitor(QtWidgets.QDialog):
    """
    For viewing optimization result.
    """

    def __init__(
        self, result_values: list, target_display: str
    ):
        """"""
        super().__init__()

        self.result_values = result_values
        self.target_display = target_display

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("??????????????????")
        self.resize(1100, 500)

        # Creat table to show result
        table = QtWidgets.QTableWidget()
        table.setStyleSheet(
                        '''QTableWidget{
                        border:1px solid grey;
                        width:30px;
                        border-radius:10px;
                        padding:2px 4px;
                        }''')

        table.setColumnCount(2)
        table.setRowCount(len(self.result_values))
        table.setHorizontalHeaderLabels(["??????", self.target_display])
        table.setEditTriggers(table.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )

        for n, tp in enumerate(self.result_values):
            setting, target_value, _ = tp
            setting_cell = QtWidgets.QTableWidgetItem(str(setting))
            target_cell = QtWidgets.QTableWidgetItem(f"{target_value:.2f}")

            setting_cell.setTextAlignment(QtCore.Qt.AlignCenter)
            target_cell.setTextAlignment(QtCore.Qt.AlignCenter)

            table.setItem(n, 0, setting_cell)
            table.setItem(n, 1, target_cell)

        # Create layout
        button = QtWidgets.QPushButton("??????")
        button.setStyleSheet("QPushButton{color:black}"
                                       "QPushButton:hover{color:grey}"
                                       "QPushButton{background-color:rgb(251, 188, 5)}"
                                       "QPushButton{border:2px}"
                                       "QPushButton{border-radius:10px}"
                                       "QPushButton{padding:2px 4px}")
        button.clicked.connect(self.save_csv)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(button)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(table)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def save_csv(self) -> None:
        """
        Save table data into a csv file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "????????????", "", "CSV(*.csv)")

        if not path:
            return

        with open(path, "w") as f:
            writer = csv.writer(f, lineterminator="\n")

            writer.writerow(["??????", self.target_display])

            for tp in self.result_values:
                setting, target_value, _ = tp
                row_data = [str(setting), str(target_value)]
                writer.writerow(row_data)


class BacktestingTradeMonitor(BaseMonitor):
    """
    Monitor for backtesting trade data.
    """

    headers = {
        "tradeid": {"display": "????????? ", "cell": BaseCell, "update": False},
        "orderid": {"display": "?????????", "cell": BaseCell, "update": False},
        "symbol": {"display": "??????", "cell": BaseCell, "update": False},
        "exchange": {"display": "?????????", "cell": EnumCell, "update": False},
        "direction": {"display": "??????", "cell": DirectionCell, "update": False},
        "offset": {"display": "??????", "cell": EnumCell, "update": False},
        "price": {"display": "??????", "cell": BaseCell, "update": False},
        "volume": {"display": "??????", "cell": BaseCell, "update": False},
        "datetime": {"display": "??????", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "??????", "cell": BaseCell, "update": False},
    }


class BacktestingOrderMonitor(BaseMonitor):
    """
    Monitor for backtesting order data.
    """

    headers = {
        "orderid": {"display": "?????????", "cell": BaseCell, "update": False},
        "symbol": {"display": "??????", "cell": BaseCell, "update": False},
        "exchange": {"display": "?????????", "cell": EnumCell, "update": False},
        "type": {"display": "??????", "cell": EnumCell, "update": False},
        "direction": {"display": "??????", "cell": DirectionCell, "update": False},
        "offset": {"display": "??????", "cell": EnumCell, "update": False},
        "price": {"display": "??????", "cell": BaseCell, "update": False},
        "volume": {"display": "?????????", "cell": BaseCell, "update": False},
        "traded": {"display": "?????????", "cell": BaseCell, "update": False},
        "status": {"display": "??????", "cell": EnumCell, "update": False},
        "datetime": {"display": "??????", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "??????", "cell": BaseCell, "update": False},
    }


class FloatCell(BaseCell):
    """
    Cell used for showing pnl data.
    """

    def __init__(self, content, data):
        """"""
        content = f"{content:.2f}"
        super().__init__(content, data)


class DailyResultMonitor(BaseMonitor):
    """
    Monitor for backtesting daily result.
    """

    headers = {
        "date": {"display": "??????", "cell": BaseCell, "update": False},
        "trade_count": {"display": "????????????", "cell": BaseCell, "update": False},
        "start_pos": {"display": "????????????", "cell": BaseCell, "update": False},
        "end_pos": {"display": "????????????", "cell": BaseCell, "update": False},
        "turnover": {"display": "?????????", "cell": FloatCell, "update": False},
        "commission": {"display": "?????????", "cell": FloatCell, "update": False},
        "slippage": {"display": "??????", "cell": FloatCell, "update": False},
        "trading_pnl": {"display": "????????????", "cell": FloatCell, "update": False},
        "holding_pnl": {"display": "????????????", "cell": FloatCell, "update": False},
        "total_pnl": {"display": "?????????", "cell": FloatCell, "update": False},
        "net_pnl": {"display": "?????????", "cell": FloatCell, "update": False},
    }


class BacktestingResultDialog(QtWidgets.QDialog):
    """
    """

    def __init__(
        self,
        main_engine: MainEngine,
        event_engine: EventEngine,
        title: str,
        table_class: QtWidgets.QTableWidget
    ):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.title = title
        self.table_class = table_class

        self.updated = False

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle(self.title)
        self.resize(1100, 600)

        self.table = self.table_class(self.main_engine, self.event_engine)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def clear_data(self):
        """"""
        self.updated = False
        self.table.setRowCount(0)

    def update_data(self, data: list):
        """"""
        self.updated = True

        data.reverse()
        for obj in data:
            self.table.insert_new_row(obj)

    def is_updated(self):
        """"""
        return self.updated


class CandleChartDialog(QtWidgets.QDialog):
    """
    """

    def __init__(self):
        """"""
        super().__init__()

        self.updated = False

        self.dt_ix_map = {}
        self.ix_bar_map = {}

        self.high_price = 0
        self.low_price = 0
        self.price_range = 0

        self.items = []

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("??????K?????????")
        self.resize(1400, 800)

        # Create chart widget
        self.chart = ChartWidget()
        self.chart.add_plot("candle", hide_x_axis=True)
        self.chart.add_plot("volume", maximum_height=200)
        self.chart.add_item(CandleItem, "candle", "candle")
        self.chart.add_item(VolumeItem, "volume", "volume")
        self.chart.add_cursor()

        # Create help widget
        text1 = "???????????? ?????? ????????????"
        label1 = QtWidgets.QLabel(text1)
        label1.setStyleSheet("color:red")

        text2 = "???????????? ?????? ????????????"
        label2 = QtWidgets.QLabel(text2)
        label2.setStyleSheet("color:green")

        text3 = "?????????????????? ?????? ???????????? Buy"
        label3 = QtWidgets.QLabel(text3)
        label3.setStyleSheet("color:yellow")

        text4 = "?????????????????? ?????? ???????????? Sell"
        label4 = QtWidgets.QLabel(text4)
        label4.setStyleSheet("color:yellow")

        text5 = "?????????????????? ?????? ???????????? Short"
        label5 = QtWidgets.QLabel(text5)
        label5.setStyleSheet("color:blue")

        text6 = "?????????????????? ?????? ???????????? Cover"
        label6 = QtWidgets.QLabel(text6)
        label6.setStyleSheet("color:blue")

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch()
        hbox1.addWidget(label1)
        hbox1.addStretch()
        hbox1.addWidget(label2)
        hbox1.addStretch()

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addWidget(label3)
        hbox2.addStretch()
        hbox2.addWidget(label4)
        hbox2.addStretch()

        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addStretch()
        hbox3.addWidget(label5)
        hbox3.addStretch()
        hbox3.addWidget(label6)
        hbox3.addStretch()

        # Set layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.chart)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

    def update_history(self, history: list):
        """"""
        self.updated = True
        self.chart.update_history(history)

        for ix, bar in enumerate(history):
            self.ix_bar_map[ix] = bar
            self.dt_ix_map[bar.datetime] = ix

            if not self.high_price:
                self.high_price = bar.high_price
                self.low_price = bar.low_price
            else:
                self.high_price = max(self.high_price, bar.high_price)
                self.low_price = min(self.low_price, bar.low_price)

        self.price_range = self.high_price - self.low_price

    def update_trades(self, trades: list):
        """"""
        trade_pairs = generate_trade_pairs(trades)

        candle_plot = self.chart.get_plot("candle")

        scatter_data = []

        y_adjustment = self.price_range * 0.001

        for d in trade_pairs:
            open_ix = self.dt_ix_map[d["open_dt"]]
            close_ix = self.dt_ix_map[d["close_dt"]]
            open_price = d["open_price"]
            close_price = d["close_price"]

            # Trade Line
            x = [open_ix, close_ix]
            y = [open_price, close_price]

            if d["direction"] == Direction.LONG and close_price >= open_price:
                color = "r"
            elif d["direction"] == Direction.SHORT and close_price <= open_price:
                color = "r"
            else:
                color = "g"

            pen = pg.mkPen(color, width=1.5, style=QtCore.Qt.DashLine)
            item = pg.PlotCurveItem(x, y, pen=pen)

            self.items.append(item)
            candle_plot.addItem(item)

            # Trade Scatter
            open_bar = self.ix_bar_map[open_ix]
            close_bar = self.ix_bar_map[close_ix]

            if d["direction"] == Direction.LONG:
                scatter_color = "yellow"
                open_symbol = "t1"
                close_symbol = "t"
                open_side = 1
                close_side = -1
                open_y = open_bar.low_price
                close_y = close_bar.high_price
            else:
                scatter_color = "blue"
                open_symbol = "t"
                close_symbol = "t1"
                open_side = -1
                close_side = 1
                open_y = open_bar.high_price
                close_y = close_bar.low_price

            pen = pg.mkPen(QtGui.QColor(scatter_color))
            brush = pg.mkBrush(QtGui.QColor(scatter_color))
            size = 10

            open_scatter = {
                "pos": (open_ix, open_y - open_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": open_symbol
            }

            close_scatter = {
                "pos": (close_ix, close_y - close_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": close_symbol
            }

            scatter_data.append(open_scatter)
            scatter_data.append(close_scatter)

            # Trade text
            volume = d["volume"]
            text_color = QtGui.QColor(scatter_color)
            open_text = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))
            close_text = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))

            open_text.setPos(open_ix, open_y - open_side * y_adjustment * 3)
            close_text.setPos(close_ix, close_y - close_side * y_adjustment * 3)

            self.items.append(open_text)
            self.items.append(close_text)

            candle_plot.addItem(open_text)
            candle_plot.addItem(close_text)

        trade_scatter = pg.ScatterPlotItem(scatter_data)
        self.items.append(trade_scatter)
        candle_plot.addItem(trade_scatter)

    def clear_data(self):
        """"""
        self.updated = False

        candle_plot = self.chart.get_plot("candle")
        for item in self.items:
            candle_plot.removeItem(item)
        self.items.clear()

        self.chart.clear_all()

        self.dt_ix_map.clear()
        self.ix_bar_map.clear()

    def is_updated(self):
        """"""
        return self.updated


def generate_trade_pairs(trades: list) -> list:
    """"""
    long_trades = []
    short_trades = []
    trade_pairs = []

    for trade in trades:
        trade = copy(trade)

        if trade.direction == Direction.LONG:
            same_direction = long_trades
            opposite_direction = short_trades
        else:
            same_direction = short_trades
            opposite_direction = long_trades

        while trade.volume and opposite_direction:
            open_trade = opposite_direction[0]

            close_volume = min(open_trade.volume, trade.volume)
            d = {
                "open_dt": open_trade.datetime,
                "open_price": open_trade.price,
                "close_dt": trade.datetime,
                "close_price": trade.price,
                "direction": open_trade.direction,
                "volume": close_volume,
            }
            trade_pairs.append(d)

            open_trade.volume -= close_volume
            if not open_trade.volume:
                opposite_direction.pop(0)

            trade.volume -= close_volume

        if trade.volume:
            same_direction.append(trade)

    return trade_pairs
