import hashlib
from ..encoding import base58

"""

Question Format

    {
        question: str,     // random general question
        question_id: str,  // hash of the question
        answer_hash: str,  // hash for the ( answer + question_id ) 
    }

"""


class Question:

    def __init__(self, question: str = None, question_id: str = None, answer_hash: str = None):
        self.question = question
        self.question_id = question_id
        self.answer_hash = answer_hash

    def verify(self):
        sha2 = hashlib.sha256()
        sha2.update(self.question.encode("utf-8"))
        q_id = sha2.hexdigest()
        return base58.encode(q_id) == self.question_id

    def from_json(self, question_document: dict):
        self.question = question_document["question"]
        self.question_id = question_document["question_id"]
        self.answer_hash = question_document["answer_hash"]

        return self

    def json_data(self) -> dict:
        document = {
            "question": self.question,
            "question_id": self.question_id,
            "answer_hash": self.answer_hash,
        }
        return document
