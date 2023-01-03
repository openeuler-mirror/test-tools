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

FROM gcr.io/oss-fuzz-base/base-builder:openEuler-22.03-LTS
RUN yum install -y libtool
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone  https://gitee.com/src-openeuler/aspell.git && \
    cp -r ./aspell/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp aspell.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r  aspell-0.60.8 $SRC && \
    cd $SRC && \
    rm -rf aspell && \
    mv aspell-0.60.8 aspell
COPY issue.patch $SRC/aspell/
RUN git clone --depth 1 -b master https://github.com/gnuaspell/aspell-fuzz.git $SRC/aspell-fuzz
RUN sed -i 's/apt-get/yum/' $SRC/aspell-fuzz/ossfuzz.sh
RUN sed -i '/autopoint/d' $SRC/aspell-fuzz/ossfuzz.sh
RUN cd $SRC/aspell && \
    git apply $SRC/aspell/issue.patch
COPY build.sh $SRC/
