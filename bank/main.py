import repository
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, constr

CBU_REGEX = r"^[0-9]{22}$"


class PostAccount(BaseModel):
    name: str

class PostTransaction(BaseModel):
    cbu: constr(regex = CBU_REGEX)
    amount: float

class PostAmount(BaseModel):
    amount: float


app = FastAPI()


@app.get("/accounts/{cbu}")
def get_account(cbu: str= Path(..., regex=CBU_REGEX)):
    ACCOUNT = repository.get_account(cbu)
    if ACCOUNT is None:
        raise HTTPException(status_code=404, detail="CBU not registered in bank")
    return ACCOUNT

@app.get("/health")
def get_health():
    return {"status": "OK"}

@app.post("/accounts")
def post_account(account: PostAccount):
    CBU_OBJ = repository.create_account(account.name)
    return CBU_OBJ


@app.post("/accounts/{cbu}/transactions")
def post_transaction(transaction: PostTransaction, cbu: str = Path(..., regex=CBU_REGEX)):
    FUNDS_OBJ = repository.add_transaction(cbu, transaction.cbu, transaction.amount)
    return FUNDS_OBJ

@app.get("/accounts/{cbu}/transactions")
def get_transactions(cbu: str = Path(..., regex=CBU_REGEX), page: int = Query(1, ge=1)):
    TRANSACTIONS = repository.get_transactions(cbu, page)
    return TRANSACTIONS

@app.post("/accounts/{cbu}/funds")
def deposit_or_withdraw_money(amount: PostAmount, cbu: str = Path(..., regex=CBU_REGEX)):
    FUNDS_OBJ = repository.modify_funds(cbu, amount.amount)
    return FUNDS_OBJ


