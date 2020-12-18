"""
  Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
 This program is licensed under Mulan PSL v2.
 You can use it according to the terms and conditions of the Mulan PSL v2.
          http://license.coscl.org.cn/MulanPSL2
 THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
 EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
 MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
 See the Mulan PSL v2 for more details.

 #############################################
 @Author    :   zengcongwei
 @Contact   :   735811396@qq.com
 @Date      :   2020/11/10
 @License   :   Mulan PSL v2
 @Desc      :   public library
 #############################################
"""

import subprocess
import re
import difflib
from lxml import etree
import argparse
import sys



class PkgInfo(object):
    def get_rpm_info(self, pkg):
        """[summary]

        Args:
            pkg ([type]): [description]

        Returns:
            [type]: [description]
        """
        cmd = "rpm -qi " + pkg
        pkg_info = subprocess.getoutput(cmd)
        return pkg_info
        # print(pkg_info)

    def get_rpm_version(self, pkg_info):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        main_version = re.search(r"Version.*", pkg_info).group().split(" ")[-1]
        release = re.search(r"Release.*", pkg_info).group().split(" ")[-1]

        version = main_version + "-" + release
        return version

    def get_rpm_frame(self, pkg_info):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        frame = re.search(r"Architecture.*", pkg_info).group().split(" ")[-1]
        return frame

    def get_rpm_file(self, pkg):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        cmd = "rpm -ql " + pkg
        path_file = subprocess.getoutput(cmd)
        return path_file

    def get_rpm_requires(self, pkg):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        cmd = "rpm -qR " + pkg
        rpm_requires = subprocess.getoutput(cmd)
        return rpm_requires

    def get_rpm_changelog(self, pkg):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        cmd = "rpm -q --changelog " + pkg
        changelog = subprocess.getoutput(cmd)
        return changelog

    def get_rpm_provides(self, pkg):
        """[summary]

        Args:
            pkg ([type]): [description]
        """
        cmd = "rpm -q --provides " + pkg
        provides = subprocess.getoutput(cmd)
        return provides

    def diff_rpm_info(self, old_info, new_info, report_name, isContext="false"):
        """[summary]

        Args:
            old_info ([type]): [description]
            new_info ([type]): [description]

        Returns:
            [type]: [description]
        """
        d = difflib.HtmlDiff()
        html = d.make_file(
            old_info.splitlines(), new_info.splitlines(), context=isContext
        )
        html = html.encode()
        fp = open(report_name + ".html", "w+b")
        fp.write(html)
        fp.close()


def diff_rpm_info(old_info, new_info, report_name, isContext="false"):
    """[summary]

    Args:
        old_info ([str]): [description]
        new_info ([str]): [description]
        report_name ([str]): [description]
        isContext (str, optional): [description]. Defaults to "false".
    """    
    d = difflib.HtmlDiff()
    html = d.make_file(old_info.splitlines(), new_info.splitlines(), context=isContext)
    html = html.encode()
    fp = open(report_name + ".html", "w+b")
    fp.write(html)
    fp.close()


if __name__ == "__main__":
    if len(sys.argv) <= 4:
        sys.argv.append("false")
    diff_rpm_info(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
