from dataclasses import dataclass
from typing import List
from ipv8.messaging.payload_dataclass import DataClassPayload
from ipv8.messaging.serialization import default_serializer

@dataclass
class BlockPayload(DataClassPayload[5]):
    index: int
    previous_hash: bytes
    transaction_hashes: bytes
    timestamp: float
    block_hash: bytes

    @classmethod
    def serializer(cls):
        return default_serializer(cls, [
            (int, "index"),
            (bytes, "previous_hash"),
            (bytes, "transaction_hashes"),
            (float, "timestamp"),
            (bytes, "block_hash")
        ])
