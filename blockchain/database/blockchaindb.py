import pymongo
from .settings import SERVER, DATABASE_NAME

COLLECTION_NAME = "BlockChain"
CONFIG_COLLECTION_NAME = "BlockChainConfig"

"""
BLOCKCHAIN DOCUMENT STRUCTURE

    {
        block_number: int,
        block_id: str,
    }

BLOCKCHAIN CONFIG STRUCTURE

    {
        config: 'blockchain',
        last_block_id: str,
        last_block_number: int,
    }

"""

class BlockChainModel:
    
    def __init__(self):
        client = pymongo.MongoClient(SERVER)
        db = client.get_database(DATABASE_NAME)
        self.collection = db.get_collection(COLLECTION_NAME)
        self.config_collection = db.get_collection(CONFIG_COLLECTION_NAME)

        #  Initialising if not done        
        res = self.config_collection.find_one({'config': 'blockchain'}, {'_id': 0})
        if res is None:
            res = self.config_collection.insert_one(
                {
                    "config": "blockchain",
                    "last_block_number": 0,
                    "last_block_id": None,
                }
            )

    def getby_block_number(self, block_number: int) -> str:
        res = self.collection.find_one({"block_number": block_number}, {"_id": 0})
        if res is not None:
            return res["block_id"]
        return None

    def getby_block_id(self, block_id: str) -> int:
        res = self.collection.find_one({"block_id": block_id}, {"_id": 0})
        if res is not None:
            return res['block_number']
        return None

    def get_last_block_number(self) -> int:
        res = self.config_collection.find_one({'config': 'blockchain'}, {'_id': 0})
        return res['last_block_number']

    def get_last_block_id(self) -> str:
        res = self.config_collection.find_one({'config': 'blockchain'}, {'_id': 0})
        return res['last_block_id']        


    def append(self, block_id: str) -> bool:
        block_number = self.get_last_block_number()
        res = self.collection.insert_one({'block_id': block_id, 'block_number': block_number})

        update_config = self.config_collection.update_one(
            {
                'config': 'blockchain'
            },
            {
                'last_block_number': block_number,
                'last_block_id': block_id,
            }
        )
        return res.acknowledged and update_config.acknowledged

    def updateby_number(self, block_number: int, block_id: str) -> bool:
        if block_number == self.get_last_block_number():
            return self.update_last(block_id)

        res = self.collection.update_one(
            {"block_number": block_number},
            {"block_id": block_id}
        )
        return res.acknowledged

    def update_last(self, block_id: str) -> bool:
        res = self.collection.update_one(
            {"block_number": block_number},
            {"block_id": block_id}
        )

        #
        update_config = self.config_collection.update_one(
            {'config': 'blockchain'},
            {'last_block_id': block_id}
        )

        return res.acknowledged and update_config.acknowledged

    def removeby_number(self, block_number: int) -> bool:
        if block_number == self.get_last_block_number():
            return self.remove_last()
        
        res = self.collection.delete_one({'block_number': block_number})
        return res.acknowledged
    

    def remove_last(self) -> bool:
        number = self.get_last_block_number()
        res = self.collection.delete_one({'block_number': number})

        #  Updating config after removal
        update_config = self.config_collection.update_one(
            {'config': 'blockchain'},
            {'last_block_number': number-1,'last_block_id': self.getby_block_number(number-1) }
        )
        return res.acknowledged and update_config.acknowledged

    def remove_until(self, block_number: int) -> dict:
        """
            Removes all blocks from chain until given block_number
            doesn't remove given block number
        """
        removed_list = []
        number = self.get_last_block_number()
        while number > block_number:
            removed_list.append(self.get_last_block_id())
            self.remove_last()
            number -= 1

        return removed_list


    def block_exists(self, block_id: str) -> bool:
        block = self.collection.find_one({'block_id': str})
        if block is not None:
            return True
        return False
