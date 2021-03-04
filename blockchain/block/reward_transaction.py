from ..transaction.output import Output
from .settings import REWARD_VALUE


class RewardTransaction:

    def __init__(self, publickey: str = None, outputs: list = None, timestamp: str = None, transaction_id: str = None, 
    signature: str = None, description: str = None):

        self.publickey = publickey
        self.inputs = []
        self.outputs = outputs
        self.timestamp = timestamp
        self.transaction_id = transaction_id  # Hash of transaction
        self.signature = signature  # signature of the hash of all details except transaction_id
        self.description = description
        self.question = None


    def verify(self):
        total_value = 0
        for output in self.outputs:
            total_value += output.value
        if total_value > REWARD_VALUE:
            return False
        return True


    def json_data(self) -> dict:
        document = {
            "public_key": self.publickey,
            "inputs": [],
            "outputs": [i.json_data() for i in self.outputs],
            "description": self.description,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "transaction_id": self.transaction_id,
            "question": None
        }
        return document

    
    def from_json(self, transaction_document: dict):
        self.publickey = transaction_document['public_key']
        self.description = transaction_document['description']
        self.timestamp = transaction_document['timestamp']
        self.signature = transaction_document['signature']
        self.transaction_id = transaction_document['transaction_id']
        self.outputs = [ Output().from_json(doc) for doc in transaction_document['outputs'] ]

