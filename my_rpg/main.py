import pygame
import json
import os
import random
from engine.fighter import Fighter
from engine.data_loader import load_characters, load_moves, load_dialogue
from engine.scene_manager import Scene, SceneManager
pygame.init()
screen = pygame.display.set_mode((800, 576))
pygame.display.set_caption("Glenunga")
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576
PLAYER_SIZE = 32
PLAYER_SPEED = 4
TILE_SIZE = 32
MAP_COLS = 50   # 25
MAP_ROWS = 36   # 18

story_progress = 0

TILE_COLORS = {
    0: (222, 184, 135),     # woodfloor
    4: (84, 99, 128), #asphalt
    2:(163, 7, 18), #fake battle floor
    5: (222, 223, 227), #whiteWalkable
    1: (44, 53, 74),    # wall
    99:(0,0,0), #void
    10:(102, 56, 0), #desk
    9: (63, 70, 92),      # door
    90:(63, 70, 92), #door2
    50 : (63, 70, 92),   # tennis court door

    #SPECIAL TILE
    500: (0,200,255),


    #NPC
    400: (0, 102, 29), #An
    401: (0, 125, 19), #Sam
    410: (0, 102, 29), #BenMiles


    #FIGHTS
    3: (181, 72, 80),      # eshay fight
    101: (163, 7, 18),     # nick fight
    102: (163, 7, 18), #dev fight
    103: (222, 184, 135), #Luka Fight scene
    #Tennis Court Fights
    104: (163, 7, 18),
    105: (163, 7, 18),
    106: (163, 7, 18),
    107: (163, 7, 18),

}
npcs = {
    400: {"dialogue": "an_intro", "speaker": "An Nguyen"},
    410: {"dialogue": "ben_miles", "speaker": "Mr Miles"},
}

npc_tiles = {400, 401, 410}

enemies = {
    3: "random_eshay",
    101: "nick",
    102: "dev",
    104: "jack_ac",
    105: "daniel_rustia",
    106: "arsh",
    107: "zenan"
}
type_chart = {
    "dickhead": {"cunt": 1.5, "sket": 0.5}, #clown type - water
    "nerd": {"sporty": 1.5, "cunt": 0.5, "sket": 0.5}, #techy - steel, electric
    "sporty": {"eshay": 1.5}, #physical - fighting flying, grass
    "stoner": {}, #lazy - fire, poison
    "eshay": {"nerd": 1.5, "sporty": 0.5}, #rodent - ghost, dark
    "prefect": {"cunt": 1.5, "eshay": 1.5}, #like light whatever - fairy
    "cunt": {"nerd": 1.5, "prefect": 0.5}, #bully - rock, ground
    "sket": {"nerd": 1.5, "cunt": 1.5, "sporty": 1.5, "dickhead": 0.5}, # whoring - psychic
    "loser": {"prefect":0.5, "stoner" : 1.5}, # common - bug type
    "behemoth": {"sporty": 1.5, "sket": 1.5, "eshay": 1.5} # dragon type
}
walls = {1, 10, 11, 12,99}
doors = {
    9: {"area": "hallway", "x": 8, "y": 32},
    90: {"area": "homegroup", "x": 19, "y": 11},
    50: {"area": "hallway", "x": 10, "y": 2},
    51: {"area": "tenniscourt", "x": 2, "y": 34},
}

def build_map(area="map1"):
    game_map = []
    for row in range(MAP_ROWS):
        line = []
        for col in range(MAP_COLS):
            if row == 0 or row == MAP_ROWS - 1 or col == 0 or col == MAP_COLS - 1:
                line.append(1)
            else:
                line.append(0)
        game_map.append(line)
    if area == "map1":
        for col in range(1, 24):
            game_map[8][col] = 1
        game_map[8][12] = 0
        game_map[8][13] = 0

        for row in range(3, 8):
            game_map[row][5] = 1
            game_map[row][6] = 1

        for row in range(3, 7):
            game_map[row][18] = 1
            game_map[row][19] = 1

        game_map[12][8] = 1
        game_map[12][9] = 1
        game_map[13][8] = 1
        game_map[14][15] = 1
        game_map[14][16] = 1

        game_map[5][12] = 3
        game_map[14][22] = 101
        game_map[10][4] = 102
        game_map[24][49] = 9
        game_map[23][49] = 9
        game_map[25][49] = 9
    elif area == "hallway":
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                game_map[row][col] = 99

            # vertical hallway
        for row in range(1, 34):
            for col in range(8, 14):
                game_map[row][col] = 0

            # door on the right side (entry from homegroup)
        game_map[32][7] = 90
        game_map[33][7] = 90

        # door at the top (to next area)
        game_map[0][10] = 51
        game_map[0][11] = 51

        #fight scene
        game_map[14][13] = 2
        game_map[15][8] = 103
        game_map[15][9] = 103
        game_map[15][10] = 103
        game_map[15][11] = 103
        game_map[15][12] = 103
        game_map[15][13] = 103
        # Bathroom entrance (open the hallway wall)
        game_map[4][14] = 0
        game_map[5][14] = 0

        # Bathroom room
        for row in range(2, 8):
            for col in range(15, 24):
                game_map[row][col] = 0

        # Cubicle walls
        for row in range(2, 5):
            game_map[row][17] = 1
        for row in range(2, 5):
            game_map[row][20] = 1

        # Cubicle doors (gaps at the bottom)
        game_map[4][17] = 0
        game_map[4][20] = 0

        # Heal trigger in middle cubicle
        game_map[2][18] = 501


        #SAM
        game_map[5][12] = 401
    elif area == "homegroup":
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                game_map[row][col] = 99

        # carve out the room (say 12 wide, 10 tall, centered)
        start_col = 1
        start_row = 1
        for row in range(start_row, start_row + 14):
            for col in range(start_col, start_col + 20):
                game_map[row][col] = 0

            #DOOR
        game_map[12][21] = 9 #change to 51 for TCourt Testing
        game_map[11][21] = 9 #change to 9 for real narative

        # Teacher's desk (wider, at the front)
        game_map[2][6] = 10
        game_map[2][7] = 10
        game_map[2][5] = 10
        game_map[2][8] = 10

        # Teacher NPC behind the desk
        game_map[1][6] = 410


        game_map[5][3] = 10
        game_map[5][4] = 10
        game_map[5][5] = 10
        game_map[6][4] = 400

        # Desk 3
        game_map[8][3] = 10
        game_map[8][4] = 10
        game_map[8][5] = 10
        game_map[9][4] = 400

        # Desk 4
        game_map[11][3] = 10
        game_map[11][4] = 10
        game_map[11][5] = 10
        game_map[12][4] = 400

        # Right column of desks
        # Desk 6
        game_map[5][8] = 10
        game_map[5][9] = 10
        game_map[5][10] = 10
        game_map[6][9] = 400

        # Desk 7
        game_map[8][8] = 10
        game_map[8][9] = 10
        game_map[8][10] = 10
        game_map[9][9] = 400

        # Desk 8
        game_map[11][8] = 10
        game_map[11][9] = 10
        game_map[11][10] = 10
        game_map[12][9] = 400

    elif area == "tenniscourt":
        for row in range(MAP_ROWS):
            for col in range(MAP_COLS):
                game_map[row][col] = 4

        # perimeter
        for col in range(0, 50):
            game_map[0][col] = 1
            game_map[35][col] = 1
        for row in range(0, 36):
            game_map[row][0] = 1
            game_map[row][49] = 1

        # === SECTION 1: Narrow entrance path (rows 30-34) ===
        for row in range(30, 35):
            for col in range(1, 12):
                game_map[row][col] = 4

        # entrance door
        game_map[35][2] = 50
        game_map[35][3] = 50

        # Sam near entrance
        game_map[33][6] = 401

        # === SECTION 2: Wide court area (rows 20-29) ===
        for row in range(20, 30):
            for col in range(1, 49):
                game_map[row][col] = 4

        # court 1 lines (walkable)
        for col in range(4, 22):
            game_map[21][col] = 5
            game_map[28][col] = 5
        for row in range(21, 29):
            game_map[row][4] = 5
            game_map[row][21] = 5
            game_map[row][13] = 5

        # court 2 lines (walkable)
        for col in range(26, 46):
            game_map[21][col] = 5
            game_map[28][col] = 5
        for row in range(21, 29):
            game_map[row][26] = 5
            game_map[row][45] = 5
            game_map[row][36] = 5

        # mid fights scattered around courts
        game_map[24][12] = 104
        game_map[24][36] = 105
        game_map[26][20] = 106
        game_map[26][42] = 107

        # wall separating section 2 from 3, gap in middle
        for col in range(1, 20):
            game_map[19][col] = 1
        for col in range(28, 49):
            game_map[19][col] = 1
        game_map[19][23] = 105
        game_map[19][24] = 105

        # === SECTION 3: Two narrow corridors side by side (rows 10-18) ===
        # left corridor
        for row in range(10, 19):
            for col in range(1, 12):
                game_map[row][col] = 4

        # right corridor
        for row in range(10, 19):
            for col in range(38, 49):
                game_map[row][col] = 4

        # fights in left corridor
        game_map[16][5] = 105
        game_map[13][8] = 106
        game_map[11][3] = 106

        # fights in right corridor
        game_map[16][42] = 105
        game_map[13][44] = 106
        game_map[11][40] = 106

        # both corridors connect to top area
        # wall with two gaps
        for col in range(1, 49):
            game_map[9][col] = 1
        game_map[9][5] = 4
        game_map[9][6] = 4
        game_map[9][42] = 4
        game_map[9][43] = 4

        # === SECTION 4: Top court - boss area (rows 1-8) ===
        for row in range(1, 9):
            for col in range(1, 49):
                game_map[row][col] = 4

        # court lines
        for col in range(15, 35):
            game_map[2][col] = 5
            game_map[7][col] = 5
        for row in range(2, 8):
            game_map[row][15] = 5
            game_map[row][34] = 5
            game_map[row][25] = 5

        # tough fights guarding boss
        game_map[6][10] = 106
        game_map[6][40] = 106

        # boss at top center
        game_map[2][24] = 107
    return game_map
GAME_MAP = build_map("homegroup")


moves_data = load_moves()
characters = load_characters()
dialogue_data = load_dialogue()
player = Fighter(characters["player"])
party = [player]
sam = Fighter(characters["sam"])


class Title(Scene):
    def __init__(self):
        self.font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 32)
        self.battle_font = pygame.font.Font(None, 24)
    def handle_event(self, event): # title actually inherits the handle event and update methods - u only need to write it out again if its overriding it
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            print("Youve pressed the A key!")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            manager.goto_scene(intro)
    def update(self):
        pass
    def draw(self, screen):
        screen.fill((0, 0, 0))
        text_image = self.font.render("Glenunga", True, (255, 255, 255))
        screen.blit(text_image, (300, 250))
        start_button = self.small_font.render("Press Space to Start", True, (255, 255, 255))
        screen.blit(start_button, (299, 350))

class Background(Scene):
    def __init__(self):
        self.x = 64
        self.y = 64
        self.camera_x = 0
        self.camera_y = 0
        self.npc_cooldown = False
        self.floor_tile = 0
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            manager.goto_scene(partymenu)
    def draw(self, screen):
        screen.fill((0, 0, 0))
        for row_index, row in enumerate(GAME_MAP):
            y = row_index * TILE_SIZE - self.camera_y
            for col_index, col in enumerate(row):
                x = col_index * TILE_SIZE - self.camera_x
                color = TILE_COLORS.get(col, (50, 100, 255))
                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, (48, 54, 240), (self.x - self.camera_x, self.y - self.camera_y, PLAYER_SIZE, PLAYER_SIZE))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover_col = (mouse_x + self.camera_x) // TILE_SIZE
        hover_row = (mouse_y + self.camera_y) // TILE_SIZE
        font = pygame.font.Font(None, 24)
        label = font.render(f"row:{hover_row} col:{hover_col}", True, (255, 255, 0))
        screen.blit(label, (mouse_x + 10, mouse_y + 10))
    def is_walkable(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if row < 0 or row >= MAP_ROWS or col < 0 or col >= MAP_COLS:
            return False
        return GAME_MAP[row][col] not in walls
    def update(self):
        global story_progress
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            new_x = self.x - PLAYER_SPEED
            if self.is_walkable(new_x, self.y) and self.is_walkable(new_x, self.y + PLAYER_SIZE - 1):
                self.x = new_x
        if keys[pygame.K_RIGHT]:
            new_x = self.x + PLAYER_SPEED
            if self.is_walkable(new_x + PLAYER_SIZE - 1, self.y) and self.is_walkable(new_x + PLAYER_SIZE - 1,
                                                                                      self.y + PLAYER_SIZE - 1):
                self.x = new_x
        if keys[pygame.K_UP]:
            new_y = self.y - PLAYER_SPEED
            if self.is_walkable(self.x, new_y) and self.is_walkable(self.x + PLAYER_SIZE - 1, new_y):
                self.y = new_y
        if keys[pygame.K_DOWN]:
            new_y = self.y + PLAYER_SPEED
            if self.is_walkable(self.x, new_y + PLAYER_SIZE - 1) and self.is_walkable(self.x + PLAYER_SIZE - 1,
                                                                                      new_y + PLAYER_SIZE - 1):
                self.y = new_y
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        center_x = self.x + PLAYER_SIZE // 2
        center_y = self.y + PLAYER_SIZE // 2
        tile_column = center_x // TILE_SIZE
        tile_row = center_y // TILE_SIZE
        tile_value = GAME_MAP[tile_row][tile_column]
        self.camera_x = self.x - SCREEN_WIDTH // 2
        self.camera_y = self.y - SCREEN_HEIGHT // 2

        if tile_value in enemies:
            GAME_MAP[tile_row][tile_column] = self.floor_tile
            enemy = Fighter(characters[enemies[tile_value]])
            new_battle = Battle(party[0], enemy)
            manager.goto_scene(new_battle)

        if tile_value in doors:
            door = doors[tile_value]
            GAME_MAP.clear()
            GAME_MAP.extend(build_map(door["area"]))
            self.x = door["x"] * TILE_SIZE
            self.y = door["y"] * TILE_SIZE
            if door["area"] == "tenniscourt":
                self.floor_tile = 4
            else:
                self.floor_tile = 0

        if tile_value == 103: #luka scene
            for r in range(MAP_ROWS):
                for c in range(MAP_COLS):
                    if GAME_MAP[r][c] == 103:
                        GAME_MAP[r][c] = 0
            enemy = Fighter(characters["luka"])
            fight = Battle(player,enemy)
            fight.scripted_loss = True
            convo = Dialogue(dialogue_data["luka_fight"], fight, background, speaker="Menacing Year 9")
            manager.goto_scene(convo)

        if tile_value == 401 and not self.npc_cooldown:
            self.npc_cooldown = True
            if story_progress == 0:
                convo = Dialogue(dialogue_data["sam_intro"], background, speaker="Sam")
            elif story_progress == 1:
                convo = Dialogue(dialogue_data["sam_heal"], background, background,speaker="Sam")
            elif story_progress == 2:
                story_progress = 3
                convo = Dialogue(dialogue_data["sam_tennis"], background, background, speaker="Sam")
            elif story_progress == 3:
                story_progress = 4
                player.moves.append("lightning lob")
                GAME_MAP[tile_row][tile_column] = 4
                party.append(sam)
                convo = Dialogue(dialogue_data["sam_lightning"], sam_joins, background, speaker="Sam")

            manager.goto_scene(convo)

        if tile_value in npcs and not self.npc_cooldown:
            self.npc_cooldown = True
            npc = npcs[tile_value]
            lines = dialogue_data[npc["dialogue"]]
            convo = Dialogue(lines, background, background, speaker=npc["speaker"])
            manager.goto_scene(convo)
        if tile_value not in npc_tiles:
            self.npc_cooldown = False

        if tile_value == 501:
            GAME_MAP[tile_row][tile_column] = 0
            story_progress = 2
            player.hp = characters["player"]["hp"]
            convo = Dialogue(["You watch the Inbetweeners 2 on the toilet... HP fully restored."], background)

            manager.goto_scene(convo)
        if tile_value == 500:
            GAME_MAP[tile_row][tile_column] = 0
            player.hp = characters["player"]["hp"]
            convo = Dialogue(["You watch the Inbetweeners 2 on the toilet... HP fully restored."], background)

            manager.goto_scene(convo)


class Battle(Scene):
    def __init__(self, player, enemy):
        self.message = ""
        self.player = player
        self.enemy = enemy
        self.small_font = pygame.font.Font(None, 32)
        self.battle_font = pygame.font.Font(None, 24)
        self.selected = 0
        self.battle_over = False
        self.scripted_loss = False
        self.enemy_max_hp = self.enemy.hp
        self.message_1 = ""
        self.message_2 = ""
        self.message_3 = ""

    def draw(self, screen):
        screen.fill((20, 20, 30))

        # Player side (left)
        name = self.small_font.render(f"{self.player.name}  Lv.{self.player.level}", True, (255, 255, 255))
        screen.blit(name, (50, 40))
        hp_text = self.battle_font.render(f"{max(self.player.hp, 0)} / {self.player.max_hp}", True, (200, 200, 200))
        screen.blit(hp_text, (50, 70))
        bar_width = 200
        pygame.draw.rect(screen, (80, 0, 0), (50, 90, bar_width, 16))
        green_width = int(bar_width * max(self.player.hp, 0) / self.player.max_hp)
        pygame.draw.rect(screen, (0, 200, 0), (50, 90, green_width, 16))

        # Enemy side (right)
        name = self.small_font.render(f"{self.enemy.name}  Lv.{self.enemy.level}", True, (255, 255, 255))
        screen.blit(name, (500, 40))
        hp_text = self.battle_font.render(f"{max(self.enemy.hp, 0)} / {self.enemy_max_hp}", True, (200, 200, 200))
        screen.blit(hp_text, (500, 70))
        pygame.draw.rect(screen, (80, 0, 0), (500, 90, bar_width, 16))
        green_width = int(bar_width * max(self.enemy.hp, 0) / self.enemy_max_hp)
        pygame.draw.rect(screen, (0, 200, 0), (500, 90, green_width, 16))

        # Divider line
        pygame.draw.line(screen, (60, 60, 80), (0, 140), (800, 140), 1)

        # Moves box (bottom left)
        pygame.draw.rect(screen, (30, 30, 45), (30, 300, 300, 200))
        pygame.draw.rect(screen, (80, 80, 100), (30, 300, 300, 200), 1)
        moves_title = self.battle_font.render("MOVES", True, (150, 150, 150))
        screen.blit(moves_title, (50, 310))
        for i, move in enumerate(self.player.moves):
            if i == self.selected:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)
            move_text = self.small_font.render(moves_data[move]["name"], True, color)
            screen.blit(move_text, (50, 340 + i * 35))

        # Message box (bottom)
        pygame.draw.rect(screen, (30, 30, 45), (30, 510, 740, 50))
        pygame.draw.rect(screen, (80, 80, 100), (30, 510, 740, 50), 1)
        text1 = self.battle_font.render(self.message_1, True, (255, 255, 255))
        screen.blit(text1, (45, 520))
        text2 = self.battle_font.render(self.message_2, True, (255, 200, 200))
        screen.blit(text2, (45, 540))
        text2 = self.battle_font.render(self.message_3, True, (59, 222, 255))
        screen.blit(text2, (45, 540))
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            self.selected += 1
            if self.selected > len(self.player.moves) -1:
                self.selected = len(self.player.moves) - 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            self.selected -= 1
            if self.selected < 0:
                self.selected = 0
        if self.enemy.is_alive() and self.player.is_alive():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                move_name = self.player.moves[self.selected]
                enemy_move = random.choice(self.enemy.moves)
                enemy_damage = max((self.enemy.attack * moves_data[enemy_move]["power"]) // 10 - self.player.defense,1)
                enemy_multiplier = type_chart.get(moves_data[enemy_move]["type"], {}).get(self.player.type, 1.0)
                enemy_damage = int(enemy_damage * enemy_multiplier)
                damage = max((self.player.attack * moves_data[move_name]["power"]) // 10 - self.enemy.defense, 1)
                multiplyer = type_chart.get(moves_data[move_name]["type"], {}).get(self.enemy.type,1.0)
                damage = int(damage * multiplyer)
                self.player.hp -= enemy_damage
                self.enemy.hp -= damage
                self.message_1 = f"{self.player.name} used {moves_data[move_name]['name']} - {damage} dmg"
                self.message_2 = f"{self.enemy.name} used {moves_data[enemy_move]['name']} - {enemy_damage} dmg"
                if not self.player.is_alive():
                    next_fighter = None
                    for i, member in enumerate(party):
                        if member.is_alive() and member is not self.player:
                            next_fighter = member
                            # move them to front of party
                            party.pop(i)
                            party.insert(0, member)
                            break
                    if next_fighter:
                        self.player = next_fighter
                        self.selected = 0
                        self.message = f"{next_fighter.name} steps in!"
                    elif self.scripted_loss:
                        global story_progress
                        story_progress = 1
                        self.player.hp = 1
                        self.message_1 = "This cunt just fucked you up...Press SPACE to continue."
                        self.message_2 = ""
                        self.battle_over = True
                    else:
                        self.message = f"{self.player.name} is dead!"
                        self.battle_over = True
                if not self.enemy.is_alive():
                    xp_gained = self.enemy.level * 5 if hasattr(self.enemy, "level") else 10
                    self.player.gain_xp(xp_gained)
                    leveled = self.player.gain_xp(xp_gained)
                    self.message_1 = f"You've killed {self.enemy.name}  +{xp_gained} XP."
                    if leveled:
                        self.message_2 = ""
                        self.message_3 = f"{self.player.name} leveled up to Lv.{self.player.level}"
                    else:
                        self.message_2 = ""
                    self.battle_over = True
        if self.battle_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.scripted_loss and self.player.is_alive():
                    # continue story - Sam finds you
                    convo = Dialogue(dialogue_data["sam_intro"], background)
                    manager.goto_scene(convo)
                elif not self.player.is_alive():
                    self.player.hp = characters["player"]["hp"]
                    GAME_MAP.clear()
                    GAME_MAP.extend(build_map())
                    background.x = 64
                    background.y = 64
                    manager.goto_scene(title)
                else:
                    manager.goto_scene(background)

class PartyMenu(Scene):
    def __init__(self):
        self.selected = 0
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
    def draw(self, screen):
        screen.fill((20, 20, 40))
        title = self.font.render("Party", True, (255, 255, 255))
        screen.blit(title, (50, 20))
        for i, member in enumerate(party):
            if i == self.selected:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)
            name = self.font.render(f"{member.name} Lv.{member.level} {member.type}", True, color)
            screen.blit(name, (50, 80 + i * 80))
            stats = self.small_font.render(f"HP: {member.hp}  ATK: {member.attack}  DEF: {member.defense}", True, (180, 180, 180))
            screen.blit(stats, (50, 110 + i * 80))
            # health bar
            bar_width = 150
            green_width = int(bar_width * max(member.hp, 0) / member.max_hp)
            pygame.draw.rect(screen, (255, 0, 0), (300, 85 + i * 80, bar_width, 15))
            pygame.draw.rect(screen, (0, 255, 0), (300, 85 + i * 80, green_width, 15))
        prompt = self.small_font.render("ENTER = set active  |  ESC = back", True, (150, 150, 150))
        screen.blit(prompt, (50, SCREEN_HEIGHT - 40))
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = min(self.selected + 1, len(party) - 1)
            elif event.key == pygame.K_UP:
                self.selected = max(self.selected - 1, 0)
            elif event.key == pygame.K_RETURN:
                # move selected member to front
                if party[self.selected].is_alive():
                    member = party.pop(self.selected)
                    party.insert(0, member)
                    self.selected = 0
                else:
                    self.message = "That party member is dead!"
            elif event.key == pygame.K_ESCAPE:
                manager.goto_scene(background)

class Dialogue(Scene):
    def __init__(self, lines, next_scene, bg_scene=None, speaker=None):
        self.current_line = 0
        self.lines = lines
        self.next_scene = next_scene
        self.bg_scene = bg_scene
        self.font = pygame.font.Font(None, 32)
        self.speaker = speaker
    def draw(self, screen):
        if self.bg_scene:
            self.bg_scene.draw(screen)
        else:
            screen.fill((0, 0, 0))
        # dark box at the bottom
        box_height = 120
        box_y = SCREEN_HEIGHT - box_height
        pygame.draw.rect(screen, (20, 20, 20), (10, box_y, SCREEN_WIDTH - 20, box_height))
        pygame.draw.rect(screen, (255, 255, 255), (10, box_y, SCREEN_WIDTH - 20, box_height), 2)
        # text inside the box
        text = self.font.render(self.lines[self.current_line], True, (255, 255, 255))
        # prompt
        prompt = self.font.render("SPACE >", True, (150, 150, 150))
        screen.blit(prompt, (SCREEN_WIDTH - 120, box_y + box_height - 35))
        if self.speaker:
            # name tab above the box
            tab_width = max(len(self.speaker) * 14 + 20, 120)
            pygame.draw.rect(screen, (40, 40, 50), (10, box_y - 30, tab_width, 30))
            pygame.draw.rect(screen, (255, 255, 255), (10, box_y - 30, tab_width, 30), 2)
            name = self.font.render(self.speaker, True, (255, 255, 0))
            screen.blit(name, (20, box_y - 25))
            # main text
            text = self.font.render(self.lines[self.current_line], True, (255, 255, 255))
            screen.blit(text, (30, box_y + 20))
        else:
            text = self.font.render(self.lines[self.current_line], True, (255, 255, 255))
            screen.blit(text, (30, box_y + 20))
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.current_line += 1
            if self.current_line >= len(self.lines):
                manager.goto_scene(self.next_scene)




background = Background()


title = Title()
manager = SceneManager(title)
intro = Dialogue(dialogue_data["wendy_intro"], background)
sam_joins = Dialogue(dialogue_data["sam_joins"], background, bg_scene=background)
partymenu = PartyMenu()




running = True
while running:
    for event in pygame.event.get():
        manager.handle_event(event)
        if event.type == pygame.QUIT:
            running = False

    manager.update()
    manager.draw(screen)
    pygame.display.flip()       # show the frame
    clock.tick(60)              # cap at 60 frames/sec
pygame.quit()