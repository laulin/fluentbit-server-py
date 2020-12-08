from ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get upgrade -y && apt-get -y install wget build-essential cmake gcc flex bison
WORKDIR /root
RUN wget https://fluentbit.io/releases/1.6/fluent-bit-1.6.1.tar.gz
RUN tar -xf fluent-bit-1.6.1.tar.gz
WORKDIR /root/fluent-bit-1.6.1/cmake
RUN cmake -DFLB_TLS=Yes ..
RUN make
RUN make install
RUN mkdir -p /fluent/etc
RUN apt-get -y remove wget build-essential cmake gcc flex bison
WORKDIR /fluent

