FROM python:3.9.7

COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install -r /requirements.txt

COPY ./src /app
WORKDIR /app

ENTRYPOINT ["/usr/local/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
