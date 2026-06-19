import pygame
import json
import os
import random
from engine.fighter import Fighter
from engine.data_loader import load_characters, load_moves, load_dialogue
from engine.scene_manager import Scene, SceneManager
pygame.init()
screen = pygame.display.set_mode((800, 576))
pygame.display.set_caption("Red Box")
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 576
PLAYER_SIZE = 32
PLAYER_SPEED = 4
TILE_SIZE = 32
MAP_COLS = 50   # 25
MAP_ROWS = 36   # 18

TILE_COLORS = {
    0: (222, 184, 135),     # floor
    1: (44, 53, 74),    # wall
    3: (181, 72, 80),      # eshay fight
    101: (163, 7, 18),     # nick fight
    102: (163, 7, 18), #dev fight
    9: (222, 184, 135),      # door
}

enemies = {
    3: "random_eshay",
    101: "nick",
    102: "dev"
}
type_chart = {
    "dickhead": {"cunt": 1.5, "sket": 0.5},
    "nerd": {"sporty": 1.5, "cunt": 0.5, "sket": 0.5},
    "sporty": {"eshay": 1.5},
    "stoner": {},
    "eshay": {"nerd": 1.5, "sporty": 0.5},
    "prefect": {"cunt": 1.5, "eshay": 1.5},
    "cunt": {"nerd": 1.5, "prefect": 0.5},
    "sket": {"nerd": 1.5, "cunt": 1.5, "sporty": 1.5, "dickhead": 0.5},
    "loser": {"prefect":0.5, "stoner" : 1.5},
    "behemoth": {"sporty": 1.5, "sket": 1.5, "eshay": 1.5}
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
    elif area == "map2":
        game_map[13][0] = 0
        game_map[14][0] = 0
        game_map[15][0] = 0
        game_map[3][24] = 9
        game_map[4][24] = 9
        game_map[5][24] = 9
        game_map[10][4] = 102
    return game_map
GAME_MAP = build_map()


moves_data = load_moves()
characters = load_characters()
dialogue_data = load_dialogue()
player = Fighter(characters["player"])
skivvy = Fighter(characters["random_eshay"])


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
        text_image = self.font.render("Red Box", True, (255, 255, 255))
        screen.blit(text_image, (300, 250))
        start_button = self.small_font.render("Press Space to Start", True, (255, 255, 255))
        screen.blit(start_button, (299, 350))

class Background(Scene):
    def __init__(self):
        self.x = 64
        self.y = 64
        self.camera_x = 0
        self.camera_y = 0
    def draw(self, screen):
        screen.fill((0, 0, 0))
        for row_index, row in enumerate(GAME_MAP):
            y = row_index * TILE_SIZE - self.camera_y
            for col_index, col in enumerate(row):
                x = col_index * TILE_SIZE - self.camera_x
                color = TILE_COLORS.get(col, (50, 100, 255))
                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, (48, 54, 240), (self.x - self.camera_x, self.y - self.camera_y, PLAYER_SIZE, PLAYER_SIZE))
    def is_walkable(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        if row < 0 or row >= MAP_ROWS or col < 0 or col >= MAP_COLS:
            return False
        return GAME_MAP[row][col] != 1
    def update(self):
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
            GAME_MAP[tile_row][tile_column] = 0
            enemy = Fighter(characters[enemies[tile_value]])
            new_battle = Battle(player, enemy)
            manager.goto_scene(new_battle)

        elif tile_value == 9:
            GAME_MAP.clear()
            GAME_MAP.extend(build_map("map2"))
            self.x = TILE_SIZE
            self.y = 14 * TILE_SIZE


class Battle(Scene):
    def __init__(self, player, enemy):
        self.message = ""
        self.player = player
        self.enemy = enemy
        self.small_font = pygame.font.Font(None, 32)
        self.battle_font = pygame.font.Font(None, 24)
        self.selected = 0
        self.battle_over = False
    def draw(self, screen):
        screen.fill((32, 46, 12))
        text = self.small_font.render(f"{self.player.name} HP: {self.player.hp}", True, (255, 255, 255))
        screen.blit(text, (50, 50))
        text = self.small_font.render(f"{self.enemy.name} HP: {self.enemy.hp}", True, (255, 255, 255))
        screen.blit(text, (500, 50))
        for i, move in enumerate(self.player.moves):
            if i == self.selected:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)
            move_text = self.small_font.render(move, True, color)
            screen.blit(move_text, (50,200 + i * 40))
        text = self.battle_font.render(self.message, True, (255, 255, 255))
        screen.blit(text, (50, 460))
        if self.battle_over:
            text = self.small_font.render(self.message, True, (255, 255, 255))
            screen.blit(text, (10, 600))
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
                self.message = f"{self.player.name} used {move_name} with {damage} damage! | {self.enemy.name} used {enemy_move} with {enemy_damage} damage!"
                if not self.enemy.is_alive():
                    self.message = f"{self.enemy.name} is dead! Press SPACE to continue."
                    self.battle_over = True
                if not self.player.is_alive():
                    self.message = f"{self.player.name} is dead! Press SPACE to continue."
                    self.battle_over = True
        if self.battle_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.player.is_alive():
                    self.player.hp = characters["player"]["hp"]
                    GAME_MAP.clear()
                    GAME_MAP.extend(build_map())
                    background.x = 64
                    background.y = 64
                    manager.goto_scene(title)
                else:
                    manager.goto_scene(background)

class Dialogue(Scene):
    def __init__(self, lines, next_scene):
        self.current_line = 0
        self.lines = lines
        self.next_scene = next_scene
        self.dialogue_text = pygame.font.Font(None, 18)
    def draw(self, screen):
        screen.fill((32, 46, 12))
        text = self.dialogue_text.render(self.lines[self.current_line], True, (255, 255, 255))
        screen.blit(text, (50, 50))
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.current_line += 1
            if self.current_line >= len(self.lines):
                manager.goto_scene(self.next_scene)


background = Background()
title = Title()
manager = SceneManager(title)
intro = Dialogue(dialogue_data["wendy_intro"], background)


battle = Battle(player, skivvy)

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