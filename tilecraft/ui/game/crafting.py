from typing import Optional
import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import Coordinate, Context, ITEM_IMAGE_MAPPING, Item
from tilecraft.ui.widget import Widget
from tilecraft.ui.game.item_rendering import TextBox, RenderDurabilityBar
from tilecraft.inventory import Inventory, HoldingItem
from tilecraft.crafting import SmallCraftingGrid, LargeCraftingGrid


class SmallCraftingWidget(Widget):
    """
        2x2 crafting grid widget in the player's inventory
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, small_crafting_grid: SmallCraftingGrid, holding_item: HoldingItem):
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


class CraftingTableWidget(Widget):
    """
        3x3 crafting grid widget to be rendered on crafting table interface
    """

    CELL_SIZE = 82

    def __init__(self, x: int, y: int, inventory: Inventory, crafting_grid: LargeCraftingGrid, holding_item: HoldingItem):
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
