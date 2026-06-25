
class Fighter:
    def __init__(self, data):
        self.name = data["name"]
        self.hp = data["hp"]
        self.type = data["type"]
        self.attack = data["attack"]
        self.defense = data["defense"]
        self.moves = data["moves"]
        self.xp = data.get("xp", 0)
        self.level = data.get("level", 1)
        self.max_hp = data["hp"]
    def is_alive(self):
        if self.hp > 0:
            return True
        else: return False
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 20:
            self.xp = 0
            self.level += 1
            self.max_hp += 5
            self.attack += 2
            self.defense += 2
            return True
        return False