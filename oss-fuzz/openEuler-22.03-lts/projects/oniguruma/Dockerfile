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
RUN yum makecache && yum install -y make autoconf automake libtool
RUN yum install rpm* -y && \
    rpmdev-setuptree && \  
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/oniguruma  && \
    cp -r ./oniguruma/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp oniguruma.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r onig-6.9.8 $SRC && \
    cd $SRC && \
    rm -rf oniguruma && \
    mv onig-6.9.8 oniguruma
RUN git clone --depth 1 https://ghproxy.com/https://github.com/kkos/oniguruma.git temp
RUN cp -r temp/harnesses oniguruma/
WORKDIR oniguruma
COPY build.sh $SRC/
COPY fuzzer.options $SRC/oniguruma/harnesses
