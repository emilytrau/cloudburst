from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Log(BaseModel):
    log: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/log")
def post_root(b: Log):
    print(b.log)

    return {"Hello": "World"}
