from dataclasses import dataclass
from typing import Optional
import pygame

from tilecraft.ui.game.item_rendering import render_info_box, render_durability_bar
from tilecraft.ui.widget import ItemContainerWidget
from tilecraft import ASSETS_DIR
from tilecraft.constants import Coordinate, Item, Context 
from tilecraft.inventory import Inventory, Armour, HoldingItem

class InventoryWidget(ItemContainerWidget):
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

        self.__inventory_slots: list[pygame.Rect] = []
        for row in range(4):
            for col in range(9):
                self.__inventory_slots.append(pygame.Rect(
                    (x + self.CELL_SIZE*col, y + self.CELL_SIZE*row),
                    (self.CELL_SIZE, self.CELL_SIZE)
                ))

        self.__number_coordinates: list[Coordinate] = []
        for row in range(4):
            for col in range(9):
                self.__number_coordinates.append(Coordinate(
                    x + self.NUMBER_OFFSET_X + self.CELL_SIZE*col, 
                    y + self.NUMBER_OFFSET_Y + self.CELL_SIZE*row
                ))


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: #1
                self.__hotbar_swap(mouse, 1)
                return True
            elif event.key == pygame.K_2: #2
                self.__hotbar_swap(mouse, 2)
                return True
            elif event.key == pygame.K_3: #3
                self.__hotbar_swap(mouse, 3)
                return True
            elif event.key == pygame.K_4: #4
                self.__hotbar_swap(mouse, 4)
                return True
            elif event.key == pygame.K_5: #5
                self.__hotbar_swap(mouse, 5)
                return True
            elif event.key == pygame.K_6: #6
                self.__hotbar_swap(mouse, 6)
                return True
            elif event.key == pygame.K_7: #7
                self.__hotbar_swap(mouse, 7)
                return True
            elif event.key == pygame.K_8: #8
                self.__hotbar_swap(mouse, 8)
                return True
            elif event.key == pygame.K_9: #9
                self.__hotbar_swap(mouse, 9)
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
                return True

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.__handle_right_click(mouse)
                return True

        return False


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

        held = self.holding_item.item
        slot = self.inventory.items[index]

        if held is not None and slot is not None and held.name == slot.name and slot.number + held.number <= held.stackNum:
            slot.number += held.number
            self.holding_item.item = None
        else:
            self.holding_item.item, self.inventory.items[index] = slot, held


    def __handle_right_click(self, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return

        held = self.holding_item.item
        if held is None:
            return

        slot = self.inventory.items[index]
        if slot is None:
            self.inventory.items[index] = Item(held.name, 1, held.enchantments, held.durability)
            held.number -= 1
        elif slot.name == held.name and slot.number + 1 <= held.stackNum:
            slot.number += 1
            held.number -= 1


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        # remove values with 0
        for i, item in enumerate(self.inventory.items):
            if item is not None and item.number == 0:
                self.inventory.items[i] = None

        # populate images list and number list
        for item in self.inventory.items:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # draw images
        for i, cell in enumerate(self.__inventory_slots):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, self.COLOUR, cell, self.WIDTH)
            if (item := self.inventory.items[i]) is not None:
                if item.enchantments is not None:
                    surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
                if item.durability is not None and item.max_durability is not None:
                    render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)

        # draw numbers
        for i, coordinate in enumerate(self.__number_coordinates):
            text = self.__font.render(numbers[i], False, (255, 255, 255))
            surface.blit(text, (coordinate.x, coordinate.y))

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        """
            Render the item description for the item being hovered over (if not None)
        """
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.inventory.items[index], mouse[0], mouse[1], font)


@dataclass
class LayerListElement:
    """
        A layer of armour consists of a renderable colour and layer number
    """
    colour: tuple[int, int, int]
    level: int


class ArmourWidget(ItemContainerWidget):
    """
        Widget to render the player's armour items and a small model of the player
    """

    CELL_SIZE = 82
    ITEM_TYPE_MAPPING = {0: "Tier1", 1: "Tier2", 2: "Tier3", 3: "Shield"}
    
    def __init__(self, x: int, y: int, armour: Armour, holding_item: HoldingItem):
        self.x = x
        self.y = y
        self.armour = armour
        self.holding_item = holding_item

        self.__cells: list[pygame.Rect] = []
        for i in range(4):
            self.__cells.append(pygame.Rect((self.x + self.CELL_SIZE*i, self.y + 240), (self.CELL_SIZE, self.CELL_SIZE)))


    def handle_event(self, event: pygame.event.Event) -> bool:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.__handle_left_click(mouse)
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

        if index not in (0, 1, 2, 3):
            raise ValueError("Index for armour widget must be in (0, 1, 2, 3)")

        held = self.holding_item.item
        slot = self.armour.items[index]

        # each slot has an expected item type that is only allowed there
        expected_item_type = self.ITEM_TYPE_MAPPING[index]

        if (
            (held is not None and slot is None and held.itemType == expected_item_type) or
            (held is None and slot is not None) or
            (held is not None and slot is not None and held.itemType == expected_item_type and slot.itemType == expected_item_type)
        ):
            self.holding_item.item, self.armour.items[index] = slot, held


    def render(self, surface: pygame.Surface, context: Context) -> None:
        mouse = pygame.mouse.get_pos()
        images: list[pygame.Surface] = []
        layer_list: list[Optional[LayerListElement]] = []

        # populate armour image list for armour slots
        for item in self.armour.items:
            images.append(self._surface_from(context, item))

        # populate layer list
        for item in self.armour.items:
            if item is None:
                layer_list.append(None)
                continue
            match item.name:
                case "Tier 1 Iron Plate":
                    layer_list.append(LayerListElement((200, 200, 200), 1))
                case "Tier 2 Iron Plate":
                    layer_list.append(LayerListElement((200, 200, 200), 2))
                case "Tier 3 Iron Plate":
                    layer_list.append(LayerListElement((200, 200, 200), 3))
                case "Tier 1 Diamond Plate":
                    layer_list.append(LayerListElement((75, 237, 219), 1))
                case "Tier 2 Diamond Plate":
                    layer_list.append(LayerListElement((75, 237, 219), 2))
                case "Tier 3 Diamond Plate":
                    layer_list.append(LayerListElement((75, 237, 219), 3))
                case "Shield":
                    # Shield does not produce an armour layer
                    pass
                case _:
                    raise ValueError("Invalid armour type encontered when constructing layer list")

        # render items to the display
        for i, cell in enumerate(self.__cells):
            surface.blit(images[i], (cell.x, cell.y))
            pygame.draw.rect(surface, (83, 83, 83), cell, 2)
            if (item := self.armour.items[i]) is not None:
                if item.enchantments is not None:
                    surface.blit(context.TC_GLINTS[item.name], (cell.x, cell.y))
                if item.durability is not None and item.max_durability is not None:
                    render_durability_bar(surface, cell.x, cell.y, item.durability, item.max_durability)

        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, 330, 240)) #Draw Black Background
        pygame.draw.rect(surface, (255, 0, 0), (self.x + 127, self.y + 82, 75, 75)) #Draw Player Icon

        # draw armour layers
        for layer in layer_list:
            if layer is None:
                continue
            match layer.level:
                case 1:
                    pygame.draw.rect(surface, layer.colour, (self.x + 112, self.y + 67, 105, 105), 12)
                case 2:
                    pygame.draw.rect(surface, layer.colour, (self.x + 99, self.y + 54, 133, 133), 12)
                case 3:
                    pygame.draw.rect(surface, layer.colour, (self.x + 84, self.y + 39, 165, 165), 12)
                case _:
                    raise ValueError("Layer of armour must be in (1, 2, 3)")

        is_holding = self.holding_item.item is not None
        if not is_holding:
            self.render_hovering_item(surface, mouse)


    def render_hovering_item(self, display: pygame.Surface, mouse: tuple[int, int]) -> None:
        if (index := self.__get_hover_box(mouse)) is None:
            return
        
        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 22)
        render_info_box(display, self.armour.items[index], mouse[0], mouse[1], font) 


class HotbarWidget(ItemContainerWidget):
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


    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.inventory.selected_hotbar = 0
                return True
            if event.key == pygame.K_2:
                self.inventory.selected_hotbar = 1
                return True
            if event.key == pygame.K_3:
                self.inventory.selected_hotbar = 2
                return True
            if event.key == pygame.K_4:
                self.inventory.selected_hotbar = 3
                return True
            if event.key == pygame.K_5:
                self.inventory.selected_hotbar = 4
                return True
            if event.key == pygame.K_6:
                self.inventory.selected_hotbar = 5
                return True
            if event.key == pygame.K_7:
                self.inventory.selected_hotbar = 6
                return True
            if event.key == pygame.K_8:
                self.inventory.selected_hotbar = 7
                return True
            if event.key == pygame.K_9:
                self.inventory.selected_hotbar = 8
                return True

        return False


    def render(self, surface: pygame.Surface, context: Context) -> None:
        images: list[pygame.Surface] = []
        numbers: list[str] = []

        # populate images and numbers arrays
        for item in self.inventory.items[27:36]:
            images.append(self._surface_from(context, item))
            numbers.append(self._quantity_from(item))

        # draw images
        for i, coordinate in enumerate(self.__coordinates):
            surface.blit(context.INFOBAR_IMAGES["slot"], (coordinate.x, coordinate.y)) # background
            surface.blit(images[i], (coordinate.x, coordinate.y))
            if (item := self.inventory.items[i+27]) is not None:
                if item.enchantments is not None:
                    surface.blit(context.TC_GLINTS[item.name], (coordinate.x, coordinate.y))
                if item.durability is not None and item.max_durability is not None:
                    render_durability_bar(surface, coordinate.x, coordinate.y, item.durability, item.max_durability)

        # draw background rects based on selected hotbar value
        for i in range(9):
            if self.inventory.selected_hotbar == i:
                pygame.draw.rect(surface, (255, 255, 255), self.__hotbar_backgrounds[i], 3)
            else:
                pygame.draw.rect(surface, (83, 83, 83), self.__hotbar_backgrounds[i], 2)

        # draw numbers
        for i in range(9):
            text = self.__font.render(numbers[i], True, (255, 0, 0), (255, 255, 255))
            surface.blit(text, (60 + 82*i, 720))


class HoldingItemWidget(ItemContainerWidget):
    """
        Widget to render the holding item on the inventory screens
    """

    def __init__(self, holding_item: HoldingItem):
        self.holding_item = holding_item
        self.__font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)


    def handle_event(self, event: pygame.event.Event) -> bool:
        return False


    def render(self, surface: pygame.Surface, context: Context) -> None:
        image = self._surface_from(context, self.holding_item.item)
        number = self._quantity_from(self.holding_item.item)

        x, y = pygame.mouse.get_pos()

        if (item := self.holding_item.item) is None:
            return

        surface.blit(image, (x, y))
        surface.blit(self.__font.render(number, False, (255, 255, 255)), (x + 52, y + 52))
        if item.enchantments is not None:
            surface.blit(context.TC_GLINTS[item.name], (x, y))
        if item.durability is not None and item.max_durability is not None:
            render_durability_bar(surface, x, y, item.durability, item.max_durability)
