from os import path, remove
import json


def read_file(filename: str = 'temp.json'):
    data = None

    if path.exists(filename):
        with open(filename, 'r') as temp:
            data = json.load(temp)
        remove(filename)

    return data


def write_to_file(output, filename: str = 'temp.json'):
    with open(filename, 'w') as temp:
        json.dump(output, temp)
