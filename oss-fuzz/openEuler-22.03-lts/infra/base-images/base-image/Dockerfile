# Copyright 2016 Google Inc.
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

# Base image for all other images.

FROM openeuler/openeuler:22.03-lts
ENV DEBIAN_FRONTEND noninteractive
RUN yum clean all && \
    yum makecache && \
    yum update -y --nogpgcheck && \
    yum install -y --nogpgcheck glibc-devel binutils gcc

ENV OUT=/out
ENV SRC=/src
ENV WORK=/work
ENV PATH="$PATH:/out"

RUN mkdir -p $OUT $SRC $WORK && chmod a+rwx $OUT $SRC $WORK
