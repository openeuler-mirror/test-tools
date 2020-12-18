#!/usr/bin/bash

# Copyright (c) 2020. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   zengcongwei
# @Contact   :   735811396@qq.com
# @Date      :   2020/8/10
# @License   :   Mulan PSL v2
# @Desc      :   public library
# #############################################

FUNC_PATH=$(
    cd "$(dirname "$0")" || exit 1
    pwd
)
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-openEuler
REPORT_PATH=${FUNC_PATH}
RESULT_PATH=${FUNC_PATH}/../results
RPM_LIST_PATH=${FUNC_PATH}/../results/pkg_list
LOG_PATH=${FUNC_PATH}/../results/logs
mkdir -p ${RPM_LIST_PATH} ${LOG_PATH} ${RESULT_PATH}

function logging() {
    printf "$(date +%Y-%m-%d\ %T)  [ %s ]  %s\\n" "$@"
}

function get_report_body() {
    old_info=$1
    new_info=$2

    local tmp_file=$(mktemp) || { exit 1; }
    python3 ${FUNC_PATH}/rpmdiff.py "$old_info" "$new_info" "$tmp_file" "Ture"

    test -f ${tmp_file}.html && {
        sed -n '/<table class="diff" id="difflib_chg_to0__top"/,/<\/table>/p' ${tmp_file}.html
        rm -rf ${tmp_file}.html
        rm -rf ${tmp_file}
        return 0
    }

    logging "ERROR" "failed to obation the report of info."
    rm -rf ${tmp_file}
    return 1
}

#获取包列表
function get_rpm_list() {
    old_url=$1
    new_url=$2
    #获取完整的包名列表
    if echo "$old_url" | grep "^http"; then
        curl ${old_url}/ | grep "i686\\|x86_64\\|noarch\\|aarch64" | awk -F "href" '{print $2}' | awk '{print $1}' | awk -F "\"" '{print $2}' | grep -v "?C=N;O=D" | sort | uniq | sed '/^$/d' >$RPM_LIST_PATH/old_rpm_list
        curl ${new_url}/ | grep "i686\\|x86_64\\|noarch\\|aarch64" | awk -F "href" '{print $2}' | awk '{print $1}' | awk -F "\"" '{print $2}' | grep -v "?C=N;O=D" | sort | uniq | sed '/^$/d' >$RPM_LIST_PATH/new_rpm_list
        test -s $RPM_LIST_PATH/old_rpm_list || {
            logging "ERROR" "There is no package in old repo!"
            exit 1
        }
        test -s $RPM_LIST_PATH/new_rpm_list || {
            logging "ERROR" "There is no package in new repo!"
            exit 1
        }
    else
        ls ${old_url}/*.rpm | awk -F "/" '{print $NF}' | sort | uniq >$RPM_LIST_PATH/old_rpm_list
        ls ${new_url}/*.rpm | awk -F "/" '{print $NF}' | sort | uniq >$RPM_LIST_PATH/new_rpm_list
    fi
    #获取简化的包名列表
    cat ${RPM_LIST_PATH}/old_rpm_list | awk -F '/' '{print $NF}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' >$RPM_LIST_PATH/old_pkg_list
    cat ${RPM_LIST_PATH}/new_rpm_list | awk -F '/' '{print $NF}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' >$RPM_LIST_PATH/new_pkg_list
}

#根据简化的列表进行对比
function get_diff_result() {
    old_pkg_list=$1
    new_pkg_list=$2
    diff_result=$(diff -y ${old_pkg_list} ${new_pkg_list})
    echo "${diff_result}" | grep ">" && echo "${diff_result}" | grep ">" | awk '{print $2}' >$RPM_LIST_PATH/add_pkgs || echo "None" >$RPM_LIST_PATH/add_pkgs
    echo "${diff_result}" | grep "<" && echo "${diff_result}" | grep "<" | awk '{print $1}' >$RPM_LIST_PATH/del_pkgs || echo "None" >$RPM_LIST_PATH/del_pkgs
    echo "${diff_result}" | grep -v '[<,>]' && echo "${diff_result}" | grep -v '[<,>]' | awk '{print $1}' >$RPM_LIST_PATH/same_pkgs || echo "None" >$RPM_LIST_PATH/same_pkgs

}

function get_diff_list() {
    cp ${REPORT_PATH}/../common/rpm_list.html ${RESULT_PATH}/rpm_list.html
    if [ ! -d ${RESULT_PATH}/RPMS_DIFF ]; then
        echo "None" >${RPM_LIST_PATH}/diff_list
    fi
    perl -pi -e "s|add_pkg|$(cat ${RPM_LIST_PATH}/add_pkgs)|gi" "${RESULT_PATH}/rpm_list.html" >/dev/null
    perl -pi -e "s|del_pkg|$(cat ${RPM_LIST_PATH}/del_pkgs)|gi" "${RESULT_PATH}/rpm_list.html" >/dev/null
    perl -pi -e "s|diff_pkg|$(cat ${RPM_LIST_PATH}/diff_list)|gi" "${RESULT_PATH}/rpm_list.html" >/dev/null
    perl -pi -e "s|same_version|$(cat ${RPM_LIST_PATH}/same_version)|gi" "${RESULT_PATH}/rpm_list.html" >/dev/null
    perl -pi -e "s|file_change|$(cat ${RPM_LIST_PATH}/file_change)|gi" "${RESULT_PATH}/rpm_list.html" >/dev/null
}

function get_rpm_name() {
    local pkg_name=$1
    local rpm_list=$2
    local rpm_ver=$3

    rpm_num=$(cat ${rpm_list} | grep -c "^${pkg_name}-[0-9]\\|^${pkg_name}-svn[0-9]\\|^${pkg_name}-v[0-9]")

    if [[ ${rpm_num} == 1 ]]; then
        cat ${rpm_list} |
            grep "^${pkg_name}-[0-9]\\|^${pkg_name}-svn[0-9]\\|^${pkg_name}-v[0-9]"
    elif [ ! -z "$rpm_ver" ]; then
        rpm_name=$(grep "^${pkg_name}-[0-9]\\|^${pkg_name}-svn[0-9]\\|^${pkg_name}-v[0-9]" <${rpm_list} | grep ${rpm_ver})
        rpm_line=$(echo ${rpm_name} | wc -l)
        [ ${rpm_line} == 1 ] || {
            logging "ERROR" "Please assign the correct version."
            exit 1
        }
        echo ${rpm_name}
    else
        mapfile -t rpms < <(grep "^${pkg_name}-[0-9]\\|^${pkg_name}-svn[0-9]\\|^${pkg_name}-v[0-9]" ${rpm_list})
        for ((i = 0; i < rpm_num; i++)); do
            [[ ${rpms[i]} > ${rpms[i + 1]} ]] && rpm_name=${rpms[i]} || rpm_name=${rpms[j]}
        done
        echo ${rpm_name}
    fi
}

#获取包信息,传入参数是两个链接或者完整路径名
function get_rpm_info() {
    local old_rpm_pkg=$1
    local new_rpm_pkg=$2

    rpm -qil --provides --requires --changelog ${old_rpm_pkg} >old_info
    rpm -qil --provides --requires --changelog ${new_rpm_pkg} >new_info

    diff old_info new_info >/dev/null && {
        oldRpm=$(mktemp)
        newRpm=$(mktemp)
        echo "$old_rpm_pkg" | grep -E '^http' && wget $old_rpm_pkg -O $oldRpm
        echo "$new_rpm_pkg" | grep -E '^http' && wget $new_rpm_pkg -O $newRpm
        rm -rf old_info new_info
        diff $oldRpm $newRpm && {
            logging "INFO" "package: $old_rpm_pkg has not changed." >${LOG_PATH}/unchangerpms.log
            return 0
        }
        logging "ERROR" "package: $old_rpm_pkg has changed." >${LOG_PATH}/changerpms.log && return 1
    }

    local diff_name=$(echo ${old_rpm_pkg} | awk -F '/' '{print $NF}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}' | awk -F- 'OFS="-"{$NF="";print}' | awk '{print substr($0, 1, length($0)-1)}')
    local rpm_diff_path=${RESULT_PATH}/RPMS_DIFF/${diff_name}
    local rpm_diff_html=${rpm_diff_path}/${diff_name}.html
    mkdir -p ${rpm_diff_path}
    rm -rf ${rpm_diff_html}
    cp ${REPORT_PATH}/../common/index.html ${rpm_diff_html}

    logging "INFO" "START------>${diff_name}"
    local old_ver=$(rpm -qi ${old_rpm_pkg} | grep Version | awk -F ": " '{print $2}')
    local old_rel=$(rpm -qi ${old_rpm_pkg} | grep Release | awk -F ": " '{print $2}')
    local new_ver=$(rpm -qi ${old_rpm_pkg} | grep Version | awk -F ": " '{print $2}')
    local new_rel=$(rpm -qi ${old_rpm_pkg} | grep Release | awk -F ": " '{print $2}')
    local old_version=$(echo "${old_ver}-${old_rel}")
    local new_version=$(echo "${new_ver}-${new_rel}")
    info_diff=$(get_report_body "$(rpm -qi $old_rpm_pkg)" "$(rpm -qi $new_rpm_pkg)")
    file_diff=$(get_report_body "$(rpm -qlv $old_rpm_pkg | awk '{print $1 "\t" $9}')" "$(rpm -qlv $new_rpm_pkg | awk '{print $1 "\t" $9}')")
    provides_diff=$(get_report_body "$(rpm -q --provides $old_rpm_pkg)" "$(rpm -q --provides $new_rpm_pkg)")
    requires_diff=$(get_report_body "$(rpm -qR $old_rpm_pkg)" "$(rpm -qR $new_rpm_pkg)")
    changelog_diff=$(get_report_body "$(rpm -q --changelog $old_rpm_pkg)" "$(rpm -q --changelog $new_rpm_pkg)")

    rpm -qlv $old_rpm_pkg | awk '{print $1 "\t" $9}' >old_files
    rpm -qlv $new_rpm_pkg | awk '{print $1 "\t" $9}' >new_files

    perl -pi -e "s|old_rpm|$old_rpm_pkg|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|new_rpm|$new_rpm_pkg|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|<p>info</p>|$info_diff|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|<p>path_file</p>|$file_diff|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|<p>provides</p>|$provides_diff|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|<p>requires</p>|$requires_diff|gi" "$rpm_diff_html" >/dev/null
    perl -pi -e "s|<p>changelog</p>|$changelog_diff|gi" "$rpm_diff_html" >/dev/null
    if [ -d ${RESULT_PATH}/RPMS_DIFF ]; then
        if [ ${old_version}X = ${new_version}X ]; then
            echo "<a href="RPMS_DIFF/${diff_name}/${diff_name}.html">${diff_name}</a>" >>${RPM_LIST_PATH}/same_version
        else
            echo "<a href="RPMS_DIFF/${diff_name}/${diff_name}.html">${diff_name}</a>" >>${RPM_LIST_PATH}/diff_list
        fi
        diff old_files new_files >/dev/null || echo "<a href="RPMS_DIFF/${diff_name}/${diff_name}.html">${diff_name}</a>" >>${RPM_LIST_PATH}/file_change
    fi
    rm -rf old_info new_info $oldRpm $newRpm old_files new_files
    logging "INFO" "END------>${diff_name}"
}

#根据给定的列表文件获取包列表
function get_list_info() {
    pkg_name_list=$1
    local old_url=$2
    local new_url=$3
    cat ${pkg_name_list}
    #获取给定url或目录的包列表
    get_rpm_list ${old_url} ${new_url}
    #获取指定的列表
    while read -r line; do
        pkg=$(echo "${line}" | awk '{print $1}')
        cat ${RPM_LIST_PATH}/old_pkg_list | grep "^${pkg}$" && echo "$pkg" >>pkg_list1
        cat ${RPM_LIST_PATH}/new_pkg_list | grep "^${pkg}$" && echo "$pkg" >>pkg_list2
    done <${pkg_name_list}
    #获取增删包列表
    if [ ! -f pkg_list1 ] && [ ! -f pkg_list2 ]; then
        logging "ERROR" "请指定正确的列表！"
        exit 1
    elif [ -f pkg_list1 ] && [ ! -f pkg_list2 ]; then
        cat pkg_list1 >${RPM_LIST_PATH}/del_pkgs
    elif [ ! -f pkg_list1 ] && [ -f pkg_list2 ]; then
        cat pkg_list2 >${RPM_LIST_PATH}/add_pkgs
    elif [ -f pkg_list1 ] && [ -f pkg_list2 ]; then
        #对列表进行排序，得到新的排序后的列表
        sort <pkg_list1 >pkg_sort_list1
        sort <pkg_list2 >pkg_sort_list2

        #获取对比结果
        get_diff_result pkg_sort_list1 pkg_sort_list2

    fi
    rm -rf pkg_list1 pkg_list2 pkg_sort_list1 pkg_sort_list2
}

main() {
    URL1=$2
    URL2=$3
    MODE=$4
    LIST_FILE=$5
    #处理参数
    while getopts rps arg; do
        case $arg in
        r)
            [ -z "$URL1" ] || [ -z "$URL2" ] && {
                logging "ERROR" "Please input the address of the RPM packages."
                exit 1
            }

            if (! curl "${URL1}/" | grep "repodata" >/dev/null) && (! test -d $URL1/repodata); then
                logging "ERROR" "请输入正确的地址！"
                exit 1

            elif (! curl "${URL2}/" | grep "repodata" >/dev/null) && (! test -d $URL2/repodata); then
                logging "ERROR" "请输入正确的地址"
                exit 1
            fi

            if curl "${URL1}/" | grep "Packages/" >dev/null || test -d $URL1/Packages; then
                old_url=$URL1/Packages
            else
                old_url=${URL1}
            fi
            if curl "${URL2}/" | grep "Packages/" >/dev/null || test -d $URL2/Packages; then
                new_url=$URL2/Packages
            else
                new_url=${URL2}
            fi
            ;;
        p)
            if (! ls ${URL1}/*.rpm) || (! ls ${URL2}/*.rpm); then
                logging "ERROR" "指定的的目录中找不到rpm包，请输入正确的目录！"
                exit 1
            else
                old_url=${URL1}
                new_url=${URL2}
            fi
            ;;
        s)
            pkg_name1=$(echo "${URL1}" | awk -F "/" '{print $NF}' | grep ".oe1.")
            pkg_name2=$(echo "${URL2}" | awk -F "/" '{print $NF}' | grep ".oe1.")
            if [ ! -n "$pkg_name1" ] || [ ! -n "$pkg_name2" ]; then
                logging "ERROR" "请指定正确包路径"
                exit 1
            fi
            ;;
        *)
            exit 1
            ;;
        esac
    done

    #处理不同模式
    if [ ${MODE}X == allX ]; then
        get_rpm_list ${old_url} ${new_url}
        get_diff_result ${RPM_LIST_PATH}/old_pkg_list ${RPM_LIST_PATH}/new_pkg_list
        if [ -f $RPM_LIST_PATH/same_pkgs ]; then
            while read -r pkg; do
                old_rpm=$(get_rpm_name ${pkg} ${RPM_LIST_PATH}/old_rpm_list)
                new_rpm=$(get_rpm_name ${pkg} ${RPM_LIST_PATH}/new_rpm_list)
                get_rpm_info ${old_url}/${old_rpm} ${new_url}/${new_rpm}
            done <$RPM_LIST_PATH/same_pkgs
        fi
        get_diff_list
    elif [ ${MODE}X == listX ]; then
        get_list_info ${LIST_FILE} ${old_url} ${new_url}
        if [ -f $RPM_LIST_PATH/same_pkgs ]; then
            while read -r pkg; do
                old_ver=$(grep "^${pkg}&" <${LIST_FILE} | awk '{print $2}')
                new_ver=$(grep "^${pkg}&" <${LIST_FILE} | awk '{print $3}')
                old_rpm=$(get_rpm_name ${pkg} ${RPM_LIST_PATH}/old_rpm_list ${old_ver})
                new_rpm=$(get_rpm_name ${pkg} ${RPM_LIST_PATH}/new_rpm_list ${new_ver})
                get_rpm_info ${old_url}/${old_rpm} ${new_url}/${new_rpm}
            done <$RPM_LIST_PATH/same_pkgs
        fi
        get_diff_list
    elif [ ${MODE}X == singleX ]; then
        get_rpm_info ${URL1} ${URL2}
    fi
}

main "$@"
