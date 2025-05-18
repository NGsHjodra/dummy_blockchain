from flask import jsonify, request

class Block_controller:
    def __init__(self, community):
        self.community = community
        self.blockchain = community.blockchain

    def get_blocks(self):
        """Get the list of blocks in the blockchain."""
        blocks = self.blockchain.get_chain()
        return jsonify(blocks)