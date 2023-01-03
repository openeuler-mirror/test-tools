#!/bin/bash -eux
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


SWIFT_PACKAGES="wget \
          binutils \
          git \
          gnupg2 \
          glibc-devel \
          libcurl \
          libedit \
          gcc \
          libpython2.7 \
          sqlite-devel \
          libstdc++-devel \
          libxml2 \
          zlib-devel \
          pkg-config \
          tzdata \
          zlib-dev"
SWIFT_SYMBOLIZER_PACKAGES="gcc gcc-c++ kernel-devel make cmake ninja-build git python3 libstdc++ libstdc++-devel binutils-devel zlib-devel"
yum makecache && yum install -y $SWIFT_PACKAGES && \
yum install -y $SWIFT_SYMBOLIZER_PACKAGES

wget https://download.swift.org/swift-5.6.1-release/centos7/swift-5.6.1-RELEASE/swift-5.6.1-RELEASE-centos7.tar.gz
tar xzf swift-5.6.1-RELEASE-centos7.tar.gz
cp -r swift-5.6.1-RELEASE-centos7/usr/* /usr/
rm -rf swift-5.6.1-RELEASE-centos7.tar.gz

mkdir /usr/lib/x86_64-linux-gnu/
ln -s /usr/lib64/libstdc++.so.6 /usr/lib/x86_64-linux-gnu/libstdc++.so.6
git clone https://gitee.com/mirrors/llvm-project.git
cd llvm-project
git checkout 63bf228450b8403e0c5e828d276be47ffbcd00d0 # TODO: Keep in sync with base-clang.
git apply ../llvmsymbol.diff --verbose
cmake -G "Ninja" \
    -DLIBCXX_ENABLE_SHARED=OFF \
    -DLIBCXX_ENABLE_STATIC_ABI_LIBRARY=ON \
    -DLIBCXXABI_ENABLE_SHARED=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_TARGETS_TO_BUILD=X86 \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DLLVM_BUILD_TESTS=OFF \
    -DLLVM_INCLUDE_TESTS=OFF llvm
ninja -j$(nproc) llvm-symbolizer

cp bin/llvm-symbolizer /usr/local/bin/llvm-symbolizer-swift
cd $SRC
rm -rf llvm-project llvmsymbol.diff

# TODO: Cleanup packages
yum remove -y wget zlib-devel
