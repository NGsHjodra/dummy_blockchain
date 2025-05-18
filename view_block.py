import json
import random
import hashlib
import string
import requests
from time import time

API_URL = "http://localhost:8080/api/blocks"
def get_blocks():
    response = requests.get(API_URL)
    if response.ok:
        blocks = response.json()
        print(f"Total Blocks: {len(blocks)}")
        print("Blocks:")
        for block in blocks:
            print(json.dumps(block, indent=4))
    else:
        print(f"❌ Failed to fetch blocks: {response.text}")

if __name__ == "__main__":
    get_blocks()