FROM gcr.io/oss-fuzz-base/base-builder:openeuler-20.03-lts-sp3

RUN yum makecache && yum install -y make autoconf automake libtool
RUN yum install rpm* -y && \
    rpmdev-setuptree && \
    cd $SRC && \
    git clone https://gitee.com/src-openeuler/oniguruma  && \
    cp -r ./oniguruma/* /root/rpmbuild/SOURCES && \
    cd /root/rpmbuild/SOURCES && \
    rpmbuild -bp oniguruma.spec && \
    cd /root/rpmbuild/BUILD && \
    cp -r onig-6.9.8 $SRC && \
    cd $SRC && \
    rm -rf oniguruma && \
    mv onig-6.9.8 oniguruma
RUN git clone --depth 1 https://ghproxy.com/https://github.com/kkos/oniguruma.git temp
RUN cp -r temp/harnesses oniguruma/
WORKDIR oniguruma
COPY build.sh $SRC/
COPY fuzzer.options $SRC/oniguruma/harnesses
