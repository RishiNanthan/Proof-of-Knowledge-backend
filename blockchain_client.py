import requests
from blockchain.blockchain import BlockChain


LOG = print


class BlockChain_Client:

    def __init__(self, ip: str="127.0.0.1", port: int=8000):
        self.ip_address = f"{ ip }:{ port }"


    def get_invited_transaction(self, transaction_id: str, ip_address: str) -> dict:
        
        try:
            address = f"http://{ address }/get_transaction"
            req = requests.get(address, {"transaction_id": transaction_id})
            if req.ok:
                transaction_data = req.json
                return transaction_data

        except Exception as e:
            LOG(e)
        
        return None


    def get_invited_block(self, block_id: str, ip_address: str) -> dict:

        try:
            address = f"http://{ ip_address }/get_block"
            req = requests.get(address, {"block_id": block_id})
            if req.ok:
                block_data = req.json
                return block_data
            
        except Exception as e:
            LOG(e)
        return None


    def send_transaction_invite(self, transaction_id: str, connected_nodes: list) -> None:
        for nodes in connected_nodes:
            address = f"http://{ node }/invite_for_transaction"
            LOG(f"Sending Transaction invite to { node }")
            try:
                req = requests.get(address, {
                    'transaction_id': transaction_id,
                    'ip_address': f"{ IP }:{ PORT }"
                })
            except Exception as e:
                LOG(e)
                

    def send_block_invite(self, block_id: str, connected_nodes: list) -> None:
        for nodes in connected_nodes:
            address = f"http://{ node }/invite_for_block"
            LOG(f"Sending Block invite to { node }")
            try:
                req = requests.get(address, {
                    'block_id': block_id,
                    'ip_address': f"{ self.ip_address }"
                })
            except Exception as e:
                LOG(e)

