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

FROM gcr.io/oss-fuzz-base/base-builder-python:openEuler-22.03-LTS

# Use source code from src-openEuler
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/python-sqlalchemy.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./python-sqlalchemy/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp python-sqlalchemy.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r SQLAlchemy-1.2.19 $SRC && \
    cd $SRC && \
    mv SQLAlchemy-1.2.19 sqlalchemy

WORKDIR $SRC/sqlalchemy
COPY build.sh sqlalchemy_fuzzer.py $SRC/
