import sys
import requests
import json

def log(s):
  requests.post("http://backend:8080/log", json={"log": s})

def main():
  print("hello world")
  s = json.dumps(sys.argv)
  print(s)
  log(s)
