import json
import random
import hashlib
import string
import requests
from time import time

API_URL = "http://localhost:8080/api/transactions"

def get_transactions():
    response = requests.get(API_URL)
    if response.ok:
        transactions = response.json()
        print(f"Total Transactions: {len(transactions)}")
        print("Transactions:")
        for tx in transactions:
            print(tx)
    else:
        print(f"❌ Failed to fetch transactions: {response.text}")

if __name__ == "__main__":
    get_transactions()
