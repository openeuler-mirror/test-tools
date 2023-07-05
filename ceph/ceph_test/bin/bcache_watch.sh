n=`ls /sys/block |grep bcache |wc -l`
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
#echo $n
LINE="------------------------------------------------------------------------------------------------------"
echo $LINE
echo `hostname`
j=$n
CACHEMODE="cachemode"
HITRATIO="hit%"
READAHEAD="rdahd"
SEQCUTOFF="seqcf"
WBPER="wb%"
WBDELAY="wbdly"
DIRTYDATA="dtydata"
STAT="stat"
CACHEPER="cache%"
BYPASS="bypass"
echo $LINE
echo -e "bcacheNo.\0011$HITRATIO\0011$BYPASS\0011$CACHEMODE\0011$READAHEAD\0011$SEQCUTOFF\0011$WBPER\0011$WBDELAY\0011$DIRTYDATA\0011$STAT\0011$CACHEPER"
echo $LINE
for i in `ls /sys/block |grep bcache`
do
        cd /sys/block/${i}/bcache
        cache_mode=`for k in {1..4};do cat cache_mode |cut -d " " -f $k |grep "\[" |sed 's/\[//g' |sed 's/\]//g';done`
        hitratio=`cat stats_five_minute/cache_hit_ratio`
        bypass=`cat stats_five_minute/bypassed`
        readahead=`cat readahead`
        seq_cutoff=`cat sequential_cutoff`
        wbper=`cat writeback_percent`
        wbdelay=`cat writeback_delay`
        dirtydata=`cat dirty_data`
        stat=`cat state`
        cache=`cat cache/cache_available_percent`
        echo -e "${i} \0011$hitratio\0011$bypass\0011$cache_mode\0011$readahead\0011$seq_cutoff\0011$wbper\0011$wbdelay \0011$dirtydata \0011$stat\0011$cache"
done

