from typing import Union
import repository
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel




class PostAccount(BaseModel):
    name: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/accounts/{cbu}")
def get_account_handler(cbu: str= Path(..., regex=r"^[0-9]+$")):
    ACCOUNT = repository.get_account(cbu)
    if ACCOUNT is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ACCOUNT

@app.post("/accounts")
def post_account_handler(account: PostAccount):
    CBU = repository.create_account(account.name)
    return CBU


