#!/bin/bash

if ! cat < /etc/profile |grep "^export HBASE_HOME=/usr/local/hbase";then
    echo "export HBASE_HOME=/usr/local/hbase" >> /etc/profile
fi

if ! cat < /etc/profile |grep '^export PATH=${HBASE_HOME}/bin:${HBASE_HOME}/sbin:${PATH}';then
    echo 'export PATH=${HBASE_HOME}/bin:${HBASE_HOME}/sbin:${PATH}' >> /etc/profile
fi
