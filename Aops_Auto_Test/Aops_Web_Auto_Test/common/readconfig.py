import configparser
from configparser import NoSectionError, NoOptionError

from Aops_Web_Auto_Test.config.conf import cm

HOST = 'HOST'
USER = 'USER'
PASSWORD = 'PASSWORD'
CHROME_DRIVER = 'CHROME_DRIVER'


class ReadConfig(object):
    """配置文件"""

    def __init__(self):
        self.config = configparser.RawConfigParser()  # 当有%的符号时请使用Raw读取
        self.config.read(cm.ini_file, encoding='utf-8')

    def _get(self, section, option):
        """获取"""
        return self.config.get(section, option)

    def _set(self, section, option, value):
        """更新"""
        self.config.set(section, option, value)
        with open(cm.ini_file, 'w') as f:
            self.config.write(f)

    @property
    def url(self):
        return self._get(HOST, HOST)

    @property
    def user(self):
        return self._get(USER, USER)

    @property
    def password(self):
        return self._get(PASSWORD, PASSWORD)

    @property
    def chrome_driver(self):
        try:
            return self._get(CHROME_DRIVER, CHROME_DRIVER)
        except (NoSectionError, NoOptionError):
            return None


ini = ReadConfig()

if __name__ == '__main__':
    print(ini.url)
