from fastapi import BackgroundTasks, FastAPI
import docker
from pydantic import BaseModel, errors

app = FastAPI()
docker_client = docker.from_env()

def create_docker_node(name: str):
    print(f"Trying to create node {name}")
    create_container = False
    try:
        container = docker_client.containers.get(name)
        print(f"Container {name} already exists")
        # Container exists
        if container.status != "running":
            container.remove(force=True)
            create_container = True
    except docker.errors.NotFound:
        create_container = True
    if create_container:
        print(f"Starting container {name}")
        container = docker_client.containers.run(
            image="compute",
            detach=True,
            hostname=name,
            name=name,
            network="clusternet",
            remove=True,
            privileged=True,
            volumes_from=["login"]
        )
    
    info = docker_client.api.inspect_container(name)
    ip = info["NetworkSettings"]["Networks"]["clusternet"]["IPAddress"]
    return ip

@app.get("/")
def read_root():
    return {"Hello": "World"}

class Log(BaseModel):
    log: str

@app.post("/log")
def logger(b: Log):
    print(b.log)

    return {}

class CreateNode(BaseModel):
    nodes: list[str]

@app.post("/create")
def create_nodes(body: CreateNode):
    ips = {}
    for node in body.nodes:
        ip = create_docker_node(node)
        ips[node] = ip

    return {"ipAddresses": ips}
