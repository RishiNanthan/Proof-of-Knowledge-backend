import hashlib
from ecdsa import BadSignatureError
from ..encoding import base58
from ..database.transactiondb import TransactionModel
from .Input import Input
from .output import Output
from .script import Script
from .question import Question
from ..database.unspent_transactiondb import UnspentTransactionModel

"""

Transaction Format

    {
        public_key: str,      // Public Key of the transaction owner
        inputs: [<Input>],    // Inputs 
        outputs: [<Output>],  // Outputs
        timestamp: str,       // Timestamp
        description: str,     // Details of transaction
        question: Question,   // Random question
        signature: str,       // signature of hash of all above details
        transaction_id: str,  // hash of all above details
    }

"""

"""
    class Transaction

        - public_key: str
        - inputs: [<Input>]
        - outputs: [<Output>]
        - question: <Question>
        - timestamp: str
        - description: str
        - signature: str
        - transaction_id: str

        - get_transaction(transaction_id: str) -> <Transaction>
        - add_free_transaction(transaction: Transaction) -> bool (@static)
        - add_chain_transaction(transaction: Transaction, block_id: str) -> bool (@static)
        - find_transaction_id() -> str
        - get_total_input_value() -> float
        - get_total_output_value() -> float
        - get_signing_message_hash() -> str
        - is_reward_transaction() -> bool
        - is_free_transaction() -> bool
        - is_chain_transaction() -> bool
        - verify_question() -> bool
        - verify_inputs() -> bool
        - verify_outputs() -> bool
        - verify_timestamp() -> bool             // to be done
        - verify_transaction_id() -> bool
        - verify_signature() -> bool
        - verify() -> bool
        - json_data() -> dict
        - from_json() -> <Transaction>

"""


def verify_script(inp: Input, public_key: str) -> bool:
    transaction = Transaction().get_transaction(inp.transaction_id)
    if not transaction.outputs[inp.index].value == inp.value or public_key != transaction.public_key:
        return False

    locking_script = transaction.outputs[inp.index].script_publickey
    script_string = inp.script_signature + " " + locking_script

    script = Script(script_string, inp.transaction_id)
    if script.verify_script():
        return True
    return False


class Transaction:

    def __init__(self, public_key: str = None, inputs: list = None, outputs: list = None, timestamp: str = None,
                 transaction_id: str = None, signature: str = None, description: str = None, question: Question = None,
                 block_id: str = None):

        self.public_key = public_key
        self.inputs = inputs if inputs is not None else []
        self.outputs = outputs
        self.timestamp = timestamp
        self.transaction_id = transaction_id  # base58 of sha256 hash of transaction
        self.signature = signature  # signature of the hash of all details except transaction_id
        self.description = description
        self.question = question
        self.__metadata = {
            "block_id": block_id,  # block id is not None, if the transaction is added in the block chain
        }

    def get_transaction(self, transaction_id: str):
        """
            Fetches transaction from transaction database given transaction id
        """
        transaction_document = TransactionModel().get_transaction(transaction_id)
        self.from_json(transaction_document)
        self.__metadata['block_id'] = transaction_document['block_id']
        return self

    @staticmethod
    def add_free_transaction(transaction) -> bool:
        """
            Inserts transaction as free transaction in database
        """
        return TransactionModel().add_free_transaction(transaction=transaction)

    @staticmethod
    def add_chain_transaction(transaction, block_id: str) -> bool:
        """
            Inserts transaction as chain transaction
        """
        return TransactionModel().add_chain_transaction(transaction, block_id)

    def is_reward_transaction(self) -> bool:
        if self.__metadata["block_id"] is not None and not len(self.inputs) and self.question is None:
            return True
        return False

    def is_free_transaction(self) -> bool:
        if self.__metadata['block_id'] is None:
            return True
        return False

    def is_chain_transaction(self) -> bool:
        if self.__metadata['block_id'] is None:
            return False
        return True

    def find_transaction_id(self) -> str:
        """
            base58 of sha256 hash of the details of entire transaction
        """
        assert self.outputs is not None and self.timestamp is not None and self.signature is not None and \
               self.description is not None and self.question is not None
        document = self.json_data()
        document.pop("transaction_id")
        document_str = str(document)

        sha256 = hashlib.sha256()
        sha256.update(document_str.encode('utf-8'))
        transaction_id = sha256.hexdigest()
        transaction_id = base58.encode(transaction_id)

        self.transaction_id = transaction_id
        return transaction_id

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
        pubkey = base58.decode_public_key(self.public_key)

        msg = self.get_signing_message_hash()
        msg = bytes.fromhex(msg)
        sign = bytes.fromhex(self.signature)

        try:
            if pubkey.verify(sign, msg):
                return True
        except BadSignatureError:
            pass

        return False

    def verify_inputs(self):
        if self.is_reward_transaction():
            return True

        for inp in self.inputs:
            if not UnspentTransactionModel().is_unspent(inp) or not Transaction().get_transaction(
                    inp.transaction_id).is_chain_transaction() or \
                    not verify_script(inp, self.public_key):
                return False
        return True

    def verify_outputs(self):
        #  More verification can be done in outputs but for time being limited functionality is added
        if len(self.outputs) and self.get_total_input_value() > self.get_total_output_value():
            return True
        return False

    def verify_question(self) -> bool:
        if self.question is not None and not self.is_reward_transaction() and self.question.verify():
            return True
        elif self.question is None and self.is_reward_transaction():
            return True
        else:
            return False

    def verify_timestamp(self):
        return True

    def verify_transaction_id(self):
        return self.find_transaction_id() == self.transaction_id

    def verify(self) -> bool:
        return self.verify_inputs() and self.verify_outputs() and self.verify_question() and self.verify_timestamp() \
            and self.verify_signature() and self.verify_transaction_id()

    def get_total_input_value(self) -> float:
        total_input = 0
        for i in self.inputs:
            total_input += i.value
        return total_input

    def get_total_output_value(self) -> float:
        total_output = 0
        for i in self.outputs:
            total_output += i.value
        return total_output

    def json_data(self) -> dict:
        document = {
            "public_key": self.public_key,
            "inputs": [i.json_data() for i in self.inputs],
            "outputs": [i.json_data() for i in self.outputs],
            "description": self.description,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "transaction_id": self.transaction_id,
            "question": self.question.json_data()
        }
        return document

    def from_json(self, transaction_document: dict):
        self.public_key = transaction_document['public_key']
        self.description = transaction_document['description']
        self.timestamp = transaction_document['timestamp']
        self.signature = transaction_document['signature']
        self.transaction_id = transaction_document['transaction_id']
        self.inputs = [Input().from_json(doc) for doc in transaction_document['inputs']]
        self.outputs = [Output().from_json(doc) for doc in transaction_document['outputs']]
        self.question = Question().from_json(transaction_document["question"])

        return self

    def __repr__(self):
        return str(self.transaction_id)

    def __str__(self):
        return str(self.transaction_id)
