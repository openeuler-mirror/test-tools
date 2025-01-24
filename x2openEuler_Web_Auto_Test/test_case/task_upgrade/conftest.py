"""
@Time : 2025/1/7 9:23
@Auth : ysc
@File : conftest.py
@IDE  : PyCharm
"""
from page_object.web_util import WebUtil
from config.config import get_config
from test_case.conftest import *


@pytest.fixture(scope='module', autouse=True)
def user_login(drivers):
    """
    用户登录
    :param drivers: 添加驱动
    :return:
    """
    x2_web = WebUtil(drivers)
    conf = get_config()
    x2_web.load_url(conf["web"]["url"])
    x2_web.sleep(5)
    x2_web.user_login(conf["web"]["username"], conf["web"]["password"])




