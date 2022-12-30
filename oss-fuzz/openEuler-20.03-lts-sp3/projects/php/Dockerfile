# Copyright 2019 Google Inc.
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
RUN yum makecache && \
    yum install -y autoconf automake libtool bison re2c pkgconfig

# Use source code from src-openEuler
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/php.git  && \
    cp -r ./php/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp php.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r php-8.2.0 $SRC && \
    cd $SRC && \
    mv php-8.2.0 php-src

WORKDIR php-src
COPY build.sh *.options $SRC/
