import redis
import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

CBU_PREFIX = os.getenv('CBU_PREFIX')
SUFFIX_LEN = 5

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)
BANK_ACCOUNTS = "Bank_Accounts"
USER_DATA = "User_Data"


# Connect to MongoDB
# Create a MongoClient instance
client = MongoClient("mongodb://localhost:27017")

# Access a specific database
db = client["transactions"]


# def add_transaction(from_cbu: str, to_cbu: str, amount: float):

def add_transaction(cbu_from: str, cbu_to: str, amount: float):
    FUNDS_STRING = r.hget(BANK_ACCOUNTS, cbu_to)
    if FUNDS_STRING is None:
        raise HTTPException(status_code=404, detail="Account not found")
    funds = float(FUNDS_STRING)
    funds += amount
    r.hset(BANK_ACCOUNTS, cbu_to, funds)
    return {"funds": funds}

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
        RANDOM = _generate_random_string(5)
        NEW_CBU = CBU_PREFIX + RANDOM
        if r.hget(BANK_ACCOUNTS, NEW_CBU) is None:
            return NEW_CBU
    

def create_account(name: str):
    CBU = _get_unused_cbu()
    r.hset(BANK_ACCOUNTS, CBU, 0)
    r.hset(USER_DATA, CBU, name)
    return {"cbu": CBU}


