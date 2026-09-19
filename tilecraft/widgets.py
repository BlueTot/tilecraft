from typing import Optional
import math
import sys
import pygame

from tilecraft import ASSETS_DIR, VERSION
from .constants import Context, Coordinate, Item, ITEM_IMAGE_MAPPING, SCREEN_WIDTH, SCREEN_HEIGHT, Button
from .player_info import Health, Hunger, Experience
from .inventory import Inventory, HoldingItem, Armour, SmallCraftingInterface, CraftingTableInterface, FurnaceInterface, EnchantingTable, Compressor, Grindstone 
from .game_state import GameState
from .ui.widget import Widget


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


class InventoryWidget(Widget):
    """
        Reusable widget that renders the player's inventory slots
        Each cell is fixed to 82x82 pixels (for now)
    """

    COLOUR = (83, 83, 83)
    WIDTH = 2
    NUMBER_OFFSET_X = 54
    NUMBER_OFFSET_Y = 52
    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, holding_item: HoldingItem):
        self.inventory = inventory
        self.holding_item = holding_item
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)

        self.__inventory_slots: list[pygame.Rect] = [None]*36
        for row in range(4):
            for col in range(9):
                index = row*9 + col
                self.__inventory_slots[index] = pygame.Rect(
                    (x + self.CELL_SIZE*col, y + self.CELL_SIZE*row), 
                    (self.CELL_SIZE, self.CELL_SIZE)
                )

        self.__number_coordinates: list[Coordinate] = [None]*36
        for row in range(4):
            for col in range(9):
                index = row*9 + col
                self.__number_coordinates[index] = Coordinate(
                    x + self.NUMBER_OFFSET_X + self.CELL_SIZE*col, 
                    y + self.NUMBER_OFFSET_Y + self.CELL_SIZE*row
                )


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: #1
                self.__hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.__hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.__hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.__hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.__hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.__hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.__hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.__hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.__hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__inventory_slots):
            if rect.collidepoint(mouse):
                return i
        return None


    def __hotbar_swap(self, mouse: tuple[int, int], key_pressed: int) -> None:
        """
            Switch items in inventory straight to hotbar
        """
        if (index := self.__get_hover_box(mouse)) is None:
            return
        self.inventory.items[key_pressed + 26], self.inventory.items[index] = self.inventory.items[index], self.inventory.items[key_pressed + 26]


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if self.holding_item.item is not None and self.inventory.items[index] is not None:
            if self.holding_item.item.name == self.inventory.items[index].name and (self.inventory.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum): #Items can be combined
                self.inventory.items[index].number += self.holding_item.item.number
                self.holding_item.item = None
            else:
                self.holding_item.item, self.inventory.items[index] = self.inventory.items[index], self.holding_item.item
        else:
            self.holding_item.item, self.inventory.items[index] = self.inventory.items[index], self.holding_item.item


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if self.holding_item.item is None:
            return

        if self.inventory.items[index] is None:
            self.inventory.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.inventory.items[index] is not None and self.inventory.items[index].name == self.holding_item.item.name and (self.inventory.items[index].number + 1 <= self.inventory.items[index].stackNum):
            self.inventory.items[index].number += 1
            self.holding_item.item.number -= 1


    def render(self, surface: pygame.Surface, context: Context):
        """
            Render inventory widget to screen
        """

        mouse = pygame.mouse.get_pos()

        images = [None]*36
        numbers = ['']*36

        # Remove Values with 0
        for i in range(len(self.inventory.items)):
            if self.inventory.items[i] is not None:
                if self.inventory.items[i].number == 0:
                    self.inventory.items[i] = None

        # Create images list and number list
        for i, item in enumerate(self.inventory.items):
            if item is None:  # Set White Background for NONE Slots
                images[i] = context.ITEM_IMAGES["none_img"]
                numbers[i] = ''
            else:
                images[i] = context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]]
                numbers[i] = str(item.number)

        # Remove Value if Number is 1
        for i in range(len(self.inventory.items)):
            if self.inventory.items[i] is not None:
                if self.inventory.items[i].number == 1:
                    numbers[i] = ''

        # draw images
        for i, cell in enumerate(self.__inventory_slots):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, self.COLOUR, cell, self.WIDTH)
            if self.inventory.items[i] is not None:
                if self.inventory.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.inventory.items[i].name], (cell.x, cell.y))
                if self.inventory.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.inventory.items[i].durability, self.inventory.items[i].max_durability)

        # draw numbers
        for i, coordinate in enumerate(self.__number_coordinates):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        """
            Render the item description for the item being hovered over (if not None)
        """
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.inventory.items[index], mouse[0], mouse[1], font) 


class ArmourWidget(Widget):
    """
        Widget to render the player's armour items and a small model of the player
    """

    CELL_SIZE = 82
    
    def __init__(self, x: int, y: int, armour: Armour, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.armour = armour
        self.holding_item = holding_item

        self.__cells: list[pygame.Rect] = []
        for i in range(4):
            self.__cells.append(pygame.Rect((self.x + self.CELL_SIZE*i, self.y + 240), (self.CELL_SIZE, self.CELL_SIZE)))


    def handle_event(self, event):
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 0: #Tier 1
            if self.holding_item.item is not None and self.armour.items[index] is None:
                if self.holding_item.item.itemType == 'Tier1':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is None and self.armour.items[index] is not None:
                self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is not None and self.armour.items[index] is not None:
                if self.holding_item.item.itemType == 'Tier1' and self.armour.items[index].itemType == 'Tier1':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item

        elif index == 1: #Tier 2
            if self.holding_item.item is not None and self.armour.items[index] is None:
                if self.holding_item.item.itemType == 'Tier2':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is None and self.armour.items[index] is not None:
                self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is not None and self.armour.items[index] is not None:
                if self.holding_item.item.itemType == 'Tier2' and self.armour.items[index].itemType == 'Tier2':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item

        elif index == 2: #Tier 3
            if self.holding_item.item is not None and self.armour.items[index] is None:
                if self.holding_item.item.itemType == 'Tier3':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is None and self.armour.items[index] is not None:
                self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is not None and self.armour.items[index] is not None:
                if self.holding_item.item.itemType == 'Tier3' and self.armour.items[index].itemType == 'Tier3':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item

        elif index == 3: #Shield
            if self.holding_item.item is not None and self.armour.items[index] is None:
                if self.holding_item.item.itemType == 'Shield':
                    self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item
            elif self.holding_item.item is None and self.armour.items[index] is not None:
                self.holding_item.item, self.armour.items[index] = self.armour.items[index], self.holding_item.item


    def render(self, surface: pygame.Surface, context: Context):
        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        layer_list = []

        # Create armour image list for armour slots
        for item in self.armour.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])

        for item in self.armour.items:
            if item is not None:
                if item.name == 'Tier 1 Iron Plate':
                    layer_list.append([(200, 200, 200), 1])
                elif item.name == 'Tier 2 Iron Plate':
                    layer_list.append([(200, 200, 200), 2])
                elif item.name == 'Tier 3 Iron Plate':
                    layer_list.append([(200, 200, 200), 3])
                elif item.name == 'Tier 1 Diamond Plate':
                    layer_list.append([(75, 237, 219), 1])
                elif item.name == 'Tier 2 Diamond Plate':
                    layer_list.append([(75, 237, 219), 2])
                elif item.name == 'Tier 3 Diamond Plate':
                    layer_list.append([(75, 237, 219), 3])
            else:
                layer_list.append(None)

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.armour.items[i] is not None:
                if self.armour.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.armour.items[i].name], (cell.x, cell.y))
                if self.armour.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.armour.items[i].durability, self.armour.items[i].max_durability)

        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, 330, 240)) #Draw Black Background
        pygame.draw.rect(surface, (255, 0, 0), (self.x + 127, self.y + 82, 75, 75)) #Draw Player Icon

        for item in layer_list: #Draw Armour Layers
            if item is not None:
                if item[1] == 1: #Tier 1
                    pygame.draw.rect(surface, item[0], (self.x + 112, self.y + 67, 105, 105), 12)
                elif item[1] == 2: #Tier 2
                    pygame.draw.rect(surface, item[0], (self.x + 99, self.y + 54, 133, 133), 12)
                elif item[1] == 3: #Tier 3
                    pygame.draw.rect(surface, item[0], (self.x + 84, self.y + 39, 165, 165), 12)

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.armour.items[index], mouse[0], mouse[1], font) 


class HotbarWidget(Widget):
    """
        Hotbar to be rendered to the main game screen at the bottom
    """

    def __init__(self, inventory: Inventory):
        self.inventory = inventory

        self.__coordinates: list[Coordinate] = []
        for i in range(9):
            self.__coordinates.append(Coordinate(7 + 82*i, 667))

        self.__hotbar_backgrounds: list[pygame.Rect] = []
        for i in range(9):
            self.__hotbar_backgrounds.append(pygame.Rect((7 + 82*i, 667), (82, 82)))

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 24)


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.inventory.selected_hotbar = 0
            if event.key == pygame.K_2:
                self.inventory.selected_hotbar = 1
            if event.key == pygame.K_3:
                self.inventory.selected_hotbar = 2
            if event.key == pygame.K_4:
                self.inventory.selected_hotbar = 3
            if event.key == pygame.K_5:
                self.inventory.selected_hotbar = 4
            if event.key == pygame.K_6:
                self.inventory.selected_hotbar = 5
            if event.key == pygame.K_7:
                self.inventory.selected_hotbar = 6
            if event.key == pygame.K_8:
                self.inventory.selected_hotbar = 7
            if event.key == pygame.K_9:
                self.inventory.selected_hotbar = 8


    def render(self, surface: pygame.Surface, context: Context):

        images = [None]*9
        numbers = ['']*9
        
        # populate images and numbers arrays
        for i in range(9):
            if self.inventory.items[i+27] is None: # Set White Background for NONE Slots
                images[i] = context.INFOBAR_IMAGES["slot"]
            else: # no enchantments
                images[i] = context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[self.inventory.items[i+27].name]]
                if self.inventory.items[i+27].number != 1:
                    numbers[i] = str(self.inventory.items[i+27].number)

        # draw images
        for i, coordinate in enumerate(self.__coordinates):
            surface.blit(context.INFOBAR_IMAGES["slot"], (coordinate.x, coordinate.y)) # background
            surface.blit(images[i], (coordinate.x, coordinate.y))
            if self.inventory.items[i+27] is not None:
                if self.inventory.items[i+27].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.inventory.items[i+27].name], (coordinate.x, coordinate.y))
                if self.inventory.items[i+27].durability is not None:
                    RenderDurabilityBar(surface, coordinate.x, coordinate.y, self.inventory.items[i+27].durability, self.inventory.items[i+27].max_durability)

        # draw background rects based on selected hotbar value
        for i in range(9):
            if self.inventory.selected_hotbar == i:
                pygame.draw.rect(surface, (255, 255, 255), self.__hotbar_backgrounds[i], 3)
            else:
                pygame.draw.rect(surface, (83, 83, 83), self.__hotbar_backgrounds[i], 2)

        # draw numbers
        for i in range(9):
            surface = self.__font.render(numbers[i], True, (255, 0, 0), (255, 255, 255))
            x = 60 + 82*i
            y = 720
            surface.blit(surface, (x, y))


class SmallCraftingWidget(Widget):
    """
        2x2 crafting grid widget in the player's inventory
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, small_crafting_grid: SmallCraftingInterface, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.small_crafting_grid = small_crafting_grid
        self.holding_item = holding_item

        self.__cells: list[pygame.Rect] = [
            pygame.Rect(
                (self.x, self.y), 
                (self.CELL_SIZE, self.CELL_SIZE)
            ),
            pygame.Rect(
                (self.x + self.CELL_SIZE, self.y), 
                (self.CELL_SIZE, self.CELL_SIZE)
            ),
            pygame.Rect(
                (self.x, self.y + self.CELL_SIZE), 
                (self.CELL_SIZE, self.CELL_SIZE)
            ),
            pygame.Rect(
                (self.x + self.CELL_SIZE, self.y + self.CELL_SIZE), 
                (self.CELL_SIZE, self.CELL_SIZE)
            ),
            pygame.Rect(
                (self.x + 247, self.y + 42), 
                (self.CELL_SIZE, self.CELL_SIZE)
            )
        ]

        self.__numbers: list[Coordinate] = [
            Coordinate(self.x + 52, self.y + 52),
            Coordinate(self.x + 135, self.y + 52),
            Coordinate(self.x + 52, self.y + 135),
            Coordinate(self.x + 135, self.y + 135),
            Coordinate(self.x + 300, self.y + 94)
        ]

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 36)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # main crafting grid
        if index != 4:
            if self.holding_item.item is not None and self.small_crafting_grid.items[index] is not None: #Items can be combined
                if self.holding_item.item.name == self.small_crafting_grid.items[index].name and (self.small_crafting_grid.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.small_crafting_grid.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.small_crafting_grid.items[index] = self.small_crafting_grid.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.small_crafting_grid.items[index] = self.small_crafting_grid.items[index], self.holding_item.item

        # result cell 
        else:
            if self.small_crafting_grid.items[4] is not None:
                self.inventory.add(self.small_crafting_grid.items[4])
                for i in range(4):
                    if self.small_crafting_grid.items[i] is not None:
                        self.small_crafting_grid.items[i].number -= 1


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 4: # cannot right click on the results box
            return

        if self.holding_item.item is None:
            return
        
        if self.small_crafting_grid.items[index] is None:
            self.small_crafting_grid.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.small_crafting_grid.items[index] is not None and self.small_crafting_grid.items[index].name == self.holding_item.item.name and (self.small_crafting_grid.items[index].number + 1 <= self.small_crafting_grid.items[index].stackNum):
            self.small_crafting_grid.items[index].number += 1
            self.holding_item.item.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        for item in self.small_crafting_grid.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for j in range(len(self.small_crafting_grid.items)):
            if self.small_crafting_grid.items[j] is not None:
                if self.small_crafting_grid.items[j].number == 1:
                    numbers[j] = ''

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83,83), cell, 2)
            if self.small_crafting_grid.items[i] is not None:
                if self.small_crafting_grid.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.small_crafting_grid.items[i].name], (cell.x, cell.y))
                if self.small_crafting_grid.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.small_crafting_grid.items[i].durability, self.small_crafting_grid.items[i].max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 172, self.y + 67))

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.small_crafting_grid.items[index], mouse[0], mouse[1], font) 


class ExperienceBarWidget(Widget):
    """
        Experience bar rendered on the main game screen
    """

    def __init__(self, experience: Experience):
        self.experience = experience 
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 45)


    def handle_event(self, event: pygame.event.Event) -> None:
        pass


    def render(self, surface: pygame.Surface, context: Context) -> None:
        levels = self.experience.levels

        try:
            percent_xp_to_next_level = (levels - math.floor(levels))
        except ZeroDivisionError:
            percent_xp_to_next_level = 0

        pygame.draw.rect(surface, "#72a34c", (5, 630, round(percent_xp_to_next_level * 738), 30))
        pygame.draw.rect(surface, "#424d42", (round(percent_xp_to_next_level * 738) + 5, 630, round((1 - percent_xp_to_next_level) * 738), 30))

        for i in range(18):
            pygame.draw.rect(surface, (0, 0, 0), (i * 41 + 5, 630, 41, 30), 2)

        experience_number = self.__font.render(str(math.floor(levels)), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (378, 615)
        surface.blit(experience_number, experience_number_r)  # Experience Number


class HealthBarWidget(Widget):
    """
        Health bar widget to be rendered on the main game screen
    """


    def __init__(self, health: Health):
        self.health = health
        self.__coordinates: list[Coordinate] = []
        for i in range(10):
            self.__coordinates.append(Coordinate(7 + 35*i, 592))


    def handle_event(self, event) -> bool:
        return False


    def render(self, surface: pygame.Surface, context: Context) -> None:
        curr = self.health.value 
        for coordinate in self.__coordinates:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_heart"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_heart"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_heart"] 
            surface.blit(image, (coordinate.x, coordinate.y))


class HungerBarWidget(Widget):
    """
        Hunger bar widget to be rendered on the main game screen
    """


    def __init__(self, hunger: Hunger):
        self.hunger = hunger
        self.__coordinates:list[Coordinate] = []
        for i in range(10):
            self.__coordinates.append(Coordinate(715 - 34*i, 592))


    def handle_event(self, event):
        pass


    def render(self, surface: pygame.Surface, context: Context):
        curr = self.hunger.value 
        for coordinate in self.__coordinates:
            if curr >= 2:
                image = context.INFOBAR_IMAGES["full_hunger"]
                curr -= 2
            elif curr == 1:
                image = context.INFOBAR_IMAGES["half_hunger"] 
                curr -= 1
            else:
                image = context.INFOBAR_IMAGES["empty_hunger"] 
            surface.blit(image, (coordinate.x, coordinate.y))


class DebugWidget(Widget):
    """
        Widget containing debug info to be rendered on the main game screen
    """


    def __init__(self, game_state: GameState):
        self.game_state = game_state 
        self.fps = 0


    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    
    def update(self, fps: float) -> None:
        self.fps = fps


    def render(self, surface: pygame.Surface, context: Context):

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)

        version = font.render(f"Tilecraft {VERSION}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(version, (0, 0))

        python_version = font.render(f"Python {sys.version[0:6]}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(python_version, (0, 25))

        pygame_version = font.render(f"Graphics: pygame {pygame.version.ver}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(pygame_version, (0, 50))

        surface_size = font.render(f"Display Size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(surface_size, (0, 75))

        seed_label = font.render(f"Seed: {self.game_state.world.seed}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(seed_label, (0, 100))

        fps_font = font.render(f"FPS: {self.fps:.2f}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(fps_font, (0, 125))

        direction_label = font.render(f"Facing: {self.game_state.player.direction}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(direction_label, (0, 150))

        target_label = font.render(f"Target Tile: {self.game_state.player.target[0]}, {self.game_state.player.target[1]}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(target_label, (0, 175))

        coords_label = font.render(f"X: {self.game_state.player.x:.3f}, Y: {self.game_state.player.y:.3f}", True, (0, 0, 0), (255, 255, 255))
        surface.blit(coords_label, (0, 200))


class CraftingTableWidget(Widget):
    """
        3x3 crafting grid widget to be rendered on crafting table interface
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, crafting_grid: CraftingTableInterface, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.crafting_grid = crafting_grid
        self.holding_item = holding_item

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 40)

        # populate pygame rect cells
        self.__cells: list[pygame.Rect] = []
        for i in range(3):
            for j in range(3):
                self.__cells.append(pygame.Rect((self.x + j * self.CELL_SIZE, self.y + i * self.CELL_SIZE), (self.CELL_SIZE, self.CELL_SIZE)))
        self.__cells.append(pygame.Rect((self.x + 375, self.y + 82), (self.CELL_SIZE, self.CELL_SIZE)))

        self.__numbers: list[Coordinate] = []

        # populate number rendering coordiantes
        self.__numbers: list[Coordinate] = []
        for cell in self.__cells:
            self.__numbers.append(Coordinate(cell.x + 52, cell.y + 52))


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # main crafting grid
        if index != 9:
            if self.holding_item.item is not None and self.crafting_grid.items[index] is not None: #Items can be combined
                if self.holding_item.item.name == self.crafting_grid.items[index].name and (self.crafting_grid.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.crafting_grid.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.crafting_grid.items[index] = self.crafting_grid.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.crafting_grid.items[index] = self.crafting_grid.items[index], self.holding_item.item

        # result cell
        else:
            if self.crafting_grid.items[9] is not None:
                self.inventory.add(self.crafting_grid.items[9])
                for i in range(9):
                    if self.crafting_grid.items[i] is not None:
                        self.crafting_grid.items[i].number -= 1


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 9: # cannot right click on results box
            return

        if self.holding_item.item is None:
            return

        if self.crafting_grid.items[index] is None:
            self.crafting_grid.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.crafting_grid.items[index] is not None and self.crafting_grid.items[index].name == self.holding_item.item.name and (self.crafting_grid.items[index].number + 1 <= self.crafting_grid.items[index].stackNum):
            self.crafting_grid.items[index].number += 1
            self.holding_item.item.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        for item in self.crafting_grid.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.crafting_grid.items)):
            if self.crafting_grid.items[i] is not None:
                if self.crafting_grid.items[i].number == 1:
                    numbers[i] = ''

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.crafting_grid.items[i] is not None:
                if self.crafting_grid.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.crafting_grid.items[i].name], (cell.x, cell.y))
                if self.crafting_grid.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.crafting_grid.items[i].durability, self.crafting_grid.items[i].max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 270, self.y + 105))

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.crafting_grid.items[index], mouse[0], mouse[1], font) 


class FurnaceWidget(Widget):
    """
        Widget for furnace smelting interface to be rendered in the inventory
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, furnace: FurnaceInterface, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.furnace = furnace 
        self.holding_item = holding_item
        self.fps = 0

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__side_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 36)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 45)
        
        # pygame.rects
        self.__cells: list[pygame.Rect] = [
            pygame.Rect((self.x, self.y), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x, self.y + 195), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x + 225, self.y + 105), (self.CELL_SIZE, self.CELL_SIZE))
        ]

        # number coordinates
        self.__numbers: list[Coordinate] = []
        for cell in self.__cells:
            self.__numbers.append(Coordinate(cell.x + 52, cell.y + 52))


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # main furnace cells
        if index != 2:
            if self.holding_item.item is not None and self.furnace.items[index] is not None: #Items can be combined
                if self.holding_item.item.name == self.furnace.items[index].name and (self.furnace.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.furnace.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.furnace.items[index] = self.furnace.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.furnace.items[index] = self.furnace.items[index], self.holding_item.item

        # result cell
        else:
            self.inventory.add(self.furnace.items[2])
            self.furnace.items[2] = None


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 2: # cannot right click on result box
            return

        if self.holding_item.item is None:
            return
            
        if self.furnace.items[index] is None:
            self.furnace.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.furnace.items[index] is not None and self.furnace.items[index].name == self.holding_item.item.name and (self.furnace.items[index].number + 1 <= self.furnace.items[index].stackNum):
            self.furnace.items[index].number += 1
            self.holding_item.item.number -= 1


    def update(self, fps: float) -> None:
        self.fps = fps


    def render(self, surface: pygame.Surface, context: Context):

        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.furnace.items)):
            if self.furnace.items[i] is not None:
                if self.furnace.items[i].number == 0:
                    self.furnace.items[i] = None

        # Convert List to Images and Numbers
        for item in self.furnace.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.furnace.items)):
            if self.furnace.items[i] is not None:
                if self.furnace.items[i].number == 1:
                    numbers[i] = ''

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.furnace.items[i] is not None:
                if self.furnace.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.furnace.items[i].name], (cell.x, cell.y))
                if self.furnace.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.furnace.items[i].durability, self.furnace.items[i].max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.furnace.fuel_img, (self.x, self.y + 105)) #Render Fire Image
        surface.blit(self.__side_font.render(str(self.furnace.fuel_val), False, (255, 0, 0)), (self.x - 38, self.y + 120)) #Render Power of Fuel Remaining
        surface.blit(self.__side_font.render(f"{int(self.furnace.smelting_time / self.fps)}", False, (255, 0, 0)), (self.x + 142, self.y + 90)) #Render Time to Smelt
        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 112, self.y + 120)) #Render Arrow

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.furnace.items[index], mouse[0], mouse[1], font) 


class EnchantingTableWidget(Widget):
    """
        Widget for enchanting table interface to be rendered on the screen
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, enchanting_table: EnchantingTable, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.enchanting_table = enchanting_table
        self.holding_item = holding_item

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)

        self.upgrade = Button(self.CELL_SIZE, self.CELL_SIZE, self.x + 112, self.y + 142, (158, 145, 115))
        self.option1 = Button(487, 82, self.x + 255, self.y + 75, (158, 145, 115))
        self.option2 = Button(487, 82, self.x + 255, self.y + 157, (158, 145, 115))
        self.option3 = Button(487, 82, self.x + 255, self.y + 240, (158, 145, 115))

        self.__cells: list[pygame.Rect] = [
            pygame.Rect((self.x + 30, self.y + 225), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x + 112, self.y + 225), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x + 30, self.y + 142), (self.CELL_SIZE, self.CELL_SIZE))
        ]

        self.__numbers: list[Coordinate] = []
        for cell in self.__cells:
            self.__numbers.append(Coordinate(cell.x + 52, cell.y + 52))

        self.__rects: list[pygame.Rect] = [
            self.__cells[0], self.__cells[1], self.__cells[2], 
            self.upgrade.rect, self.option1.rect, self.option2.rect, self.option3.rect
        ]


    def handle_event(self, event):
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__rects):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # regular cells
        if index >= 0 and index < 3:
            if self.holding_item.item is not None and self.enchanting_table.items[index] is not None: #Items can be combined
                if self.holding_item.item.name == self.enchanting_table.items[index].name and (self.enchanting_table.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.enchanting_table.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.enchanting_table.items[index] = self.enchanting_table.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.enchanting_table.items[index] = self.enchanting_table.items[index], self.holding_item.item
            if index == 0:
                self.enchanting_table.enchant_set()

        # upgrade button
        elif index == 3:
            self.enchanting_table.enchant_upgrade()

        # option 1
        elif index == 4:
            self.enchanting_table.enchant1()

        # option 2
        elif index == 5:
            self.enchanting_table.enchant2()

        # option 3
        elif index == 6:
            self.enchanting_table.enchant3()


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index >= 3: # cannot right click on buttons
            return

        if self.holding_item.item is None:
            return

        if self.enchanting_table.items[index] is None:
            self.enchanting_table.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.enchanting_table.items[index] is not None and self.enchanting_table.items[index].name == self.holding_item.item.name and (self.enchanting_table.items[index].number + 1 <= self.enchanting_table.items[index].stackNum):
            self.enchanting_table.items[index].number += 1
            self.holding_item.item.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:

        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.enchanting_table.items)):
            if self.enchanting_table.items[i] is not None:
                if self.enchanting_table.items[i].number == 0:
                    self.enchanting_table.items[i] = None

        # Convert List to Images and Numbers
        for item in self.enchanting_table.items:
            if item is None:  # Set White Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.enchanting_table.items)):
            if self.enchanting_table.items[i] is not None:
                if self.enchanting_table.items[i].number == 1:
                    numbers[i] = ''

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.enchanting_table.items[i] is not None:
                if self.enchanting_table.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.enchanting_table.items[i].name], (cell.x, cell.y))
                if self.enchanting_table.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.enchanting_table.items[i].durability, self.enchanting_table.items[i].max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(str(numbers[i]), False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__font.render(f'Enchanting Table LEVEL {self.enchanting_table.enchanting_level}', False, (0, 0, 0)), (self.x, self.y))

        self.upgrade.render(surface, 'Upgrade', 21)
        self.option1.render(surface, self.enchanting_table.option_list[0], 30)
        self.option2.render(surface, self.enchanting_table.option_list[1], 30)
        self.option3.render(surface, self.enchanting_table.option_list[2], 30)

        if not is_holding:
            self.render_hovering_label(surface, mouse)

    def render_hovering_label(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index >= 3: # buttons are out of bounds
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.enchanting_table.items[index], mouse[0], mouse[1], font) 


class CompressorWidget(Widget):
    """
        Widget to show the compressing interface on the screen
    """

    X = 225 
    Y = 142
    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, compressor: Compressor, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.compressor = compressor
        self.holding_item = holding_item
        self.fps = 0

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 45)
        self.__side_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 36)

        self.__cells: list[pygame.Rect] = [
            pygame.Rect((self.x, self.y), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x + 225, self.y), (self.CELL_SIZE, self.CELL_SIZE))
        ]

        self.__numbers: list[Coordinate] = []
        for cell in self.__cells:
            self.__numbers.append(Coordinate(cell.x + 52, cell.y + 52))


    def handle_event(self, event):
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # input box
        if index != 1:
            if self.holding_item.item is not None and self.compressor.items[index] is not None: #Items can be combined
                if self.holding_item.item.name == self.compressor.items[index].name and (self.compressor.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.compressor.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.compressor.items[index] = self.compressor.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.compressor.items[index] = self.compressor.items[index], self.holding_item.item

        # result index
        else:
            self.inventory.add(self.compressor.items[1])
            self.compressor.items[1] = None


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 1: # cannot right click on result box
            return

        if self.holding_item.item is None:
            return

        if self.compressor.items[index] is None:
            self.compressor.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.compressor.items[index] is not None and self.compressor.items[index].name == self.holding_item.item.name and (self.compressor.items[index].number + 1 <= self.compressor.items[index].stackNum):
            self.compressor.items[index].number += 1
            self.holding_item.item.number -= 1


    def update(self, fps: float) -> None:
        self.fps = fps


    def render(self, surface: pygame.Surface, context: Context):

        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.compressor.items)):
            if self.compressor.items[i] is not None:
                if self.compressor.items[i].number == 0:
                    self.compressor.items[i] = None

        for item in self.compressor.items:
            if item is None: #Set Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.compressor.items)):
            if self.compressor.items[i] is not None:
                if self.compressor.items[i].number == 1:
                    numbers[i] = ''

        
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.compressor.items[i] is not None:
                if self.compressor.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.compressor.items[i].name], (cell.x, cell.y))
                if self.compressor.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.compressor.items[i].durability, self.compressor.items[i].max_durability)
        
        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 112, self.y + 30))  # Render Arrow
        surface.blit(self.__side_font.render(f"{int(self.compressor.compressing_time / self.fps)}", False, (255, 0, 0)), (self.x + 135, self.y))  # Render Time to Compress

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.compressor.items[index], mouse[0], mouse[1], font) 


class GrindstoneWidget(Widget):
    """
        Repairing and disenchanting interface to be rendered on the screen
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, grindstone: Grindstone, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.inventory = inventory
        self.grindstone = grindstone
        self.holding_item = holding_item

        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
        self.__arrow_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 45)

        self.__cells: list[pygame.Rect] = [
            pygame.Rect((self.x, self.y), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x, self.y + 90), (self.CELL_SIZE, self.CELL_SIZE)),
            pygame.Rect((self.x + 250, self.y + 46), (self.CELL_SIZE, self.CELL_SIZE))
        ]

        self.__numbers: list[Coordinate] = []
        for cell in self.__cells:
            self.__numbers.append(Coordinate(cell.x, cell.y))


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)


    def __get_hover_box(self, mouse: tuple[int, int]) -> Optional[int]:
        for i, rect in enumerate(self.__cells):
            if rect.collidepoint(mouse):
                return i
        return None


    def __handle_left_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        # input boxes
        if index != 2:
            if self.holding_item.item is not None and self.grindstone.items[index] is not None:  # Items can be combined
                if self.holding_item.item.name == self.grindstone.items[index].name and (self.grindstone.items[index].number + self.holding_item.item.number <= self.holding_item.item.stackNum):
                    self.grindstone.items[index].number += self.holding_item.item.number
                    self.holding_item.item = None
                else:
                    self.holding_item.item, self.grindstone.items[index] = self.grindstone.items[index], self.holding_item.item
            else:
                self.holding_item.item, self.grindstone.items[index] = self.grindstone.items[index], self.holding_item.item

        # result index
        else:
            self.inventory.add(self.grindstone.items[2])
            if self.grindstone.items[0] is not None and self.grindstone.items[1] is None:
                if self.grindstone.items[0].enchantments is not None:
                    self.grindstone.disenchant()
            self.grindstone.items[0], self.grindstone.items[1], self.grindstone.items[2] = None, None, None


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 2: # cannot right click on results box
            return

        if self.holding_item.item is None:
            return

        if self.grindstone.items[index] is None:
            self.grindstone.items[index] = Item(self.holding_item.item.name, 1, self.holding_item.item.enchantments, self.holding_item.item.durability)
            self.holding_item.item.number -= 1
        elif self.grindstone.items[index] is not None and self.grindstone.items[index].name == self.holding_item.item.name and (self.grindstone.items[index].number + 1 <= self.grindstone.items[index].stackNum):
            self.grindstone.items[index].number += 1
            self.holding_item.item.number -= 1


    def render(self, surface: pygame.Surface, context: Context):

        mouse = pygame.mouse.get_pos()
        is_holding = self.holding_item.item is not None

        images = []
        numbers = []

        # Remove Value if Number is 0
        for i in range(len(self.grindstone.items)):
            if self.grindstone.items[i] is not None:
                if self.grindstone.items[i].number == 0:
                    self.grindstone.items[i] = None

        for item in self.grindstone.items:
            if item is None:  # Set Background for NONE Slots
                images.append(context.ITEM_IMAGES["none_img"])
                numbers.append('')
            else:
                images.append(context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item.name]])
                numbers.append(str(item.number))

        # Remove Value if Number is 1
        for i in range(len(self.grindstone.items)):
            if self.grindstone.items[i] is not None:
                if self.grindstone.items[i].number == 1:
                    numbers[i] = ''

        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if self.grindstone.items[i] is not None:
                if self.grindstone.items[i].enchantments is not None:
                    surface.blit(context.TC_GLINTS[self.grindstone.items[i].name], (cell.x, cell.y))
                if self.grindstone.items[i].durability is not None:
                    RenderDurabilityBar(surface, cell.x, cell.y, self.grindstone.items[i].durability, self.grindstone.items[i].max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        pygame.draw.rect(surface, (0, 0, 0), (self.x - 10, self.y - 10, 102, 194), 2)
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 40, self.y + 10, 30, 194), 2)
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 92, self.y + 10, 30, 194), 2)
        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 142, self.y + 65))  # Render Arrow

        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.grindstone.items[index], mouse[0], mouse[1], font) 


class HoldingItemWidget(Widget):
    """
        Widget to render the holding item on the inventory screens
    """

    def __init__(self, holding_item: HoldingItem):
        self.holding_item = holding_item
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)


    def handle_event(self, event: pygame.event.Event) -> None:
        pass


    def render(self, surface: pygame.Surface, context: Context):

        if self.holding_item.item is None:
            image = context.ITEM_IMAGES["none_img"]
            number = ''
        else:
            image = context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[self.holding_item.item.name]]
            number = str(self.holding_item.item.number)

        if self.holding_item.item is not None:
            if self.holding_item.item.number == 1:
                number = ''

        x, y = pygame.mouse.get_pos()

        if self.holding_item.item is not None:
            surface.blit(image, (x, y))
            surface.blit(self.__font.render(number, False, (255, 255, 255)), (x + 52, y + 52))
            if self.holding_item.item.enchantments is not None:
                surface.blit(context.TC_GLINTS[self.holding_item.item.name], (x, y))
            if self.holding_item.item.durability is not None:
                RenderDurabilityBar(surface, x, y, self.holding_item.item.durability, self.holding_item.item.max_durability)
