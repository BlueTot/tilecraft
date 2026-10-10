from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import pygame
import os

from tilecraft import ASSETS_DIR

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 750

class Button:
    def __init__(self, length, width, x, y, colour):
        self.length = length
        self.width = width
        self.x = x
        self.y = y
        self.colour = colour
        self.rect = pygame.Rect((x, y), (length, width))

    def render(self, display, text, size):
        self.font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), size)
        self.text = self.font.render(text, False, (0, 0, 0))
        pygame.draw.rect(display, self.colour, self.rect)
        pygame.draw.rect(display, (255, 255, 255), self.rect, 3)
        self.text_x = (self.length - len(text) * size) // 2
        if self.text_x < 0:
            self.text_x = 0
        self.text_y = (self.width - size) // 2
        display.blit(self.text, (self.x + self.text_x, self.y + self.text_y))

class Grid:
    def __init__(self, colour, rect, width, img):
        self.colour = colour
        self.rect = rect
        self.width = width
        self.img = img

class Text:
    def __init__(self, surface, x, y):
        self.surface = surface
        self.x = x
        self.y = y

@dataclass
class Coordinate:
    x: int
    y: int

@dataclass
class ItemType: #Class to store item details for every item in game
    type: str
    stack: int
    tier: Optional[str]
    max_durability: Optional[int]
    rarity: int

@dataclass
class TileType: #Class to store tile details for every tile type in the game
    breaking_time: Optional[int]
    tool: Optional[str]
    tier: Optional[int]

# List for Hotbar Orders
HOTBAR_ORDER = ['Hotbar1', 'Hotbar2', 'Hotbar3', 'Hotbar4', 'Hotbar5', 'Hotbar6', 'Hotbar7', 'Hotbar8', 'Hotbar9']

# Colours for all rarities
ITEM_COLOURS = { 
    1: (255, 255, 255),
    2: (0, 255, 0),
    3: (0, 0, 255),
    4: "#C71585",
    5: "#d4af37"
}

# Rarities and their levels
TC_RARITIES = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 3,
    "Epic": 4,
    "Legendary": 5
}

#Dictionary of all items in the game
ITEM_TYPES = {
    "Oak Log": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Oak Planks": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Stick": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Crafting Table": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Wooden Pickaxe": ItemType("Pickaxe", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Axe": ItemType("Axe", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Shovel": ItemType("Shovel", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Hoe": ItemType("Hoe", 1, 1, 59, TC_RARITIES["Common"]),
    "Cobblestone": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Mine Entrance": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Stone Pickaxe": ItemType("Pickaxe", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Axe": ItemType("Axe", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Shovel": ItemType("Shovel", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Hoe": ItemType("Hoe", 1, 2, 131, TC_RARITIES["Common"]),
    "Furnace": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Compressor": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Grindstone": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Coal": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Iron Ore": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Iron Ingot": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Iron Pickaxe": ItemType("Pickaxe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Axe": ItemType("Axe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Shovel": ItemType("Shovel", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Hoe": ItemType("Hoe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Bucket": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Water Bucket": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Lava Bucket": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Shield": ItemType("Shield", 1, None, 336, TC_RARITIES["Uncommon"]),
    "Flint and Steel": ItemType("Item", 1, None, 64, TC_RARITIES["Common"]),
    "Iron Plate": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Tier 1 Iron Plate": ItemType("Tier1", 1, None, 120, TC_RARITIES["Uncommon"]),
    "Tier 2 Iron Plate": ItemType("Tier2", 1, None, 240, TC_RARITIES["Uncommon"]),
    "Tier 3 Iron Plate": ItemType("Tier3", 1, None, 480, TC_RARITIES["Uncommon"]),
    "Diamond": ItemType("Item", 64, None, None, TC_RARITIES["Rare"]),
    "Diamond Pickaxe": ItemType("Pickaxe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Axe": ItemType("Axe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Shovel": ItemType("Shovel", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Hoe": ItemType("Hoe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Plate": ItemType("Item", 64, None, None, TC_RARITIES["Rare"]),
    "Tier 1 Diamond Plate": ItemType("Tier1", 1, None, 280, TC_RARITIES["Rare"]),
    "Tier 2 Diamond Plate": ItemType("Tier2", 1, None, 560, TC_RARITIES["Rare"]),
    "Tier 3 Diamond Plate": ItemType("Tier3", 1, None, 1120, TC_RARITIES["Rare"]),
    "Jukebox": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Pigstep Disc": ItemType("Item", 1, None, None, TC_RARITIES["Rare"]),
    "Obsidian": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Enchanting Table": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Book": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Bookshelf": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Lapis Lazuli": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Bread": ItemType("Food", 64, None, None, TC_RARITIES["Common"]),
    "Golden Carrot": ItemType("Food", 64, None, None, TC_RARITIES["Common"]),
    "Golden Apple": ItemType("Food", 64, None, None, TC_RARITIES["Uncommon"]),
    "Dirt": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Sand": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Snow": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Gravel": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Flint": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Bed": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Hay Bale": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
}

ITEM_IMAGE_MAPPING = {
    "Oak Log": "wood",
    "Oak Planks": "planks",
    "Stick": "stick",
    "Crafting Table": "crafting_table",
    "Wooden Pickaxe": "wooden_pickaxe",
    "Wooden Axe": "wooden_axe",
    "Wooden Shovel": "wooden_shovel",
    "Wooden Hoe": "wooden_hoe",
    "Cobblestone": "cobblestone",
    "Mine Entrance": "mine_entrance",
    "Stone Pickaxe": "stone_pickaxe",
    "Stone Axe": "stone_axe",
    "Stone Shovel": "stone_shovel",
    "Stone Hoe": "stone_hoe",
    "Furnace": "furnace",
    "Compressor": "compressor",
    "Grindstone": "grindstone",
    "Coal": "coal",
    "Iron Ore": "iron_ore",
    "Iron Ingot": "iron_ingot",
    "Iron Pickaxe": "iron_pickaxe",
    "Iron Axe": "iron_axe",
    "Iron Shovel": "iron_shovel",
    "Iron Hoe": "iron_hoe",
    "Bucket": "bucket",
    "Water Bucket": "water_bucket",
    "Lava Bucket": "lava_bucket",
    "Shield": "shield",
    "Flint and Steel": "flint_and_steel",
    "Iron Plate": "iron_plate",
    "Tier 1 Iron Plate": "tier1_iron_plate",
    "Tier 2 Iron Plate": "tier2_iron_plate",
    "Tier 3 Iron Plate": "tier3_iron_plate",
    "Diamond": "diamond",
    "Diamond Pickaxe": "diamond_pickaxe",
    "Diamond Axe": "diamond_axe",
    "Diamond Shovel": "diamond_shovel",
    "Diamond Hoe": "diamond_hoe",
    "Diamond Plate": "diamond_plate",
    "Tier 1 Diamond Plate": "tier1_diamond_plate",
    "Tier 2 Diamond Plate": "tier2_diamond_plate",
    "Tier 3 Diamond Plate": "tier3_diamond_plate",
    "Jukebox": "jukebox",
    "Pigstep Disc": "pigstep_disc",
    "Obsidian": "obsidian",
    "Enchanting Table": "enchanting_table",
    "Book": "book",
    "Bookshelf": "bookshelf",
    "Lapis Lazuli": "lapis",
    "Bread": "bread",
    "Golden Carrot": "golden_carrot",
    "Golden Apple": "golden_apple",
    "Dirt": "dirt",
    "Sand": "sand",
    "Snow": "snow",
    "Gravel": "gravel",
    "Flint": "flint",
    "Bed": "bed",
    "Hay Bale": "hay",
}

class Item: #Item in the inventory
    def __init__(self, name: str, number: int, enchantments, durability):
        self.name: str = name #Item Name
        self.number: int = number #Quantity
        self.enchantments = enchantments #Enchantments List
        self.durability = durability #Durability of tool
        # self.img = context.ITEM_TYPES[self.name].img #Image
        self.stackNum = ITEM_TYPES[self.name].stack #Stackability
        self.itemType = ITEM_TYPES[self.name].type #Type of item
        self.toolTier = ITEM_TYPES[self.name].tier #Tier of tool
        self.max_durability = ITEM_TYPES[self.name].max_durability #Maximum durability
        self.rarity = ITEM_TYPES[self.name].rarity #Rarity of item
        if self.enchantments is not None:
            self.rarity += 1
        self.colour = ITEM_COLOURS[self.rarity]
        if self.toolTier is not None:
            self.mining_speed = 2 * self.toolTier - 1 #Mining speed
        else:
            self.mining_speed = None
        if self.enchantments is not None:
            if self.mining_speed is not None:
                for i in self.enchantments:
                    if i[0] == "Efficiency":
                        self.mining_speed += i[1]**2 + 1
        if self.name == "Bookshelf" or self.name == "Cobblestone" or self.name == "Gravel" or self.name == "Hay Bale" or \
                self.name == "Iron Ore" or self.name == "Oak Log" or self.name == "Oak Planks" or self.name == "Obsidian" or \
                self.name == "Mine Entrance" or self.name == "Dirt" or self.name == "Sand" or self.name == "Snow":
            self.hasTile = True #Has a placable tile
            self.targetTile = self.name #Placable tile name
            # self.tile_img = context.TILE_TYPES[self.targetTile].img
            # self.alpha_tile_img = context.TILE_TYPES[self.targetTile].alpha_img
        else: #Item cannot be placed
            self.hasTile = False
            self.targetTile = None
            # self.tile_img = None
            # self.alpha_tile_img = None

    @classmethod
    def new(cls, name: str, number: int) -> Item:
        """
            Return a new unenchanted item with no durability
        """
        return cls(name, number, None, None)


    @classmethod
    def clone(cls, item: Item) -> Item:
        """
            Returns a copy of the item
        """
        return cls(item.name, item.number, item.enchantments, item.durability)


    def set_max_durability(self) -> Item:
        """
            Sets the item to have max durability
        """
        self.durability = ITEM_TYPES[self.name].max_durability
        return self


    def __repr__(self) -> str:
        """
            Print method
        """
        return f"Item({self.name}, {self.number}, {self.enchantments}, {self.durability})"


class Recipe:
    def __init__(self, requirements, result):
        self.requirements = requirements
        self.result = (result.name, result.number, result.enchantments, result.durability)

    def canCraft(self, crafting_grid: list[Optional[Item]]):
        for i in range(9):
            if crafting_grid[i] is not None:
                if crafting_grid[i].name != self.requirements[i]:
                    return False
            elif crafting_grid[i] != self.requirements[i]:
                return False
        return True

    def craft(self, crafting_grid: list[Optional[Item]]):
        if crafting_grid[9] != Item(self.result[0], self.result[1], self.result[2], self.result[3]):
            crafting_grid[9] = Item(self.result[0], self.result[1], self.result[2], self.result[3])

@dataclass
class TileImageEntry:
    regular_image_name: Optional[str]
    alpha_image_name: Optional[str]

TILE_IMAGE_MAPPING = {
    "Air": TileImageEntry(None, None),
    "Grass": TileImageEntry("grass_tile", "alpha_grass_tile"),
    "Netherrack": TileImageEntry("netherrack_tile", "alpha_netherrack_tile"),
    "Sand": TileImageEntry("sand_tile", "alpha_sand_tile"),
    "Snow": TileImageEntry("snow_tile", "alpha_snow_tile"),
    "Bookshelf": TileImageEntry("bookshelf_tile", "alpha_bookshelf_tile"),
    "Coal Ore": TileImageEntry("coal_ore_tile", "alpha_coal_ore_tile"),
    "Cobblestone": TileImageEntry("cobblestone_tile", "alpha_cobblestone_tile"),
    "Diamond Ore": TileImageEntry("diamond_ore_tile", "alpha_diamond_ore_tile"),
    "Dirt": TileImageEntry("dirt_tile", "alpha_dirt_tile"),
    "Gravel": TileImageEntry("gravel_tile", "alpha_gravel_tile"),
    "Hay Bale": TileImageEntry("hay_bale_tile", "alpha_hay_bale_tile"),
    "Iron Ore": TileImageEntry("iron_ore_tile", "alpha_iron_ore_tile"),
    "Lapis Ore": TileImageEntry("lapis_ore_tile", "alpha_lapis_ore_tile"),
    "Lava": TileImageEntry("lava_tile", "alpha_lava_tile"),
    "Leaf": TileImageEntry("leaf_tile", "alpha_leaf_tile"),
    "Mine Entrance": TileImageEntry("mine_entrance_tile", "alpha_mine_entrance_tile"),
    "Oak Log": TileImageEntry("oak_log_tile", "alpha_oak_log_tile"),
    "Oak Planks": TileImageEntry("oak_planks_tile", "alpha_oak_planks_tile"),
    "Obsidian": TileImageEntry("obsidian_tile", "alpha_obsidian_tile"),
    "Stone": TileImageEntry("stone_tile", "alpha_stone_tile"),
    "Tree": TileImageEntry("tree_tile", "alpha_tree_tile"),
    "Water": TileImageEntry("water_tile", "alpha_water_tile"),
}

TILE_TYPES = {
    "Air": TileType(None, None, None),
    "Grass": TileType(0.6, "Shovel", 0), 
    "Netherrack": TileType(None, None, None), 
    "Sand": TileType(0.6, "Shovel", 0), 
    "Snow": TileType(0.6, "Shovel", 0), 
    "Bookshelf": TileType(2, "Axe", 0), 
    "Coal Ore": TileType(3, "Pickaxe", 1), 
    "Cobblestone": TileType(2, "Pickaxe", 1), 
    "Diamond Ore": TileType(3, "Pickaxe", 3), 
    "Dirt": TileType(0.6, "Shovel", 0), 
    "Gravel": TileType(0.6, "Shovel", 0), 
    "Hay Bale": TileType(0.5, "Hoe", 0), 
    "Iron Ore": TileType(3, "Pickaxe", 2), 
    "Lapis Ore": TileType(3, "Pickaxe", 2), 
    "Lava": TileType(None, None, None), 
    "Leaf": TileType(0, "None", 0), 
    "Mine Entrance": TileType(2, "Pickaxe", 1), 
    "Oak Log": TileType(2, "Axe", 0), 
    "Oak Planks": TileType(2, "Axe", 0), 
    "Obsidian": TileType(50, "Pickaxe", 4), 
    "Stone": TileType(1.5, "Pickaxe", 1), 
    "Tree": TileType(2, "Axe", 0), 
    "Water": TileType(None, None, None) 
}


class RandomNumberGenerator:
    def __init__(self, initial_value: int):
        self.value = initial_value

    def next_random(self, start: int, stop: int) -> int:
        self.value = (self.value * 63) % 3301667478 #multiplication and modulo
        self.value = self.value ^ 24465343 #XOR
        self.value = (self.value * 255) % 4294967296 #multiplication and modulo
        self.value = self.value ^ 573522635 #XOR
        self.value = self.value | 78187493520 #OR
        self.value = ((self.value + 14351514) * 32) % 7777333 #addition, multplication, modulo
        return self.value % (stop - 1) + start


@dataclass
class Context:
    """
        Constants to be passed around
        Initialised after pygame is initialised
    """
    ITEM_IMAGES: dict[str, pygame.Surface]
    TC_GLINTS: dict[any, any]
    TILE_IMAGES: dict[str, pygame.Surface] 
    BREAKING_LIST: list[pygame.Surface]
    INFOBAR_IMAGES: dict[str, pygame.Surface]
    LOADING_IMAGE: pygame.Surface
    TITLE_SCREEN_IMAGE: pygame.Surface

def create_context() -> Context:

    # [EXPORT] Create PYGAME inventory images for hotbar
    ITEM_IMAGES = {
        "wood": pygame.image.load(str(ASSETS_DIR / "item_imgs/oak_log.png")).convert_alpha(), #0
        "planks": pygame.image.load(str(ASSETS_DIR / "item_imgs/oak_planks.png")).convert_alpha(), #1
        "stick": pygame.image.load(str(ASSETS_DIR / "item_imgs/stick.png")).convert_alpha(), #2
        "crafting_table": pygame.image.load(str(ASSETS_DIR / "item_imgs/crafting_table.png")).convert_alpha(), #3
        "wooden_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_pickaxe.png")).convert_alpha(), #4
        "wooden_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_axe.png")).convert_alpha(), #5
        "wooden_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_shovel.png")).convert_alpha(), #6
        "wooden_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_hoe.png")).convert_alpha(), #7
        "cobblestone": pygame.image.load(str(ASSETS_DIR / "item_imgs/cobblestone.png")).convert_alpha(), #8
        "mine_entrance": pygame.image.load(str(ASSETS_DIR / "item_imgs/mine_entrance.png")).convert_alpha(), #9
        "stone_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_pickaxe.png")).convert_alpha(), #10
        "stone_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_axe.png")).convert_alpha(), #11
        "stone_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_shovel.png")).convert_alpha(), #12
        "stone_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_hoe.png")).convert_alpha(), #13
        "furnace": pygame.image.load(str(ASSETS_DIR / "item_imgs/furnace.png")).convert_alpha(), #14
        "compressor": pygame.image.load(str(ASSETS_DIR / "item_imgs/compressor.png")).convert_alpha(), #15
        "grindstone": pygame.image.load(str(ASSETS_DIR / "item_imgs/grindstone.png")).convert_alpha(), #16
        "coal": pygame.image.load(str(ASSETS_DIR / "item_imgs/coal.png")).convert_alpha(), #17
        "iron_ore": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_ore.png")).convert_alpha(), #18
        "iron_ingot": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_ingot.png")).convert_alpha(), #19
        "iron_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_pickaxe.png")).convert_alpha(), #20
        "iron_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_axe.png")).convert_alpha(), #21
        "iron_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_shovel.png")).convert_alpha(), #22
        "iron_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_hoe.png")).convert_alpha(), #23
        "bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/bucket.png")).convert_alpha(), #24
        "water_bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/water_bucket.png")).convert_alpha(), #25
        "lava_bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/lava_bucket.png")).convert_alpha(), #26
        "shield": pygame.image.load(str(ASSETS_DIR / "item_imgs/shield.png")).convert_alpha(), #27
        "flint_and_steel": pygame.image.load(str(ASSETS_DIR / "item_imgs/flint_and_steel.png")).convert_alpha(), #28
        "iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_plate.png")).convert_alpha(), #29
        "tier1_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier1_iron_plate.png")).convert_alpha(), #30
        "tier2_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier2_iron_plate.png")).convert_alpha(), #31
        "tier3_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier3_iron_plate.png")).convert_alpha(), #32
        "diamond": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond.png")).convert_alpha(), #33
        "diamond_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_pickaxe.png")).convert_alpha(), #34
        "diamond_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_axe.png")).convert_alpha(), #35
        "diamond_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_shovel.png")).convert_alpha(), #36
        "diamond_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_hoe.png")).convert_alpha(), #37
        "diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_plate.png")).convert_alpha(), #38
        "tier1_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier1_diamond_plate.png")).convert_alpha(), #39
        "tier2_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier2_diamond_plate.png")).convert_alpha(), #40
        "tier3_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier3_diamond_plate.png")).convert_alpha(), #41
        "jukebox": pygame.image.load(str(ASSETS_DIR / "item_imgs/jukebox.png")).convert_alpha(), #42
        "pigstep_disc": pygame.image.load(str(ASSETS_DIR / "item_imgs/pigstep_disc.png")).convert_alpha(), #43
        "obsidian": pygame.image.load(str(ASSETS_DIR / "item_imgs/obsidian.png")).convert_alpha(), #44
        "enchanting_table": pygame.image.load(str(ASSETS_DIR / "item_imgs/enchanting_table.png")).convert_alpha(), #45
        "book": pygame.image.load(str(ASSETS_DIR / "item_imgs/book.png")).convert_alpha(), #46
        "bookshelf": pygame.image.load(str(ASSETS_DIR / "item_imgs/bookshelf.png")).convert_alpha(), #47
        "lapis": pygame.image.load(str(ASSETS_DIR / "item_imgs/lapis_lazuli.png")).convert_alpha(), #48
        "bread": pygame.image.load(str(ASSETS_DIR / "item_imgs/bread.png")).convert_alpha(), #49
        "golden_carrot": pygame.image.load(str(ASSETS_DIR / "item_imgs/golden_carrot.png")).convert_alpha(), #50
        "golden_apple": pygame.image.load(str(ASSETS_DIR / "item_imgs/golden_apple.png")), #51
        "dirt": pygame.image.load(str(ASSETS_DIR / "item_imgs/dirt.png")).convert_alpha(), #52
        "sand": pygame.image.load(str(ASSETS_DIR / "item_imgs/sand.png")).convert_alpha(), #53
        "snow": pygame.image.load(str(ASSETS_DIR / "item_imgs/snow.png")).convert_alpha(), #54
        "gravel": pygame.image.load(str(ASSETS_DIR / "item_imgs/gravel.png")).convert_alpha(), #55
        "flint": pygame.image.load(str(ASSETS_DIR / "item_imgs/flint.png")).convert_alpha(), #56
        "bed": pygame.image.load(str(ASSETS_DIR / "item_imgs/bed.png")).convert_alpha(), #57
        "hay": pygame.image.load(str(ASSETS_DIR / "item_imgs/hay_bale.png")).convert_alpha(), #58
        "none_img": pygame.image.load(str(ASSETS_DIR / "item_imgs/slot.png")).convert_alpha(),  # White Space
        "fire": pygame.image.load(str(ASSETS_DIR / "item_imgs/fire.png")).convert_alpha(),  # Fire when smelting
        "no_fire": pygame.image.load(str(ASSETS_DIR / "item_imgs/no_fire.png")).convert_alpha(),  # No fire when smelting
    }

    # Create GLINT images for enchanted items
    glint_list = []
    glint_fullname_list = []
    glint_num_list = []
    new_glint_name_list = []
    int_glint_num_list = []
    item_names = []
    for filename in os.listdir(str(ASSETS_DIR / "glints")):
        glint_num_list.append(filename[5:-4])
        glint_fullname_list.append(filename[:-4])
    for i in glint_num_list:
        int_glint_num_list.append(int(i))
    new_glint_num_list = sorted(int_glint_num_list)
    for i in new_glint_num_list:
        index = glint_num_list.index(str(i))
        new_glint_name_list.append(glint_fullname_list[index])
    for i in new_glint_name_list:
        image = pygame.image.load(str(ASSETS_DIR / f"glints/{i}.png")).convert_alpha()
        glint_list.append(image)
    for key in ITEM_TYPES.keys():
        item_names.append(key)

    # [EXPORT]
    TC_GLINTS = dict(zip(item_names, glint_list))

    def set_alpha(path: str) -> pygame.Surface:
        image = pygame.image.load(path).convert()
        image.set_alpha(200)
        return image

    # [EXPORT] Create Tile Images
    TILE_IMAGES = {
        "grass_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/grass.png")).convert(),  # Grass
        "netherrack_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/netherrack.png")).convert(),  # Netherrack
        "sand_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/sand.png")).convert(),  # Sand
        "snow_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/snow.png")).convert(),  # Snow
        "bookshelf_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/bookshelf_tile.png")).convert(),
        "coal_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/coal_ore_tile.png")).convert(),
        "cobblestone_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/cobblestone_tile.png")).convert(),
        "diamond_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/diamond_ore_tile.png")).convert(),
        "dirt_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/dirt_tile.png")).convert(),
        "gravel_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/gravel_tile.png")).convert(),
        "hay_bale_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/hay_bale_tile.png")).convert(),
        "iron_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/iron_ore_tile.png")).convert(),
        "lapis_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/lapis_ore_tile.png")).convert(),
        "lava_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/lava_tile.png")).convert(),
        "leaf_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/leaf.png")).convert_alpha(),
        "mine_entrance_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/mine_entrance_tile.png")).convert(),
        "oak_log_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")).convert(),
        "oak_planks_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_planks_tile.png")).convert(),
        "obsidian_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/obsidian_tile.png")).convert(),
        "stone_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/stone_tile.png")).convert(),
        "tree_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "water_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/water_tile.png")).convert(),
        "alpha_grass_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/grass.png")),  # Grass
        "alpha_netherrack_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/netherrack.png")),  # Netherrack
        "alpha_sand_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/sand.png")),  # Sand
        "alpha_snow_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/snow.png")),  # Snow
        "alpha_bookshelf_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/bookshelf_tile.png")),
        "alpha_coal_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/coal_ore_tile.png")),
        "alpha_cobblestone_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/cobblestone_tile.png")),
        "alpha_diamond_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/diamond_ore_tile.png")),
        "alpha_dirt_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/dirt_tile.png")),
        "alpha_gravel_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/gravel_tile.png")),
        "alpha_hay_bale_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/hay_bale_tile.png")),
        "alpha_iron_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/iron_ore_tile.png")),
        "alpha_lapis_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/lapis_ore_tile.png")),
        "alpha_lava_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/lava_tile.png")),
        "alpha_leaf_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/leaf.png")),
        "alpha_mine_entrance_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/mine_entrance_tile.png")),
        "alpha_oak_log_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "alpha_oak_planks_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_planks_tile.png")),
        "alpha_obsidian_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/obsidian_tile.png")),
        "alpha_stone_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/stone_tile.png")),
        "alpha_tree_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "alpha_water_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/water_tile.png")),
        "bedrock_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/bedrock.png")),
    }

    # [EXPORT] Create Breaking Images
    BREAKING_LIST = [
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking1.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking2.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking3.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking4.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking5.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking6.png")).convert_alpha()
    ]

    # [EXPORT]
    INFOBAR_IMAGES = {
        "full_heart" : pygame.image.load(str(ASSETS_DIR / "FullHeart_20x20.png")).convert(),  # Full Heart (2)
        "half_heart" : pygame.image.load(str(ASSETS_DIR / "half_heart_20x20.png")).convert(),  # Half Heart (1)
        "empty_heart" : pygame.image.load(str(ASSETS_DIR / "empty_heart_20x20.png")).convert(),  # Empty Heart (0)
        "full_hunger" : pygame.image.load(str(ASSETS_DIR / "hunger_20x20.png")),  # Full Hunger (2)
        "half_hunger" : pygame.image.load(str(ASSETS_DIR / "half_hunger_20x20.png")),  # Half Hunger (1)
        "empty_hunger" : pygame.image.load(str(ASSETS_DIR / "empty_hunger_20x20.png")),  # Empty Hunger (0)
        "slot": pygame.image.load(str(ASSETS_DIR / "item_imgs/slot.png")).convert(),
        "experience_bar": pygame.image.load(str(ASSETS_DIR / "item_imgs/experience.png")).convert(),
    }

    # [EXPORT]
    loading = pygame.image.load(str(ASSETS_DIR / "loading.png")).convert()

    # [EXPORT]
    title_screen_image = pygame.image.load(str(ASSETS_DIR / "background_vB1_0_pre3.png"))

    context = Context(
        ITEM_IMAGES = ITEM_IMAGES,
        TC_GLINTS = TC_GLINTS,
        TILE_IMAGES = TILE_IMAGES,
        BREAKING_LIST = BREAKING_LIST,
        INFOBAR_IMAGES = INFOBAR_IMAGES,
        LOADING_IMAGE = loading,
        TITLE_SCREEN_IMAGE = title_screen_image,
    )

    # return context to be passed around
    return context