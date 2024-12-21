#!/usr/bin/bash
# Copyright (c) [2020] Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
####################################
#@Author    	:   lemon.higgins
#@Contact   	:   lemon.higgins@aliyun.com
#@Date      	:   2020-12-02 09:51:00
#@License   	:   Mulan PSL v2
#@Version   	:   1.0
#@Desc      	:
#####################################

function logger() {
    printf "$(date +%Y-%m-%d\ %T)  $0  [ %s ]  %s\n" "$@" 1>&2
}

function clone_spec() {
    url=$1
    pkg=$2
    down_path=$3
    rename_spec=${4-"${3}.spec"}
    os=$5
    raw="raw/master"
    test "$os"x == "fedora"x && raw=$raw"/f"

    wget "$url"/"$pkg"/"$raw"/"$pkg".spec -O "$down_path"/"$rename_spec" >/dev/null 2>&1 || {
        logger "ERROR" "failed to download the spec of $pkg."
        return 1
    }

    return 0
}

function clean_downfile() {
    rm -rf "$1"
}

function check_test() {
    rpm_path=$1
    test -d "$rpm_path" || {
        logger "ERROR" "can not find the dir:${rpm_path}."
        exit 1
    }
    rpm=$2
    test -z "$rpm" && {
        logger "ERROR" "Missing parameters."
        exit 1
    }
    path_spec=$(find "$rpm_path" -name "*${rpm}.spec")
    test -f "$path_spec" || {
        logger "ERROR" "${path_spec} not in ${path_spec}."
        exit 1
    }

    grep "^%check" "$path_spec" >/dev/null
    test $? -ne 0 && {
        logger "DEBUG" "the spec:${rpm}.spec no check."
        exit 0
    }

    grep -A 10 "^%check" "$path_spec" | grep 'make.*check\|make.*test' >/dev/null
    test $? -ne 0 && {
        logger "ERROR" "check in the spec:${rpm}.spec is not used."
        exit 1
    }

    logger "INFO " "make check in the spec:${rpm}.spec and is used."
    return 0
}

function diff_check() {
    rpm_path=$1
    test -d "$rpm_path" || {
        logger "ERROR" "can not find the dir:${rpm_path}."
        exit 1
    }

    rpm=$2
    test -z "$rpm" && {
        logger "ERROR" "Missing parameters."
        exit 1
    }

    f_path_spec="$rpm_path/fedora_${rpm}.spec"

    o_path_spec="$rpm_path/openEuler_${rpm}.spec"

    f_check=$(mktemp)
    o_check=$(mktemp)

    if grep -A 10 "^%check" "$f_path_spec" >$f_check; then
        grep -A 10 "^%check" "$o_path_spec" >$o_check || {
            if grep 'make.*check\|make.*test' "$f_check" >/dev/null; then
                logger "ERROR" "'make check' exists in the upstream community,but we do not."
                return 1
            else
                logger "WARN " "'make check' does not exist in the upstream community,so we do not need."
                return 0
            fi
        }

        grep 'make.*check\|make.*test' "$f_check" >/dev/null && {
            grep 'make.*check\|make.*test' "$o_check" >/dev/null || {
                logger "ERROR" "'make check' exists in the upstream community,but we do not."
                return 1
            }

            logger "INFO " "'make check' exists in both the upstream and we."
            return 0
        }

        grep 'make.*check\|make.*test' "$o_check" >/dev/null && {
            logger "INFO " "there is no 'make check' in the upstream community,but we do."
            return 0
        }

        logger "INFO " "there is no 'make check' in the upstream and we."
        return 0
    fi

    if grep -A 10 "^%check" "$o_path_spec" > $o_check; then
        grep 'make.*check\|make.*test' "$o_check" >/dev/null && {
            logger "INFO " "there is no 'make check' in the upstream community,but we do."
            return 0
        }

        logger "INFO " "there is no 'make check' in the upstream and we,but have check."
    fi

    logger "INFO " "there is no 'make check' in the upstream and we."

}

function diff_fedora_openeuler() {
    spec_dir=$(mktemp -d)

    trap 'clean_downfile "$spec_dir"' EXIT INT TERM

    pkg=$1

    clone_spec "https://src.fedoraproject.org/rpms" "$pkg" "$spec_dir" fedora_"$pkg".spec fedora
    test $? -ne 0 && return 1

    clone_spec "https://gitee.com/src-openeuler" "$pkg" "$spec_dir" openEuler_"$pkg".spec
    test $? -ne 0 && return 1

    diff_check "$spec_dir" "$pkg"
}

function check_openeuler() {

    spec_dir=$(mktemp -d)

    trap 'clean_downfile "$spec_dir"' EXIT INT TERM

    pkg=$1

    clone_spec "https://gitee.com/src-openeuler" "$pkg" "$spec_dir" "$pkg".spec || return 1

    check_test "$spec_dir" "$pkg" || return 1
}

function usage() {
    echo -e "Usage:\n
    -c: 检测包的spec文件中，%check是否被使用．
    -d: 对比包的spec文件中％check，在fedora和openEuler中的情况．
    
    Example:
        bash makecheck.sh -c autoconf
        bash makecheck.sh -d autoconf\n"
}

while getopts "c:d:h" option; do
    case $option in
    c)
        pkg=$OPTARG
        [[ -z "$pkg" ]] && {
            usage
            exit 1
        }
        
        check_openeuler "$pkg"
        ;;
    d)
        pkg=$OPTARG
        [[ -z "$pkg" ]] && {
            usage
            exit 1
        }
        
        diff_fedora_openeuler "$pkg"
        ;;
    h)
        usage
        ;;
    *)
        usage
        ;;
    esac
done

