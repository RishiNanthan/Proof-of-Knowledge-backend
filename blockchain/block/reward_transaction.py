from ..transaction.output import Output
from .settings import REWARD_VALUE
from ..encoding.encoding import decode_public_key
from ecdsa import BadSignatureError
import hashlib



class RewardTransaction:

    def __init__(self, public_key: str = None, outputs: list = None, timestamp: str = None, transaction_id: str = None,
                 signature: str = None, description: str = None):

        self.public_key = public_key      # base58 of ecdsa public key
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
        try:
            self.verify_signature()
            return True
        except Exception:
            return False


    def get_signing_message_hash(self) -> str:
        document = self.json_data()
        document.pop("signature")
        document.pop("transaction_id")
        document_str = str(document)

        sha256 = hashlib.sha256()
        sha256.update(document_str.encode('utf-8'))
        message_hash = sha256.hexdigest()

        return message_hash

    def verify_signature(self) -> bool:
        pubkey = decode_public_key(self.public_key)

        msg = self.get_signing_message_hash()
        msg = bytes.fromhex(msg)
        sign = bytes.fromhex(self.signature)

        try:
            if pubkey.verify(sign, msg):
                return True
        except BadSignatureError:
            pass

        return False

    def json_data(self) -> dict:
        document = {
            "public_key": self.public_key,
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
        self.public_key = transaction_document['public_key']
        self.description = transaction_document['description']
        self.timestamp = transaction_document['timestamp']
        self.signature = transaction_document['signature']
        self.transaction_id = transaction_document['transaction_id']
        self.outputs = [Output().from_json(doc) for doc in transaction_document['outputs']]
