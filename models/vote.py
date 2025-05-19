from dataclasses import dataclass
from ipv8.messaging.payload_dataclass import DataClassPayload
from ipv8.messaging.serialization import default_serializer

@dataclass
class Vote(DataClassPayload[2]):
    msg_id = 2
    block_hash: bytes
    voter_mid: bytes
    vote_decision: bytes  # e.g., b"accept" or b"reject"
    signature: bytes
    public_key: bytes
    timestamp: float
    # public_key: bytes

    @classmethod
    def serializer(cls):
        return default_serializer(cls, [
            (bytes, "block_hash"),
            (bytes, "voter_mid"),
            (bytes, "vote_decision"),
            (bytes, "signature"),
            (bytes, "public_key")
            (float, "timestamp"),
            # (bytes, "public_key")
        ])

    def to_signable_bytes(self) -> bytes:
        """Create the message used for signing and verifying."""
        return b"|".join([
            self.block_hash,
            self.voter_mid,
            self.vote_decision,
            str(self.timestamp).encode('utf-8')
        ])