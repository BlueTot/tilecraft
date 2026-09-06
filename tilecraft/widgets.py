from typing import Optional
import pygame

from tilecraft import ASSETS_DIR
from .constants import Context, Coordinate, Item, ITEM_IMAGE_MAPPING
from .inventory import Inventory, HoldingItem, RenderDurabilityBar, TextBox


class Widget:
    """
        Widget is a collection of images, rects, and text bundled together to be rendered on a Screen
    """

    def __init__(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """
            Handle an event
        """

    def render(self, display: pygame.Surface, context: Context) -> None:
        """
            Render the widget
        """


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


    def render(self, display: pygame.Surface, context: Context):
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
            display.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(display, self.COLOUR, cell, self.WIDTH)
            if self.inventory.items[i] is not None:
                if self.inventory.items[i].enchantments is not None:
                    display.blit(context.TC_GLINTS[self.inventory.items[i].name], (cell.x, cell.y))
                if self.inventory.items[i].durability is not None:
                    RenderDurabilityBar(display, cell.x, cell.y, self.inventory.items[i].durability, self.inventory.items[i].max_durability)

        # draw numbers
        for i, coordinate in enumerate(self.__number_coordinates):
            surface = self.__font.render(numbers[i], False, (255, 255, 255))
            display.blit(surface, (coordinate.x, coordinate.y))

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(display, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]):
        """
            Render the item description for the item being hovered over (if not None)
        """
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        TextBox(display, self.inventory.items[index], mouse[0], mouse[1], font) 
