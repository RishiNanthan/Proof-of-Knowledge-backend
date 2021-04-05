
from blockchain.blockchain import BlockChain
import blockchain_client
import blockchain_server


IP = None
PORT = None


def initialise():

    global IP, PORT

    if IP is None or PORT is None:
        IP = input("Enter IP address: ")
        PORT = int(input("Enter PORT number: "))

    blockchain_server.IP = IP
    blockchain_server.PORT = PORT


if __name__ == '__main__':
    initialise()
    blockchain_server.run_server()
