from quantitativetrader.trader.ui import QtGui


WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (22, 26, 30)
GREY_COLOR = (100, 100, 100)

UP_COLOR = (52, 168, 83)
DOWN_COLOR = (234, 67, 53)
CURSOR_COLOR = (251, 188, 5)

PEN_WIDTH = 1
BAR_WIDTH = 0.3

AXIS_WIDTH = 0.8
NORMAL_FONT = QtGui.QFont("微软雅黑", 9)


def to_int(value: float) -> int:
    """"""
    return int(round(value, 0))
