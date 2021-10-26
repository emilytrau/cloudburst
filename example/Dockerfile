# Base image
FROM ubuntu:20.04 as base

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential wget python3 python3-pip libssl-dev libjson-c-dev libmariadbclient-dev libopenmpi-dev

## Install MUNGE
RUN wget https://github.com/dun/munge/releases/download/munge-0.5.14/munge-0.5.14.tar.xz \
    && tar xf munge-0.5.14.tar.xz \
    && cd munge-0.5.14 \
    && mkdir -p /opt/munge \
    && ./configure --prefix=/opt/munge --sysconfdir=/etc \
    && make \
    && make install \
    && cd .. \
    && rm -rf munge-0.5.14.tar.xz munge-0.5.14

## Install SLURM
RUN wget https://download.schedmd.com/slurm/slurm-20.02.7.tar.bz2 \
    && tar xf slurm-20.02.7.tar.bz2 \
    && cd slurm-20.02.7 \
    && mkdir -p /opt/slurm \
    && ./configure --prefix=/opt/slurm --sysconfdir=/etc \
    && make \
    && make install \
    && cd .. \
    && rm -rf slurm-20.02.7.tar.bz2 slurm-20.02.7

## Install extra utilities
RUN apt-get update && apt-get install -y curl inetutils-ping

## Create system users
RUN useradd -ms /bin/bash user \
    && useradd slurm

RUN chown -R slurm /opt/slurm

ENV PATH="/opt/munge/bin:/opt/slurm/bin:${PATH}"
COPY ./example/entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

# SLURM daemon image
FROM base as slurm

COPY ./example/cloudburst.ini /etc/cloudburst/cloudburst.ini
COPY ./client /client
RUN pip install -e /client

CMD [ "/opt/slurm/sbin/slurmctld", "-D", "-v" ]

# Compute node image
FROM base as compute

WORKDIR /home/user

CMD [ "/opt/slurm/sbin/slurmd", "-D", "-v" ]
