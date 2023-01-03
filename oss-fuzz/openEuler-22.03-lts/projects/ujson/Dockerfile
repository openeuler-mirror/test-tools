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

FROM gcr.io/oss-fuzz-base/base-builder-python:openEuler-22.03-LTS

RUN pip3 install hypothesis

# Use source code from src-openEuler
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/python-ujson.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./python-ujson/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp ujson.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r ujson-4.0.2 $SRC && \
    cd $SRC && \
    mv ujson-4.0.2 ultrajson

WORKDIR ultrajson

COPY build.sh json_differential_fuzzer.py ujson_fuzzer.py hypothesis_structured_fuzzer.py $SRC/
