import redis
import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import HTTPException
import datetime

# Load environment variables from .env file
load_dotenv()

PAGE_SIZE = 10
CBU_PREFIX = os.getenv('CBU_PREFIX')
SUFFIX_LEN = 15

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)
BANK_ACCOUNTS = "Bank_Accounts"
USER_DATA = "User_Data"


# Connect to MongoDB
# Create a MongoClient instance
client = MongoClient("mongodb://localhost:27017")

# Access a specific database
db = client["transactions_db"]
collection = db["transactions"]





def _paginate(page_number, values):
    total_pages = (len(values) + PAGE_SIZE - 1) // PAGE_SIZE
    if page_number > total_pages:
        page_number = total_pages
    elif page_number < 1:
        page_number = 1

    start_index = (page_number - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE

    return values[start_index:end_index]

def modify_funds(cbu: str, amount: float):
    FUNDS_STRING = r.hget(BANK_ACCOUNTS, cbu)
    if FUNDS_STRING is None:
        raise HTTPException(status_code=404, detail="Account not found")
    funds = float(FUNDS_STRING)
    funds += amount
    if funds < 0:
        raise HTTPException(status_code=403, detail="Insufficient funds")
    r.hset(BANK_ACCOUNTS, cbu, funds)
    return {"funds": funds}


def add_transaction(cbu_from: str, cbu_to: str, amount: float):
    if cbu_from == cbu_to:
        raise HTTPException(status_code=400, detail="Transactions have to be between different accounts")
    FUNDS_STRING = r.hget(BANK_ACCOUNTS, cbu_to)
    if FUNDS_STRING is None:
        raise HTTPException(status_code=404, detail="Account not found")
    funds = float(FUNDS_STRING)
    funds += amount
    if funds < 0:
        raise HTTPException(status_code=403, detail="Insufficient funds")
    r.hset(BANK_ACCOUNTS, cbu_to, funds)
    TRANSACTION = {
        "from": cbu_from if amount > 0 else cbu_to,
        "to": cbu_to if amount > 0 else cbu_from,
        "amount": abs(amount),
        "date": datetime.datetime.now()
    }
    collection.update_one({"cbu": cbu_to}, {"$push": {"transactions": {"$each": [TRANSACTION], "$position": 0}}})
    return {"funds": funds, "transaction": TRANSACTION}

def get_transactions(cbu: str, page: int):
    TRANSACTIONS_DOC = collection.find_one({"cbu": cbu})
    if TRANSACTIONS_DOC is None:
        HTTPException(status_code=404, detail="Account not found")
    return {"transactions":_paginate(page, TRANSACTIONS_DOC["transactions"])}

def get_account(cbu: str ):
    FUNDS = r.hget(BANK_ACCOUNTS, cbu)
    NAME = r.hget(USER_DATA, cbu)
    if FUNDS is None: return None
    return {"funds": float(FUNDS), "name": NAME}

def _generate_random_string(n):
    digits = "0123456789"
    random_string = ''.join(random.choice(digits) for _ in range(n))
    return random_string

def _get_unused_cbu():
    while True:
        RANDOM = _generate_random_string(SUFFIX_LEN)
        NEW_CBU = CBU_PREFIX + RANDOM
        if r.hget(BANK_ACCOUNTS, NEW_CBU) is None:
            return NEW_CBU
    

def create_account(name: str):
    CBU = _get_unused_cbu()
    r.hset(BANK_ACCOUNTS, CBU, 0)
    r.hset(USER_DATA, CBU, name)
    BASE_DOCUMENT = {"cbu": CBU, "transactions": []}
    collection.insert_one(BASE_DOCUMENT)
    return {"cbu": CBU}


