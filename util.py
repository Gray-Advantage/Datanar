from json import load

with open("configuration.json") as config_file:
    CONFIG = load(config_file)
