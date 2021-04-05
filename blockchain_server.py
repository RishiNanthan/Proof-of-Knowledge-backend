
from blockchain.blockchain import BlockChain
from blockchain_client import BlockChain_Client
from blockchain.encoding.base58 import encode, decode_private_key

from flask import Flask, jsonify, request, render_template, url_for, redirect

import random
import hashlib

LOG = print

IP = None
PORT = None
CONNECTED_NODES = set([])
BLOCKCHAIN = BlockChain()
CLIENT = BlockChain_Client(IP, PORT)

ACK_MSG = {
    "error": False,
    "acknowledged": True,
}

def ERROR_MSG(msg: str) -> dict:
    return {
        "error": True,
        "msg": msg
    }


def SEND_DATA(data: dict) -> dict:
    return {
        "error": False,
        "data": data,
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
    LOG(f"Node: {ip} connected.")
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
            CLIENT.send_block_invite(block_id, CONNECTED_NODES)
    return jsonify(ACK_MSG)


@app.route('/invite_for_transaction')
def invite_for_transaction():
    transaction_id = request.args.get("transaction_id")
    ip_address = request.args.get("ip_address")
    LOG(f"Invited for transaction {transaction_id} at {ip_address}.")
    if BLOCKCHAIN.get_transaction(transaction_id) is None and transaction_id not in BLOCKCHAIN.transaction_pool.keys() and \
         transaction_id not in BLOCKCHAIN.solved_transaction_pool.keys():
        transaction_data = CLIENT.get_invited_transaction(transaction_id, ip_address)
        if transaction_data is not None:
            BLOCKCHAIN.add_transaction_pool(transaction_data)
            CLIENT.send_transaction_invite(transaction_id, CONNECTED_NODES)
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
    if transaction_data is None:
        return jsonify(ERROR_MSG("NO_SUCH_TRANSACTION"))
    return jsonify(SEND_DATA(transaction_data))


@app.route('/get_block')
def get_block():
    block_id = request.args.get('block_id')
    block_data = BLOCKCHAIN.get_block(block_id)
    if block_data is None and block_id in BLOCKCHAIN.block_pool.keys():
        block_data = BLOCKCHAIN.block_pool[block_id].json_data()
    if block_data is None:
        return jsonify(ERROR_MSG("NO_SUCH_BLOCK"))
    return jsonify(SEND_DATA(block_data))


@app.route('/get_block_by_number')
def get_block_by_number():
    block_number = int(request.args.get('block_number'))
    block_id = BLOCKCHAIN.block_chain_model.getby_block_number(block_number)
    if block_id is None:
        return jsonify(ERROR_MSG("NO_SUCH_BLOCK"))
    return redirect(f"/get_block?block_id={block_id}")


@app.route('/get_last_block_number')
def get_last_block_number():
    block_number = BLOCKCHAIN.block_chain_model.get_last_block_number()
    return jsonify(SEND_DATA({'block_number': block_number}))


@app.route('/create_transaction', methods=["POST"])                     #   To be completed
def create_transaction():
    transaction_data = request.get_json()
    if BLOCKCHAIN.add_transaction_pool(transaction_data):
        return jsonify(ACK_MSG)
    return jsonify(ERROR_MSG("INVALID_TRANSACTION"))


@app.route("/create_address") 
def create_address():
    public_key, private_key = BlockChain.generate_keys()
    data = {
        "public_key": public_key,
        "private_key": private_key,
    }
    # return jsonify(SEND_DATA(data))
    return jsonify(data)                                        # Change this to previous


@app.route("/find_hash")
def find_hash():
    """
        /find_hash => gives base58 of sha256 of given document
    """
    document = request.get_json()
    document_data = str(document)
    sha = hashlib.sha256()
    sha.update(document_data.encode('utf-8'))
    hash_str = sha.hexdigest()
    hash_base58 = encode(hash_str)
    return jsonify(SEND_DATA({"hash": hash_base58}))


@app.route("/get_signature", methods=["POST"])
def get_signature():
    private_key = request.values["private_key"]
    document = request.get_json()
    
    document = str(document)
    private_key = decode_private_key(private_key)

    data = private_key.sign(document.encode('utf-8'))
    data = encode(data.hex())

    return jsonify(SEND_DATA({"sign": data}))


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
