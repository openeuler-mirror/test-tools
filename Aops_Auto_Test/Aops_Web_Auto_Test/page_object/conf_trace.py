# -*-coding:utf-8-*-
from Aops_Web_Auto_Test.page_object.base_page import CommonPagingWebPage
from Aops_Web_Auto_Test.common.readelement import Element

conf_trace_ele = Element('conf_trace')


class ConfTracePage(CommonPagingWebPage):

    def enter_domain_page(self):
        """进入业务域菜单"""
        expanded = self.get_element_attr(conf_trace_ele['conf_trace_menu'], 'aria-expanded')
        if expanded == "false":
            self.click_element(conf_trace_ele['conf_trace_menu'])
        self.click_element(conf_trace_ele['domain_magt_menu'])

    def add_domain(self, cluster_name, domain_name, action='confirm'):
        """
        新建命令
        :param cluster_name: 需要添加域名的集群名称
        :param domain_name: 要添加的域名
        :param action: 操作确认或取消，默认为'confirm'
        """
        self.click_element(conf_trace_ele['add_domain_button'])
        self.find_element(conf_trace_ele['add_domain_page_title'])
        self.select_cluster(cluster_name)
        self.input_text(conf_trace_ele['domain_name'], domain_name)
        self.file_trace()
        self.file_monitor()
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            raise RuntimeError(f"处理按钮时发生错误：{e}")

    def delete_domain(self, domain_name, action='confirm'):
        """
        删除domain
        :param domain_name: 要删除的域名
        :param action: 操作确认或取消，默认为'confirm'
        """
        new_loc = self.replace_locator_text(conf_trace_ele['delete_domain'], domain_name)
        self.click_element(new_loc)
        try:
            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
            else:
                raise ValueError("action参数必须是confirm或者cancel")
        except Exception as e:
            raise RuntimeError(f"处理按钮时发生错误：{e}")

    def get_all_domain(self):
        """
        从业务域列表获取所有业务域名称
        """
        return self.get_column_data_all_pages(1)[1]

    def file_trace(self, action: bool = True) -> None:
        """
        文件跟踪开关状态

        :param action: 控制开关状态，True=开启/False=关闭
        :param action: 操作确认或取消，默认为'confirm'
        """
        if not isinstance(action, bool):
            raise ValueError("action参数必须是布尔类型")

        def get_current_state() -> str:
            return self.get_element_attr(conf_trace_ele['file_trace'], 'aria-checked')

        current_state = get_current_state()
        target_state = 'true' if action else 'false'

        try:
            if current_state != target_state:
                self.click_element(conf_trace_ele['file_trace'])
                if get_current_state() != target_state:
                    raise RuntimeError(
                        f"状态修正失败：预期 {target_state}，当前 {get_current_state()}"
                    )
        except Exception as e:
            raise RuntimeError(
                f"文件跟踪开关操作失败（action={action}）: {str(e)}"
            ) from e

    def file_monitor(self, action: bool = True) -> None:
        """
        文件监控开关状态

        :param action: 控制开关状态，True=开启/False=关闭
        :param action: 操作确认或取消，默认为'confirm'
        """
        if not isinstance(action, bool):
            raise ValueError("action参数必须是布尔类型")

        def get_current_state() -> str:
            return self.get_element_attr(conf_trace_ele['file_monitor'], 'aria-checked')

        current_state = get_current_state()
        target_state = 'true' if action else 'false'

        try:
            if current_state != target_state:
                self.click_element(conf_trace_ele['file_trace'])
                if get_current_state() != target_state:
                    raise RuntimeError(
                        f"状态修正失败：预期 {target_state}，当前 {get_current_state()}"
                    )
        except Exception as e:
            raise RuntimeError(
                f"文件监控开关操作失败（action={action}）: {str(e)}"
            ) from e

    def enter_domain_detail(self, domain):
        """
        进入业务域详情页面
        """
        new_loc = self.replace_locator_text(conf_trace_ele['domain_detail_button'], domain)
        self.click_element(new_loc)

    def add_host(self, domain, hosts=None, select_all=False, action='confirm'):
        """
        给业务域添加主机

        :param domain: 域名字符串，用于进入域名详细页面
        :param hosts: 主机列表，指定要添加的主机；若为None且select_all为False，则会抛出异常
        :param select_all: 布尔值，表示是否选择所有主机；True选择所有主机，False只选择指定的主机
        :param action: 操作动作，'confirm'表示确认添加，'cancel'表示取消操作
        """
        if not isinstance(domain, str):
            raise TypeError("domain参数必须是字符串类型")
        if hosts is not None and not isinstance(hosts, list):
            raise TypeError("hosts参数必须是列表类型或None")
        if action not in ['confirm', 'cancel']:
            raise ValueError("action参数必须是'confirm'或'cancel'")
        if hosts is None and not select_all:
            raise ValueError("当select_all为False时，hosts参数不能为空")
        try:
            self.enter_domain_detail(domain)
            self.click_element(conf_trace_ele['add_host'])
            self.find_element(conf_trace_ele['add_host_title'])

            if select_all:
                self.click_element(conf_trace_ele['add_host_all'])
            else:
                for host in hosts:
                    new_loc = self.replace_locator_text(conf_trace_ele['host_checkbox'], host)
                    self.click_element(new_loc)
            self.click_element(conf_trace_ele['right_icon'])

            if action == "confirm":
                self.click_confirm_button()
            elif action == "cancel":
                self.click_cancel_button()
    
        except KeyError as ke:
            raise RuntimeError(f"配置文件中缺少关键定位器：{ke}")
        except TypeError as te:
            raise RuntimeError(f"类型错误：{te}")
        except Exception as e:
            raise RuntimeError(f"处理按钮时发生未知错误：{e}")




