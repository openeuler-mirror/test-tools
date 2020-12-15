# -*- coding: utf-8 -*-

"""
 Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
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
# @Date      	:   2020-04-09 09:39:43
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   Public function
#####################################


from lxml import etree
import urllib.request
import logging
import re
import time
import pandas
import os
import yaml


class IssueScouter(object):
    """
    从github上,爬取自己关注的仓库的相关issue.
    Args:
        object ([type]): [account, repository, platform_url]
    """

    def __init__(self, platform, account, repository, platform_url, status):
        self.platform = platform
        self.account = account
        self.repository = repository
        self.platform_url = platform_url
        self.status = status
        if self.platform == "github":
            self.issues_url = (
                self.platform_url
                + self.account
                + "/"
                + self.repository
                + "/"
                + "issues"
            )
        elif self.platform == "gitlab":
            self.issues_url = (
                self.platform_url
                + self.account
                + "/"
                + self.repository
                + "/-/"
                + "issues"
            )
        else:
            logging.error(
                "Currently, only the gitHub and gitLab platforms are supported."
            )
            exit(1)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
        }
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def check_url(self):
        """
        检测github的用户和仓库名是否正确
        """
        with urllib.request.urlopen(
            urllib.request.Request(url=self.platform_url, headers=self.headers)
        ) as url:
            if url.status != 200:
                logging.error(
                    "Unable to connect to the platform website, please check your network."
                )
                exit(1)

        with urllib.request.urlopen(
            urllib.request.Request(
                url=self.platform_url + self.account, headers=self.headers
            )
        ) as url:
            if url.status != 200:
                logging.error(
                    "The user(" + self.account + ") can't be found on platform."
                )
                exit(1)

        with urllib.request.urlopen(
            urllib.request.Request(
                url=self.platform_url + self.account + "/" + self.repository,
                headers=self.headers,
            )
        ) as url:
            if url.status != 200:
                logging.error(
                    "Under the user("
                    + self.account
                    + "), the repository("
                    + self.repository
                    + ") was not found."
                )
                exit(1)

    def crawl_issues_id(self):
        """
        从自己关注的仓库地址中获取issue的id

        Returns:
            [list]: [返回issue的id集合]
        """
        issues_id = []

        with urllib.request.urlopen(
            urllib.request.Request(url=self.issues_url, headers=self.headers)
        ) as req:
            if req.status != 200:
                logging.error("Need to confirm whether the repository has issue.")
                exit(1)
            html = etree.HTML(req.read().decode())
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
                logging.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )
                exit(1)

        if len(total_pages) == 0:
            if len(issues_num) == 0:
                logging.info(
                    "No issue issued under the repository(%s)." % self.repository
                )
                return issues_id
            total_pages = "1"

        for page in range(1, int(total_pages[0]) + 1):
            if self.platform == "github":
                page_url = (
                    self.issues_url
                    + "?page="
                    + str(page)
                    + "&q=is%3A"
                    + self.status
                    + "+is%3Aissue"
                )
            elif self.platform == "gitlab":
                page_url = (
                    self.issues_url
                    + "?page="
                    + str(page)
                    + "&scope=all&state="
                    + issue_status
                )
            else:
                logging.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )
                exit(1)

            page_req = urllib.request.urlopen(
                urllib.request.Request(url=page_url, headers=self.headers)
            )
            page_html = etree.HTML(page_req.read().decode())
            if self.platform == "github":
                page_issue_id = page_html.xpath(
                    '//*[@id="js-repo-pjax-container"]//div[@aria-label="Issues"]//div/@id'
                )
            elif self.platform == "gitlab":
                page_issue_id = page_html.xpath(
                    '//*[@class="issues-holder"]//span[@class="issuable-reference"]/text()'
                )
            else:
                logging.error(
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
            time.sleep(5)

            issue_info = [self.account, self.repository, issue_id]
            issue_url = self.issues_url + "/" + issue_id
            issue_req = urllib.request.urlopen(
                urllib.request.Request(url=issue_url, headers=self.headers)
            )
            issue_html = etree.HTML(issue_req.read().decode())

            if self.platform == "github":
                issue_title = (
                    issue_html.xpath(
                        '//*[@id="partial-discussion-header"]//h1/span[@class="js-issue-title"]/text()'
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
                logging.error(
                    "Currently, only the gitHub and gitLab platforms are supported."
                )
                exit(1)

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
