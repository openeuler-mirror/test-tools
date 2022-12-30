# Copyright 2018 Google Inc.
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
RUN yum makecache && yum install -y make autoconf automake libtool cmake nasm
# Use source code from src-openEuler
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/qpdf.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./qpdf/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp qpdf.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r qpdf-8.4.2 $SRC && \
    cd $SRC && \
    rm -rf qpdf && \
    mv qpdf-8.4.2 qpdf

RUN git clone --depth 1 https://ghproxy.com/https://github.com/madler/zlib.git zlib
RUN git clone --depth 1 https://ghproxy.com/https://github.com/libjpeg-turbo/libjpeg-turbo libjpeg-turbo
WORKDIR qpdf
COPY build.sh qpdf_read_memory_fuzzer.cc $SRC/
# This is to fix Fuzz Introspector build by using LLVM old pass manager
# re https://github.com/ossf/fuzz-introspector/issues/305
ENV OLD_LLVMPASS 1
