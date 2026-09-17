from __future__ import annotations

from typing import Optional
import pygame
import math

from tilecraft import ASSETS_DIR
from .constants import Coordinate, Item, Context, ITEM_IMAGE_MAPPING, CRAFTING_RECIPES, RandomNumberGenerator, Button
from .player_info import Experience


def DurabilityBar(durability, max_durability):
    durabilityPercent = math.floor((durability / max_durability) * 100)
    if durabilityPercent == 100:
        return None
    elif 75 < durabilityPercent <= 99:
        return "#00ff00"
    elif 50 < durabilityPercent <= 75:
        return "#ffff00"
    elif 25 < durabilityPercent <= 50:
        return "#ff8000"
    elif 5 < durabilityPercent <= 25:
        return "#ff0000"
    elif 0 < durabilityPercent <= 5:
        return "#000000"

def RenderDurabilityBar(display, x, y, durability, max_durability):
    colour = DurabilityBar(durability, max_durability)
    if colour is not None:
        pygame.draw.rect(display, (0, 0, 0), (x + 5, y + 72, 72, 5))
        pygame.draw.rect(display, colour, (x + 5, y + 72, math.floor(72 * durability / max_durability), 5))


class HoldingItem:
    def __init__(self):
        self.item: Optional[Item] = None
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)

    def render(self, display: pygame.Surface, context: Context):

        if self.item is None:
            image = context.ITEM_IMAGES["none_img"]
            number = ''
        else:
            image = context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[self.item.name]]
            number = str(self.item.number)

        if self.item is not None:
            if self.item.number == 1:
                number = ''

        x, y = pygame.mouse.get_pos()

        if self.item is not None:
            display.blit(image, (x, y))
            display.blit(self.__font.render(number, False, (255, 255, 255)), (x + 52, y + 52))
            if self.item.enchantments is not None:
                display.blit(context.TC_GLINTS[self.item.name], (x, y))
            if self.item.durability is not None:
                RenderDurabilityBar(display, x, y, self.item.durability, self.item.max_durability)


class Inventory:
    """
        Player's inventory consists of 36 slots, the last 9 slots belong to the hotbar
    """

    def __init__(self):
        self.items = [None]*36
        self.full = False
        self.__selected_hotbar = 0
    
    @property
    def selected_hotbar(self):
        return self.__selected_hotbar

    @selected_hotbar.setter
    def selected_hotbar(self, index: int):
        self.__selected_hotbar = index

    @property
    def hotbar_item(self) -> Optional[Item]:
        return self.items[self.__selected_hotbar + 27]

    @hotbar_item.setter
    def hotbar_item(self, item: Optional[Item]) -> None:
        self.items[self.__selected_hotbar + 27] = item

    #add items to inventory
    def add(self, item: Item):
        self.full = True

        # TEST FOR FULL INVENTORY
        for i in self.items:
            if i is None:
                self.full = False
                break
        if self.full:
            # temporarily do not print to screen
            print("Your inventory is nearly full or is already full. New items added may be lost.")
        # Add items to inventory and combine into singular stacks (if stackable)
        if item is not None:
            if item.stackNum == 64:
                Call = False
                for j in range(len(self.items)):
                    if self.items[j] is not None:
                        if item.name == self.items[j].name and self.items[j].number < 64:
                            self.items[j] = Item(self.items[j].name, item.number + self.items[j].number, self.items[j].enchantments, self.items[j].durability) #Add values
                            Call = True
                            break
                if not Call:
                    for j in range(len(self.items)):
                        if self.items[j] is None:
                            self.items[j] = item
                            break
            elif item.stackNum == 1:
                for j in range(len(self.items)):
                    if self.items[j] is None:
                        self.items[j] = item
                        break

        # Separate Items into stacks (Armour = Stack of 1), (Item = Stack of 64)
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].stackNum == 1 and self.items[i].number > 1:  # Armour
                    count = 0
                    while count < self.items[i].number:  # Separate into individual items
                        if None in self.items:
                            none_index = self.items.index(None)
                            self.items[none_index] = Item(self.items[i].name, 1, self.items[i].enchantments, self.items[i].durability)
                        count += 1
                    self.items[i] = None
                elif self.items[i].stackNum == 64 and self.items[i].number > 64:  # Item
                    while self.items[i].number > 64:  # Separate into stacks of 64
                        self.items[i].number -= 64
                        if None in self.items:
                            none_index = self.items.index(None)
                            self.items[none_index] = Item(self.items[i].name, 64, self.items[i].enchantments, self.items[i].durability)
                    if None in self.items:  # Remainder (Less than 64)
                        none_index = self.items.index(None)
                        self.items[none_index] = Item(self.items[i].name, self.items[i].number, self.items[i].enchantments, self.items[i].durability)
                        self.items[i] = None


class Armour:
    """
        Player's armour items consist of four slots:
        1) tier 1 plate, 2) tier 2 plate, 3) tier 3 plate, 4) shield
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*4


class SmallCraftingInterface:
    """
        2x2 small crafting grid in the player's inventory
        consists of four cells and one result cell
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*5


    def update(self):
        """
            Update attempts to craft an item from the ingredients
        """
        if self.items[0] is not None and self.items[1] is None and self.items[2] is None and self.items[3] is None:
            if self.items[0].name == 'Oak Log':
                self.items[4] = Item("Oak Planks", 4, None, None)
            else:
                self.items[4] = None
        elif self.items[0] is not None and self.items[1] is None and self.items[2] is not None and self.items[3] is None:
            if self.items[0].name == 'Oak Planks' and self.items[2].name == 'Oak Planks':
                self.items[4] = Item("Stick", 4, None, None)
            else:
                self.items[4] = None
        elif self.items[0] is not None and self.items[1] is not None and self.items[2] is not None and self.items[3] is not None:
            if self.items[0].name == 'Oak Planks' and self.items[1].name == 'Oak Planks' and self.items[2].name == 'Oak Planks' and self.items[3].name == 'Oak Planks':
                self.items[4] = Item("Crafting Table", 1, None, None)
            else:
                self.items[4] = None
        elif self.items[0] is not None and self.items[1] is None and self.items[2] is None and self.items[3] is not None:
            if self.items[0].name == 'Iron Ingot' and self.items[3].name == 'Flint':
                self.items[4] = Item("Flint and Steel", 1, None, None)
            else:
                self.items[4] = None
        else:
            self.items[4] = None


class CraftingTableInterface:
    """
        3x3 crafting grid in the crafting table interface
        Consists of 9 crafting slots and 1 result slot
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*10


    def update(self):
        for recipe in CRAFTING_RECIPES.values():
            if recipe.canCraft(self.items):
                recipe.craft(self.items)
                return
            else:
                self.items[9] = None


class FurnaceInterface:
    """
        Smelting interrface in the inventory screen
        Consists of a fuel slot, item slot, and result slot
    """
    def __init__(self, context: Context):

        self.items: list[Optional[Item]] = [None]*3
        self.fuel_val = 0
        self.fuel_img = context.ITEM_IMAGES["no_fire"]
        self.smelting_time = 0


    def smelt(self, context: Context, fps: float, experience: Experience):
        """
            Progress smelting an item by one tick
        """

        # Load Fuel
        if self.items[1] is not None:
            if self.items[1].name == "Coal" and self.fuel_val == 0:
                self.items[1] = Item(self.items[1].name, self.items[1].number - 1, self.items[1].enchantments, self.items[1].durability)
                self.fuel_val = 8

        # Smelting Process
        if self.items[0] is not None:
            if self.items[0].name == "Iron Ore" and self.fuel_val > 0:
                self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time >= 5 * fps:
            self.smelting_time = 0
            self.items[0] = Item(self.items[0].name, self.items[0].number - 1, self.items[0].enchantments, self.items[0].durability)
            self.fuel_val -= 1
            if self.items[2] is None:
                self.items[2] = Item("Iron Ingot", 1, None, None)
                experience.add_points(12)
            else:
                self.items[2] = Item("Iron Ingot", self.items[2].number + 1, None, None)
                experience.add_points(12)

        # Render Fire
        if self.fuel_val > 0:
            self.fuel_img = context.ITEM_IMAGES["fire"]
        else:
            self.fuel_img = context.ITEM_IMAGES["no_fire"]


class EnchantingTable:
    def __init__(self):
        self.items: list[Optional[Item]] = [None]*3
        self.option_list = ['', '', '']
        self.enchanting_level = 0
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.optional_enchant2 = None
        self.optional_enchant3 = None

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)

        self.upgrade = Button(82, 82, 112, 142, (158, 145, 115))
        self.option1 = Button(487, 82, 255, 75, (158, 145, 115))
        self.option2 = Button(487, 82, 255, 157, (158, 145, 115))
        self.option3 = Button(487, 82, 255, 240, (158, 145, 115))

        self.__CELLS: list[pygame.Rect] = [
            pygame.Rect((30, 225), (82, 82)),
            pygame.Rect((112, 225), (82, 82)),
            pygame.Rect((30, 142), (82, 82))
        ]

        self.__NUMBERS: list[Coordinate] = [
            Coordinate(82, 277),
            Coordinate(165, 277),
            Coordinate(82, 195)
        ]

        self.__RECTS: list[pygame.Rect] = [
            self.__CELLS[0], self.__CELLS[1], self.__CELLS[2], 
            self.upgrade.rect, self.option1.rect, self.option2.rect, self.option3.rect
        ]


    def enchant_set(self, rng: RandomNumberGenerator):
        if self.items[0] is not None:
            if self.items[0].enchantments is None:
                self.level1 = 0
                self.level2 = 0
                self.level3 = 0
                self.optional_enchant2 = None
                self.optional_enchant3 = None
                if self.enchanting_level == 0:  # LEVEL 0
                    self.level1 = 0
                    self.level2 = 0
                    self.level3 = rng.next_random(0, 1)
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 1:  # LEVEL 1
                    self.level1 = 1
                    self.level2 = rng.next_random(1, 2)
                    self.level3 = 2
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 2:  # LEVEL 2
                    self.level1 = 2
                    self.level2 = rng.next_random(2, 3)
                    self.level3 = 3
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 3:  # LEVEL 3
                    self.level1 = 3
                    self.level2 = rng.next_random(3, 4)
                    self.level3 = 4
                    self.optional_enchant2 = None
                    self.optional_enchant3 = rng.next_random(0, 1)
                elif self.enchanting_level == 4:  # LEVEL 4
                    self.level1 = 4
                    self.level2 = rng.next_random(4, 5)
                    self.level3 = 5
                    self.optional_enchant2 = rng.next_random(0, 1)
                    self.optional_enchant3 = rng.next_random(1, 2)
                else:  # LEVEL 5
                    self.level1 = rng.next_random(4, 5)
                    self.level2 = 5
                    self.level3 = 5
                    self.optional_enchant2 = rng.next_random(1, 2)
                    self.optional_enchant3 = rng.next_random(2, 3)

                if self.items[0].itemType == 'Tier1' or self.items[0].itemType == 'Tier2' or self.items[0].itemType == 'Tier3':  # Armour
                    self.option_list[0] = f'Protection {self.level1}'
                    self.option_list[1] = f'Protection {self.level2}'
                    self.option_list[2] = f'Protection {self.level3}'
                elif self.items[0].itemType == 'Pickaxe' or self.items[0].itemType == 'Axe' or self.items[0].itemType == 'Shovel' or self.items[0].itemType == 'Hoe':  # Tools
                    self.option_list[0] = f'Efficiency {self.level1}'
                    self.option_list[1] = f'Efficiency {self.level2}'
                    self.option_list[2] = f'Efficiency {self.level3}'
                for i in range(len(self.option_list)):
                    if self.option_list[i] == 'Protection 0' or self.option_list[i] == 'Efficiency 0':
                        self.option_list[i] = 'N/A'
            else:
                self.option_list[0] = self.option_list[1] = self.option_list[2] = ''
        else:
            self.option_list[0] = self.option_list[1] = self.option_list[2] = ''


    def enchant_upgrade(self, rng: RandomNumberGenerator):
        if self.items[2] is not None and self.enchanting_level < 5:
            if self.items[2].name == 'Bookshelf' and self.items[2].number > 3:
                self.items[2].number -= 4
                self.enchanting_level += 1
                self.enchant_set(rng)  # Set Enchants


    def enchant1(self, rng: RandomNumberGenerator, experience: Experience):  # First ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, no extras)
        if self.items[1] is not None:
            if self.items[1].number > 0 and experience.levels > 0:  # REQUIRE 1 Lapis + 1 Experience
                if self.option_list[0] != 'N/A' and self.items[0] is not None:
                    self.items[0] = Item(
                        self.items[0].name, 
                        self.items[0].number, 
                        [
                            [self.option_list[0][0:-2], int(self.option_list[0][-1])]
                        ], 
                        self.items[0].number
                    )
                    self.items[1].number -= 1
                    experience.subtract(1)
                    self.enchant_set(rng)  # Remove Enchants


    def enchant2(self, rng: RandomNumberGenerator, experience: Experience):  # Second ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2)
        if self.items[1] is not None:
            if self.items[1].number > 1 and experience.levels > 1:  # REQUIRE 2 Lapis + 2 Experience
                if self.option_list[1] != 'N/A' and self.items[0] is not None:  # Test for None
                    if self.optional_enchant2 is not None:  # Extra enchantment
                        if self.optional_enchant2 > 0:  # Enchantment level > 0
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[1][0:-2], int(self.option_list[1][-1])], 
                                    ['Unbreaking', self.optional_enchant2]
                                ],
                                self.items[0].durability
                            )
                        else:  # No extra enchantment
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[1][0:-2], int(self.option_list[1][-1])]
                                ], 
                                self.items[0].durability
                            )
                    else:
                        self.items[0] = Item(
                            self.items[0].name, 
                            self.items[0].number, 
                            [
                                [self.option_list[1][0:-2], int(self.option_list[1][-1])]
                            ], 
                            self.items[0].durability
                        )
                    self.items[1].number -= 2
                    experience.subtract(2)
                    self.enchant_set(rng)  # Remove Enchants


    def enchant3(self, rng: RandomNumberGenerator, experience: Experience):  # Third ENCHANTING BOX (ENCHANTS start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3)
        if self.items[1] is not None:
            if self.items[1].number > 2 and experience.levels > 2:  # REQUIRE 3 Lapis + 3 Experience
                if self.option_list[2] != 'N/A' and self.items[0] is not None:  # Test for None
                    if self.optional_enchant3 is not None:  # Extra enchantment
                        if self.optional_enchant3 > 0:  # Enchantment level > 0
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[2][0:-2], int(self.option_list[2][-1])], 
                                    ['Unbreaking', self.optional_enchant3]
                                ],
                                self.items[0].durability
                            )
                        else:  # No extra enchantment
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[2][0:-2], int(self.option_list[2][-1])]
                                ], 
                                self.items[0].durability
                            )
                    else:  # No extra enchantment
                        self.items[0] = Item(
                            self.items[0].name, 
                            self.items[0].number, 
                            [
                                [self.option_list[2][0:-2], int(self.option_list[2][-1])]
                            ], 
                            self.items[0].durability
                        )
                    self.items[1].number -= 3
                    experience.subtract(3)
                    self.enchant_set(rng)  # Remove Enchants

    # interface method?
    def get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__RECTS):
            if rect.collidepoint(mouse):
                return i
        return None

    # interface method?
    def handle_left_click(self, mouse: tuple[int, int], holding_item: HoldingItem, experience: Experience, rng: RandomNumberGenerator) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        # regular cells
        if index >= 0 and index < 3:
            if holding_item.item is not None and self.items[index] is not None: #Items can be combined
                if holding_item.item.name == self.items[index].name and (self.items[index].number + holding_item.item.number <= holding_item.item.stackNum):
                    self.items[index].number += holding_item.item.number
                    holding_item.item = None
                else:
                    holding_item.item, self.items[index] = self.items[index], holding_item.item
            else:
                holding_item.item, self.items[index] = self.items[index], holding_item.item
            if index == 0:
                self.enchant_set(rng)

        # upgrade button
        elif index == 3:
            self.enchant_upgrade(rng)

        # option 1
        elif index == 4:
            self.enchant1(rng, experience)

        # option 2
        elif index == 5:
            self.enchant2(rng, experience)

        # option 3
        elif index == 6:
            self.enchant3(rng, experience)

    # interface method?
    def handle_right_click(self, mouse: tuple[int, int], holding_item: HoldingItem) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        if index >= 3: # cannot right click on buttons
            return

        if holding_item.item is None:
            return

        if self.items[index] is None:
            self.items[index] = Item(holding_item.item.name, 1, holding_item.item.enchantments, holding_item.item.durability)
            holding_item.item.number -= 1
        elif self.items[index] is not None and self.items[index].name == holding_item.item.name and (self.items[index].number + 1 <= self.items[index].stackNum):
            self.items[index].number += 1
            holding_item.item.number -= 1

    def render(self, display: pygame.Surface, context: Context, mouse: tuple[int, int], is_holding: bool):

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 0:
                    self.items[i] = None

        # Convert List to Images and Numbers
        for item in self.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 1:
                    numbers[i] = ''

        for i, cell in enumerate(self.__CELLS):
            display.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(display, (83, 83, 83), cell, 2)
            if self.items[i] is not None:
                if self.items[i].enchantments is not None:
                    display.blit(context.TC_GLINTS[self.items[i].name], (cell.x, cell.y))
                if self.items[i].durability is not None:
                    RenderDurabilityBar(display, cell.x, cell.y, self.items[i].durability, self.items[i].max_durability)

        for i, coordinate in enumerate(self.__NUMBERS):
            surface = self.__font.render(str(numbers[i]), False, (255, 255, 255))
            display.blit(surface, (coordinate.x, coordinate.y))

        display.blit(self.__font.render(f'Enchanting Table LEVEL {self.enchanting_level}', False, (0, 0, 0)), (0, 0))

        self.upgrade.render(display, 'Upgrade', 21)
        self.option1.render(display, self.option_list[0], 30)
        self.option2.render(display, self.option_list[1], 30)
        self.option3.render(display, self.option_list[2], 30)

        if not is_holding:
            self.render_hovering_label(display, mouse)

    def render_hovering_label(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.get_hover_box(mouse)) is None:
            return

        if index >= 3: # buttons are out of bounds
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.items[index], mouse[0], mouse[1], font) 


class Compressor:
    def __init__(self):
        self.items: list[Optional[Item]] = [None, None]
        self.compressor_image_list = []
        self.compressor_number_list = []
        self.compressing_time = 0

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__title_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 40)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 45)
        self.__side_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 36)

        self.__CELLS: list[pygame.Rect] = [
            pygame.Rect((225, 142), (82, 82)),
            pygame.Rect((450, 142), (82, 82))
        ]

        self.__NUMBERS: list[Coordinate] = [
            Coordinate(277, 195),
            Coordinate(502, 195)
        ]

    def compress(self, fps: float):

        #Compressing Process
        if self.items[0] is not None:
            if self.items[0].number >= 2:
                if self.items[0].name == 'Iron Ingot':
                    if self.items[1] is not None:
                        if self.items[1].name == 'Iron Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
                elif self.items[0].name == 'Diamond':
                    if self.items[1] is not None:
                        if self.items[1].name == 'Diamond Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
        else:
            self.compressing_time = 0

        #Finish Compressing Item
        if self.compressing_time >= 5 * fps:
            self.compressing_time = 0
            self.items[0] = Item(self.items[0].name, self.items[0].number - 2, self.items[0].enchantments, self.items[0].durability)
            if self.items[1] is None:
                if self.items[0].name == 'Iron Ingot':
                    self.items[1] = Item("Iron Plate", 1, None, None)
                elif self.items[0].name == 'Diamond':
                    self.items[1] = Item("Diamond Plate", 1, None, None)
            else:
                if self.items[0].name == 'Iron Ingot' and self.items[1].name == 'Iron Plate':
                    self.items[1] = Item("Iron Plate", self.items[1].number + 1, None, None)
                elif self.items[0].name == 'Diamond' and self.items[1].name == 'Diamond Plate':
                    self.items[1] = Item("Diamond Plate", self.items[1].number + 1, None, None)

    # interface method?
    def get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__CELLS):
            if rect.collidepoint(mouse):
                return i
        return None

    # interface method?
    def handle_left_click(self, mouse: tuple[int, int], holding_item: HoldingItem, inventory: Inventory) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        # input box
        if index != 1:
            if holding_item.item is not None and self.items[index] is not None: #Items can be combined
                if holding_item.item.name == self.items[index].name and (self.items[index].number + holding_item.item.number <= holding_item.item.stackNum):
                    self.items[index].number += holding_item.item.number
                    holding_item.item = None
                else:
                    holding_item.item, self.items[index] = self.items[index], holding_item.item
            else:
                holding_item.item, self.items[index] = self.items[index], holding_item.item

        # result index
        else:
            inventory.add(self.items[1])
            self.items[1] = None

    # interface method?
    def handle_right_click(self, mouse: tuple[int, int], holding_item: HoldingItem) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        if index == 1: # cannot right click on result box
            return

        if holding_item.item is None:
            return

        if self.items[index] is None:
            self.items[index] = Item(holding_item.item.name, 1, holding_item.item.enchantments, holding_item.item.durability)
            holding_item.item.number -= 1
        elif self.items[index] is not None and self.items[index].name == holding_item.item.name and (self.items[index].number + 1 <= self.items[index].stackNum):
            self.items[index].number += 1
            holding_item.item.number -= 1

    def render(self, display: pygame.Surface, context: Context, mouse: tuple[int, int], fps: float, is_holding: bool):

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 0:
                    self.items[i] = None

        for item in self.items:
            if item is None: #Set Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 1:
                    numbers[i] = ''

        display.blit(self.__title_font.render('Compressor', False, (0, 0, 0)), (262, 0))
        
        for i, cell in enumerate(self.__CELLS):
            display.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(display, (83, 83, 83), cell, 2)
            if self.items[i] is not None:
                if self.items[i].enchantments is not None:
                    display.blit(context.TC_GLINTS[self.items[i].name], (cell.x, cell.y))
                if self.items[i].durability is not None:
                    RenderDurabilityBar(display, cell.x, cell.y, self.items[i].durability, self.items[i].max_durability)

        
        for i, coordinate in enumerate(self.__NUMBERS):
            surface = self.__font.render(numbers[i], False, (255, 255, 255))
            display.blit(surface, (coordinate.x, coordinate.y))

        display.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (337, 172))  # Render Arrow
        display.blit(self.__side_font.render(f"{int(self.compressing_time / fps)}", False, (255, 0, 0)), (360, 142))  # Render Time to Compress

        if not is_holding:
            self.render_hovering_item(display, mouse)

    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.items[index], mouse[0], mouse[1], font) 


class Grindstone:
    def __init__(self):
        self.items: list[Optional[Item]] = [None, None, None]

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__title_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 35)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 45)

        self.__CELLS: list[pygame.Rect] = [
            pygame.Rect((225, 87), (82, 82)),
            pygame.Rect((225, 177), (82, 82)),
            pygame.Rect((475, 133), (82, 82))
        ]

        self.__NUMBERS: list[Coordinate] = [
            Coordinate(277, 139),
            Coordinate(277, 229),
            Coordinate(527, 185)
        ]


    def repair_and_disenchant(self):
        if self.items[0] is not None and self.items[1] is None:
            if self.items[0].enchantments is not None:
                self.items[2] = Item(self.items[0].name, self.items[0].number, None, self.items[0].durability)
                return
        elif self.items[0] is not None and self.items[1] is not None:
            if self.items[0].durability is not None and self.items[1].durability is not None:
                if self.items[0].name == self.items[1].name:
                    total_durability = self.items[0].durability + self.items[1].durability
                    if total_durability > self.items[0].max_durability:
                        total_durability = self.items[0].max_durability
                    self.items[2] = Item(self.items[0].name, self.items[0].number, None, total_durability)
                    return
        self.items[2] = None


    def disenchant(self, experience: Experience):
        enchantments = self.items[0].enchantments
        for i in enchantments:
            experience.add_points(int(i[1]) * 8)


    # interface method?
    def get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__CELLS):
            if rect.collidepoint(mouse):
                return i
        return None


    # interface method?
    def handle_left_click(self, mouse: tuple[int, int], holding_item: HoldingItem, inventory: Inventory, experience: Experience) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        # input boxes
        if index != 2:
            if holding_item.item is not None and self.items[index] is not None:  # Items can be combined
                if holding_item.item.name == self.items[index].name and (self.items[index].number + holding_item.item.number <= holding_item.item.stackNum):
                    self.items[index].number += holding_item.item.number
                    holding_item.item = None
                else:
                    holding_item.item, self.items[index] = self.items[index], holding_item.item
            else:
                holding_item.item, self.items[index] = self.items[index], holding_item.item

        # result index
        else:
            inventory.add(self.items[2])
            if self.items[0] is not None and self.items[1] is None:
                if self.items[0].enchantments is not None:
                    self.disenchant(experience)
            self.items[0], self.items[1], self.items[2] = None, None, None


    # interface method?
    def handle_right_click(self, mouse: tuple[int, int], holding_item: HoldingItem) -> None:
        if (index := self.get_hover_box(mouse)) is None:
            return

        if index == 2: # cannot right click on results box
            return

        if holding_item.item is None:
            return

        if self.items[index] is None:
            self.items[index] = Item(holding_item.item.name, 1, holding_item.item.enchantments, holding_item.item.durability)
            holding_item.item.number -= 1
        elif self.items[index] is not None and self.items[index].name == holding_item.item.name and (self.items[index].number + 1 <= self.items[index].stackNum):
            self.items[index].number += 1
            holding_item.item.number -= 1


    def render(self, display: pygame.Surface, context: Context, mouse: tuple[int, int], is_holding: bool):

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 0:
                    self.items[i] = None

        for item in self.items:
            if item is None:  # Set Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.items)):
            if self.items[i] is not None:
                if self.items[i].number == 1:
                    numbers[i] = ''

        display.blit(self.__title_font.render("Repair & Disenchant", False, (0, 0, 0)), (90, 0))

        for i, cell in enumerate(self.__CELLS):
            display.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(display, (83, 83, 83), cell, 2)
            if self.items[i] is not None:
                if self.items[i].enchantments is not None:
                    display.blit(context.TC_GLINTS[self.items[i].name], (cell.x, cell.y))
                if self.items[i].durability is not None:
                    RenderDurabilityBar(display, cell.x, cell.y, self.items[i].durability, self.items[i].max_durability)

        for i, coordinate in enumerate(self.__NUMBERS):
            surface = self.__font.render(numbers[i], False, (255, 255, 255))
            display.blit(surface, (coordinate.x, coordinate.y))

        pygame.draw.rect(display, (0, 0, 0), (215, 77, 102, 194), 2)
        pygame.draw.rect(display, (0, 0, 0), (185, 97, 30, 194), 2)
        pygame.draw.rect(display, (0, 0, 0), (317, 97, 30, 194), 2)
        display.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (367, 152))  # Render Arrow

        if not is_holding:
            self.render_hovering_item(display, mouse)

    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.items[index], mouse[0], mouse[1], font) 


#Convert Numbers to Roman Numerals
def DecimalToRoman(num):
    num = int(num)
    nums = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    symbols = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12
    roman_value = ""
    while num:
        div = num // nums[i]
        num %= nums[i]
        while div:
            roman_value += symbols[i]
            div -= 1
        i -= 1
    return roman_value


#Info Box for Items (with and without enchantments)
def TextBox(display: pygame.Surface, item: Item, x: int, y: int, font: pygame.font.Font):
    try:
        if item is not None: #Check to prevent crashes
            length_list = [len(item.name * 15)]
            if item.enchantments is not None:
                width = (1 + len(item.enchantments)) * 37
                for i in item.enchantments:
                    length_list.append(len(str(i[0]) + DecimalToRoman(str(i[1]))) * 15)
            else:
                width = 37
            if item.durability is not None:
                width += 22
                length_list.append(len(f"Durability: {item.durability}/{item.max_durability}") * 15)
            length = max(length_list)
            if x + length > 750:
                x -= length
            if y + width > 750:
                y -= width
            pygame.draw.rect(display, (0, 0, 0), (x, y, length, width))
            display.blit(font.render(item.name, False, item.colour), (x + 15, y + 15))
            if item.durability is not None: #WITH DURABILITY
                if item.enchantments is not None:
                    for i in range(len(item.enchantments)):
                        display.blit(font.render(f'{item.enchantments[i][0]} {DecimalToRoman(item.enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
                display.blit(font.render(f"Durability: {item.durability}/{item.max_durability}", False, (175, 175, 175)), (x + 15, y + width - 20))
            else: #EVERYTHING ELSE
                if item.enchantments is not None:
                    for i in range(len(item.enchantments)):
                        display.blit(font.render(f'{item.enchantments[i][0]} {DecimalToRoman(item.enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
    except IndexError:
        pass

