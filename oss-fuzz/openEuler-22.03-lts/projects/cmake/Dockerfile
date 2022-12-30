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

FROM gcr.io/oss-fuzz-base/base-builder:openEuler-22.03-LTS
# RUN apt-get update && apt-get install -y make autoconf automake libtool \
#   pkg-config libssl-dev
RUN yum install -y make autoconf automake libtool \
  pkg-config openssl-devel
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/cmake && \
    cp -r ./cmake/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp cmake.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r cmake-3.24.3 $SRC && \
    cd $SRC && \
    rm -rf cmake && \
    mv cmake-3.24.3 CMake
RUN git clone --depth 1 https://github.com/strongcourage/fuzzing-corpus
WORKDIR CMake
COPY build.sh $SRC/
# This is to fix Fuzz Introspector build by using LLVM old pass manager
# re https://github.com/ossf/fuzz-introspector/issues/305
ENV OLD_LLVMPASS 1
