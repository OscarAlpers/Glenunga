
class Fighter:
    def __init__(self, data):
        self.name = data["name"]
        self.hp = data["hp"]
        self.type = data["type"]
        self.attack = data["attack"]
        self.defense = data["defense"]
        self.moves = data["moves"]
    def is_alive(self):
        if self.hp > 0:
            return True
        else: return False