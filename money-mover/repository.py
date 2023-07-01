import psycopg2
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime
import bank_api
from functools import reduce
import random


# Load environment variables from .env file
load_dotenv()

PAGE_SIZE = 10
CBU_PREFIX = os.getenv('CBU_PREFIX')
SUFFIX_LEN = 15




# Establish a connection to the PostgreSQL database
connection = psycopg2.connect(
    host="localhost",
    port=5433,
    database="your_database",
    user="postgres",
    password="your_password"
)

cursor = connection.cursor()

# Connect to MongoDB
# Create a MongoClient instance
client = MongoClient("mongodb://localhost:27017")

# Access a specific database
db = client["transactions_db"]
collection = db["transactions"]

SPANISH_NOUNS = [
    "amor", "amistad", "familia", "vida", "persona", "casa", "trabajo", "tiempo", "dia", "noche",
    "mes", "año", "mujer", "hombre", "niño", "niña", "bebé", "perro", "gato", "animal",
    "naturaleza", "ciudad", "pais", "mar", "montaña", "rio", "sol", "luna", "estrella",
    "aire", "viento", "fuego", "agua", "tierra", "flores", "arbol", "fruta", "verdura",
    "comida", "bebida", "plato", "taza", "ropa", "zapatos", "sombrero", "camisa", "pantalon",
    "vestido", "chaqueta", "bolsa", "cama", "mesa", "silla", "puerta", "ventana", "television",
    "radio", "libro", "papel", "lapicero", "telefono", "ordenador", "coche", "bicicleta", "avion",
    "barco", "tren", "calle", "parque", "playa", "bosque", "campo", "estadio", "escuela",
    "universidad", "hospital", "oficina", "gimnasio", "música", "arte", "cine", "teatro", "concierto",
    "deporte", "futbol", "baloncesto", "tenis", "natacion", "correr", "saltar", "guitarra", "piano",
    "pintura", "escultura", "poesia", "historia", "ciencia", "matematicas", "fisica", "quimica", "biologia",
    "geografia", "medicina", "ingenieria", "economia", "politica", "religion", "cultura", "tradicion", "celebracion",
    "cumpleaños", "boda", "navidad", "fiesta", "viaje", "vacaciones", "aventura", "sueño", "esperanza",
    "deseo", "alegria", "tristeza", "risa", "llanto", "emocion", "felicidad", "miedo", "amor",
    "odio", "paz", "guerra", "libertad", "justicia", "sueño", "esfuerzo", "exito", "fracaso"
    # Add more nouns as desired
]


def _paginate(page_number, values):
    total_pages = (len(values) + PAGE_SIZE - 1) // PAGE_SIZE
    if page_number > total_pages:
        page_number = total_pages
    elif page_number < 1:
        page_number = 1

    start_index = (page_number - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE

    return values[start_index:end_index]

def _get_details_from_money_key(money_key: str):
    QUERY = "SELECT bank_cbu, user_id, bank_name, name FROM Users JOIN PaymentMethods ON Users.id = PaymentMethods.user_id WHERE money_key = %(money_key)s"
    cursor.execute(QUERY, {"money_key": money_key})
    ROWS = cursor.fetchone()
    if ROWS is None:
        return None
    return {"user_id": ROWS[1], "bank_cbu": ROWS[0], "bank_name": ROWS[2], "name": ROWS[3]}

def _formatted_bank_details(bank_details: dict):
    return f"{bank_details['name']} - {bank_details['bank_cbu']} ({bank_details['bank_name']})"

def add_transaction(money_key_from: str, money_key_to: str, amount: float):
    MONEY_KEY_FROM_DETAILS = _get_details_from_money_key(money_key_from)
    MONEY_KEY_TO_DETAILS = _get_details_from_money_key(money_key_to)

    if MONEY_KEY_FROM_DETAILS is None or MONEY_KEY_TO_DETAILS is None:
        raise HTTPException(status_code=404, detail="MoneyKey not found")

    bank_api.send_money(MONEY_KEY_FROM_DETAILS['bank_cbu'], MONEY_KEY_TO_DETAILS['bank_cbu'], amount)
    
    TRANSACTION = {
        "from": _formatted_bank_details(MONEY_KEY_FROM_DETAILS),
        "origin_money_key": money_key_from, 
        "to": _formatted_bank_details(MONEY_KEY_TO_DETAILS),
        "dest_money_key": money_key_to,
        "amount": amount,
        "date": datetime.now()
    }
    collection.update_one({"user_id": MONEY_KEY_TO_DETAILS['user_id']}, {"$push": {"transactions": {"$each": [TRANSACTION], "$position": 0}}})
    if MONEY_KEY_FROM_DETAILS['user_id'] != MONEY_KEY_TO_DETAILS['user_id']:
        collection.update_one({"user_id": MONEY_KEY_FROM_DETAILS['user_id']}, {"$push": {"transactions": {"$each": [TRANSACTION], "$position": 0}}})
    return {"transaction": TRANSACTION}

def _generate_random_numbers(qty: int, min: int, max: int):
    numbers = set()
    while len(numbers) < qty:
        number = random.randint(min, max)
        numbers.add(number)
    return list(numbers)

def _generate_alias():
    while True:
        WORDS = map(lambda x: SPANISH_NOUNS[x], _generate_random_numbers(3, 0, len(SPANISH_NOUNS)-1))
        ALIAS = reduce(lambda prev, next: f"{prev}.{next}",WORDS)
        QUERY = "SELECT count(*) FROM PaymentMethods WHERE money_key = %(alias)s"
        cursor.execute(QUERY, {"alias": ALIAS})
        COUNT = cursor.fetchone()[0]
        if COUNT == 0:
            return ALIAS

def _validate_and_get_money_key(user_id: int, type: str):
    if type == "alias":
        return _generate_alias()
    if type not in ["email", "cuit", "phone_number"]:
        raise HTTPException(status_code=404, detail="MoneyKey type is invalid")
    VALUE_QUERY = "SELECT " + type + " FROM Users WHERE id = %(user_id)s"
    cursor.execute(VALUE_QUERY, {"user_id": user_id, "type": type})
    MONEY_KEY = cursor.fetchone()[0]
    QUERY = "SELECT count(*) FROM PaymentMethods WHERE money_key = %(money_key)s"
    cursor.execute(QUERY, {"money_key": MONEY_KEY})
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=409, detail="MoneyKey type is already used")
    return MONEY_KEY

def _cbu_exists(cbu: str):
    QUERY = "SELECT count(*) FROM PaymentMethods WHERE bank_cbu = %(bank_cbu)s"
    cursor.execute(QUERY, {"bank_cbu": cbu})
    return cursor.fetchone()[0] > 0

def add_money_key(user_id: int, cbu: str, type: str):
    if _cbu_exists(cbu):
        raise HTTPException(status_code=409, detail="CBU is already registered with another key")
    MONEY_KEY = _validate_and_get_money_key(user_id, type)
    BANK_NAME = bank_api.get_bank_name(cbu)
    QUERY = "INSERT INTO PaymentMethods VALUES (%(money_key)s, %(bank_name)s, %(bank_cbu)s, %(user_id)s)"
    cursor.execute(QUERY, {"money_key": MONEY_KEY, "bank_name": BANK_NAME, "bank_cbu": cbu, "user_id": user_id})
    connection.commit()
    return {"money_key": MONEY_KEY}


def get_transactions(user_id: int, page: int):
    TRANSACTIONS_DOC = collection.find_one({"user_id": user_id})
    if TRANSACTIONS_DOC is None:
        HTTPException(status_code=404, detail="Account not found")
    return {"transactions":_paginate(page, TRANSACTIONS_DOC["transactions"])}

def get_user(user_id: int ):
    QUERY = "SELECT * FROM Users LEFT OUTER JOIN PaymentMethods ON Users.id = PaymentMethods.user_id WHERE id = %(user_id)s"
    cursor.execute(QUERY, {"user_id": user_id})
    USER_DATA = cursor.fetchall()
    TO_RETURN = {
        "name": USER_DATA[0][1],
        "email": USER_DATA[0][3],
        "phone_number": USER_DATA[0][4],
        "cuit": USER_DATA[0][5],
    }
    TO_RETURN["payment_methods"] = reduce(lambda prev, next: [*prev, {"money_key": next[6], "bank_name": next[7]}], USER_DATA, [])
    return TO_RETURN


def _exists_user(email: str, phone_number: str, cuit: str):
    QUERY = "SELECT count(*) FROM Users WHERE email=%(email)s OR phone_number=%(phone_number)s OR cuit=%(cuit)s"
    cursor.execute(QUERY, {"email": email, "phone_number": phone_number, "cuit": cuit})
    RESULT = cursor.fetchone()
    return RESULT[0] > 0


def create_account(name: str, password: str, email: str, phone_number: str, cuit: str):
    if _exists_user(email, phone_number, cuit):
        raise HTTPException(status_code=409, detail="User already registered")
    QUERY = "INSERT INTO Users (name , pwd_hash, email, phone_number, cuit) VALUES (%(name)s, %(password)s, %(email)s, %(phone_number)s, %(cuit)s) RETURNING id"
    cursor.execute(QUERY, {"name": name, "password": password, "email": email, "phone_number": phone_number, "cuit": cuit})

    USER_ID = cursor.fetchone()[0] 
    connection.commit()
    BASE_DOCUMENT = {"user_id": USER_ID, "transactions": []}
    collection.insert_one(BASE_DOCUMENT)
    return {"user_id": USER_ID}


def close_connections():
    cursor.close()
    connection.close()


