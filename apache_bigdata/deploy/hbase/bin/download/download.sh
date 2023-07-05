#!/bin/bash

cd "$(dirname "$0")"||exit 1
tool_root_dir=$(cd ../..||exit 1;pwd)
source "${tool_root_dir}/conf/config"

echo "start download packages!"

has_wget=$(command -v wget)
if [ "${has_wget}" == "" ]; then
  echo "Please install wget first!"
  exit 1
fi

mkdir -p "${tool_root_dir}/deps/${platform}/${hbase_version}/" > /dev/null 2>&1
# Download hbase
if ! wget -O "${tool_root_dir}/deps/${platform}/${hbase_version}/${package}" "${download_url}/tarball/${arch}/${os}/${platform}/${package}"; then
    echo "Failed to download ${package}, Please check your configure!"
    exit 1
fi
