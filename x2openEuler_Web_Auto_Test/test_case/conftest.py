"""
@Time : 2025/1/6 20:15
@Auth : ysc
@File : conftest.py
@IDE  : PyCharm
"""
import os.path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
driver = None


@pytest.fixture(scope='session', autouse=True)
def drivers(request):

    global driver
    if driver is None:
        option = webdriver.ChromeOptions()
        option.add_argument('no-sandbox')
        option.add_argument("ignore-certificate-errors")
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/chromedriver"
        if os.path.exists(current_path):
            service = Service(executable_path=current_path)
            driver = webdriver.Chrome(service=service, options=option)
        else:
            driver = webdriver.Chrome(options=option)
        driver.maximize_window()

    def teardown():
        driver.quit()

    request.addfinalizer(teardown)
    return driver
