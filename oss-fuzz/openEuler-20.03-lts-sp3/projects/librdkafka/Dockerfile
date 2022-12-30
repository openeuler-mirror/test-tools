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
FROM gcr.io/oss-fuzz-base/base-builder:openeuler-20.03-lts-sp3
RUN yum makecache && yum install -y make cmake flex bison openssl openssl-devel cyrus-sasl cyrus-sasl-devel
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/huyab/librdkafka.git && \
    cp -r ./librdkafka/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp librdkafka.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r  librdkafka-1.9.2 $SRC && \
    cd $SRC && \
    rm -rf librdkafka && \
    mv librdkafka-1.9.2 librdkafka
RUN git clone https://ghproxy.com/https://github.com/edenhill/librdkafka temp
RUN rm -rf librdkafka/tests && cp -r temp/tests librdkafka/
WORKDIR $SRC
COPY build.sh $SRC/
