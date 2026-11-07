from typing import Optional
import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import Coordinate, Context, Item, Button
from tilecraft.ui.widget import ItemContainerWidget
from tilecraft.ui.game.item_rendering import render_info_box, render_durability_bar
from tilecraft.inventory import Inventory, FurnaceInterface, EnchantingTable, Compressor, Grindstone, HoldingItem


class FurnaceWidget(ItemContainerWidget):
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
        self.fps = 0.0

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


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
                return True

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)
                return True

        return False


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

            held = self.holding_item.item
            slot = self.furnace.items[index]

            if (
                held is not None and
                slot is not None and
                held.name == slot.name and
                slot.number + held.number <= held.max_quantity
            ):
                slot.number += held.number
                self.holding_item.item = None
            else:
                self.holding_item.item, self.furnace.items[index] = slot, held

        # result cell
        else:
            self.inventory.add(self.furnace.items[2])
            self.furnace.items[2] = None


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 2: # cannot right click on result box
            return

        held = self.holding_item.item
        if held is None:
            return

        slot = self.furnace.items[index]
        if slot is None:
            self.furnace.items[index] = Item(held.name, 1, held.enchantments, held.durability)
            held.number -= 1
        elif slot is not None and slot.name == held.name and slot.number + 1 <= slot.max_quantity:
            slot.number += 1
            held.number -= 1


    def update(self, fps: float) -> None:
        self.fps = fps


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        fuel_img = context.ITEM_IMAGES["fire" if self.furnace.fuel_val > 0 else "no_fire"]

        # remove value if number is 0
        for i, item in enumerate(self.furnace.items):
            if item is not None and item.number == 0:
                self.furnace.items[i] = None

        # Convert List to Images and Numbers
        for item in self.furnace.items:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # render cells to display
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if (item := self.furnace.items[i]) is None:
                continue
            if item.enchantments is not None:
                surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
            if item.durability is not None and item.max_durability is not None:
                render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(fuel_img, (self.x, self.y + 105)) #Render Fire Image
        surface.blit(self.__side_font.render(str(self.furnace.fuel_val), False, (255, 0, 0)), (self.x - 38, self.y + 120)) #Render Power of Fuel Remaining
        surface.blit(self.__side_font.render(f"{int(self.furnace.smelting_time / self.fps)}", False, (255, 0, 0)), (self.x + 142, self.y + 90)) #Render Time to Smelt
        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 112, self.y + 120)) #Render Arrow

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.furnace.items[index], mouse[0], mouse[1], font)


class EnchantingTableWidget(ItemContainerWidget):
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


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
                return True

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)
                return True

        return False


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

            held = self.holding_item.item
            slot = self.enchanting_table.items[index]
            if (
                held is not None and
                slot is not None and
                held.name == slot.name and
                slot.number + held.number <= held.max_quantity
            ):
                slot.number += held.number
                self.holding_item.item = None
            else:
                self.holding_item.item, self.enchanting_table.items[index] = slot, held

            if index == 0:
                self.enchanting_table.update()

        # upgrade button
        elif index == 3:
            self.enchanting_table.upgrade()

        # option 1
        elif index == 4:
            self.enchanting_table.enchant(1)

        # option 2
        elif index == 5:
            self.enchanting_table.enchant(2)

        # option 3
        elif index == 6:
            self.enchanting_table.enchant(3)


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index >= 3: # cannot right click on buttons
            return

        held = self.holding_item.item
        if held is None:
            return

        slot = self.enchanting_table.items[index]
        if slot is None:
            self.enchanting_table.items[index] = Item(held.name, 1, held.enchantments, held.durability)
            held.number -= 1
        elif slot is not None and slot.name == held.name and slot.number + 1 <= slot.max_quantity:
            slot.number += 1
            held.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        # remove value if number is 0
        for i, item in enumerate(self.enchanting_table.items):
            if item is not None and item.number == 0:
                self.enchanting_table.items[i] = None

        # populate image and number list
        for item in self.enchanting_table.items:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # render cells to display
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if (item := self.enchanting_table.items[i]) is None:
                continue
            if item.enchantments is not None:
                surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
            if item.durability is not None and item.max_durability is not None:
                render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__font.render(f'Enchanting Table LEVEL {self.enchanting_table.enchanting_level}', False, (0, 0, 0)), (self.x, self.y))

        self.upgrade.render(surface, 'Upgrade', 21)
        self.option1.render(surface, self.enchanting_table.option(0), 30)
        self.option2.render(surface, self.enchanting_table.option(1), 30)
        self.option3.render(surface, self.enchanting_table.option(2), 30)

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_label(surface, mouse)

    def render_hovering_label(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index >= 3: # buttons are out of bounds
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.enchanting_table.items[index], mouse[0], mouse[1], font) 


class CompressorWidget(ItemContainerWidget):
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
        self.fps = 0.0

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


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
                return True

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)
                return True

        return False


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

            held = self.holding_item.item
            slot = self.compressor.items[index]

            if (
                held is not None and 
                slot is not None and 
                held.name == slot.name and 
                slot.number + held.number <= held.max_quantity
            ):
                slot.number += held.number
                self.holding_item.item = None
            else:
                self.holding_item.item, self.compressor.items[index] = slot, held

        # result index
        else:
            self.inventory.add(self.compressor.items[1])
            self.compressor.items[1] = None


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 1: # cannot right click on result box
            return

        held = self.holding_item.item
        if held is None:
            return

        slot = self.compressor.items[index]
        if slot is None:
            self.compressor.items[index] = Item(held.name, 1, held.enchantments, held.durability)
            held.number -= 1
        elif slot is not None and slot.name == held.name and (slot.number + 1 <= slot.max_quantity):
            slot.number += 1
            held.number -= 1


    def update(self, fps: float) -> None:
        self.fps = fps


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        # remove value if number is 0
        for i, item in enumerate(self.compressor.items):
            if item is not None and item.number == 0:
                self.compressor.items[i] = None

        # populate image and number lists
        for item in self.compressor.items:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # render cells to display
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if (item := self.compressor.items[i]) is None:
                continue
            if item.enchantments is not None:
                surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
            if item.durability is not None and item.max_durability is not None:
                render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)
        
        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 112, self.y + 30))  # Render Arrow
        surface.blit(self.__side_font.render(f"{int(self.compressor.compressing_time / self.fps)}", False, (255, 0, 0)), (self.x + 135, self.y))  # Render Time to Compress

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.compressor.items[index], mouse[0], mouse[1], font) 


class GrindstoneWidget(ItemContainerWidget):
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


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
                return True

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)
                return True

        return False


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

            held = self.holding_item.item
            slot = self.grindstone.items[index]
            if (
                held is not None and
                slot is not None and
                held.name == slot.name and
                slot.number + held.number <= held.max_quantity
            ):
                slot.number += held.number
                self.holding_item.item = None
            else:
                self.holding_item.item, self.grindstone.items[index] = slot, held

        # result index
        else:
            self.inventory.add(self.grindstone.items[2])
            if (
                self.grindstone.items[0] is not None and
                self.grindstone.items[1] is None and
                self.grindstone.items[0].enchantments is not None
            ):
                self.grindstone.repair_and_disenchant()
            self.grindstone.items = [None, None, None]


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        if index == 2: # cannot right click on results box
            return

        held = self.holding_item.item
        if held is None:
            return

        slot = self.grindstone.items[index]
        if slot is None:
            self.grindstone.items[index] = Item(held.name, 1, held.enchantments, held.durability)
            held.number -= 1
        elif slot.name == held.name and slot.number + 1 <= slot.max_quantity:
            slot.number += 1
            held.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        # remove value if number is 0
        for i, item in enumerate(self.grindstone.items):
            if item is not None and item.number == 0:
                self.grindstone.items[i] = None

        # populate images and numbers list
        for item in self.grindstone.items:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # render cells to display
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if (item := self.grindstone.items[i]) is None:
                continue
            if item.enchantments is not None:
                surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
            if item.durability is not None and item.max_durability is not None:
                render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)

        for i, coordinate in enumerate(self.__numbers):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        pygame.draw.rect(surface, (0, 0, 0), (self.x - 10, self.y - 10, 102, 194), 2)
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 40, self.y + 10, 30, 194), 2)
        pygame.draw.rect(surface, (0, 0, 0), (self.x + 92, self.y + 10, 30, 194), 2)
        surface.blit(self.__arrow_font.render('-->', False, (0, 0, 0)), (self.x + 142, self.y + 65))  # Render Arrow

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.grindstone.items[index], mouse[0], mouse[1], font) 
