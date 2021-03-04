import pymongo
from .settings import SERVER, DATABASE_NAME


COLLECTION_NAME = "Block"


"""
BLOCK DOCUMENT STRUCTURE

    {
        block_id: str,
        version: int,
        previous_block: str,
        timestamp: str,
        solved_transactions: [
            {
                transaction: <Transaction>,
                solution: str,                       // Answer for the question posted in the transaction
            }
            ....
        ]
        reward_transaction: <Transaction>
    }

"""

class BlockModel:
    
    def __init__(self):
        client = pymongo.MongoClient(SERVER)
        db = client.get_database(DATABASE_NAME)
        self.collection = db.get_collection(COLLECTION_NAME)


    def block_exists(self):
        query_result = self.collection.find_one({ "block_id": block_id }, { "_id": 0 })
        return query_result is not None


    def add_block(self, block) -> bool:
        query_result = self.collection.insert_one(block.json_data())
        return query_result.acknowledged


    def get_block(self, block_id: str) -> dict:
        query_result = self.collection.find_one({ "block_id": block_id }, { "_id": 0 })
        return query_result
        
