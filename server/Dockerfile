FROM python:3.9.7

COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

COPY . /app
WORKDIR /app

RUN python3 -m pip install -e /app

ENTRYPOINT ["/usr/local/bin/uvicorn", "CloudBurstServer:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
