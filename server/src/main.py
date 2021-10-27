import configparser
import docker
from fastapi import FastAPI
from pydantic import BaseModel
import sys

class DockerBackend:
    def __init__(self) -> None:
        self.docker_client = docker.from_env()

    def create_node(self, name: str) -> str:
        print(f"Trying to create node {name}")
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
                name=name,
                network="cloudnet",
                remove=True,
                privileged=True,
                volumes_from=["cloud-login"]
            )

        info = self.docker_client.api.inspect_container(name)
        ip = info["NetworkSettings"]["Networks"]["cloudnet"]["IPAddress"]
        return ip

    def destroy_node(self, name: str):
        print(f"Trying to destroy node {name}")
        try:
            container = self.docker_client.containers.get(name)
            container.remove(force=True)
        except docker.errors.NotFound:
            print(f"Container {name} doesn't exist")


config = configparser.ConfigParser()
config.read("/etc/cloudburst/cloudburstd.ini")

CLOUD = config["config"].get("cloud", "openstack")

app = FastAPI()
if CLOUD == "docker":
    backend = DockerBackend()
elif CLOUD == "openstack":
    pass
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
    ips = {}
    for node in body.nodes:
        ip = backend.create_node(node)
        ips[node] = ip

    return {"ipAddresses": ips}

@app.post("/destroy")
def destroy_nodes(body: NodeList):
    for node in body.nodes:
        backend.destroy_node(node)
    
    return {}
