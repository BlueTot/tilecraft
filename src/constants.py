from dataclasses import dataclass
from typing import Optional
import pygame

class Button:
    def __init__(self, length, width, x, y, colour):
        self.length = length
        self.width = width
        self.x = x
        self.y = y
        self.colour = colour
        self.rect = pygame.Rect((x, y), (length, width))

    def render(self, display, text, size):
        self.font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', size)
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


# Create crafting recipes
CRAFTING_RECIPES = {
    "OakPlanks_recipe" : Recipe(
        ["Oak Log", None, None,
        None, None, None,
        None, None, None], Item("Oak Planks", 4, None, ITEM_TYPES["Oak Planks"].max_durability)),
    "Stick_recipe" : Recipe(
        ["Oak Planks", None, None,
        "Oak Planks", None, None,
        None, None, None], Item("Stick", 5, None, ITEM_TYPES["Stick"].max_durability)),
    "CraftingTable_recipe" : Recipe(
        ["Oak Planks", "Oak Planks", None,
        "Oak Planks", "Oak Planks", None,
        None, None, None], Item("Crafting Table", 1, None, ITEM_TYPES["Crafting Table"].max_durability)),
    "WoodenPickaxe_recipe" : Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
        None, "Stick", None,
        None, "Stick", None], Item("Wooden Pickaxe", 1, None, ITEM_TYPES["Wooden Pickaxe"].max_durability)),
    "WoodenAxe_recipe" : Recipe(
        [None, "Oak Planks", "Oak Planks",
        None, "Stick", "Oak Planks",
        None, "Stick", None], Item("Wooden Axe", 1, None, ITEM_TYPES["Wooden Axe"].max_durability)),
    "WoodenShovel_recipe" : Recipe(
        [None, "Oak Planks", None,
        None, "Stick", None,
        None, "Stick", None], Item("Wooden Shovel", 1, None, ITEM_TYPES["Wooden Shovel"].max_durability)),
    "WoodenHoe_recipe" : Recipe(
        [None, "Oak Planks", "Oak Planks",
        None, "Stick", None,
        None, "Stick", None], Item("Wooden Hoe", 1, None, ITEM_TYPES["Wooden Hoe"].max_durability)),
    "MineEntrance_recipe" : Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
        "Cobblestone", "Wooden Pickaxe", "Cobblestone",
        "Cobblestone", "Cobblestone", "Cobblestone"], Item("Mine Entrance", 1, None, ITEM_TYPES["Mine Entrance"].max_durability)),
    "StonePickaxe_recipe" : Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
        None, "Stick", None,
        None, "Stick", None], Item("Stone Pickaxe", 1, None, ITEM_TYPES["Stone Pickaxe"].max_durability)),
    "StoneAxe_recipe" : Recipe(
        [None, "Cobblestone", "Cobblestone",
        None, "Stick", "Cobblestone",
        None, "Stick", None], Item("Stone Axe", 1, None, ITEM_TYPES["Stone Axe"].max_durability)),
    "StoneShovel_recipe" : Recipe(
        [None, "Cobblestone", None,
        None, "Stick", None,
        None, "Stick", None], Item("Stone Shovel", 1, None, ITEM_TYPES["Stone Shovel"].max_durability)),
    "StoneHoe_recipe" : Recipe(
        [None, "Cobblestone", "Cobblestone",
        None, "Stick", None,
        None, "Stick", None], Item("Stone Hoe", 1, None, ITEM_TYPES["Stone Hoe"].max_durability)),
    "Furnace_recipe" : Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
        "Cobblestone", None, "Cobblestone",
        "Cobblestone", "Cobblestone", "Cobblestone"], Item("Furnace", 1, None, ITEM_TYPES["Furnace"].max_durability)),
    "Compressor_recipe" : Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
        "Cobblestone", "Iron Ingot", "Cobblestone",
        "Cobblestone", "Cobblestone", "Cobblestone"], Item("Compressor", 1, None, ITEM_TYPES["Compressor"].max_durability)),
    "Grindstone_recipe" : Recipe(
        ["Stick", "Cobblestone", "Stick",
        "Oak Planks", None, "Oak Planks",
        None, None, None], Item("Grindstone", 1, None, ITEM_TYPES["Grindstone"].max_durability)),
    "IronPickaxe_recipe" : Recipe(
        ["Iron Ingot", "Iron Ingot", "Iron Ingot",
        None, "Stick", None,
        None, "Stick", None], Item("Iron Pickaxe", 1, None, ITEM_TYPES["Iron Pickaxe"].max_durability)),
    "IronAxe_recipe" : Recipe(
        [None, "Iron Ingot", "Iron Ingot",
        None, "Stick", "Iron Ingot",
        None, "Stick", None], Item("Iron Axe", 1, None, ITEM_TYPES["Iron Axe"].max_durability)),
    "IronShovel_recipe" : Recipe(
        [None, "Iron Ingot", None,
        None, "Stick", None,
        None, "Stick", None], Item("Iron Shovel", 1, None, ITEM_TYPES["Iron Shovel"].max_durability)),
    "IronHoe_recipe" : Recipe(
        [None, "Iron Ingot", "Iron Ingot",
        None, "Stick", None,
        None, "Stick", None], Item("Iron Hoe", 1, None, ITEM_TYPES["Iron Hoe"].max_durability)),
    "Bucket_recipe" : Recipe(
        [None, None, None,
        "Iron Ingot", None, "Iron Ingot",
        None, "Iron Ingot", None], Item("Bucket", 1, None, ITEM_TYPES["Bucket"].max_durability)),
    "Shield_recipe" : Recipe(
        ["Oak Planks", "Iron Ingot", "Oak Planks",
        "Oak Planks", "Oak Planks", "Oak Planks",
        None, "Oak Planks", None], Item("Shield", 1, None, ITEM_TYPES["Shield"].max_durability)),
    "FlintAndSteel_recipe" : Recipe(
        ["Iron Ingot", None, None,
        None, "Flint", None,
        None, None, None], Item("Flint and Steel", 1, None, ITEM_TYPES["Flint and Steel"].max_durability)),
    "Tier1IronPlate_recipe" : Recipe(
        [None, "Iron Plate", None,
        None, None, None,
        None, "Iron Plate", None], Item("Tier 1 Iron Plate", 1, None, ITEM_TYPES["Tier 1 Iron Plate"].max_durability)),
    "Tier2IronPlate_recipe" : Recipe(
        [None, "Iron Plate", None,
        "Iron Plate", None, "Iron Plate",
        None, "Iron Plate", None], Item("Tier 2 Iron Plate", 1, None, ITEM_TYPES["Tier 2 Iron Plate"].max_durability)),
    "Tier3IronPlate_recipe" : Recipe(
        ["Iron Plate", "Iron Plate", "Iron Plate",
        "Iron Plate", None, "Iron Plate",
        "Iron Plate", "Iron Plate", "Iron Plate"], Item("Tier 3 Iron Plate", 1, None, ITEM_TYPES["Tier 3 Iron Plate"].max_durability)),
    "DiamondPickaxe_recipe" : Recipe(
        ["Diamond", "Diamond", "Diamond",
        None, "Stick", None,
        None, "Stick", None], Item("Diamond Pickaxe", 1, None, ITEM_TYPES["Diamond Pickaxe"].max_durability)),
    "DiamondAxe_recipe" : Recipe(
        [None, "Diamond", "Diamond",
        None, "Stick", "Diamond",
        None, "Stick", None], Item("Diamond Axe", 1, None, ITEM_TYPES["Diamond Axe"].max_durability)),
    "DiamondShovel_recipe" : Recipe(
        [None, "Diamond", None,
        None, "Stick", None,
        None, "Stick", None], Item("Diamond Shovel", 1, None, ITEM_TYPES["Diamond Shovel"].max_durability)),
    "DiamondHoe_recipe" : Recipe(
        [None, "Diamond", "Diamond",
        None, "Stick", None,
        None, "Stick", None], Item("Diamond Hoe", 1, None, ITEM_TYPES["Diamond Hoe"].max_durability)),
    "Tier1DiamondPlate_recipe" : Recipe(
        [None, "Diamond Plate", None,
        None, None, None,
        None, "Diamond Plate", None], Item("Tier 1 Diamond Plate", 1, None, ITEM_TYPES["Tier 1 Diamond Plate"].max_durability)),
    "Tier2DiamondPlate_recipe" : Recipe(
        [None, "Diamond Plate", None,
        "Diamond Plate", None, "Diamond Plate",
        None, "Diamond Plate", None], Item("Tier 2 Diamond Plate", 1, None, ITEM_TYPES["Tier 2 Diamond Plate"].max_durability)),
    "Tier3DiamondPlate_recipe" : Recipe(
        ["Diamond Plate", "Diamond Plate", "Diamond Plate",
        "Diamond Plate", None, "Diamond Plate",
        "Diamond Plate", "Diamond Plate", "Diamond Plate"], Item("Tier 3 Diamond Plate", 1, None, ITEM_TYPES["Tier 3 Diamond Plate"].max_durability)),
    "Jukebox_recipe" : Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
        "Oak Planks", "Diamond", "Oak Planks",
        "Oak Planks", "Oak Planks", "Oak Planks"], Item("Jukebox", 1, None, ITEM_TYPES["Jukebox"].max_durability)),
    "EnchantingTable_recipe" : Recipe(
        [None, "Book", None,
        "Diamond", "Obsidian", "Diamond",
        "Obsidian", "Obsidian", "Obsidian"], Item("Enchanting Table", 1, None, ITEM_TYPES["Enchanting Table"].max_durability)),
    "Bookshelf_recipe" : Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
        "Book", "Book", "Book",
        "Oak Planks", "Oak Planks", "Oak Planks"], Item("Bookshelf", 1, None, ITEM_TYPES["Bookshelf"].max_durability)),
    "Bread_recipe" : Recipe(
        ["Hay Bale", None, None,
        None, None, None,
        None, None, None], Item("Bread", 3, None, ITEM_TYPES["Bread"].max_durability)),
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

