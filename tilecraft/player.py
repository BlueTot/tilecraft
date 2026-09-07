import sys
import math
import pygame

from tilecraft import ASSETS_DIR, VERSION
from .constants import Context, RandomNumberGenerator, Item
from .generation import Tile, UndergroundGeneratePortal, OverworldGeneratePortal
from .inventory import Inventory, Armour, SmallCraftingInterface, CraftingTableInterface, FurnaceInterface, EnchantingTable, Compressor, Grindstone, HoldingItem
from .player_info import HealthBar, HungerBar, Experience
from .world import TilecraftWorld

HUNGER_DECREMENT = 512

#Player Class and Methods
class Player:
    def __init__(self, context: Context, rng: RandomNumberGenerator, world: TilecraftWorld):
        self.world = world

        self.advancements = []
        self.image = pygame.Surface((32, 32))  # Create Player Image
        self.image.fill((255, 0, 0))  # Fill Player Red
        self.rect = pygame.Rect((359, 359), (32, 32))  # Create Player Rect
        self.x = 0  # Set Starting X Coordinate
        self.y = 0  # Set Starting Y Coordinate
        self.actualX = 0
        self.actualY = 0
        self.dimension = "Overworld"
        self.regenerate_val = False
        self.regenerate_start_time = 180
        self.debug_menu = False
        self.direction = 'East'
        self.direction_list = ['North', 'East', 'South', 'West']
        self.target = [1, 0]
        self.breaking_time = 0
        self.mouse_button = 1
        self.isBreaking = False
        self.canEnterPortal = True
        self.isShifting = False
        self.breaking_delay = 0
        self.isInstantMining = False

        self.rng = rng    

        #TO PREVENT PLAYERS FROM SPAWNING INSIDE A TREE OR BOULDER
        while True: #Infinite loop
            if world.Tiles[(self.x, self.y)].tile != "Air": #If tile that player spawns in is not air
                self.x += 1 #increase x by 1
            else:
                break #tile is air so the loop ends

        self.health = 20
        self.health_bar = HealthBar()
        
        self.hunger = 20
        self.hunger_bar = HungerBar()

        self.experience = Experience()

        self.distance = 0  # Set Distance Travelled
        self.dead = False
        self.hunger_subtracted = 0

        self.backdrop = pygame.Rect((30, 592), (697, 30))  # Set Background for Hunger and Health Bar

        # inventory
        self.inventory = Inventory()
        self.waiting_list = []
        self.selected_slot = 'slot1'

        self.armour = Armour() # armour
        self.craft_interface = SmallCraftingInterface() # small crafting grid
        self.crafting_grid = CraftingTableInterface() # crafting table
        self.furnace = FurnaceInterface(context) # furnace interface
        self.enchanting_table = EnchantingTable() # enchanting table interface
        self.compressor = Compressor() # compressor interface
        self.grindstone = Grindstone() # grindstone interface
        self.holding_item = HoldingItem()


    # Hunger mechanism to decrease hunger as distance travelled increases
    def hunger_mechanism(self):
        if self.hunger > 0 and self.distance != 0 and self.distance // HUNGER_DECREMENT != self.hunger_subtracted:
            self.hunger -= 1
            self.hunger_subtracted += 1

    #Update Health and Regeneration
    def health_update(self, frame_count: int):
        if self.hunger >= 17 and self.health < 20 and frame_count % 16 == 0:
            self.hunger -= 1
            self.health += 1
        if self.hunger == 0 and frame_count % 16 == 0:
            self.health -= 1
        if self.health == 0:
            self.dead = True
        if self.regenerate_val and self.health < 20:
            if self.regenerate_start_time < 60:
                if frame_count % 5 == 0:
                    self.health += 1
                self.regenerate_start_time += 1
            else:
                self.regenerate_val = False

    # remove items that shouldn't be there
    def remove_items(self):
        all_lists = [self.enchanting_table.items, self.inventory.items, self.craft_interface.items,
                    self.crafting_grid.items, self.furnace.items, self.compressor.items, self.grindstone.items]
        for i in all_lists:
            for j in range(len(i)):
                if i[j] is not None:
                    if i[j].number <= 0:
                        i[j] = None
                    elif i[j].durability is not None:
                        if i[j].durability <= 0:
                            i[j] = None
        self.enchanting_table.items, self.inventory.items, self.craft_interface.items, \
        self.crafting_grid.items, self.furnace.items, self.compressor.items, self.grindstone.items = all_lists
        if self.holding_item.item is not None:
            if self.holding_item.item.number <= 0:
                self.holding_item.item = None
            elif self.holding_item.item.durability is not None:
                if self.holding_item.item.durability <= 0:
                    self.holding_item.item = None

    def collide(self): #Collisions with tiles
        self.canMove = True
        try:
            if self.dimension == "Overworld": #Overworld dimension
                call = False
                for key, value in self.world.Tiles.items():
                    if -32 <= (key[0] * 32 - self.left) <= 1032 and -32 <= (key[1] * 32 - self.top) <= 1032: #in render distance
                        if pygame.Rect((self.x * 32, self.y * 32, 32, 32)).colliderect(pygame.Rect((key[0] * 32, key[1] * 32, 32, 32))): #collision
                            if not (value.tile == "Air" or value.tile == "Mine Entrance"): #collision with tile
                                self.canMove = False
                            elif value.tile == "Mine Entrance" and self.canEnterPortal: #enter portal
                                self.canEnterPortal = False
                                self.dimension = "Underground"
                                self.x = value.x
                                self.y = value.y
                                if self.world.is_underground_generated:
                                    try:
                                        if self.world.UndergroundTiles[(round(self.x), round(self.y))].tile != "Mine Entrance":
                                            self.world.UndergroundTiles = UndergroundGeneratePortal(round(self.x), round(self.y), self.world.UndergroundTiles)
                                    except KeyError:
                                        self.world.generate_chunks(self.dimension)
                                        self.world.UndergroundTiles = UndergroundGeneratePortal(round(self.x), round(self.y), self.world.UndergroundTiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
            elif self.dimension == "Underground" and self.world.is_underground_generated: #Underground dimension
                call = False
                for key, value in self.world.UndergroundTiles.items():
                    if -32 <= (key[0] * 32 - self.left) <= 1032 and -32 <= (key[1] * 32 - self.top) <= 1032: #in render distance
                        if pygame.Rect((self.x * 32, self.y * 32, 32, 32)).colliderect(pygame.Rect((key[0] * 32, key[1] * 32, 32, 32))): #collision
                            if not (value.tile == "Air" or value.tile == "Mine Entrance"): #collision with tile
                                self.canMove = False
                            elif value.tile == "Mine Entrance" and self.canEnterPortal: #enter portal
                                self.canEnterPortal = False
                                self.dimension = "Overworld"
                                self.x = value.x
                                self.y = value.y
                                try:
                                    if self.world.Tiles[(round(self.x), round(self.y))].tile != "Mine Entrance":
                                        self.world.Tiles = OverworldGeneratePortal(round(self.x), round(self.y), self.world.Tiles)
                                except KeyError:
                                    self.world.generate_chunks(self.dimension)
                                    self.world.Tiles = OverworldGeneratePortal(round(self.x), round(self.y), self.world.Tiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
        except KeyError:
            self.world.generate_chunks(self.dimension)
        return self.canMove

    #Player Move Keybinds
    def move(self):
        # Position calculation
        self.left = self.x * 32 - 359
        self.right = self.x * 32 + 391
        self.bottom = self.y * 32 + 391
        self.top = self.y * 32 - 359
        self.ScreenLeft = self.x * 32 - 359
        self.ScreenRight = self.x * 32 + 391
        self.ScreenBottom = self.y * 32 + 391
        self.ScreenTop = self.y * 32 - 359

        key = pygame.key.get_pressed() #Get Keyboard Input (Press Key)
        mods = pygame.key.get_mods()
        self.pastX = self.x
        self.pastY = self.y
        if mods & pygame.KMOD_SHIFT:
            self.isShifting = True
        else:
            self.isShifting = False

        if key[pygame.K_w]: #Forwards
            if key[pygame.K_r]: #Sprinting
                if self.direction == 'North':
                    self.y -= 5 / 16
                elif self.direction == 'East':
                    self.x += 5 / 16
                elif self.direction == 'South':
                    self.y += 5 / 16
                elif self.direction == 'West':
                    self.x -= 5 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y -= 1 / 16
                    elif self.direction == 'East':
                        self.x += 1 / 16
                    elif self.direction == 'South':
                        self.y += 1 / 16
                    elif self.direction == 'West':
                        self.x -= 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
            else: #Not Sprinting
                if self.direction == 'North':
                    self.y -= 3 / 16
                elif self.direction == 'East':
                    self.x += 3 / 16
                elif self.direction == 'South':
                    self.y += 3 / 16
                elif self.direction == 'West':
                    self.x -= 3 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y -= 1 / 16
                    elif self.direction == 'East':
                        self.x += 1 / 16
                    elif self.direction == 'South':
                        self.y += 1 / 16
                    elif self.direction == 'West':
                        self.x -= 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
        elif key[pygame.K_s]: #Backwards
            if key[pygame.K_r]: #Sprinting
                if self.direction == 'North':
                    self.y += 5 / 16
                elif self.direction == 'East':
                    self.x -= 5 / 16
                elif self.direction == 'South':
                    self.y -= 5 / 16
                elif self.direction == 'West':
                    self.x += 5 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y += 1 / 16
                    elif self.direction == 'East':
                        self.x -= 1 / 16
                    elif self.direction == 'South':
                        self.y -= 1 / 16
                    elif self.direction == 'West':
                        self.x += 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
            else: #Not Sprinting
                if self.direction == 'North':
                    self.y += 3 / 16
                elif self.direction == 'East':
                    self.x -= 3 / 16
                elif self.direction == 'South':
                    self.y -= 3 / 16
                elif self.direction == 'West':
                    self.x += 3 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y += 1 / 16
                    elif self.direction == 'East':
                        self.x -= 1 / 16
                    elif self.direction == 'South':
                        self.y -= 1 / 16
                    elif self.direction == 'West':
                        self.x += 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
        if self.direction == 'North':
            self.target = [math.floor(self.x + 0.5), math.floor(self.y) - 1] #Target tile in north direction
        elif self.direction == 'East':
            self.target = [math.ceil(self.x) + 1, math.floor(self.y + 0.5)] #Target tile in east direction
        elif self.direction == 'South':
            self.target = [math.floor(self.x + 0.5), math.ceil(self.y) + 1] #Target tile in south direction
        elif self.direction == 'West':
            self.target = [math.floor(self.x) - 1, math.floor(self.y + 0.5)] #Target tile in west direction
        try:
            if self.dimension == "Overworld":
                if self.world.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and self.world.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    self.world.Tiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
            elif self.dimension == "Underground" and self.world.is_underground_generated:
                if self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
        except KeyError:
            self.world.generate_chunks(self.dimension)


    def place_tile(self): #Place tiles
        if self.isShifting: #is shifting = can edit background tiles
            if self.dimension == "Overworld": #Overworld background tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Open space to place tile
                        self.world.UnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1]) #Place tile
                        self.inventory.hotbar_item.number -= 1 #Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None #Remove from inventory
            elif self.dimension == "Underground": #Underground background tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
        else:
            if self.dimension == "Overworld": #Overworld Collision tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.Tiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.Tiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.Tiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.Tiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
            elif self.dimension == "Underground": #Underground Collision Tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory

    def breaking(self, fps: float): #Breaking process of tile
        if self.breaking_delay == 0:
            if self.isShifting: #can edit background tiles
                if self.dimension == "Overworld": #Overworld background tiles
                    tile = self.world.UnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None: #Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * 30) >= 1:
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground background tiles
                    tile = self.world.UndergroundUnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
            else:
                if self.dimension == "Overworld": #Overworld collision tiles
                    tile = self.world.Tiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground collision tiles
                    tile = self.world.UndergroundTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7

    def break_add_item(self, value, fps: float):
        if not self.isInstantMining:
            self.breaking_delay = fps * 3/10
        if self.dimension == "Overworld":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    self.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    self.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    self.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    self.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    self.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    self.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        self.inventory.add(Item("Flint", 1, None, None))
                    else:
                        self.inventory.add(Item("Gravel", 1, None, None))
                else:
                    self.inventory.add(Item(value.tile, 1, None, None))
        elif self.dimension == "Underground":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    self.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    self.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    self.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    self.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    self.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    self.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        self.inventory.add(Item("Flint", 1, None, None))
                    else:
                        self.inventory.add(Item("Gravel", 1, None, None))
                else:
                    self.inventory.add(Item(value.tile, 1, None, None))
        if self.inventory.hotbar_item is not None:
            if self.inventory.hotbar_item.durability is not None:
                if self.inventory.hotbar_item.enchantments is not None:
                    for i in self.inventory.hotbar_item.enchantments:
                        if i[0] == "Unbreaking":
                            if self.rng.next_random(1, i[1] + 1) == 1:
                                self.inventory.hotbar_item.durability -= 1
                            break
                    else:
                        self.inventory.hotbar_item.durability -= 1
                else:
                    self.inventory.hotbar_item.durability -= 1

    def break_tile(self, value, fps: float):
        if self.isShifting:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UndergroundUnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
        else:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.Tiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UndergroundTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])

    def pick_up_liquid(self): #Picking up liquids with a bucket
        if self.dimension == "Overworld": #Overworld
            if self.isShifting: #Background tiles
                if self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Water": #Wate
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision tiles
                if self.world.Tiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1],)
                elif self.world.Tiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
        elif self.dimension == "Underground": #Underground
            if self.isShifting: #Background Tiles
                if self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision Tiles
                if self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])

    def place_liquid(self):
        if self.dimension == "Overworld":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
        elif self.dimension == "Underground":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])

    def render(self, context: Context, display: pygame.Surface, screen_width: int, screen_height: int, fps: float):

        if self.breaking_delay > 0:
            self.breaking_delay -= 1
        else:
            self.breaking_delay = 0

        # DRAW BACKDROP FOR HUNGER AND HEALTH BARS
        pygame.draw.rect(display, (255, 255, 255), self.backdrop)

        # DRAW PLAYER
        display.blit(self.image, (self.rect.x, self.rect.y))
        if self.direction == 'North':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (375, 359), width=4)
        elif self.direction == 'East':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (391, 375), width=4)
        elif self.direction == 'South':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (375, 391), width=4)
        elif self.direction == 'West':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (359, 375), width=4)

        # render health and hunger bars
        self.health_bar.render(display, context, self.health)
        self.hunger_bar.render(display, context, self.hunger)

        # RENDER DEBUG MENU
        if self.debug_menu:
            font9 = pygame.font.Font(
                str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
            version = font9.render(f"Tilecraft {VERSION}", True, (0, 0, 0), (255, 255, 255))
            display.blit(version, (0, 0))
            python_version = font9.render(f"Python {sys.version[0:6]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(python_version, (0, 25))
            pygame_version = font9.render(f"Graphics: pygame {pygame.version.ver}", True, (0, 0, 0), (255, 255, 255))
            display.blit(pygame_version, (0, 50))
            display_size = font9.render(f"Display Size: {screen_width}x{screen_height}", True, (0, 0, 0), (255, 255, 255))
            display.blit(display_size, (0, 75))
            SEEDs = font9.render(f"Seed: {self.world.seed}", True, (0, 0, 0), (255, 255, 255))
            display.blit(SEEDs, (0, 100))
            fps_font = font9.render(f"FPS: {fps:.2f}", True, (0, 0, 0), (255, 255, 255))
            display.blit(fps_font, (0, 125))
            Direction = font9.render(f"Facing: {self.direction}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Direction, (0, 150))
            Target = font9.render(f"Target Tile: {self.target[0]}, {self.target[1]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Target, (0, 175))
            Coords = font9.render(f"X: {round(self.x, 3)}, Y: {round(self.y, 3)}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Coords, (0, 200))
