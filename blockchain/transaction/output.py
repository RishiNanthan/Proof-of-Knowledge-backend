

output_format = """

Output Format

    {
        index: int,                    // index of the output array
        value: float,                  // value to be transferred
        public_key: str,               // value transferred to ID
        script_public_signature: str,  // Locking script
    }

"""


class Output:

    def __init__(self, index: int=None, value: float=None, script_public_signature: str=None, public_key: str=None):
        self.index = index
        self.value = value
        self.script_public_signature = script_public_signature        #  Locking Script
        self.public_key = public_key


    def json_data(self):
        data = {
            "index": self.index,
            "value": self.value,
            "public_key": self.public_key,
            "script_public_signature": self.script_public_signature,
        }
        return data


    def from_json(self, output_document: dict):
        self.index = output_document['index']
        self.value = output_document['value']
        self.public_key = output_document['public_key']
        self.script_publickey = output_document['script_public_signature']
        

    def __str__(self):
        return f"index: {self.index}, value: {self.value}, public_key: {self.public_key}, script_public_signature: {self.script_public_signature}"


print(output_format)