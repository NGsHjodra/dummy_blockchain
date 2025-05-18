import json
import random
import hashlib
import string
import requests
from time import time

API_URL = "http://localhost:8080/api/send_transaction"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_transaction():
    sender_mid = random_string(16)
    receiver_mid = random_string(16)
    cert_hash = hashlib.sha256(random_string(32).encode()).hexdigest()
    timestamp = time()
    signature = hashlib.sha256(f"{sender_mid}{receiver_mid}{cert_hash}{timestamp}".encode()).hexdigest()
    public_key = random_string(32)

    transaction = {
        "sender_mid": sender_mid,
        "receiver_mid": receiver_mid,
        "cert_hash": cert_hash,
        "timestamp": timestamp,
        "signature": signature,
        "public_key": public_key
    }
    
    return transaction

def send_transaction(transaction):
    response = requests.post(API_URL, json=transaction)
    if response.ok:
        print(f"✅ Sent: {transaction}")
    else:
        print(f"❌ Failed to send: {response.text}")

if __name__ == "__main__":
    for _ in range(10):  # Change to any number of transactions you want to send
        tx = generate_transaction()
        send_transaction(tx)
