# Base image
FROM ubuntu:20.04 as base

RUN apt-get update && apt-get install -y build-essential wget python3 python3-pip libssl-dev libjson-c-dev

## Install MUNGE
RUN wget https://github.com/dun/munge/releases/download/munge-0.5.14/munge-0.5.14.tar.xz \
    && tar xf munge-0.5.14.tar.xz \
    && cd munge-0.5.14 \
    && mkdir -p /opt/munge /config /data \
    && ./configure --prefix=/opt/munge --sysconfdir=/config --localstatedir=/data --runstatedir=/run \
    && make \
    && make install \
    && cd .. \
    && rm -rf munge-0.5.14.tar.xz munge-0.5.14

## Install SLURM
RUN wget https://download.schedmd.com/slurm/slurm-21.08.2.tar.bz2 \
    && tar xf slurm-21.08.2.tar.bz2 \
    && cd slurm-21.08.2 \
    && mkdir -p /opt/slurm /config /data \
    && ./configure --prefix=/opt/slurm --sysconfdir=/config --localstatedir=/data --runstatedir=/run \
    && make \
    && make install \
    && cd .. \
    && rm -rf slurm-21.08.2.tar.bz2 slurm-21.08.2

## Create system users
RUN useradd munge \
    && useradd slurm \
    && useradd -ms /bin/bash user

ENV PATH="/opt/munge/bin:/opt/slurm/bin:${PATH}"

# MUNGE daemon image
FROM base as munge

RUN chown -R munge /config /data /run

USER munge
CMD [ "/opt/munge/sbin/munged", "--foreground", "--verbose" ]

# SLURM daemon image
FROM base as slurm

RUN chown -R slurm /config /data /run

COPY ./client /client
RUN pip install -e /client

COPY ./example/slurm.conf /config/slurm.conf

CMD [ "/opt/slurm/sbin/slurmctld", "-D", "-v", "-f", "/config/slurm.conf" ]

# Compute node image
FROM base as compute

USER user
WORKDIR /home/user

ENTRYPOINT [ "/bin/bash" ]
