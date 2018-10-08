import pathlib
import yaml
import os

BASE_DIR = pathlib.Path(__file__).parent
config_path = os.path.join(BASE_DIR, 'config', 'dh.yaml')

def get_config(path):
    with open(path) as f:
        config = yaml.load(f)
    return config

config = get_config(config_path)