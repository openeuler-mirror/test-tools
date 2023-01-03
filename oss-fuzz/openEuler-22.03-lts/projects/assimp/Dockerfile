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
# RUN apt-get update && apt-get install -y cmake ninja-build
RUN yum install -y cmake ninja-build
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/assimp  && \
    cp -r ./assimp/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp assimp.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r assimp-5.2.4 $SRC && \
    cd $SRC && \
    rm -rf assimp && \
    mv assimp-5.2.4 assimp

WORKDIR assimp
COPY build.sh $SRC/

