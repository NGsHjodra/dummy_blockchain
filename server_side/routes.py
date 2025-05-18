from flask import Flask, jsonify, render_template
from .api.transaction.transaction_controller import Transaction_controller
from .api.block.block_controller import Block_controller

def routes(app, community):
    transaction_controller = Transaction_controller(community)
    block_controller = Block_controller(community)
    
    app.add_url_rule('/api/blocks', 'blocks', block_controller.get_blocks)

    app.add_url_rule('/api/transactions', 'transactions', transaction_controller.get_transactions)
    app.add_url_rule('/api/send_transaction', 'send_transaction', transaction_controller.send_transaction, methods=['POST'])