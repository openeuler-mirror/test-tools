import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from Aops_Web_Auto_Test.common.readconfig import ini

driver = None


@pytest.fixture(scope='module', autouse=True)
def drivers(request):

    global driver
    if driver is None:
        option = webdriver.ChromeOptions()
        option.add_argument('no-sandbox')
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
