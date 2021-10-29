import configparser
import docker
from fastapi import FastAPI
import openstack
import openstack.compute.v2.flavor
import openstack.compute.v2.image
import openstack.compute.v2.keypair
import openstack.compute.v2.server
import openstack.config
import openstack.connection
import openstack.network.v2.network
from pydantic import BaseModel
import sys
import uuid

class DockerBackend:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()

    def create_node(self, name: str) -> str:
        print(f"Trying to create node {name}")
        server_id = uuid.uuid4()
        create_container = False
        try:
            container = self.docker_client.containers.get(name)
            print(f"Container {name} already exists")
            # Container exists
            if container.status != "running":
                container.remove(force=True)
                create_container = True
        except docker.errors.NotFound:
            create_container = True
        if create_container:
            print(f"Starting container {name}")
            container = self.docker_client.containers.run(
                image="compute",
                detach=True,
                hostname=name,
                labels={
                    # Mark that we manage this instance
                    "CLOUDBURST_MANAGED": "yes",
                    # Instance UUID for correlating state with SLURM
                    "CLOUDBURST_INSTANCE_ID": str(server_id),
                },
                name=name,
                network="clusternet",
                remove=True,
                privileged=True,
                volumes_from=["login"],
            )

        info = self.docker_client.api.inspect_container(name)
        ip = info["NetworkSettings"]["Networks"]["clusternet"]["IPAddress"]
        return ip, server_id

    def destroy_node(self, name: str):
        print(f"Trying to destroy node {name}")
        try:
            container = self.docker_client.containers.get(name)
            container.remove(force=True)
        except docker.errors.NotFound:
            print(f"Container {name} doesn't exist")

class OpenStackBackend:
    def __init__(self, config) -> None:
        credentials_file = config.get("openstack", "credentials_file", fallback=None)
        if credentials_file is None:
            raise Exception("OpenStack credentials file must be specified")
        os_config = openstack.config.OpenStackConfig(config_files=[credentials_file])
        self.connection = openstack.connection.from_config(config=os_config.get_one())
            
        image_id = config.get("openstack", "image", fallback=None)
        if image_id is None:
            raise Exception("No OpenStack image specified")
        image: openstack.compute.v2.image.Image = self.connection.compute.find_image(image_id)
        if image is None:
            raise Exception("Couldn't find OpenStack image ID")
        self.image = image

        flavor_id = config.get("openstack", "flavor", fallback=None)
        if flavor_id is None:
            raise Exception("No OpenStack flavor specified")
        flavor: openstack.compute.v2.flavor.Flavor = self.connection.compute.find_flavor(flavor_id)
        if flavor is None:
            raise Exception("Couldn't find OpenStack flavor ID")
        self.flavor = flavor

        availability_zone = config.get("openstack", "availability_zone", fallback=None)
        if availability_zone is None:
            raise Exception("No OpenStack availability zone specified")
        found_az = False
        for az in self.connection.compute.availability_zones():
            if az.name == availability_zone:
                found_az = True
                break
        if not found_az:
            raise Exception("Couldn't find OpenStack availability zone")
        self.availability_zone = availability_zone

        availability_zone: openstack.compute.v2.flavor.Flavor = self.connection.compute.find_flavor(flavor_id)
        if flavor is None:
            raise Exception("Couldn't find OpenStack flavor ID")
        self.flavor = flavor

        network_id = config.get("openstack", "network", fallback=None)
        if network_id is None:
            raise Exception("No OpenStack network specified")
        network: openstack.network.v2.network.Network = self.connection.network.find_network(network_id)
        if network is None:
            raise Exception("Couldn't find OpenStack network ID")
        self.network = network

        keypair_id = config.get("openstack", "keypair", fallback=None)
        self.keypair = None
        if keypair_id is not None:
            keypair: openstack.compute.v2.keypair.Keypair = self.connection.compute.find_keypair(keypair_id)
            if keypair is None:
                raise Exception("Keypair name specified but matching key was not found")
            self.keypair = keypair
    
    def get_quota(self):
        limits = self.connection.get_compute_limits()
        max_cores = limits["max_total_cores"]
        max_instances = limits["max_total_instances"]
        max_ram = limits["max_total_ram_size"]
        used_cores = limits["total_cores_used"]
        used_instances = limits["total_instances_used"]
        used_ram = limits["total_ram_used"]
        return {}

    def create_node(self, name: str) -> str:
        print(f"Trying to create node {name}")
        server_id = uuid.uuid4()

        server: openstack.compute.v2.server.Server = self.connection.compute.create_server(
            name=name,
            image_id=self.image.id,
            flavor_id=self.flavor.id,
            availability_zone=self.availability_zone,
            networks=[{"uuid": self.network.id}],
            security_groups=[],
            key_name=self.keypair.name if self.keypair is not None else None,
            metadata={
                # Mark that we manage this instance
                "CLOUDBURST_MANAGED": "yes",
                # Instance UUID for correlating state with SLURM
                "CLOUDBURST_INSTANCE_ID": str(server_id),
            },
        )
        server = self.connection.compute.wait_for_server(server)
        ip = server.addresses[self.network.name][0]["addr"]
        return ip, server_id

    
    def destroy_node(self, name: str):
        print(f"Trying to destroy node {name}")
        # OpenStack instance names aren't unique so we kill all with this name
        for server in self.connection.servers(details=False):
            if server.name == name:
                self.connection.compute.delete_server(server)

config = configparser.ConfigParser()
config.read("/etc/cloudburst/cloudburstd.ini")

CLOUD = config.get("config", "cloud", fallback="openstack")

app = FastAPI()
if CLOUD == "docker":
    backend = DockerBackend()
elif CLOUD == "openstack":
    backend = OpenStackBackend(config)
else:
    print(f"Unknown cloud backend: {CLOUD}")
    sys.exit(1)

class Log(BaseModel):
    log: str

@app.post("/log")
def logger(b: Log):
    print(b.log)

    return {}

class NodeList(BaseModel):
    nodes: list[str]

@app.post("/create")
def create_nodes(body: NodeList):
    node_details = {}
    for node in body.nodes:
        ip, id = backend.create_node(node)
        node_details[node] = {
            "ip": ip,
            "instance_id": id,
        }

    return {"nodes": node_details}

@app.post("/destroy")
def destroy_nodes(body: NodeList):
    for node in body.nodes:
        backend.destroy_node(node)
    
    return {}
