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
#RUN yum makecache && yum install -y make autoconf automake libtool libffi-devel xz-devel zlib-devel ilmbase-devel
RUN yum makecache && yum install -y make autoconf automake libtool libffi-devel xz-devel zlib-devel
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/OpenEXR && \
    cp -r ./OpenEXR/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp OpenEXR.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r  openexr-3.1.5 $SRC && \
    cd $SRC && \
    rm -rf OpenEXR && \
    mv openexr-3.1.5 openexr
WORKDIR openexr
COPY build.sh $SRC/

