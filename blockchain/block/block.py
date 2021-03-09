from ..encoding.encoding import base58_encode, base58_decode
from ..transaction.transaction import Transaction
from .solved_transaction import SolvedTransaction
from .reward_transaction import RewardTransaction
from hashlib import sha256
from .settings import VERSION, TRANSACTION_COUNT, REWARD_VALUE

"""
BLOCK DOCUMENT STRUCTURE

    {
        block_id: str,
        version: int,
        previous_block: str,
        timestamp: str,
        solved_transactions: [
            <SolvedTransaction>             // Answer for the question posted in the transaction
            ....
        ]
        reward_transaction: <RewardTransaction>            // Input is [], Output total value is REWARD_VALUE, question=null
    }

SOLVED TRANSACTION

    {
        transaction: <Transaction>,
        solution: str,
    }

"""


class Block:

    def __init__(self, previous_block: str = None, block_id: str = None, timestamp: str = None,
                 reward_transaction: RewardTransaction = None,
                 solved_transactions: list = None, version: int = None):

        self.block_id = block_id                       # base58 of sha256 hash of block
        self.previous_block = previous_block
        self.timestamp = timestamp
        self.solved_transactions = solved_transactions if solved_transactions is not None else []
        self.version = version
        self.reward_transaction = reward_transaction

    def find_hash(self) -> str:
        # returns hash without encoding -change if it doesnt feel good
        document = self.json_data()
        document.pop("block_id")
        document_string = str(document)

        hash_fun = sha256()
        hash_fun.update(document_string)
        hash_string = hash_fun.hexdigest()
        return hash_string

    def find_block_id(self) -> str:
        hash_string = self.find_hash()
        return base58_encode(hash_string)

    def verify(self) -> bool:
        if self.find_block_id() != self.block_id:
            return False

        for solved_transaction in self.solved_transactions:
            if not solved_transaction.verify():
                return False

        return self.reward_transaction.verify()

    def json_data(self) -> dict:
        document = {
            "block_id": self.block_id,
            "version": self.version,
            "previous_block": self.previous_block,
            "timestamp": self.timestamp,
            "solved_transactions": self.solved_transactions,
            "reward_transaction": self.reward_transaction,
        }
        return document

    def from_json(self, block_document: dict):
        self.block_id = block_document['block_id']
        self.version = block_document['version']
        self.previous_block = block_document['previous_block']
        self.timestamp = block_document['timestamp']

        self.solved_transactions = [SolvedTransaction().from_json(doc) for doc in block_document['solved_transactions']]
        self.reward_transaction = RewardTransaction().from_json(block_document["reward_transaction"])

    def __str__(self):
        return str(self.json_data())

    def __repr__(self):
        return str(self.block_id)
