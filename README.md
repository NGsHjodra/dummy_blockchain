# 🎓 Blockchain Certificate System (PoA)

This system uses a lightweight Proof-of-Authority (PoA) blockchain to issue and verify graduation certificates securely.

---

## 🔄 System Flow
user     → manually sends public key to university

uni      → creates transaction after graduation
         → signs transaction with its private key
         → sends transaction to the network

network  → receives transaction (on_transaction_received)
         → verifies signature
         → gossips transaction to peers

validator → receives transaction
          → stores in mempool (pending)

proposer → checks if it’s their turn (round-robin)
         → collects TXs from mempool
         → creates block
         → signs and broadcasts block to validator set

validator → receives block
          → verifies block + TXs
          → signs vote and sends to proposer

proposer → collects votes
         → if threshold met → commits block
         → broadcasts committed block

user     → receives certificate (off-chain or on-chain)



# how to run the code

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
