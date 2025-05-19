from .block import Block
from time import time

class Blockchain:
    def __init__(self, max_block_size):
        self.chain = []
        self.max_block_size = max_block_size
        self.current_transactions = []

    def create_block(self, transactions: list, previous_hash: str = None):
        block = Block(
            index=len(self.chain),
            previous_hash=previous_hash or (self.chain[-1].hash if self.chain else 'None'),
            transactions=transactions,
            timestamp=time()
        )
        return block

    def add_block(self, block):
        """Add a block to the chain."""
        if block.previous_hash != (self.chain[-1].hash if self.chain else 'None'):
            raise ValueError("Invalid previous hash")
        self.chain.append(block)

    def add_transaction(self, transaction):
        self.current_transactions.append(transaction)

    def is_block_full(self):
        return len(self.current_transactions) >= self.max_block_size

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def get_chain(self):
        return [block.to_dict() for block in self.chain]