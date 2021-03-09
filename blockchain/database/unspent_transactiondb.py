import pymongo
from .settings import SERVER, DATABASE_NAME

COLLECTION_NAME = "Unspent_Transaction"

"""
            UNSPENT TRANSACTION DOCUMENT STRUCTURE

            {
                transaction_id: str,
                output_index: int,
                spend_block: str,
                spend_transaction: str,
            }

"""


class UnspentTransactionModel:

    def __init__(self):
        client = pymongo.MongoClient(SERVER)
        db = client.get_database(DATABASE_NAME)
        self.collection = db.get_collection(COLLECTION_NAME)

    def add_chain_transaction(self, transaction, block_id: str) -> bool:
        inputs = transaction.inputs
        outputs = transaction.outputs
        transaction_id = transaction.transaction_id

        for i in inputs:
            self.collection.update_one(
                {
                    "transaction_id": i.transaction_id,
                    "output_index": i.index,
                },
                {
                    "$set": {
                        "spend_block": block_id,
                        "spend_transaction": transaction.transaction_id,
                    }
                }
            )

        unspent_documents = [
            {
                "transaction_id": transaction_id,
                "output_index": output.index,
                "spend_block": None,
                "spend_transaction": None,
            } for output in outputs
        ]

        self.collection.insert_many(unspent_documents)

    def is_unspent(self, transaction_input):
        queryset = self.collection.find_one(
            {
                "transaction_id": transaction_input.transaction_id,
                "output_index": transaction_input.index,
                "spend_block": None,
                "spend_transaction": None,
            }
        )
        return queryset.count()
