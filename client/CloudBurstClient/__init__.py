import os
import subprocess
import sys
import requests

def log(s):
  print(s)
  requests.post("http://backend:8080/log", json={"log": s})

def parse_hosts(hosts_str):
  hosts = []
  process = subprocess.run(["scontrol", "show", "hostname", hosts_str], capture_output=True, text=True)
  for line in process.stdout.splitlines():
    if line != "":
      hosts.append(line)
  return hosts

def main():
  name = os.path.basename(sys.argv[0])
  if name == "CloudBurstResume":
    hosts = parse_hosts(sys.argv[1])
    response = requests.post("http://backend:8080/create", json={"nodes": hosts})
    payload = response.json()
    ips = payload["ipAddresses"]
    for node, ip in ips.items():
      subprocess.run(["scontrol", "update", f"NodeName={node}", f"NodeAddr={ip}"])
    os.system("scontrol reconfigure") # TODO: figure out why we need this
  elif name == "CloudBurstSuspend":
    hosts = parse_hosts(sys.argv[1])
    requests.post("http://backend:8080/destroy", json={"nodes": hosts})
