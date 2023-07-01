import os
from fastapi import HTTPException
import requests

def _get_bank_details(cbu: str):
    BANK_DETAILS = os.getenv(cbu[:7])
    if BANK_DETAILS is None:
        raise HTTPException(status_code=400, detail="CBU is not valid")
    SPLITTED = BANK_DETAILS.split(';')
    return {'name': SPLITTED[0], 'HOST': SPLITTED[1]}

def _is_cbu_valid(cbu: str):
    URL = _get_bank_details(cbu)['HOST'] + f"/accounts/{cbu}"
    try:
        response = requests.get(URL)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Bank service is not up")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])


def get_bank_name(cbu: str):
    return _get_bank_details(cbu)['name']

def _bank_transaction(cbu_from: str, cbu_to: str, amount: float):
    BASE_URL = _get_bank_details(cbu_to)['HOST']
    URL = f"{BASE_URL}/accounts/{cbu_to}/transactions"
    BODY = {"cbu": cbu_from, "amount": amount}
    try:
        requests.get(f"{BASE_URL}/health")
        response = requests.post(URL, json=BODY)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail="Bank service is not up")
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.json()['detail'])

def send_money(cbu_from: str, cbu_to: str, amount: float):
    _is_cbu_valid(cbu_from)
    _is_cbu_valid(cbu_to)
    _bank_transaction(cbu_to, cbu_from, -amount)
    try:
        _bank_transaction(cbu_from, cbu_to, amount)
    except HTTPException as e:
        _bank_transaction(cbu_to, cbu_from, amount)
        raise e
    return