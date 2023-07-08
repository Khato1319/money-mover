from typing import Union
import repository
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, constr

EMAIL_REGEX=r'^[\w\.-]{0,64}@[\w\.-]+\.\w{0,255}$'
PHONE_REGEX=r"^[0-9]{10}$"
CUIT=r"^[0-9]{2}-[0-9]{8}-[0-9]$"
CBU_REGEX = r"^[0-9]{22}$"
MONEY_KEY_TYPE_REGEX=r"^(email|alias|cuit|phone_number)$"

class PostUser(BaseModel):
    name: str
    password: str
    email: constr(regex = EMAIL_REGEX)
    phone_number: constr(regex = PHONE_REGEX)
    cuit: constr(regex = CUIT)

class PostTransaction(BaseModel):
    origin_money_key: str
    dest_money_key: str
    amount: float
    password: str

class PostMoneyKey(BaseModel):
    cbu: constr(regex = CBU_REGEX)
    type: constr(regex=MONEY_KEY_TYPE_REGEX)
    password: str


app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    # Close the database connection
    repository.close_connections()


@app.get("/users/{user_id}")
def get_user(user_id: int= Path(..., ge=1)):
    ACCOUNT = repository.get_user(user_id)
    if ACCOUNT is None:
        raise HTTPException(status_code=404, detail="User not found")
    return ACCOUNT

@app.post("/users")
def post_user(account: PostUser):
    CBU_OBJ = repository.create_account(account.name, account.password, account.email, account.phone_number, account.cuit)
    return CBU_OBJ

@app.post("/users/{user_id}/money_keys")
def post_money_key(money_key: PostMoneyKey, user_id: int = Path(..., ge=1)):
    MONEY_KEY_OBJ = repository.add_money_key(user_id, money_key.password, money_key.cbu, money_key.type)
    return MONEY_KEY_OBJ

@app.post("/users/transactions")
def post_transaction(transaction: PostTransaction):
    TRANSACTION_OBJ = repository.add_transaction(transaction.origin_money_key, transaction.dest_money_key, transaction.amount, transaction.password)
    return TRANSACTION_OBJ

@app.get("/users/{user_id}/transactions")
def get_transactions(user_id: int = Path(..., ge=1), page: int = Query(1, ge=1)):
    TRANSACTIONS = repository.get_transactions(user_id, page)
    return TRANSACTIONS


