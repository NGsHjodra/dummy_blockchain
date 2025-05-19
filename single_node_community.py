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
from ipv8.keyvault.crypto import default_eccrypto, ECCrypto
from server_side.app import Server
from threading import Thread
from binascii import unhexlify

from models.transaction import Transaction
from models.blockchain import Blockchain
from models.vote import Vote
from models.block import Block

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainCommunity(Community, PeerObserver):
    community_id = b"myblockchain-test-02"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.crypto = ECCrypto()

        self.add_message_handler(Transaction, self.on_transaction_received)
        self.add_message_handler(Vote, self.on_vote_received)
        self.seen_messages_hash = set()
        self.known_peers = set()
        self.node_id = None
        self.transactions = []
        self.votes = []
        self.proposing_block = None
        self.blockchain = Blockchain(max_block_size=10)

    def on_peer_added(self, peer: Peer) -> None:
        self.known_peers.add(peer)
        logger.info(f"[{self.node_id}]Peer added: {peer}")

    def on_peer_removed(self, peer: Peer) -> None:
        self.known_peers.discard(peer)
        logger.info(f"[{self.node_id}]Peer removed: {peer.mid.hex()[:6]}")

    def started(self) -> None:
        self.network.add_peer_observer(self)

        self.register_task("send_dummy_payloads",self.send_dummy_payloads, interval=5.0, delay=5.0)

    async def send_dummy_payloads(self):
        dummy_transaction = Transaction(
            sender_mid=self.my_peer.mid,
            receiver_mid=self.my_peer.mid,
            cert_hash=b"dummy_cert_hash",
            timestamp=0.0,
            signature=b"dummy_signature",
            public_key=b"dummy_public_key"
        )
        self.broadcast(dummy_transaction)
        logger.info(f"[{self.node_id}] Dummy transaction sent")

        dummy_vote = Vote(
            block_hash=b"dummy_block_hash",
            voter_mid=self.my_peer.mid,
            vote_decision=b"dummy_vote_decision",
        )
        self.broadcast(dummy_vote)
        logger.info(f"[{self.node_id}] Dummy vote sent")

        self.cancel_pending_task("send_dummy_payloads")
        logger.info(f"[{self.node_id}] Dummy transaction task cancelled")

    def broadcast(self, payload: Transaction) -> None:
        for peer in self.get_peers():
            self.ez_send(peer, payload)

    def is_proposer(self) -> bool:
        return self.node_id == 0
    
    def create_and_broadcast_transaction(self, sender_mid: bytes, receiver_mid: bytes, cert_hash: bytes,
                                    timestamp: float, signature: bytes, public_key: bytes) -> None:
        transaction = Transaction(
            sender_mid=sender_mid,
            receiver_mid=receiver_mid,
            cert_hash=cert_hash,
            timestamp=timestamp,
            signature=signature,
            public_key=public_key
        )
        self.broadcast(transaction)
        logger.info(f"[{self.node_id}] Transaction created and broadcasted")
        
    @lazy_wrapper(Transaction)
    def on_transaction_received(self, peer: Peer, payload: Transaction) -> None:
        if payload.cert_hash == b"dummy_cert_hash":
            logger.info(f"[{self.node_id}] Dummy transaction received, ignoring")
            return
        
        message_id = payload.sender_mid.hex() + payload.receiver_mid.hex() + payload.cert_hash.hex()
        if message_id in self.seen_messages_hash:
            return

        self.seen_messages_hash.add(message_id)

        # Double save the transaction may be a problem
        if payload not in self.transactions:
            self.transactions.append(payload)

        self.blockchain.add_transaction(payload)

        logger.info(f"[{self.node_id}] Transaction received current transactions: {len(self.blockchain.current_transactions)}")

        self.broadcast(payload)
        logger.info(f"[{self.node_id}] Transaction broadcasted")

        if self.blockchain.is_block_full() and self.is_proposer():
            last_block = self.blockchain.get_last_block()
            new_block = self.blockchain.create_block(
                transactions=self.blockchain.current_transactions,
                previous_hash=last_block.hash if last_block else None
            )
            logger.info(f"[{self.node_id}] New block created: {new_block.index}")
            self.blockchain.current_transactions = []

            # decide to only broadcast the vote
            vote = Vote(
                block_hash=unhexlify(new_block.hash),
                voter_mid=self.my_peer.mid,
                vote_decision=b"accept",  # or b"reject"
            )

            self.proposing_block = new_block
            logger.info(f"[{self.node_id}] Proposing block: {new_block.index}")

            self.broadcast(vote)
            logger.info(f"[{self.node_id}] Vote broadcasted")
            self.votes.append(vote)
            logger.info(f"[{self.node_id}] Vote added to list")
            self.seen_messages_hash.add(vote.voter_mid.hex() + vote.block_hash.hex())

    @lazy_wrapper(Vote)
    def on_vote_received(self, peer: Peer, payload: Vote) -> None:
        if payload.block_hash == b"dummy_block_hash":
            logger.info(f"[{self.node_id}] Dummy vote received, ignoring")
            return

        message_id = payload.voter_mid.hex() + payload.block_hash.hex()
        if message_id in self.seen_messages_hash:
            return

        self.seen_messages_hash.add(message_id)

        if payload not in self.votes and self.is_proposer():
            if self.proposing_block is None:
                logger.info(f"[{self.node_id}] No proposing block, ignoring vote")
                return
            self.votes.append(payload)
            logger.info(f"[{self.node_id}] Vote received current votes: {len(self.votes)}")

            accept_count = sum(1 for vote in self.votes if vote.vote_decision == b"accept")

            if accept_count > 3:
                logger.info(f"[{self.node_id}] Majority accepted the block, adding to blockchain")
                self.blockchain.add_block(self.proposing_block)
                logger.info(f"[{self.node_id}] Block added to blockchain: {self.proposing_block.index}")
                self.proposing_block = None  # Reset proposing block after processing
                self.votes = []  # Reset votes after processing

        vote = Vote(
            block_hash=payload.block_hash,
            voter_mid=self.my_peer.mid,
            vote_decision=payload.vote_decision,
        )

        self.broadcast(vote)
        logger.info(f"[{self.node_id}] Vote broadcasted")

    def get_transactions(self):
        return self.transactions

def start_node(node_id, server_port):
    async def boot():
        logger.info(f"Starting node with ID {node_id} on port {server_port}")
        builder = ConfigBuilder().clear_keys().clear_overlays()
        crypto = ECCrypto()
        key_path = f"key_{node_id}.pem"
        if not os.path.exists(key_path):
            key = crypto.generate_key("medium")
            with open(key_path, "wb") as f:
                f.write(key.key_to_bin())
        
        logger.info(f"Key loaded from {key_path}")

        port = server_port + 10
        
        logger.info(f"Starting node with ID {node_id} on port {port}")

        generation_status = "medium"
        alias_status = "my peer"
        builder.add_key(alias_status, generation_status, key_path)
        builder.set_port(port)

        builder.add_overlay("BlockchainCommunity", "my peer",
                          [WalkerDefinition(Strategy.RandomWalk, 10, {'timeout': 3.0})],
                          default_bootstrap_defs, {}, [('started', )])

        ipv8 = IPv8(builder.finalize(), extra_communities={'BlockchainCommunity': BlockchainCommunity})

        try:
            await ipv8.start()
            community = ipv8.get_overlay(BlockchainCommunity)
            community.node_id = node_id
            community.server = Server(community, port=server_port)
            
            flask_thread = Thread(
                target=community.server.start,
                daemon=True
            )
            flask_thread.start()
            
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info(f"Node {node_id} cancelled")
        finally:
            await ipv8.stop()
            logger.info(f"Node {node_id} stopped")
    
    asyncio.run(boot())