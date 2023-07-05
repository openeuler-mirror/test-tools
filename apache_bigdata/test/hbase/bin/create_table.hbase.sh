
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
disable "ImportTable"

drop "ImportTable"

rows_start = 1
rows_end = 1073741823
split_num = 800

splitArr = []

interval = (rows_end - rows_start + 1)/split_num

puts "interval=%d" % interval

for i in 1..split_num
  j="%032d" % (rows_start  + interval * i) 
  splitArr.push(j)
end

create "ImportTable",{NAME => "f1", COMPRESSION => "SNAPPY"}, SPLITS => splitArr 

list

exit
