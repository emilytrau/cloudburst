#!/usr/bin/env python3

def run():
  import uvicorn
  uvicorn.run("CloudBurstServer:app", host="0.0.0.0", port=8080, log_level="info", workers=1)
