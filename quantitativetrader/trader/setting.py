"""
Global setting of Quantitative Trading Robots.
"""

from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone

from .utility import load_json

SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,
    "order_update_interval": 120,
    "position_update_interval": 120,
    "account_update_interval": 120,
    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "database.timezone": get_localzone().zone,
    "database.driver": "sqlite",                # see database.Driver
    "database.database": "database.db",         # for sqlite, use this as filepath
    "database.host": "localhost",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "",
    "database.authentication_source": "admin",  # for mongodb
}

SETTINGS_MAP: Dict[str, Any] = {
    "font.family": "字体样式",
    "font.size": "字体大小",
    "order_update_interval": "订单更新间隔",
    "position_update_interval": "仓位更新间隔",
    "account_update_interval": "账户更新间隔",
    "log.active": "是否打印日志",
    "log.level": "日志等级",
    "log.console": "是否控制台打印日志",
    "log.file": "是否文件打印日志",

    "email.server": "邮箱服务器",
    "email.port": "邮箱端口",
    "email.username": "邮箱账户",
    "email.password": "邮箱密码",
    "email.sender": "邮件发送者",
    "email.receiver": "邮件接收者",

    "database.timezone": "数据库时区",
    "database.driver": "数据库驱动",         
    "database.database": "数据库类型",    
    "database.host": "数据库主机",
    "database.port": "数据库端口",
    "database.user": "数据库账户",
    "database.password": "数据库密码",
    "database.authentication_source": "数据库授权", 
}
# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
