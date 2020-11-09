# -*- coding: utf-8 -*-

# Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
# @Author    	:   lemon.higgins
# @Contact   	:   lemon.higgins@aliyun.com
# @Date      	:   2020-04-09 09:39:43
# @License   	:   Mulan PSL v2
# @Version   	:   1.0
# @Desc      	:   Public function
#####################################


from lxml import etree
import urllib
import logging
import time
import pandas
import os
import yaml


class IssueScouter(object):
    """
    从github上,爬去自己关注的仓库的相关issue.
    Args:
        object ([type]): [account, repository, platform_url]
    """

    def __init__(self, account, repository, platform_url):
        self.account = account
        self.repository = repository
        self.platform_url = platform_url
        self.issues_url = (
            self.platform_url + self.account + "/" + self.repository + "/" + "issues"
        )
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def check_url(self):
        """
        docstring
        """
        with urllib.request.urlopen(self.platform_url) as url:
            if url.status is not 200:
                logging.error(
                    "Unable to connect to the github website, please check your network."
                )
                exit(1)

        with urllib.request.urlopen(self.platform_url + self.account) as url:
            if url.status is not 200:
                logging.error(
                    "The user(" + self.account + ") can't be found on github."
                )
                exit(1)

        with urllib.request.urlopen(
            self.platform_url + self.account + "/" + self.repository
        ) as url:
            if url.status is not 200:
                logging.error(
                    "Under the user("
                    + self.account
                    + "), the repository("
                    + self.repository
                    + ") was not found."
                )
                exit(1)

    def crawl_issues_id(self, issue_status):
        """
        从自己关注的仓库地址中获取issue的id
        Args:
            issue_status (str): [issue状态]

        Returns:
            [list]: [返回issue的id集合]
        """
        issues_id = []

        with urllib.request.urlopen(
            self.platform_url + self.account + "/" + self.repository + "/" + "issues"
        ) as req:
            if req.status is not 200:
                logging.error("Need to confirm whether the repository has issue.")
                exit(1)
            html = etree.HTML(req.read().decode())
            total_pages = html.xpath(
                '//*[@id="js-repo-pjax-container"]//em[@class="current"]/@data-total-pages'
            )

            issues_num = html.xpath(
                '//*[@id="js-issues-toolbar"]//a[@class="btn-link selected"]'
            )

        if len(total_pages) is 0:
            if len(issues_num) is 0:
                logging.info(
                    "No issue issued under the repository(%s)." % self.repository
                )
                return issues_id
            total_pages = "1"

        for page in range(1, int(total_pages[0]) + 1):
            page_url = (
                self.issues_url
                + "?page="
                + str(page)
                + "&q=is%3A"
                + issue_status
                + "+is%3Aissue"
            )
            page_req = urllib.request.urlopen(page_url)
            page_html = etree.HTML(page_req.read().decode())
            page_issue_id = page_html.xpath(
                '//*[@id="js-repo-pjax-container"]//div[@aria-label="Issues"]//div/@id'
            )

            for issue_id in page_issue_id:
                issues_id.append(issue_id.rsplit("_", 1)[1])

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
            issue_req = urllib.request.urlopen(issue_url)
            issue_html = etree.HTML(issue_req.read().decode())

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

            account_list.append(issue_info[0])
            repository_list.append(issue_info[1])
            id_list.append(issue_info[2])

            title_list.append(issue_title)
            desc_list.append(issue_desc)
            time_list.append(issue_create_time)
            status_list.append(issue_status)
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

    platform_url = data.get("platform").get("url")
    issue_status = data.get("issue").get("status")

    for obj in data.get("object"):
        account = obj.get("account")
        repository = obj.get("repository")

        issues = issueScouter(account, repository, platform_url)

        issues.check_url()

        issues_id = issues.crawl_issues_id(issue_status)

        if len(issues_id) is not 0:
            issues.crawl_issues_info(issues_id)
