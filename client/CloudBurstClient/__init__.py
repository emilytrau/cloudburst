import configparser
import os
import subprocess
import sys
import requests

config = configparser.ConfigParser()
config.read("/etc/cloudburst/cloudburst.ini")

BACKEND = config["config"]["server_address"]

def log(s):
  print(s)
  requests.post(f"{BACKEND}/log", json={"log": s})

def parse_hosts(hosts_str):
  hosts = []
  process = subprocess.run(["scontrol", "show", "hostname", hosts_str], capture_output=True, text=True)
  for line in process.stdout.splitlines():
    if line != "":
      hosts.append(line)
  return hosts

def resume():
  hosts = parse_hosts(sys.argv[1])
  response = requests.post(f"{BACKEND}/create", json={"nodes": hosts})
  payload = response.json()
  node_details = payload["nodes"]
  for name, details in node_details.items():
    ip = details["ip"]
    instance_id = details["instance_id"]
    # TODO: tag instance id in slurm metadata
    subprocess.run(["scontrol", "update", f"NodeName={name}", f"NodeAddr={ip}"], check=True)
  os.system("scontrol reconfigure") # TODO: figure out why we need this

def resume_fail():
  # TODO: implement this
  pass

def suspend():
  hosts = parse_hosts(sys.argv[1])
  requests.post(f"{BACKEND}/destroy", json={"nodes": hosts})
