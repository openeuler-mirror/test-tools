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

FROM gcr.io/oss-fuzz-base/base-builder-go-codeintelligencetesting:openeuler-20.03-lts-sp3
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/tidb -b openEuler-20.03-LTS-SP3 && \
    cp -r ./tidb/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp tidb.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r tidb-4.0.14 $SRC && \
    cd $SRC && \
    rm -rf tidb && \
    mv tidb-4.0.14 tidb
COPY build.sh \
     fuzzMarshalJSON.go \
     fuzzNewBitLiteral.go \
     fuzzNewHexLiteral.go \
     $SRC/
WORKDIR $SRC/tidb
