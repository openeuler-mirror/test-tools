import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.common.readconfig import ini
from Aops_Web_Auto_Test.utils.LogUtil import my_log

log = my_log()
driver = None


@pytest.fixture(scope='session', autouse=True)
def drivers(request):

    global driver
    if driver is None:
        option = webdriver.ChromeOptions()
        prefs = {'download.default_directory': cm.TESTDATA_PATH}
        option.add_argument('no-sandbox')
        option.add_experimental_option('prefs', prefs)
        option.add_argument('--disable-notifications')
        option.add_argument('--disable-popup-blocking')
        option.add_argument('--autoplay-policy=no-user-gesture-required')
        if ini.chrome_driver:
            service = Service(executable_path=ini.chrome_driver)
            driver = webdriver.Chrome(service=service, options=option)
        else:
            driver = webdriver.Chrome(options=option)
        driver.maximize_window()

    def fn():
        driver.quit()

    request.addfinalizer(fn)
    return driver


test_case_counter = 0
total_test_cases = None


def pytest_collection_finish(session):
    global total_test_cases
    total_test_cases = len(session.items)
    log.info(f"共收集到 {total_test_cases} 个测试用例")


def pytest_runtest_setup(item):
    global test_case_counter
    test_case_counter += 1
    log.info(f"开始执行第 {test_case_counter} 个测试用例: {item.name}")

