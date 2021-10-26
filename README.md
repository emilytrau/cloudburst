# CloudBurst

Tooling to connect SLURM's [Cloud Scheduling](https://slurm.schedmd.com/elastic_computing.html) to OpenStack

## Building

To run the development environment you will need [Docker](https://docs.docker.com/engine/install/#server) and [Docker Compose](https://docs.docker.com/compose/install/).

```sh
# First time setup
./dev-setup.sh

docker-compose up --build
# In another terminal
./login.sh
srun -M cloud hostname
```

Files placed in the `home/` folder will be mounted under `/home/user` on the login and compute nodes.
