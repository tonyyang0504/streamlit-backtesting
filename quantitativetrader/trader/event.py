"""
Event type string used in Quantitative Trading Robots.
"""

from quantitativetrader.event import EVENT_TIMER  # noqa

EVENT_TICK = "eTick."
EVENT_BAR = 'eBar'  # Kline for 1min updating
EVENT_TRADE = "eTrade."
EVENT_ORDER = "eOrder."
EVENT_POSITION = "ePosition."
EVENT_ACCOUNT = "eAccount."
EVENT_CONTRACT = "eContract."
EVENT_LOG = "eLog"
