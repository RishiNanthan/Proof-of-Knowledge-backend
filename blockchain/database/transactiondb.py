import pymongo
from .settings import SERVER, DATABASE_NAME

COLLECTION_NAME = "Transaction"

transaction_format = """

Transaction Format

    {
        block_id: str,        // Block id if it's stored in chain
        public_key: str,      // Public Key of the transaction owner
        inputs: [<Input>],    // Inputs 
        outputs: [<Output>],  // Outputs
        timestamp: str,       // Timestamp
        description: str,     // Details of transaction
        question: Question,   // Random question
        signature: str,       // signature of hash of all above details
        transaction_id: str,  // hash of all above details
    }

Input Format

    {
        transaction_id: str,    // Hash of Previous Transaction
        index: int,             // previous transaction Output index
        value: float,           // Value holded by the previous transaction
        script_signature: str,  // Script to unlock previous transaction script
    }

Output Format

    {
        index: int,                    // index of the output array
        value: float,                  // value to be transferred
        public_key: str,               // value transferred to ID
        script_public_signature: str,  // Locking script
    }

Question Format

    {
        question: str,     // random general question
        question_id: str,  // hash of the question
        answer_hash: str,  // hash for the ( answer + question_id ) 
    }


"""


class TransactionModel:

    def __init__(self):
        client = pymongo.MongoClient(SERVER)
        db = client.get_database(DATABASE_NAME)
        self.collection = db.get_collection(COLLECTION_NAME)

    def add_free_transaction(self, transaction) -> bool:
        if not self.transaction_exists(transaction_id=transaction.transaction_id):
            document = transaction.json_data()
            if "block_id" not in document.keys():
                document["block_id"] = None
            ack = self.collection.insert_one(document)
            return ack.acknowledged
        return False

    def add_chain_transaction(self, transaction, block_id: str) -> bool:
        free_transaction = self.get_transaction(transaction.transaction_id)
        if free_transaction is not None and free_transaction['block_id'] is None:
            ack = self.collection.update_one(
                {
                    "transaction_id": transaction.transaction_id,
                },
                {
                    "block_id": block_id,
                }
            )
            return ack.acknowledged
        else:
            document = transaction.json_data()
            document['block_id'] = block_id
            ack = self.collection.insert_one(document)
            return ack.acknowledged

    def transaction_exists(self, transaction_id: str) -> bool:
        transaction = self.collection.find_one({"transaction_id": transaction_id})
        return transaction is not None

    def get_transaction(self, transaction_id: str):
        transaction = self.collection.find_one({"transaction_id": transaction_id})
        return transaction
