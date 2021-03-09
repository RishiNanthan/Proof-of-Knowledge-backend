import pymongo
from .settings import SERVER, DATABASE_NAME

COLLECTION_NAME = "Unspent_Transaction"

"""
            UNSPENT TRANSACTION DOCUMENT STRUCTURE

            {
                transaction_id: str,
                output_index: int,
                spend_block: str,
            }

"""


class UnspentTransactionModel:

    def __init__(self):
        client = pymongo.MongoClient(SERVER)
        db = client.get_database(DATABASE_NAME)
        self.collection = db.get_collection(COLLECTION_NAME)

    def add_transaction(self, transaction):
        inputs = transaction.inputs
        outputs = transaction.outputs
        transaction_id = transaction.transaction_id

        #  Change this to add block_id where the transaction is stored
        for i in inputs:
            self.collection.delete_one(
                {
                    "transaction_id": i.transaction_id,
                    "output_index": i.index,
                }
            )

        unspent_documents = [
            {
                "transaction_id": transaction_id,
                "output_index": output.index
            } for output in outputs
        ]

        self.collection.insert_many(unspent_documents)

    def is_unspent(self, transaction_input):
        queryset = self.collection.find_one(
            {
                "transaction_id": transaction_input.transaction_id,
                "output_index": transaction_input.index,
                "spend_block": None,
            }
        )
        return queryset.count()
