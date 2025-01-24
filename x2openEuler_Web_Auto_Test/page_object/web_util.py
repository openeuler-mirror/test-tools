"""
@Time : 2024/10/28 9:52
@Auth : ysc
@File : web_util.py
@IDE  : PyCharm
"""
from common.readelement import Element
from page_object.base_page import BasePage

common = Element('common')


class WebUtil(BasePage):
    """
    常用的web界面元素
    """
    def alert_message(self):
        """
        获取弹窗元素
        """
        self.mouse_move(common["assert"])
        alert = self.find_element(common["assert"])

        return alert.text

    def execute_script(self, js):
        """
        打开标签页
        :param js: 标签数据
        :return:
        """
        self.driver.execute_script(js)

    def switch_handle(self, count=0):
        """
        根切换标签页
        :param count:
        :return:
        """
        self.driver.switch_to.window(self.driver.window_handles[count])

    def user_login(self, username, password):
        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return:
        """
        self.send_keys(common["user_name"], username)
        self.send_keys(common["user_passwd"], password)
        self.click(common["disclaimer"])
        self.click(common["login"])

    def user_logout(self):
        """
        用户登出
        :return:
        """
        self.click(common["user"])
        self.click(common["logout"])
        self.click(common['confirm_button'])

    def change_passwd(self, old_password, new_password):
        """
        修改密码
        :return:
        """
        self.click(common["user"])
        self.click(common["change_passwd"])
        self.send_keys(common["old_passwd_input"], old_password)
        self.send_keys(common["new_passwd_input", new_password])
        self.send_keys(common["confirm_passwd_input"], new_password)
        self.click(common['confirm_button'])

