#!/bin/bash
root_path=$(cd $(dirname $0)||exit 1;pwd)

cd ${root_path}
ceph pg dump pgs|awk '{print $1,$17}' > pgdump
ceph osd tree up > osdtree
if [[ "$(arch)" = "aarch64" ]];then
  ./primarypgbalancer-opt-arm-v3 pgdump osdtree > newpgmap
elif [[ "$(arch)" = "x86_64" ]];then
  ./primarypgbalancer-opt-x86-v3 pgdump osdtree > newpgmap
else
  echo "pg balance not support arch $(arch)"
  exit 1
fi
ceph osd set-require-min-compat-client luminous --yes-i-really-mean-it
source ${root_path}/newpgmap
