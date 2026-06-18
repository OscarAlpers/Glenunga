import json

def load_characters():
    with open("data/characters.json") as f:
        return json.load(f)

def load_moves():
    with open("data/moves.json") as f:
        return json.load(f)