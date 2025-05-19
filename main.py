from multiprocessing import Process
import os, asyncio
from single_node_community import start_node
from threading import Thread

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NUM_PEERS = 5

def run_peer(offset):
    dev_mode = True
    port = 8080 + offset
    logger.info(f"Starting peer {offset} on port {port}")
    start_node(node_id=offset, server_port=port)

if __name__ == "__main__":
    processes = []

    for i in range(NUM_PEERS):
        logger.info(f"Preparing to start peer {i}")

        p = Process(target=run_peer, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
