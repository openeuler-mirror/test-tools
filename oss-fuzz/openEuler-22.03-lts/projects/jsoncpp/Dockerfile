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
# RUN apt-get update -y && apt-get install -y curl wget \
#     binutils cmake ninja-build liblzma-dev libz-dev pkg-config autoconf libtool
RUN yum install -y curl wget \
    binutils cmake ninja-build xz-devel zlib-devel pkg-config autoconf libtool doxygen
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/jsoncpp -b openEuler-22.03-LTS && \
    cp -r ./jsoncpp/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp jsoncpp.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r jsoncpp-1.9.5 $SRC && \
    cd $SRC && \
    rm -rf jsoncpp && \
    mv jsoncpp-1.9.5 jsoncpp
WORKDIR jsoncpp
RUN git clone --depth 1 https://github.com/google/libprotobuf-mutator.git
RUN (mkdir LPM && cd LPM && cmake ../libprotobuf-mutator -GNinja -DLIB_PROTO_MUTATOR_DOWNLOAD_PROTOBUF=ON -DLIB_PROTO_MUTATOR_TESTING=OFF -DCMAKE_BUILD_TYPE=Release && ninja)
COPY build.sh *.proto *.h *.cc $SRC/
# This is to fix Fuzz Introspector build by using LLVM old pass manager
# re https://github.com/ossf/fuzz-introspector/issues/305
ENV OLD_LLVMPASS 1
