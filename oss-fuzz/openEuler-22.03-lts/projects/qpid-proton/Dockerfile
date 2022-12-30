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
RUN yum makecache && \
    yum install -y \
        cmake

# Use source code from src-openEuler
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/qpid-proton.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./qpid-proton/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp qpid-proton.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r qpid-proton-0.24.0 $SRC && \
    cd $SRC && \
    rm -rf qpid-proton && \
    mv qpid-proton-0.24.0 qpid-proton

WORKDIR qpid-proton
COPY build.sh $SRC/
