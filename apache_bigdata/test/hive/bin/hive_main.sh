#!/bin/bash
# Copyright (c) 2023. Huawei Technologies Co.,Ltd.ALL rights reserved.
# This program is licensed under Mulan PSL v2.
# You can use it according to the terms and conditions of the Mulan PSL v2.
#          http://license.coscl.org.cn/MulanPSL2
# THIS PROGRAM IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# #############################################
# @Author    :   hekeming
# @Contact   :   hk16897@126.com
# @Date      :   2023/07/03
# @License   :   Mulan PSL v2
# @Desc      :   Test SSH link
# ############################################
############################# 参数数量合法性检查 ##########################################
if [[ $# -ne 1 ]]; then
    echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql|tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql"
    exit 1
fi

###### 测试环境准备 ###########################
app_dir=$(cd "$(dirname "$0")"/..||exit 1;pwd)
tmp_log=${app_dir}/report/hive_tpcds_new.report
inputParameter=$1
source  ${app_dir}/../tools/commonConfig

########### STEP 1 ############################
# 性能数据采集shell脚本
#logPath='/tmp/dataCollection/'
#source ${logPath}dataCollect.sh

########### STEP 2-1 prepare ##################
case ${inputParameter} in
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
        bash "${app_dir}"/bin/hive_tpcds_test.sh prepare
        ;;
    tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
        bash "${app_dir}"/bin/hive_tpch.sh prepare
        ;;
    *)  echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql"
        exit 1
        ;;
esac


########### STEP 2-2 datacollect on ###########
# 判断上一条命令是否执行成功
if [ $? -ne 0 ]; then
    echo "[ERROR] prepare failed"
    exit 1
fi
# 基础性能数据采集开启
# data_collect --nmon -f 5 -c 60 -- --perf -n AmbariServer -s 5 -d 10 -T 0 --

########### STEP 2-3 testing ##################
case ${inputParameter} in
    sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql)
        bash "${app_dir}"/bin/hive_tpcds_test.sh "${1}"
        ;;
    tpch_query1.sql|tpch_query2.sql|tpch_query3.sql|tpch_query4.sql|tpch_query5.sql|tpch_query6.sql|tpch_query7.sql|tpch_query8.sql|tpch_query9.sql|tpch_query10.sql|tpch_query11.sql|tpch_query12.sql|tpch_query13.sql|tpch_query14.sql|tpch_query15.sql|tpch_query16.sql|tpch_query17.sql|tpch_query18.sql|tpch_query19.sql|tpch_query20.sql|tpch_query21.sql|tpch_query22.sql)
        bash "${app_dir}"/bin/hive_tpch.sh "${inputParameter}"
        ;;
    *)  echo "[Usage] bash ${0##*/} sql1.sql|sql2.sql|sql3.sql|sql4.sql|sql5.sql|sql6.sql|sql7.sql|sql8.sql|sql9.sql|sql10.sql"
        exit 1
        ;;
esac

########### STEP 3 ##################
if [ ! -f "${tmp_log}" ]; then
    echo "[ERROR] ${tmp_log} miss..."
    exit 1
fi

result_delay=$(cat < "${tmp_log}" | grep "Result" | awk '{print $11}' | sed -n '1p')
echo "${result_delay}"

# 性能数据采集停止
# data_collect stop
