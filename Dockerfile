FROM ubuntu:bionic

RUN apt-get update -y \
    && apt-get install -y \
    build-essential \
    bison \
    flex \
    libgmp3-dev \
    libmpc-dev \
    libmpfr-dev \
    texinfo \
    libcloog-isl-dev \
    libisl-0.18-dev

ARG INSTALL_PREFIX=/usr/local/cross
ARG TARGET=riscv-elf
ENV PATH "$INSTALL_PREFIX/bin:$PATH"

RUN apt-get install -y wget curl git

WORKDIR /tmp/
RUN curl -L https://github.com/bminor/binutils-gdb/archive/master.tar.gz | tar -xzC ./
RUN mkdir build-binutils \
    && cd build-binutils \
    && ../binutils-gdb-master/configure --target=$TARGET --prefix="$INSTALL_PREFIX" --with-sysroot --disable-nls --disable-werror \
    && make \
    && make install


RUN curl -L https://github.com/gcc-mirror/gcc/archive/master.tar.gz | tar -xzC ./

RUN apt-get install -y gcc-multilib

RUN which -- $TARGET-as || echo $TARGET-as is not in the PATH
 
RUN mkdir build-gcc \
    && cd build-gcc \
    && ../gcc-master/configure --target=$TARGET --prefix="$INSTALL_PREFIX" --disable-nls --enable-languages=c,c++ --without-headers
WORKDIR /tmp/build-gcc    
RUN make all-gcc -j8
RUN  make all-target-libgcc 
RUN  make install-gcc 
RUN  make install-target-libgcc

    
FROM ubuntu:bionic

RUN apt-get update -y \
    && apt-get install -y \
    build-essential \
    bison \
    flex \
    libgmp3-dev \
    libmpc-dev \
    libmpfr-dev \
    texinfo \
    libcloog-isl-dev \
    libisl-0.18-dev

ARG INSTALL_PREFIX=/usr/local/cross
ARG TARGET=riscv-elf

ENV PATH "$INSTALL_PREFIX/bin:$PATH"
ENV CROSS_COMPILE ${TARGET}-

RUN mkdir -p $INSTALL_PREFIX
COPY --from=0 $INSTALL_PREFIX $INSTALL_PREFIX