# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################

FROM gcr.io/oss-fuzz-base/base-builder:openeuler-20.03-lts-sp3
# RUN apt-get update && apt-get install -y make
RUN yum install -y make python3-devel-3.7.9-29.oe1
RUN  pip3 install pathfix.py
RUN yum install rpm* -y && \
    rpmdev-setuptree 
RUN cd $SRC && \
    git clone  https://gitee.com/huyab/fio.git && \
    cp -r ./fio/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    sed -i '45d' fio.spec && \
    sed -i '44a /usr/bin/pathfix.py -i /interpreter -p -n\\' fio.spec && \
    rpmbuild -bp fio.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r  fio-3.32 $SRC && \
    cd $SRC && \
    rm -rf fio && \
    mv fio-3.32 fio
WORKDIR $SRC/fio
COPY build.sh $SRC/
