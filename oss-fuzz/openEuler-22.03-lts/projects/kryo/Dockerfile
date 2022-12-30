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
RUN curl -L https://repo.huaweicloud.com/apache/maven/maven-3/3.6.3/binaries/apache-maven-3.6.3-bin.zip -o maven.zip && \
    unzip maven.zip -d $SRC/maven && \
    rm -rf maven.zip

# Change jdk version to compile source-code from src-openEuler
ENV MVN $SRC/maven/apache-maven-3.6.3/bin/mvn
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV JVM_LD_LIBRARY_PATH $JAVA_HOME/jre/lib/amd64/server
ENV PATH $PATH:$JAVA_HOME/bin

RUN cd /tmp &&\
curl -L -O https://repo.huaweicloud.com/java/jdk/8u202-b08/jdk-8u202-linux-x64.tar.gz && \
mkdir -p $JAVA_HOME &&\
tar -xzv --strip-components=1 -f jdk-8u202-linux-x64.tar.gz --directory $JAVA_HOME && \
rm -f jdk-8u202-linux-x64.tar.gz && \
rm -rf $JAVA_HOME/jmods $JAVA_HOME/lib/src.zip

# Use source code from src-openEuler
RUN yum install rpm* maven-local -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/kryo.git -b openEuler-22.03-LTS && \
    cp -r ./kryo/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp kryo.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r kryo-kryo-parent-4.0.2 $SRC && \
    cd $SRC && \
    rm -rf kryo && \
    mv kryo-kryo-parent-4.0.2 kryo && \
    sed -i '27d' kryo/pom-main.xml && \
    yum remove -y maven-local

COPY build.sh $SRC/
COPY DeserializeCollectionsFuzzer.java DeserializeNumbersFuzzer.java DeserializeStringFuzzer.java $SRC/
WORKDIR $SRC/kryo
