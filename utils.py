import json
import string
import random
from os import path, remove


def read_tmp_file(filename: str = 'temp.json'):
    data = None

    if path.exists(filename):
        with open(filename, 'r') as temp:
            data = json.load(temp)
        remove(filename)

    return data


def write_to_tmp_file(output, filename: str = 'temp.json'):
    with open(filename, 'w') as temp:
        json.dump(output, temp)


def generate_salt() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
