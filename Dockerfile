FROM ubuntu:jammy

ARG USER
ARG USER_ID
ARG GROUP

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && apt-get -y install tzdata

RUN apt-get update \
    && apt-get install -y build-essential \
        gcc \
        g++ \
        gdb \
        clang-15 \
        clangd-15 \
        make \
        ninja-build \
        autoconf \
        automake \
        libtool \
        valgrind \
        locales-all \
        dos2unix \
        rsync \
        tar \
        python3 \
        python3-pip \
        python3-dev \
        git \
        unzip \
        wget \
        gpg \
        ca-certificates \
        openssl \
        openjdk-17-jdk \
        openjdk-17-jre \
        git \
        ant \
        libxml2-utils \
    && apt-get clean

RUN update-java-alternatives --set /usr/lib/jvm/java-1.17.0-openjdk-amd64
RUN echo 'export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:bin/javac::")' >> ~/.bashrc

RUN useradd -g $GROUP -u $USER_ID $USER

USER $USER

RUN mkdir /etc/cassandra /var/lib/cassandra
