import json
import random
import hashlib
import string
import requests
from time import time
from ipv8.keyvault.crypto import ECCrypto
from models.transaction import Transaction

API_URL = "http://localhost:8080/api/send_transaction"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_transaction():
    crypto = ECCrypto()
    private_key = crypto.generate_key("medium")
    public_key_bin = private_key.pub().key_to_bin()
    public_key = crypto.key_from_public_bin(public_key_bin)

    sender_mid = random_string(16)
    receiver_mid = random_string(16)
    cert_hash = hashlib.sha256(random_string(32).encode()).hexdigest()
    timestamp = time()
    signature = b""
    # public_key = public_key

    transaction = Transaction(
        sender_mid=sender_mid.encode(),
        receiver_mid=receiver_mid.encode(),
        cert_hash=bytes.fromhex(cert_hash),
        timestamp=timestamp,
        signature=signature,
        public_key=public_key_bin
    )

    signable_message = transaction.to_signable_bytes()
    signature = crypto.create_signature(private_key, signable_message)

    transaction.signature = signature
    
    # convert to dict for sending
    transaction_dict = transaction.to_dict()

    print(f"Generated transaction: {transaction_dict}")
    return transaction_dict

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
