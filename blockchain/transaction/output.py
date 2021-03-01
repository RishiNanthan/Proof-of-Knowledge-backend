

output_format = """

Output Format

    {
        index: int,                    // index of the output array
        value: float,                  // value to be transferred
        script_public_signature: str,  // Locking script
    }

"""


class Output:

    def __init__(self, index: int, value: float, script_public_signature: str):
        self.index = index
        self.value = value
        self.script_public_signature = script_public_signature        #  Locking Script


    def json_data(self):
        data = {
            "index": self.index,
            "value": self.value,
            "script_public_signature": self.script_public_signature,
        }
        return data


    def from_json(self, output_document: dict):
        self.index = output_document['index']
        self.value = output_document['value']
        self.script_publickey = output_document['script_public_signature']
        

    def __str__(self):
        return f"index: {self.index}, value: {self.value}, script_public_signature: {self.script_public_signature}"


print(output_format)