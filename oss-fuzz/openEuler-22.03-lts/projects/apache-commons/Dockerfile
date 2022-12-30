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

FROM gcr.io/oss-fuzz-base/base-builder-jvm:openEuler-22.03-LTS
RUN yum makecache && yum install unzip -y
RUN curl -L https://repo.huaweicloud.com/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.zip -o maven.zip && \
    unzip maven.zip -d $SRC/maven && \
    rm -rf maven.zip
ENV MVN $SRC/maven/apache-maven-3.6.3/bin/mvn

# Use source code from src-openEuler
RUN yum install rpm* maven-local -y && \
    rpmdev-setuptree && \
    git clone https://gitee.com/src-openeuler/apache-commons-compress.git -b openEuler-20.03-LTS-SP3 && \
    git clone https://gitee.com/src-openeuler/apache-commons-math.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./apache-commons-compress/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp apache-commons-compress.spec && \
    cp -r $SRC/apache-commons-math/* /root/rpmbuild/SOURCES && \
    rpmbuild -bp apache-commons-math.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r commons-math3-3.4.1-src commons-compress-1.21-src $SRC && \
    cd $SRC && \
    mv commons-math3-3.4.1-src commons-math && \
    mv commons-compress-1.21-src commons-compress

# Remove JAVA because maven-local changed the PATH
RUN yum remove java -y
# Dictionaries
RUN git clone --depth 1 https://github.com/google/fuzzing && \
    mv fuzzing/dictionaries/zip.dict $SRC/CompressZipFuzzer.dict && \
    rm -rf fuzzing

# Seed corpus (go-fuzz-corpus)
RUN git clone --depth 1 https://github.com/dvyukov/go-fuzz-corpus && \
    zip -j $SRC/CompressTarFuzzer_seed_corpus.zip go-fuzz-corpus/tar/corpus/* && \
    zip -j $SRC/CompressZipFuzzer_seed_corpus.zip go-fuzz-corpus/zip/corpus/* && \
    rm -rf go-fuzz-corpus

# Compress
RUN zip -uj $SRC/CompressTarFuzzer_seed_corpus.zip commons-compress/src/test/resources/*.tar && \
    zip -uj $SRC/CompressZipFuzzer_seed_corpus.zip commons-compress/src/test/resources/*.zip && \
    zip -j $SRC/CompressSevenZFuzzer_seed_corpus.zip commons-compress/src/test/resources/bla.7z

# Copy build script and all fuzzers
COPY build.sh $SRC/
COPY *Fuzzer.java $SRC/
WORKDIR $SRC/
