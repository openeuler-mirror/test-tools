# -*-coding:utf-8-*-
import string

import pytest
from Aops_Web_Auto_Test.common import createtestdata
from Aops_Web_Auto_Test.page_object.conf_trace import ConfTracePage


@pytest.fixture(scope='class')
def domain(drivers) -> ConfTracePage:
    return ConfTracePage(drivers)


class TestDomain:

    @pytest.fixture(scope="function", autouse=True)
    def create_data(self, domain):
        self.domain_name = None
        yield
        try:
            domain.click_close_button()
        except Exception as e:
            print(f"关闭新增业务域时发生错误：{e}")
            pass

        if self.domain_name:
            try:
                domain.delete_domain(self.domain_name)
            except Exception as e:
                print(f"删除domain: {self.domain_name}失败", e)
                pass

    def test_add_domain_01_valid_data(self, drivers, domain):
        """添加业务域-有效数据"""
        domain.enter_domain_page()
        domain_name = createtestdata.domain_name()
        self.domain_name = domain_name
        domain.add_domain('local-cluster', domain_name)
        domain.click_refresh_button()
        assert domain.search_in_column(domain_name)

    def test_add_domain_02_duplicate_data(self, drivers, domain):
        """添加业务域-重复添加"""
        domain.enter_domain_page()
        domain_name = createtestdata.domain_name()
        domain.add_domain('local-cluster', domain_name)
        domain.click_refresh_button()
        assert domain.search_in_column(domain_name)
        self.domain_name = domain_name
        domain.add_domain('local-cluster', domain_name)
        assert domain.get_notice_text() == "失败"

    def test_add_domain_03_cancal(self, drivers, domain):
        """添加业务域-取消添加"""
        domain.enter_domain_page()
        domain_name = createtestdata.domain_name()
        domain.add_domain('local-cluster', domain_name, action='cancel')
        domain.click_refresh_button()
        assert not domain.search_in_column(domain_name)

    def test_add_domain_04_invalid_domain(self, drivers, domain):
        """添加业务域-无效的domain"""
        domain.enter_domain_page()
        domain_name = createtestdata.domain_name(min_len=27, max_len=28)
        domain.add_domain('local-cluster', domain_name)
        assert domain.get_item_explain_error("业务域名称") == "名称长度不应超过26个字符"
        domain.click_cancel_button()
        domain.add_domain('local-cluster', "")
        assert domain.get_item_explain_error("业务域名称") == "请输入业务域名称"
        domain.click_cancel_button()
        domain_name = createtestdata.domain_name(characters="".join(set(string.printable) - set(string.ascii_letters) - set(string.digits) - {'-', '_', '.'}))
        domain.add_domain('local-cluster', domain_name)
        assert domain.get_item_explain_error("业务域名称") == "名称只能输入大小写字母、下划线、中划线和小数点"

    def test_delete_domain_01(self, drivers, domain):
        """删除业务域"""
        domain.enter_domain_page()
        domain_name = createtestdata.domain_name()
        domain.add_domain('local-cluster', domain_name)
        domain.click_refresh_button()
        assert domain.search_in_column(domain_name)
        domain.delete_domain(domain_name)
        assert not domain.search_in_column(domain_name)


