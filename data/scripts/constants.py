# Constants
import pygame

# Window Data ==================================================================
WIN_RES = {"W": 600, "H": 800}
TITLE = "Avalanche Agent"
AUTHOR = "zyenapz"
VERSION = "1.0"

# Colors =======================================================================
LIGHT_GREEN = (155,188,15)
SNOW_WHITE = (245, 245, 255)

# Sprite groups ================================================================
sprites = pygame.sprite.Group()
snowballs = pygame.sprite.Group()
impacted_snowballs = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player_group = pygame.sprite.Group()