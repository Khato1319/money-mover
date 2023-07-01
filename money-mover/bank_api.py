import os
from fastapi import HTTPException

def _get_bank_details(cbu: str):
    BANK_DETAILS = os.getenv(cbu[:7])
    if BANK_DETAILS is None:
        raise HTTPException(status_code=400, detail="CBU is not valid")
    SPLITTED = BANK_DETAILS.split(';')
    return {'name': SPLITTED[0], 'HOST': SPLITTED[1]}

def get_bank_name(cbu: str):
    return _get_bank_details(cbu)['name']

def send_money(cbu_from: str, cbu_to: str, amount: float):
    return