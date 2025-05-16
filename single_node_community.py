import os
from asyncio import run
from dataclasses import dataclass
import asyncio

import logging

from ipv8.community import Community, CommunitySettings
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.peerdiscovery.network import PeerObserver
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.payload_dataclass import DataClassPayload
from ipv8.messaging.serialization import default_serializer
from ipv8.types import Peer
from ipv8.util import run_forever
from ipv8_service import IPv8

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Transaction(DataClassPayload[1]):
    sender_mid: bytes
    receiver_mid: bytes
    cert_hash: bytes
    timestamp: float
    signature: bytes
    public_key: bytes

    @classmethod
    def serializer(cls):
        return default_serializer(cls,
            [(bytes, "sender_mid"),
             (bytes, "receiver_mid"),
             (bytes, "cert_hash"),
             (float, "timestamp"),
             (bytes, "signature"),
             (bytes, "public_key")]
        )

class BlockchainCommunity(Community, PeerObserver):
    community_id = b"myblockchain-test-01"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.add_message_handler(Transaction, self.on_transaction_received)
        self.seen_messages_hash = set()
        self.known_peers = set()
        self.node_id = None

    def on_peer_added(self, peer: Peer) -> None:
        self.known_peers.add(peer)
        logger.info(f"[{self.node_id}]Peer added: {peer}")

    def on_peer_removed(self, peer: Peer) -> None:
        self.known_peers.discard(peer)
        logger.info(f"[{self.node_id}]Peer removed: {peer}")

    def started(self) -> None:
        self.node_id = self.my_peer.mid[:6]
        self.network.add_peer_observer(self)
        async def send_transaction() -> None:
            await asyncio.sleep(2)
            logger.info(f"[{self.node_id}]Sending transaction")
            transaction = Transaction(
                sender_mid=self.node_id,
                receiver_mid=self.node_id,
                cert_hash=b"cert_hash",
                timestamp=0.0,
                signature=b"signature",
                public_key=b"public_key"
            )
            self.broadcast(transaction)
            
        self.register_task("send_transaction", send_transaction, interval=5.0, delay=5)

    def broadcast(self, payload: Transaction) -> None:
        for peer in self.get_peers():
            self.ez_send(peer, payload)
    
    def create_and_broadcast_transaction(self, receiver_mid: bytes, cert_hash: bytes,
                                    timestamp: float, signature: bytes, public_key: bytes) -> None:
        transaction = Transaction(
            sender_mid=self.node_id,
            receiver_mid=receiver_mid,
            cert_hash=cert_hash,
            timestamp=timestamp,
            signature=signature,
            public_key=public_key
        )
        self.broadcast(transaction)

    @lazy_wrapper(Transaction)
    def on_transaction_received(self, peer: Peer, payload: Transaction) -> None:
        logger.info(f"[{self.node_id}]Transaction received: {payload}")
        pass


async def start_communities() -> None:
    for i in [1, 2, 3]:
        builder = ConfigBuilder().clear_keys().clear_overlays()
        builder.add_key("my peer", "medium", f"ec{i}.pem")
        builder.set_port(8080 + i)
        builder.add_overlay("MyCommunity", "my peer",
                            [WalkerDefinition(Strategy.RandomWalk,
                                              10, {'timeout': 3.0})],
                            default_bootstrap_defs, {}, [('started',)])
        
        await IPv8(builder.finalize(),
                   extra_communities={'MyCommunity': BlockchainCommunity}).start()
    await run_forever()


run(start_communities())