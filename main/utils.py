import json
import random
import string
from os import path, remove, listdir, remove


def read_tmp_file(filename: str = 'temp.json') -> dict:
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


def purge_old_files(dir_with_files: str):
    old_files = listdir(dir_with_files)
    if len(old_files) > 20:
        for old_file in old_files:
            remove(path.join(dir_with_files, old_file))
