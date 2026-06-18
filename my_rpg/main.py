import pygame
import json
import os
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Red Box")
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 32
PLAYER_SPEED = 4
TILE_SIZE = 32
GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


def load_characters():
    with open("data/characters.json") as f:
        data = json.load(f)
    return data

def load_moves():
    with open("data/moves.json") as f:
        data = json.load(f)
    return data



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

moves_data = load_moves()
characters = load_characters()
reggie = Fighter(characters["reggie"])
skivvy = Fighter(characters["random_eshay"])




class Scene: #contains an even, update and draw.
    def handle_event(self, event): #  is a blank template — a contract. It lists the three things every scene must be able to do but does none of them (all pass)
        pass
    def update(self):
        pass
    def draw(self, screen):
        pass


class Title(Scene):
    def __init__(self):
        self.font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 32)
        self.battle_font = pygame.font.Font(None, 24)
    def handle_event(self, event): # title actually inherits the handle event and update methods - u only need to write it out again if its overriding it
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            print("Youve pressed the A key!")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            manager.goto_scene(background)
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
    def draw(self, screen):
        screen.fill((0, 0, 0))
        for row_index, row in enumerate(GAME_MAP):
            y = row_index * TILE_SIZE
            for col_index, col in enumerate(row):
                x = col_index * TILE_SIZE
                if col == 1:
                    pygame.draw.rect(screen, (100, 255, 255), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif col == 0:
                    pygame.draw.rect(screen, (50, 100, 255), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(screen, (200, 0, 207), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))
    def is_walkable(self, x, y):
        tile_column = x // TILE_SIZE
        tile_row = y // TILE_SIZE
        return GAME_MAP[tile_row][tile_column] != 1
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
        if self.x > SCREEN_WIDTH - PLAYER_SIZE:
            self.x = (SCREEN_WIDTH - PLAYER_SIZE)
        if self.y > SCREEN_HEIGHT - PLAYER_SIZE:
            self.y = (SCREEN_HEIGHT - PLAYER_SIZE)
        center_x = self.x + PLAYER_SIZE // 2
        center_y = self.y + PLAYER_SIZE // 2
        tile_column = center_x // TILE_SIZE
        tile_row = center_y // TILE_SIZE
        if GAME_MAP[tile_row][tile_column] == 3:
            GAME_MAP[tile_row][tile_column] = 0
            manager.goto_scene(battle)

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
        screen.fill((200, 0, 207))
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
            screen.blit(move_text, (50,300 + i * 40))
        text = self.battle_font.render(self.message, True, (255, 255, 255))
        screen.blit(text, (10, 400))
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
                damage = max((self.player.attack * moves_data[move_name]["power"]) // 10 - self.enemy.defense, 1)
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
                manager.goto_scene(background)










class SceneManager:
    def __init__(self, start_scene):
        self.current = start_scene
    def handle_event(self, event):
        self.current.handle_event(event)
    def update(self):
        self.current.update()
    def goto_scene(self, new_scene):
        self.current = new_scene
    def draw(self, screen):
        self.current.draw(screen)



title = Title()

background = Background()

manager = SceneManager(title)
battle = Battle(reggie, skivvy)

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