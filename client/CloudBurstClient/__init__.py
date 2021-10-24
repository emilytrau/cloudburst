import json
import os
import subprocess
import sys

import pyslurm
import requests

def log(s):
  print(s)
  requests.post("http://backend:8080/log", json={"log": s})

def parse_hosts(hosts_str):
  hosts = []
  hostlist = pyslurm.hostlist()
  success = hostlist.create(hosts_str)
  if not success:
    log("Couldn't get hostlist")
    # TODO: handle this error
    return None
  while hostlist.count() > 0:
    hosts.append(hostlist.pop())
  hostlist.destroy()
  return hosts

def main():
  name = os.path.basename(sys.argv[0])
  if name == "CloudBurstResume":
    hosts = parse_hosts(sys.argv[1])
    if hosts is None:
      log("Couldn't get hostlist")
      # TODO: handle this error
      return

    response = requests.post("http://backend:8080/create", json={"nodes": hosts})
    payload = response.json()
    ips = payload["ipAddresses"]
    for node, ip in ips.items():
      subprocess.run(["scontrol", "update", f"NodeName={node}", f"NodeAddr={ip}"])
    os.system("scontrol reconfigure") # TODO: figure out why we need this
  elif name == "CloudBurstSuspend":
    hosts = parse_hosts(sys.argv[1])
    if hosts is None:
      log("Couldn't get hostlist")
      # TODO: handle this error
      return

    requests.post("http://backend:8080/destroy", json={"nodes": hosts})
