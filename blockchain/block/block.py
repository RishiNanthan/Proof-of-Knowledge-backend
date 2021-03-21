from ..encoding.encoding import base58_encode, base58_decode
from ..transaction.transaction import Transaction
from .solved_transaction import SolvedTransaction
from hashlib import sha256
from .settings import VERSION, TRANSACTION_COUNT, REWARD_VALUE
from ..database.blockdb import BlockModel


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

"""

class Block

    - block_id: str
    - previous_block: str
    - solved_transactions: [<SolvedTransaction>]
    - reward_transaction: <Transaction>
    - version: int
    - timestamp: str
    - miner_public_key: str

    Methods
    - find_block_id() -> str
    - get_block(block_id: str) -> Block
    - add_block(block: Block) -> bool  (@static)
    - verify() -> bool
    - verify_solved_transactions() -> bool
    - verify_timestamp() -> bool
    - verify_reward_transaction() -> bool
    - verify_block_id() -> bool
    - json_data() -> dict
    - from_json(block_document: dict) -> Block

"""


class Block:

    def __init__(self, previous_block: str = None, block_id: str = None, timestamp: str = None,
                 reward_transaction: Transaction = None, miner_public_key: str = None,
                 solved_transactions: list = None, version: int = None):

        self.block_id = block_id                       # base58 of sha256 hash of block
        self.previous_block = previous_block
        self.timestamp = timestamp
        self.solved_transactions = solved_transactions if solved_transactions is not None else []
        self.version = version
        self.miner_public_key = miner_public_key
        self.reward_transaction = reward_transaction

    def get_block(self, block_id):
        block_document = BlockModel().get_block(block_id)
        return self.from_json(block_document)

    def add_block(self):
        return BlockModel().add_block(self.json_data())

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
        return self.verify_solved_transactions() and self.verify_reward_transaction() and self.verify_timestamp() and self.verify_block_id()

    def verify_solved_transactions(self) -> bool:
        for transaction in self.solved_transactions:
            if not transaction.verify():
                return False
        return True

    def verify_reward_transaction(self) -> bool:
        if len(self.reward_transaction.inputs) == 0 and self.reward_transaction.question is None and self.reward_transaction.get_total_output_value() <= REWARD_VALUE:
            return True
        return False

    def verify_block_id(self) -> bool:
        return self.find_block_id() == self.block_id

    def verify_timestamp(self) -> bool:
        # To be implemented
        return True

    def json_data(self) -> dict:
        document = {
            "block_id": self.block_id,
            "version": self.version,
            "previous_block": self.previous_block,
            "timestamp": self.timestamp,
            "miner_public_key": self.miner_public_key,
            "solved_transactions": self.solved_transactions,
            "reward_transaction": self.reward_transaction,
        }
        return document

    def from_json(self, block_document: dict):
        self.block_id = block_document['block_id']
        self.version = block_document['version']
        self.previous_block = block_document['previous_block']
        self.timestamp = block_document['timestamp']
        self.miner_public_key = block_document["miner_public_key"]

        self.solved_transactions = [SolvedTransaction().from_json(doc) for doc in block_document['solved_transactions']]
        self.reward_transaction = RewardTransaction().from_json(block_document["reward_transaction"])
        return self

    def __str__(self):
        return str(self.json_data())

    def __repr__(self):
        return str(self.block_id)
