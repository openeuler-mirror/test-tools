
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
RUN yum makecache && yum install -y unzip
RUN curl -L https://repo.huaweicloud.com/apache/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.zip -o maven.zip && \
    unzip maven.zip -d $SRC/maven && \
    rm -rf maven.zip
ENV MAVEN_HOME $SRC/maven/apache-maven-3.8.6
ENV PATH $MAVEN_HOME/bin:$PATH

RUN git clone --depth 1 https://github.com/google/fuzzing
RUN cat fuzzing/dictionaries/json.dict > $SRC/JsonFuzzer.dict

ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV JVM_LD_LIBRARY_PATH $JAVA_HOME/jre/lib/amd64/server
ENV PATH $PATH:$JAVA_HOME/bin

RUN cd /tmp &&\
curl -L -O https://repo.huaweicloud.com/java/jdk/8u202-b08/jdk-8u202-linux-x64.tar.gz && \
mkdir -p $JAVA_HOME &&\
tar -xzv --strip-components=1 -f jdk-8u202-linux-x64.tar.gz --directory $JAVA_HOME && \
rm -f jdk-8u202-linux-x64.tar.gz && \
rm -rf $JAVA_HOME/jmods $JAVA_HOME/lib/src.zip

RUN git clone --depth 1 https://github.com/dvyukov/go-fuzz-corpus && \
    zip -j $SRC/JsonFuzzer_seed_corpus.zip go-fuzz-corpus/json/corpus/*

ENV JACKSON_BRANCH=jackson-annotations-2.9.8

# Use source code from src-openEuler
RUN yum install rpm* maven-local -y && \
    rpmdev-setuptree && \
    git clone https://gitee.com/src-openeuler/jackson-core.git -b openEuler-20.03-LTS-SP3 && \
    git clone https://gitee.com/src-openeuler/jackson-databind.git -b openEuler-20.03-LTS-SP3 && \
    cp -r ./jackson-core/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp jackson-core.spec && \
    cp -r $SRC/jackson-databind/* /root/rpmbuild/SOURCES && \
    rpmbuild -bp jackson-databind.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r jackson-core-jackson-core-2.9.8 jackson-databind-jackson-databind-2.9.8 $SRC && \
    cd $SRC && \
    rm -rf jackson-core jackson-databind && \
    mv jackson-core-jackson-core-2.9.8 jackson-core && \
    mv jackson-databind-jackson-databind-2.9.8 jackson-databind && \
    yum remove maven-local -y

#COPY jackson-core-jackson-core-2.9.8 jackson-core
#COPY jackson-databind-jackson-databind-2.9.8 jackson-databind
RUN git clone --depth 1 --branch=$JACKSON_BRANCH https://github.com/FasterXML/jackson-annotations

COPY build.sh $SRC/
COPY JsonFuzzer.java $SRC/
WORKDIR $SRC/
