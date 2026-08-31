import math
import pygame

from .constants import RandomNumberGenerator, Context, TILE_IMAGE_MAPPING
from .generation import OverworldGeneratedList, OverworldGenerate, SpawnOverworldGenerate, SpawnOverworldBoundGenerate, UndergroundGeneratedList, SpawnUndergroundGenerate, UndergroundGenerate, NetherGeneratedList, SpawnNetherGenerate, SpawnNetherBoundGenerate, NetherGenerate

class TilecraftWorld:
    """
        World map of tiles and structures
    """
    def __init__(self, rng: RandomNumberGenerator, seed: int):
        self.empty_vil1 = []
        self.empty_vil2 = []
        self.empty_vil3 = []
        self.empty_vil4 = []
        self.empty_vil_total = []
        self.bastion = []
        self.bound_bastion = []
        self.fortress = []
        self.bound_fortress = []
        self.empty_bastion = []
        self.overworld_portal = []
        self.bound_overworld_portal = []
        self.nether_portal = []
        self.bound_nether_portal = []
        self.empty_ruined_portal1 = []
        self.empty_ruined_portal2 = []
        self.empty_ruined_portal_total = []
        self.seed = seed #World Seed
        self.is_underground_generated = False
        self.is_nether_generated = False
        self.rng = rng

        self.village, self.ruined_portal, self.obsidian_counts, \
        self.UnderTiles, self.Tiles = SpawnOverworldGenerate(self.rng, self.seed)  # Spawn Generation for Structures and Biomes
        self.bound_village, self.bound_ruined_portal = SpawnOverworldBoundGenerate(self.village, self.ruined_portal)  # Spawn Bounding Box Generation
        self.bound_village2 = self.bound_village.copy()
        self.bound_village3 = self.bound_village.copy()
        self.bound_village4 = self.bound_village.copy()
        self.bound_ruined_portal2 = self.bound_ruined_portal.copy()
        self.overworld_generated_list = OverworldGeneratedList()

    #Generate Chunks Per Frame
    def generate_chunks(self, player_dimension: str):
        if player_dimension == 'Overworld':
            for i in self.render_list:
                if i not in self.overworld_generated_list:
                    self.village, self.ruined_portal, self.obsidian_counts, self.overworld_generated_list, \
                    self.bound_village, self.bound_village2, self.bound_village3, self.bound_village4, self.bound_ruined_portal, self.bound_ruined_portal2, self.UnderTiles, self.Tiles = \
                    OverworldGenerate(self.rng, i[0], i[1], self.village, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4,
                                                      self.bound_ruined_portal, self.bound_ruined_portal2, self.seed, self.UnderTiles, self.Tiles)
        elif player_dimension == "Underground" and self.is_underground_generated:
            for i in self.render_list:
                if i not in self.UndergroundGeneratedList:
                    self.UndergroundUnderTiles, self.UndergroundTiles = UndergroundGenerate(self.rng, self.seed, i[0], i[1], self.UndergroundUnderTiles, self.UndergroundTiles, self.UndergroundGeneratedList)
        elif player_dimension == 'Nether':
            for i in self.render_list:
                if i not in self.nether_generated_list:
                    self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion = NetherGenerate(self.rng, i[0], i[1], self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion, self.seed)

    #Calculate Render List Per Frame
    def render_chunks(self, left, right, top, bottom):
        self.render_list = []
        self.render_blocks_list = []
        left_chunk = math.floor(left / 32) // 16 * 16
        right_chunk = math.floor(right / 32) // 16 * 16
        top_chunk = math.floor(top / 32) // 16 * 16
        bottom_chunk = math.floor(bottom / 32) // 16 * 16
        for i in range(left_chunk, right_chunk + 1, 16):
            for j in range(top_chunk, bottom_chunk + 1, 16):
                self.render_list.append([i, j])
        for i in range(left_chunk, right_chunk + 1):
            for j in range(top_chunk, bottom_chunk + 1):
                self.render_blocks_list.append([i, j])

    #Generate Underground for the first time
    def generateUnderground(self):
        self.UndergroundUnderTiles, self.UndergroundTiles = SpawnUndergroundGenerate(self.rng, self.seed)
        self.UndergroundGeneratedList = UndergroundGeneratedList()

    # Generate nether for the first time
    def generateNether(self, player_x: float, player_y: float):
        if self.is_nether_generated:
            return

        self.is_nether_generated = True

        # Initialise nether portal bounding box
        self.bound_nether_portal = []
        self.bastion, self.fortress = SpawnNetherGenerate(self.rng, self.seed)
        self.bound_bastion, self.bound_fortress = SpawnNetherBoundGenerate(self.bastion, self.fortress)
        self.nether_generated_list = NetherGeneratedList(player_x, player_y)

    def render(self, display, context: Context, player_dimension: str, player_left: int, player_top: int, player_rect: pygame.Rect, player_breaking_time: float, player_target: tuple[int, int]):

        def tile_image(tile_name: str) -> pygame.Surface:
            return context.TILE_IMAGES[TILE_IMAGE_MAPPING[tile_name].alpha_image_name]

        # DRAW OVERWORLD DIMENSION
        if player_dimension == "Overworld":
            for key, value in self.UnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                    else:
                        display.blit(context.TILE_IMAGES["bedrock_tile"], (value.x * 32 - player_left, value.y * 32 - player_top))
                    pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            for key, value in self.Tiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                        pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            # DRAWING OVERWORLD STRUCTURES
            for k in range(len(self.village)):
                if -32 <= (self.village[k][0] * 32 - player_left) <= 1032 and -32 <= (self.village[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (255, 165, 0), (self.village[k][0] * 32 - player_left, self.village[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.ruined_portal)):
                if -32 <= (self.ruined_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.ruined_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (56, 0, 89), (self.ruined_portal[k][0] * 32 - player_left, self.ruined_portal[k][1] * 32 - player_top), 10, 10)

            # DRAWING OVERWORLD EMPTY STRUCTURES
            for k in range(len(self.empty_vil_total)):
                if -32 <= (self.empty_vil_total[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_vil_total[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (153, 102, 0), (self.empty_vil_total[k][0] * 32 - player_left, self.empty_vil_total[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.empty_ruined_portal_total)):
                if -32 <= (self.empty_ruined_portal_total[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_ruined_portal_total[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (255, 255, 255), (self.empty_ruined_portal_total[k][0] * 32 - player_left, self.empty_ruined_portal_total[k][1] * 32 - player_top), 12, 12)
            # DRAWING OVERWORLD NETHER PORTALS
            for k in range(len(self.overworld_portal)):
                if -32 <= (self.overworld_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.overworld_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (128, 0, 128), (self.overworld_portal[k][0] * 32 - player_left, self.overworld_portal[k][1] * 32 - player_top), 10, 10)

        #DRAW UNDERGROUND DIMENSION
        elif player_dimension == "Underground" and self.is_underground_generated:
            for key, value in self.UndergroundUnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                    else:
                        display.blit(context.ITEM_IMAGES["bedrock_tile"], (value.x * 32 - player_left, value.y * 32 - player_top))
                    pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            for key, value in self.UndergroundTiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                        pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline

        # DRAW NETHER DIMENSION
        elif player_dimension == "Nether":
            # DRAWING NETHERRACK TEXTURES
            for k in range(player_rect.x - 384, player_rect.x + 384, 24):
                for j in range(player_rect.y - 384, player_rect.y + 384, 24):
                    display.blit(context.ITEM_IMAGES["netherrack_tile"], (k, j))
            # DRAWING NETHER NETHER PORTALS
            for k in range(len(self.nether_portal)):
                if -32 <= (self.nether_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.nether_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (128, 0, 128), (self.nether_portal[k][0] * 32 - player_left, self.nether_portal[k][1] * 32 - player_top), 10, 10)
            # DRAWING NETHER STRUCTURES
            for k in range(len(self.fortress)):
                if -32 <= (self.fortress[k][0] * 32 - player_left) <= 1032 and -32 <= (self.fortress[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (134, 71, 71), (self.fortress[k][0] * 32 - player_left, self.fortress[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.bastion)):
                if -32 <= (self.bastion[k][0] * 32 - player_left) <= 1032 and -32 <= (self.bastion[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (218, 165, 32), (self.bastion[k][0] * 32 - player_left, self.bastion[k][1] * 32 - player_top), 10, 10)
            # DRAWING NETHER EMPTY STRUCTURES
            for k in range(len(self.empty_bastion)):
                if -32 <= (self.empty_bastion[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_bastion[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (0, 0, 0), (self.empty_bastion[k][0] * 32 - player_left, self.empty_bastion[k][1] * 32 - player_top), 10, 10)

        # DRAW BREAKING ANIMATION
        if 1 <= math.floor(player_breaking_time) <= 6:
            display.blit(context.BREAKING_LIST[math.floor(player_breaking_time) - 1], (player_target[0] * 32 - player_left, player_target[1] * 32 - player_top))
        pygame.draw.rect(display, (50, 50, 50), (player_target[0] * 32 - player_left, player_target[1] * 32 - player_top, 32, 32), 1)  # Draw target block outline
