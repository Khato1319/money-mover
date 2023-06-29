import redis
import os
import random

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CBU_PREFIX = os.getenv('CBU_PREFIX')
SUFFIX_LEN = 5

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)
BANK_ACCOUNTS = "Bank_Accounts"
USER_DATA = "User_Data"

def get_account(cbu: str ):
    FUNDS = r.hget(BANK_ACCOUNTS, cbu)
    NAME = r.hget(USER_DATA, cbu)
    if FUNDS is None: return None
    return {"funds": FUNDS, "name": NAME}

def _generate_random_string(n):
    digits = "0123456789"
    random_string = ''.join(random.choice(digits) for _ in range(n))
    return random_string

def _get_unused_cbu():
    while True:
        RANDOM = _generate_random_string(5)
        print(RANDOM)
        NEW_CBU = CBU_PREFIX + RANDOM
        if r.hget(BANK_ACCOUNTS, NEW_CBU) is None:
            return NEW_CBU
    

def create_account(name: str):
    CBU = _get_unused_cbu()
    r.hset(BANK_ACCOUNTS, CBU, 0)
    r.hset(USER_DATA, CBU, name)
    return {"cbu": CBU}


