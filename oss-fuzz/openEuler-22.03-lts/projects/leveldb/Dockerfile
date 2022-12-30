# Copyright 2020 Google Inc.
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

FROM gcr.io/oss-fuzz-base/base-builder:openEuler-22.03-LTS
# RUN apt-get update && apt-get install -y make autoconf automake libtool gettext pkg-config build-essential
RUN yum install -y make autoconf automake libtool gettext pkg-config gcc gcc-c++ kernel-devel
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/huyab/leveldb.git && \
    cp -r ./leveldb/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp leveldb.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r  leveldb-1.23 $SRC && \
    cd $SRC && \
    rm -rf leveldb && \
    mv leveldb-1.23 leveldb
WORKDIR $SRC/

# Copy in our files
COPY build.sh $SRC/
COPY *.cc $SRC/leveldb/
COPY *.options $SRC/
