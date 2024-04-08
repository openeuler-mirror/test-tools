import pytest
from selenium import webdriver
driver = None


@pytest.fixture(scope='module', autouse=True)
def drivers(request):

    global driver
    if driver is None:
        option = webdriver.ChromeOptions()
        option.add_argument('no-sandbox')
        driver = webdriver.Chrome(options=option)
        driver.maximize_window()

    def fn():
        driver.quit()

    request.addfinalizer(fn)
    return driver

