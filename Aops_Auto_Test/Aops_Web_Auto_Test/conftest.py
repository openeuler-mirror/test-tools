import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from Aops_Web_Auto_Test.config.conf import cm
from Aops_Web_Auto_Test.common.readconfig import ini

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
