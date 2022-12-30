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

# RUN apt-get update && apt-get install -y make
RUN yum install -y make
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/haproxy -b openEuler-22.03-LTS && \
    cp -r ./haproxy/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp haproxy.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r haproxy-2.4.8 $SRC && \
    cd $SRC && \
    rm -rf haproxy && \
    mv haproxy-2.4.8 haproxy
WORKDIR $SRC

COPY build.sh $SRC
COPY fuzz* $SRC/
