from string import Template
import os

temp = Template("""
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
ARG TARGET=${target}
ENV PATH "$$INSTALL_PREFIX/bin:$$PATH"

RUN apt-get install -y wget curl git

WORKDIR /tmp/
RUN mkdir binutils-gdb
RUN curl -L https://github.com/bminor/binutils-gdb/archive/master.tar.gz \
    | tar --strip-components 1 -xzC ./binutils-gdb
RUN mkdir build-binutils \
    && cd build-binutils \
    && ../binutils-gdb/configure --target=$$TARGET --prefix="$$INSTALL_PREFIX" --with-sysroot --disable-nls --disable-werror \
    && make \
    && make install


RUN mkdir gcc
RUN curl -L ${gcc_url} \
    | tar --strip-components 1 -xzC ./gcc

RUN apt-get install -y gcc-multilib

RUN which -- $$TARGET-as || echo $$TARGET-as is not in the PATH
 
RUN mkdir build-gcc \
    && cd build-gcc \
    && ../gcc/configure --target=$$TARGET --prefix="$$INSTALL_PREFIX" --disable-nls --enable-languages=c,c++ --without-headers
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
ARG TARGET=${target}

ENV PATH "$$INSTALL_PREFIX/bin:$$PATH"
ENV CROSS_COMPILE $${TARGET}-

RUN mkdir -p $$INSTALL_PREFIX
COPY --from=0 $$INSTALL_PREFIX $$INSTALL_PREFIX
""")

vers = [
    ("7.1.0", "riscv64-elf"),
    ("7.2.0", "riscv64-elf"),
    ("7.3.0", "riscv64-elf"),
    ("7.4.0", "riscv64-elf"),
    ("7.5.0", "riscv64-elf"),        
    ("8.1.0", "riscv64-elf"),
    ("8.2.0", "riscv64-elf"),
    ("8.3.0", "riscv64-elf"),
    ("8.4.0", "riscv64-elf"),
    ("9.1.0", "riscv-elf"),
    ("9.2.0", "riscv-elf"),
    ("9.3.0", "riscv-elf"),
    ("10.1.0", "riscv-elf")    
]

def output_docker_file(d, gcc_url, target):
    os.makedirs(d, exist_ok=True)
    with open("{}/Dockerfile".format(d), "w") as f:
        s = temp.substitute(gcc_url=gcc_url, target=target)
        f.write(s)

for v, target in vers:
    url = "https://github.com/gcc-mirror/gcc/archive/releases/gcc-{}.tar.gz".format(v)
    output_docker_file(v, url, target)

output_docker_file("master", "https://github.com/gcc-mirror/gcc/archive/master.tar.gz", "riscv-elf")

