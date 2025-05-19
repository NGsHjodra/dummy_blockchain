# 🎓 Blockchain Certificate System (PoA)

This system uses a lightweight Proof-of-Authority (PoA) blockchain to issue and verify graduation certificates securely.

---

## System Flow
```
user     → manually sends public key to the university

uni      → creates transactions after graduation
         → Signs transactions with its private key
         → sends transactions to the network

network  → receives transaction (on_transaction_received)
         → verifies signature
         → gossip transaction to peers

validator → receives transaction

proposer → checks if it’s their turn (round-robin)
         → collects TXs 
         → creates a block
         → signs and broadcasts a block to the validator set

validator → receives block
          → verifies block + TXs
          → signs the vote and sends it to the proposer

proposer → collects votes
         → if threshold met → commits block
         → broadcasts a committed block

user     → receives certificate (check view_transaction.py)
```

---

## Node Architecture Overview

This project implements a Proof-of-Authority (PoA) blockchain using the [IPv8 framework](https://github.com/Tribler/py-ipv8). It features:

### Features
- Transaction Verification (with signature validation)
- Block Proposal (by designated proposer)
- Vote Collection and Threshold Consensus
- Block Commitment when a vote threshold is reached
- Genesis Block Bootstrapping
- Dummy Payload Broadcast for Debugging
- HTTP Server exposing RESTful API endpoints

# How to run the code

## 1. Install the required packages
```
pip install -r requirements.txt
```
## 2. Run the code

### 2.1. Run main.py
```
python main.py
```
### 2.2. Run send_transaction.py
```
python send_transaction.py
```
### 2.3. Run view_transaction.py
```
python view_transaction.py
```
### 2.4. Run view_chain.py
```
python view_chain.py
```

## Optionally, you can change the port number in view_block.py and view_transaction.py from 8080 to 8084 to check the block and transaction for the other nodes.


---

## 🔍 What Each File Does

### `main.py`  
Starts a blockchain node:
- Loads or generates cryptographic keys
- Initializes peer-to-peer communication using IPv8
- Starts the API server
- Handles transaction reception, block proposal, voting, and block commitment

### `send_transaction.py`  
Sends a transaction to the network:
- Simulates a university issuing a certificate
- Generates a new key pair for each transaction
- Signs the transaction with the private key
- Sends it to the node via `/api/send_transaction`

### `view_transaction.py`  
Fetches and displays pending transactions:
- Queries the `/api/transactions` endpoint
- Displays current transactions stored in the mempool
- Useful for checking if your transaction was received

### `view_chain.py`  
Displays the entire blockchain:
- Calls the `/api/blocks` endpoint
- Prints all committed blocks in formatted JSON
- Useful for auditing and debugging the block history
