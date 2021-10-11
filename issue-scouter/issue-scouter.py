# -*- coding: utf-8 -*-

"""
 Copyright (c) 2021. Huawei Technologies Co.,Ltd.ALL rights reserved.
 This program is licensed under Mulan PSL v2.
 You can use it according to the terms and conditions of the Mulan PSL v2.
          http://license.coscl.org.cn/MulanPSL2
 THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
 EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
 MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
 See the Mulan PSL v2 for more details.
"""
####################################
# @Author    	:   lemon.higgins
# @Contact   	:   lemon.higgins@aliyun.com
# @modified by 	:   meitingli(244349477@qq.com)
# @Date      	:   2020-04-09 09:39:43
# @License   	:   Mulan PSL v2
# @Version   	:   2.0
# @Desc      	:   Issue scouter tool
#####################################

from lxml import etree
import urllib.request
import logging
import re
import time
import pandas
import os
import yaml
import random 


class IssueScouter(object):
    """
    从github上,爬取自己关注的仓库的相关issue.
    Args:
        object ([type]): [account, repository, platform_url]
    """

    def __init__(self, platform, account, repository, platform_url, status):
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger()
        self.platform = platform
        self.account = account
        self.repository = repository
        self.platform_url = platform_url
        self.status = status
        if self.platform == "github":
            self.issues_url = (
                self.platform_url
                +self.account
                +"/"
                +self.repository
                +"/"
                +"issues"
            )
        elif self.platform == "gitlab":
            self.issues_url = (
                self.platform_url
                +self.account
                +"/"
                +self.repository
                +"/-/"
                +"issues"
            )
        else:
            self.logger.error(
                "Currently, only the gitHub and gitLab platforms are supported."
            )
            exit(1)

    def check_url(self):
        """
        检测github的用户和仓库名是否正确
        """
        url = self.platform_url + self.account + "/" + self.repository
        self.logger.info("Start to check %s.", url)
        isConnect = self.get_connect(url)
        if isConnect == False:
            url = self.platform_url + self.account
            if self.get_connect(url) == False:
                self.logger.error("The user(%s) can't be found on platform.", self.account)
            elif self.get_connect(self.platform_url) == False:
                self.logger.error("Unable to connect to the platform website, please check your network."
                )
            else:
                self.logger.error(
                    "Under the user(%s), the repository(%s) was not found.", self.account, self.repository
                )
            exit(1)

    def crawl_issues_id(self):
        """
        从自己关注的仓库地址中获取issue的id

        Returns:
            [list]: [返回issue的id集合]
        """
        self.logger.info("Start to get issue id list.")
        issues_id = []
        html = self.get_connect(self.issues_url)
        if html == False:
            self.logger.error("Need to confirm whether the repository has issue.")
            exit(1)

        if self.platform == "github":
            total_pages = html.xpath(
                '//*[@id="js-repo-pjax-container"]//em[@class="current"]/@data-total-pages'
            )

            issues_num = html.xpath(
                '//*[@id="js-issues-toolbar"]//a[@class="btn-link selected"]'
            )
        elif self.platform == "gitlab":
            total_pages = html.xpath(
                '//*[@id="content-body"]//li[@class="d-none d-md-block js-last-button js-pagination-page page-item"]/a/text()'
            )
            issues_num = html.xpath('//*[@id="state-opened"]/span[2]/text()')
        else:
            self.logger.error(
                "Currently, only the gitHub and gitLab platforms are supported."
            )
            exit(1)

        if len(total_pages) == 0:
            if len(issues_num) == 0:
                self.logger.info(
                    "No issue issued under the repository(%s).", self.repository 
                )
                return issues_id
            total_pages = "1"

        for page in range(1, int(total_pages[0]) + 1):
            if self.platform == "github":
                page_url = (
                    self.issues_url
                    +"?page="
                    +str(page)
                    +"&q=is%3A"
                    +self.status
                    +"+is%3Aissue"
                )
            elif self.platform == "gitlab":
                page_url = (
                    self.issues_url
                    +"?page="
                    +str(page)
                    +"&scope=all&state="
                    +issue_status
                )
            else:
                self.logger.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )
                exit(1)

            page_html = self.get_connect(self.issues_url)
            if page_html == False:
                self.logger.error("Get issue page html failed.")
                exit(1)

            if self.platform == "github":
                page_issue_id = page_html.xpath(
                    '//*[@id="js-repo-pjax-container"]//div[@aria-label="Issues"]//div/@id'
                )
            elif self.platform == "gitlab":
                page_issue_id = page_html.xpath(
                    '//*[@class="issues-holder"]//span[@class="issuable-reference"]/text()'
                )
            else:
                self.logger.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )
                exit(1)

            for issue_id in page_issue_id:
                issues_id.append(re.sub("[a-z_\n#]", "", issue_id))

        return issues_id

    def crawl_issues_info(self, issues_id):
        """
        根据issue的id号,获取每个issue的详细信息

        Args:
            issues_id (list): [所有issue的id号形成的集合]
        """
        (
            account_list,
            repository_list,
            id_list,
            title_list,
            desc_list,
            time_list,
            status_list,
            url_list,
        ) = ([], [], [], [], [], [], [], [])

        for issue_id in issues_id:
            self.logger.info("Start to get issue detail for %s.", str(issue_id))
            time.sleep(random.randint(1, 5))
            issue_info = [self.account, self.repository, issue_id]
            issue_url = self.issues_url + "/" + issue_id
        
            issue_html = self.get_connect(issue_url)
            if issue_html == False:
                self.logger.error("Get issue page html for issue id %s failed.", issue_id)
                continue

            if self.platform == "github":
                issue_title = (
                    issue_html.xpath(
                        '//*[@id="partial-discussion-header"]//h1/span[contains(@class,"js-issue-title")]/text()'
                    )[0]
                    .replace("\n", "")
                    .strip()
                )

                issue_descs = issue_html.xpath(
                    '//div[@class="js-quote-selection-container"]/div/div[1]//div[@class="edit-comment-hide"]//td//*/text()'
                )
                issue_desc = ""
                for desc in issue_descs:
                    issue_desc += desc

                issue_create_time = (
                    issue_html.xpath(
                        '//*[@id="partial-discussion-header"]//relative-time/@datetime'
                    )[0]
                    .replace("\n", "")
                    .strip()
                )
            elif self.platform == "gitlab":
                issue_title = issue_html.xpath(
                    '//*[@class="title-container"]/h2[@class="title"]/text()'
                )[0]

                issue_descs = issue_html.xpath(
                    '//*[@class="description"]/div[@class="md"]//*/text()'
                )
                issue_desc = ""
                for desc in issue_descs:
                    issue_desc += desc

                issue_create_time = issue_html.xpath(
                    '//*[@id="content-body"]//div[@class="issuable-meta"]/time/@datetime'
                )[0]
            else:
                self.logger.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )

            account_list.append(issue_info[0])
            repository_list.append(issue_info[1])
            id_list.append(issue_info[2])

            title_list.append(issue_title)
            desc_list.append(issue_desc)
            time_list.append(issue_create_time)
            status_list.append(self.status)
            url_list.append(issue_url)

        data = {
            "github account": account_list,
            "github repository": repository_list,
            "issue id": id_list,
            "issue title": title_list,
            "issue desc": desc_list,
            "create time": time_list,
            "issue status": status_list,
            "issue url": url_list,
        }

        df = pandas.DataFrame(data)
        df.to_csv(self.account + "_" + self.repository + ".csv")

    def get_header(self):
        """
        从User-Agent.txt文件中随机获取ua作为header  
        """
        lines = open('user-agent.txt').read().splitlines()
        ua = random.choice(lines)
        header = {
            'User-Agent': ua
        }
        return header
    
    def get_connect(self, req_url):
        """
        请求访问指定url，获取并返回html信息  
        
        Args:
            req_url (str): 指定的url
        """
        for i in range(1, 10):
            time.sleep(random.randint(1, 10))
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(url=req_url, headers=self.get_header()),
                    timeout=10
                ) as url:
                    if url.status == 200:
                        return etree.HTML(url.read().decode())
            except Exception:
                self.logger.warning("Request timeout.")             
        return False

if __name__ == "__main__":
    with open(
        os.path.split(os.path.realpath(__file__))[0] + "/issue-scouter.yaml", "r"
    ) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    issue_status = data.get("issue").get("status")

    for platform in data.get("platforms"):
        platform_name = platform.get("platform").get("name")
        platform_url = platform.get("platform").get("url")

        for obj in platform.get("platform").get("object"):
            account = obj.get("account")
            repository = obj.get("repository")

            issues = IssueScouter(
                platform_name, account, repository, platform_url, issue_status
            )
            
            issues.check_url()

            issues_id = issues.crawl_issues_id()

            if len(issues_id) != 0:
                issues.crawl_issues_info(issues_id)
