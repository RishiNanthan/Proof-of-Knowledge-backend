
from blockchain.blockchain import BlockChain
from .blockchain_client import BlockChain_Client

from flask import Flask, jsonify, request, render_template, url_for

import random


IP = None
PORT = None
CONNECTED_NODES = set([])
BLOCKCHAIN = BlockChain()
CLIENT = BlockChain_Client(IP, PORT)

ACK_MSG = {
    "acknowledged": True,
}


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    """
    data = {
        "IP_ADDRESS": f"{ IP }:{ PORT }",
        "CONNECTED_NODES": CONNECTED_NODES,
    }
    return jsonify(data)
    """
    return render_template("index.html")


@app.route('/connect')
def connect():
    ip = request.args.get("ip_address")
    CONNECTED_NODES.add(ip)
    return jsonify(ACK_MSG)


@app.route('/invite_for_block')
def invite_for_block():
    block_id = request.args.get("block_id")
    ip_address = request.args.get("ip_address")
    print(block_id, ip_address)
    if BLOCKCHAIN.get_blockby_id(block_id) is None and block_id not in BLOCKCHAIN.block_pool.keys():
        block_data = CLIENT.get_invited_block(block_id, ip_address)
        if block_data is not None:
            BLOCKCHAIN.add_block_pool(block_data)
    return jsonify(ACK_MSG)


@app.route('/invite_for_transaction')
def invite_for_transaction():
    transaction_id = request.args.get("transaction_id")
    ip_address = request.args.get("ip_address")
    print(transaction_id, ip_address)
    if BLOCKCHAIN.get_transaction(transaction_id) is None and transaction_id not in BLOCKCHAIN.transaction_pool.keys() and \
         transaction_id not in BLOCKCHAIN.solved_transaction_pool.keys():
        transaction_data = CLIENT.get_invited_transaction(transaction_id, ip_address)
        if transaction_data is not None:
            BLOCKCHAIN.add_transaction_pool(transaction_data)
    return jsonify(ACK_MSG)


@app.route('/get_transaction')
def get_transaction():
    transaction_id = request.args.get('transaction_id')
    transaction_data = BLOCKCHAIN.get_transaction(transaction_id)
    if transaction_data is None:
        if transaction_id in BLOCKCHAIN.transaction_pool.keys():
            transaction_data = BLOCKCHAIN.transaction_pool[transaction_id].json_data()
        elif transaction_id in BLOCKCHAIN.solved_transaction_pool.keys():
            transaction_data = BLOCKCHAIN.solved_transaction_pool[transaction_id].transaction.json_data()
    return jsonify(transaction_data)


@app.route('/get_block')
def get_block():
    block_id = request.args.get('block_id')
    block_data = BLOCKCHAIN.get_block(block_id)
    if block_data is None and block_id in BLOCKCHAIN.block_pool.keys():
        block_data = BLOCKCHAIN.block_pool[block_id].json_data()    
    return jsonify(block_data)


@app.route('/get_next_block')                         #   To be completed
def get_next_block():
    cur_block_id = request.args.get('block_id')
    return jsonify({})


@app.route('/create_transaction', methods=["POST"])                     #   To be completed
def create_transaction():
    print(request.get_data())
    return jsonify({})


@app.route("/create_address") 
def create_address():
    public_key, private_key = BlockChain.generate_keys()
    data = {
        "public_key": public_key,
        "private_key": private_key,
    }
    return jsonify(data)


@app.route("/get_client_transactions")                 # To be completed
def get_client_transactions():
    transaction = {
        "transaction_id": "fgdjAGFUGu" + str(random.randrange(5000)),
        "description": "Hello World",
        "public_key": "dgyZGGuf",
        "signature": "fgvujAGFU",
        "timestamp": "17-01-2000 12:00:00",
        "inputs": [
            {
                "previous_transaction": "gfkbgbghg",
                "index": 0,
                "value": random.randrange(0, 500),
                "script": "OP_CHKSIG SIG",
            }
        ],
        "outputs": [
            {
                "value": 4.5,
                "script": "OP_CHKSIG",
            },
        ],
    }

    data = {
        "transactions": [transaction],
    }
    return jsonify(data)



def run_server():
    app.run(IP, PORT, debug=False)
