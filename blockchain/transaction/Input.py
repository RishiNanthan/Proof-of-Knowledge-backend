import base64
from .script import Script


"""

Input Format

    {
        transaction_id: str,    // Hash of Previous Transaction
        index: int,             // previous transaction Output index
        value: float,           // Value holded by the previous transaction
        script_signature: str,  // Script to unlock previous transaction script
    }

"""

class Input:
    
    def __init__(self, transaction_id: str=None, index: int=None, value: float=None, script_signature: str=None):
        self.transaction_id = transaction_id
        self.value = value
        self.index = index
        self.script_signature = script_signature                                 # unlocking script
        
        
    def json_data(self) -> dict:
        data = {
            "transaction_id": self.transaction_id,
            "index": self.index,
            "value": self.value,
            "script_signature": self.script_signature,
        }
        return data


    def from_json(self, input_document: dict):
        self.transaction_id = input_document['transaction_id']
        self.index = input_document['index']
        self.value = input_document['value']
        self.script_signature = input_document['script_signature']


    def __str__(self) -> str:
        return f"transaction_id: {self.transaction_id}, index: {self.index}, value: {self.value}, " + \
             f"script_signature: {self.script_signature}"

