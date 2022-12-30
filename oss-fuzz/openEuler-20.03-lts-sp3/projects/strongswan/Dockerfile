# Copyright 2017 Google Inc.
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
##############################################################################
FROM gcr.io/oss-fuzz-base/base-builder:openeuler-20.03-lts-sp3
RUN yum install -y automake autoconf libtool pkg-config gettext perl python flex bison gperf gmp-devel
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/strongswan && \
    cp -r ./strongswan/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp strongswan.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r strongswan-5.9.7 $SRC && \
    cd $SRC && \
    rm -rf strongswan && \
    mv strongswan-5.9.7 strongswan
#RUN sed -i "1298a libfuzzer=\"\"" strongswan/configure.ac && \
#    sed -i "1299a FUZZING_CFLAGS=\"-fsanitize=fuzzer\"" strongswan/configure.ac && \
#    sed -i "1300a AC_SUBST(FUZZING_CFLAGS)" strongswan/configure.ac
RUN git clone --depth 1 https://github.com/strongswan/fuzzing-corpora.git strongswan/fuzzing-corpora
RUN git clone -b 5.9.7 https://github.com/strongswan/strongswan.git strongswan-temp && \
rm -r strongswan/fuzz && \
cp -r strongswan-temp/fuzz strongswan/ && \
rm -rf strongswan-temp

WORKDIR strongswan
COPY build.sh $SRC/
