from flask import request
from flask import jsonify, render_template
from binascii import unhexlify

class Transaction_controller:
    def __init__(self, community):
        self.community = community

    def get_transactions(self):
        transactions = self.community.get_transactions()
        transactions_list = [transaction.to_dict() for transaction in transactions]
        return jsonify(transactions_list)

    def send_transaction(self):
        data = request.get_json()

        sender_mid = bytes.fromhex(data.get('sender_mid'))
        receiver_mid = bytes.fromhex(data.get('receiver_mid'))
        cert_hash = bytes.fromhex(data.get('cert_hash'))
        timestamp = float(data.get('timestamp'))
        signature = bytes.fromhex(data.get('signature'))
        public_key = bytes.fromhex(data.get('public_key'))

        self.community.create_and_broadcast_transaction(
            sender_mid=sender_mid,
            receiver_mid=receiver_mid,
            cert_hash=cert_hash,
            timestamp=timestamp,
            signature=signature,
            public_key=public_key
        )
        return jsonify({"status": "success"})