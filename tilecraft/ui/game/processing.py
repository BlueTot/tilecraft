from typing import Optional
import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import Coordinate, Context, ITEM_IMAGE_MAPPING, Item, Button
from tilecraft.ui.widget import Widget
from tilecraft.ui.game.item_rendering import TextBox, RenderDurabilityBar
from tilecraft.inventory import Inventory, FurnaceInterface, EnchantingTable, Compressor, Grindstone, HoldingItem


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
