from ..transaction.transaction import Transaction
from hashlib import sha256


class SolvedTransaction:

    def __init__(self, transaction: Transaction = None, solution: str = None):
        self.transaction = transaction
        self.solution = solution

    def verify(self):
        hash_message = self.solution + self.transaction.question.question_id
        sha2 = sha256()
        sha2.update(hash_message)
        if sha2.hexdigest() != self.transaction.question.answer_hash:
            return False
        return self.transaction.verify_transaction()

    def from_json(self, document):
        self.transaction = Transaction().from_json(document["transaction"])
        self.solution = document["solution"]

    def json_data(self):
        document = {
            "transaction": self.transaction.json_data(),
            "solution": self.solution,
        }
        return document
