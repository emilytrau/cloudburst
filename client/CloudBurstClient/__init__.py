import json
import os
import sys

import pyslurm
import requests

def log(s):
  requests.post("http://backend:8080/log", json={"log": s})

def main():
  print("hello world")
  s = json.dumps(sys.argv)
  print(s)
  log(s)

  name = os.path.basename(sys.argv[0])
  if name == "CloudBurstResume":
    hostlist = pyslurm.hostlist()
    hosts = []
    success = hostlist.create(sys.argv[1])
    if not success:
      log("Couldn't get hostlist")
      # TODO: handle this error
      return
    while hostlist.count() > 0:
      hosts.append(hostlist.pop())
    hostlist.destroy()

    log(json.dumps(hosts))
    response = requests.post("http://backend:8080/create", json={"nodes": hosts})
    payload = response.json()
    ips = payload["ipAddresses"]
    log(json.dumps(payload))
    for node, ip in ips.items():
      n = pyslurm.node()
      n.update({
        "node_names": node,
        "node_addr": ip,
      })
    os.system("scontrol reconfigure")
