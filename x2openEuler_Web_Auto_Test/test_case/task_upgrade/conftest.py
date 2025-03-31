"""
@Time : 2025/1/7 9:23
@Auth : ysc
@File : conftest.py
@IDE  : PyCharm
"""
from x2openEuler_Web_Auto_Test.page_object.web_util import WebUtil
from x2openEuler_Web_Auto_Test.config.config import get_config
from x2openEuler_Web_Auto_Test.test_case.conftest import *
from datetime import datetime


@pytest.fixture(scope='session', autouse=True)
def user_login(drivers, worker_id):
    """
    用户登录
    :param worker_id 每个进程的work_id
    :param drivers: 添加驱动
    :return:
    """
    x2_web = WebUtil(drivers)
    conf = get_config()
    x2_web.load_url(conf["web"]["url"])
    x2_web.sleep(5)
    if worker_id == "master":
        x2_web.user_login(conf["web"]["user_1"]["username"], conf["web"]["user_1"]["password"])
    else:
        # 获取进程id的索引值：gw0, gw1.....
        index = int(worker_id[2:])
        user_index = f"user_{index + 1}"
        x2_web.user_login(conf["web"][user_index]["username"], conf["web"][user_index]["password"])


def pytest_html_results_table_header(cells):
    """
    增加运行时间列——表头
    """
    cells.insert(2, '<th class="sortable time" data-column-type="time">运行时间</th>')
    # delete Links
    cells.pop()


def pytest_html_results_table_row(cells):
    """
    增加运行时间列——表数据
    """
    cells.insert(2, f'<td class="col-time">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>')
    # delete Links
    cells.pop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    钩子函数，用例失败时截图嵌入报告中
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == "call" or report.when == "setup":
        item.test_result = report
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            _driver = item.funcargs['drivers']
            img_base64 = "data:image/jpg;base64," + _driver.get_screenshot_as_base64()
            if img_base64:
                html = '<div><img src="%s" align="right" style="width:860px;height:430px;display:block;" ' \
                       'class="img"/></div>' % img_base64
                extra.append(pytest_html.extras.html(html))
            report.extras = extra
