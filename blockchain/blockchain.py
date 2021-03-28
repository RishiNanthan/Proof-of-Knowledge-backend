# Classes
from .block.block import Block, SolvedTransaction
from .transaction.transaction import Transaction
from .address import address

from .settings import TRANSACTIONS_PER_BLOCK, VERSION

# Database Models
from .database.blockchaindb import BlockChainModel
from .database.blockdb import BlockModel
from .database.transactiondb import TransactionModel
from .database.unspent_transactiondb import UnspentTransactionModel

# Other Libraries
import time
import hashlib
from .encoding import base58

"""

    class Blockchain
        - blockchain_model: BlockChainModel
        - block_model: BlockModel
        - transaction_model: TransactionModel
        - unspent_transaction_model: UnspentTransactionModel
        - transaction_pool: [<Transaction>]  // to be verified by human for question validity
        - block_pool: [<Block>] // to be verified by human for question validity
        - solved_transaction_pool: [<SolvedTransaction>]

        Methods

        - generate_keys() -> (ecdsa.PublicKey, ecdsa.PrivateKey)
        - add_block_pool(block_data: dict) -> bool
        - add_transaction_pool(transaction_data: dict) -> bool
        - store_block(block_data: dict) -> bool
        - store_transaction(transaction_data: dict) -> bool
        - get_block(block_id: str) -> dict
        - get_transaction(transaction_id: str) -> dict
        - mine_block() -> dict
        - solve_transaction() -> bool


"""

class BlockChain:

    def __init__(self):
        """

            This is the Interface / Entry Point to all the internal components.

        """

        self.block_chain_model = BlockChainModel()
        self.block_model = BlockModel()
        self.transaction_model = TransactionModel()
        self.unspent_transaction_model = UnspentTransactionModel()

        self.transaction_pool = {}
        self.block_pool = {}
        self.solved_transaction_pool = {}


    @staticmethod
    def generate_keys() -> tuple:
        """
            Generates new private_key, public_key pair

            Returns:
            (public_key, private_key)

        """
        return address.generate_keys()
    

    def add_block_pool(self, block_data: dict) -> bool:
        """
            Adds the block to the block_pool

            Parameters:
                block_data: dict

            Returns:
                bool
        """

        block = Block()
        block.from_json(block_data)

        if block.block_id in self.block_pool.keys():
            return True

        if block.verify():
            self.block_pool[block.block_id] = block
            self.store_block(block_data)
            return True
        return False


    def add_transaction_pool(self, transaction_data: dict) -> bool:
        """
            Adds the transaction to the transaction pool

            Parameters:
                transaction_data: dict

            Returns:
                bool
        """

        transaction = Transaction()
        transaction.from_json(transaction_data)

        if transaction.transaction_id in self.transaction_pool.keys():
            return True

        if transaction.verify():
            self.transaction_pool[transaction.transaction_id] = transaction
            self.store_transaction(transaction_data)
            return True
        return False
        

    def store_block(self, block_data: dict) -> bool:
        """
            Stores the block to the database. If already found or not valid block, returns False

            Parameters:
                block_data: dict

            Returns:
                bool

        """

        block = Block()
        block.from_json(block_data)
        if block.verify():
            return self.block_model.add_block(block)
        else:
            return False


    def store_transaction(self, transaction_data: dict) -> bool:
        """
            Stores the transaction to the database. If already found or not valid transaction, returns False

            Parameters:
                transaction_data: dict

            Returns:
                bool

        """

        transaction = Transaction()
        transaction.from_json(transaction_data)
        if transaction.verify():
            return self.transaction_model.add_transaction(transaction)
        else:
            return False

    def add_blockto_chain(self, block_data: dict) -> bool:
        block = Block().from_json(block_data)
        prev_block_id = block.previous_block
        if self.block_chain_model.block_exists(prev_block_id):
            if self.block_chain_model.get_last_block_id() == prev_block_id:
                self.block_chain_model.append(block_id=block.block_id)
                # Do stuffs like calculate unspend transactions
                return block.add_tochain()

            else:
                prev_block_number = self.block_chain_model.getby_block_id(prev_block_id)
                cur_block_id = self.block_chain_model.getby_block_number(prev_block_number + 1)
                cur_block = self.block_model.get_block(cur_block_id)

                # Check Timestamp  To be implemented

                if cur_block.timestamp > block.timestamp:
                    removed_blocks = self.block_chain_model.remove_until(prev_block_number) # removed block ids
                    for removed_block in removed_blocks:
                        self.unspent_transaction_model.free_block_transactions(removed_block)
                    self.block_chain_model.append(block_id=block.block_id)
                    
                    return block.add_tochain()

        return False


    def get_blockby_id(self, block_id: str) -> dict:
        """
            Gets the corresponding block from the database. If not found, returns None

            Parameters:
                block_id: str // hexadecimal string

            Returns:
                Block Dict

        """

        block_data = self.block_model.get_block(block_id)
        if block_data is None:
            return None
        
        return block_data

    def get_blockby_number(self, block_number: int) -> dict:
        """
            Gets the corresponding block from the database. If not found, returns None

            Parameters:
                block_id: str // hexadecimal string

            Returns:
                Block Dict

        """
        block_id = self.block_chain_model.getby_block_number(block_number)
        block_data = self.block_model.get_block(block_id)
        if block_data is None:
            return None
        return block_data


    def get_transaction(self, transaction_id: str) -> dict:
        """
            Gets the corresponding transaction from the database. If not found, returns None

            Parameters:
                transaction_id: str // hexadecimal string

            Returns:
                Transaction Dict

        """

        transaction_data = self.transaction_model.get_transaction(transaction_id)
        if transaction_data is None:
            return None

        return transaction_data

    def solve_transaction(self, transaction_id: str, answer: str) -> bool:
        transaction = self.transaction_pool[transaction_id]
        question_id = transaction.question.question_id
        sha = hashlib.sha256()
        sha.update((answer+question_id).encode('utf-8'))
        ans = sha.hexdigest()
        ans = base58.encode(ans)
        
        if ans == transaction.question.answer_hash:
            self.transaction_pool.pop(transaction.transaction_id)
            solved_transaction = SolvedTransaction(transaction, answer)
            self.solved_transaction_pool[transaction.transaction_id] = solved_transaction
            return True
        return False


    def mine_block(self, reward_transaction_data: dict, miner_public_key: str) -> dict:
        """
            Creates a block using transactions from transaction_pool, returns None incase of failure

            Parameters:
                reward_transaction_data: dict

            Returns:
                str    // Block_Hash
  
        """

        if len(self.solved_transaction_pool) >= TRANSACTIONS_PER_BLOCK:
            new_block = Block()
            new_block.solved_transactions = self.solved_transaction_pool[: TRANSACTIONS_PER_BLOCK]
            
            reward = Transaction().from_json(reward_transaction_data)
            new_block.reward_transaction = reward

            # To be implemented
            new_block.timestamp = ""
            new_block.miner_public_key = miner_public_key
            new_block.version = VERSION
            new_block.block_id = new_block.find_block_id()

            self.add_block_pool(new_block.json_data())
            return new_block.json_data()

        return None
