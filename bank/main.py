from typing import Union
import repository
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, constr

CBU_REGEX = r"^[0-9]+$"


class PostAccount(BaseModel):
    name: str

class PostTransaction(BaseModel):
    cbu: constr(regex = CBU_REGEX)
    amount: float


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/accounts/{cbu}")
def get_account_handler(cbu: str= Path(..., regex=CBU_REGEX)):
    ACCOUNT = repository.get_account(cbu)
    if ACCOUNT is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ACCOUNT

@app.post("/accounts")
def post_account_handler(account: PostAccount):
    CBU_OBJ = repository.create_account(account.name)
    return CBU_OBJ


@app.post("/accounts/{cbu}/transactions")
def post_transaction(transaction: PostTransaction, cbu: str = Path(..., regex=CBU_REGEX)):
    FUNDS_OBJ = repository.add_transaction(transaction.cbu, cbu, transaction.amount)
    return FUNDS_OBJ



