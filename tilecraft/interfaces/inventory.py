import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import SCREEN_WIDTH 
from tilecraft.interfaces.interface import GameRunningScreen, ScreenID
from tilecraft.ui.widget import Widget
from tilecraft.ui.game import (
    ArmourWidget,
    CompressorWidget,
    CraftingTableWidget,
    EnchantingTableWidget,
    FurnaceWidget,
    GrindstoneWidget,
    HoldingItemWidget,
    InventoryWidget,
    SmallCraftingWidget
)


class InventoryScreen(GameRunningScreen):
    """
        Screen containing the inventory, armour, and small crafting grid widgets
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            ArmourWidget(
                0, 0, 
                self.game_state.player.armour, 
                self.game_state.player.holding_item
            ),
            SmallCraftingWidget(
                390, 75, 
                self.game_state.player.inventory, 
                self.game_state.player.craft_interface, 
                self.game_state.player.holding_item
            ),
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def update(self, fps: float):

        # update backend
        self.game_state.player.craft_interface.update()

        # update frontend
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class CraftingScreen(GameRunningScreen):
    """
        Screen showing the 3x3 crafting grid and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            CraftingTableWidget(
                195, 75,
                self.game_state.player.inventory,
                self.game_state.player.crafting_grid,
                self.game_state.player.holding_item
            ),
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def update(self, fps: float) -> None:

        # update backend
        self.game_state.player.crafting_grid.update()

        # update frontend
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)
        


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        # render title
        title_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 40)
        world_map.blit(title_font.render("Crafting Table", False, (0, 0, 0)), (195, 0))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class SmeltingScreen(GameRunningScreen):
    """
        Screen showing the furance interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            FurnaceWidget(
                225, 67,
                self.game_state.player.inventory,
                self.game_state.player.furnace,
                self.game_state.player.holding_item
            ) ,
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def update(self, fps: float) -> None:
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        # render title
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 40)
        world_map.blit(font.render('Furnace', False, (0, 0, 0)), (300, 0))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class EnchantingScreen(GameRunningScreen):
    """
        Screen showing the enchanting table interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            EnchantingTableWidget(
                0, 0,
                self.game_state.player.inventory,
                self.game_state.player.enchanting_table,
                self.game_state.player.holding_item
            ),
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def update(self, fps: float) -> None:
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class CompressingScreen(GameRunningScreen):
    """
        Screen showing the compressor interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            CompressorWidget(
                225, 142,
                self.game_state.player.inventory,
                self.game_state.player.compressor,
                self.game_state.player.holding_item
            ),
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def update(self, fps: float) -> None:
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        # render title
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 40)
        world_map.blit(font.render('Compressor', False, (0, 0, 0)), (262, 0))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class GrindstoneScreen(GameRunningScreen):
    """
        Screen showing the grindstone interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.__widgets: list[Widget] = [
            InventoryWidget(
                0, 390, 
                self.game_state.player.inventory, 
                self.game_state.player.holding_item
            ),
            GrindstoneWidget(
                225, 87,
                self.game_state.player.inventory,
                self.game_state.player.grindstone,
                self.game_state.player.holding_item
            ),
            HoldingItemWidget(self.game_state.player.holding_item),
        ]


    def handle_event(self, event: pygame.event.Event) -> None:

        for widget in self.__widgets:
            widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.request_screen(ScreenID.GAME)


    def update(self, fps: float) -> None:

        # update backend
        self.game_state.player.grindstone.repair_and_disenchant()

        # update frontend
        super().update(fps)
        for widget in self.__widgets:
            widget.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        # render title centered 
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 35)
        surface = font.render("Repair & Disenchant", False, (0, 0, 0))
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, 35))
        world_map.blit(surface, (rect.x, rect.y))

        for widget in self.__widgets:
            widget.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display
