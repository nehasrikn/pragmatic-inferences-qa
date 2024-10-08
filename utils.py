import json
import os
import pwd
from typing import List, Any, Tuple, Union
import pandas as pd

PROJECT_ROOT_DIR="/fs/clip-projects/rlab/nehasrik/pragmatic-inferences-qa"

def get_username():
    return pwd.getpwuid(os.getuid())[0]

PROJECT_ROOT_DIR_MAP = {
    'nehasrik': PROJECT_ROOT_DIR
}

if get_username() not in PROJECT_ROOT_DIR_MAP:
    raise ValueError(f"Unknown username {get_username()}. Please add the username to the PROJECT_ROOT_DIR_MAP in utils.py")

PROJECT_ROOT_DIR = PROJECT_ROOT_DIR_MAP[get_username()] 

def list_dir(path: str) -> List[str]:
    if not path.startswith(PROJECT_ROOT_DIR):
        path = os.path.join(PROJECT_ROOT_DIR, path)
    return os.listdir(path)

def load_csv(path: str) -> pd.DataFrame:
    if not path.startswith(PROJECT_ROOT_DIR):
        path = os.path.join(PROJECT_ROOT_DIR, path)
    return pd.read_csv(path)

def load_jsonlines(path: str) -> List[Any]:
    if not path.startswith(PROJECT_ROOT_DIR):
        path = os.path.join(PROJECT_ROOT_DIR, path)
    with open(path, 'r') as f:
        return [json.loads(line) for line in f.readlines()]

def write_json(d: dict, path: str) -> None:
    if not path.startswith(PROJECT_ROOT_DIR):
        path = os.path.join(PROJECT_ROOT_DIR, path)
    with open(path, 'w') as fp:
        json.dump(d, fp, indent=2, ensure_ascii=False)

def load_json(path: str) -> dict:
    if not path.startswith(PROJECT_ROOT_DIR):
        path = os.path.join(PROJECT_ROOT_DIR, path)
    with open(path, 'r') as json_file:
        data = json.load(json_file)
    return data

def get_file_with_prefix(directory, prefix):
    if not directory.startswith(PROJECT_ROOT_DIR):
        directory = os.path.join(PROJECT_ROOT_DIR, directory)
    
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            return os.path.join(directory, filename)

    return None  # Return None if no file with the specified prefix is found