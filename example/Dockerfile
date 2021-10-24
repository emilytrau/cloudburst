# Base image
FROM ubuntu:20.04 as base

RUN apt-get update && apt-get install -y build-essential wget python3 python3-pip libssl-dev libjson-c-dev inetutils-ping

## Install MUNGE
RUN wget https://github.com/dun/munge/releases/download/munge-0.5.14/munge-0.5.14.tar.xz \
    && tar xf munge-0.5.14.tar.xz \
    && cd munge-0.5.14 \
    && mkdir -p /opt/munge /mungeconfig /mungedata \
    && ./configure --prefix=/opt/munge --sysconfdir=/mungeconfig --localstatedir=/mungedata --runstatedir=/run \
    && make \
    && make install \
    && cd .. \
    && rm -rf munge-0.5.14.tar.xz munge-0.5.14

## Install SLURM
## 20.02.7 is the latest supported by pyslurm
RUN wget https://download.schedmd.com/slurm/slurm-20.02.7.tar.bz2 \
    && tar xf slurm-20.02.7.tar.bz2 \
    && cd slurm-20.02.7 \
    && mkdir -p /opt/slurm /config /data \
    && ./configure --prefix=/opt/slurm --sysconfdir=/config --localstatedir=/data --runstatedir=/run --enable-multiple-slurmd \
    && make \
    && make install \
    && cd .. \
    && rm -rf slurm-20.02.7.tar.bz2 slurm-20.02.7

## Install pyslurm
RUN wget https://github.com/PySlurm/pyslurm/archive/refs/tags/20-02-0.tar.gz \
    && tar xf 20-02-0.tar.gz \
    && cd pyslurm-20-02-0 \
    && python3 -m pip install cython \
    && python3 setup.py build --slurm=/opt/slurm \
    && python3 setup.py install \
    && cd .. \
    && rm -rf 20-02-0.tar.gz pyslurm-20-02-0

## Create system users
RUN useradd slurm \
    && useradd -ms /bin/bash user

ENV PATH="/opt/munge/bin:/opt/slurm/bin:${PATH}"
COPY ./example/slurm.conf /config/slurm.conf
COPY ./example/entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

# SLURM daemon image
FROM base as slurm

RUN chown -R slurm /config /data

COPY ./client /client
RUN pip install -e /client

CMD [ "/opt/slurm/sbin/slurmctld", "-D", "-v", "-f", "/config/slurm.conf" ]

# Compute node image
FROM base as compute

RUN mkdir /data/slurmd
WORKDIR /home/user

CMD [ "/opt/slurm/sbin/slurmd", "-D", "-v", "-f", "/config/slurm.conf" ]
