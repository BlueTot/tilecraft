from collections.abc import Callable
import pygame

from tilecraft.constants import Context
from tilecraft.interfaces.interface import Interface, ScreenID
from tilecraft.game_state import GameState 

from .gameplay import GameScreen, DeathScreen
from .generation import OverworldGeneratingScreen, UndergroundGeneratingScreen
from .inventory import InventoryScreen, CraftingScreen, SmeltingScreen, EnchantingScreen, CompressingScreen, GrindstoneScreen
from .menus import TitleScreen, HowToPlayScreen, PatchNotesScreen, GameCreditsScreen


# type definition for interface constructor
ScreenConstructor = Callable[[pygame.Surface, Context, GameState], Interface]


# mapping of screen ID to screen constructor
SCREEN_TYPES: dict[ScreenID, ScreenConstructor] = {
    ScreenID.GAME: GameScreen, 
    ScreenID.INVENTORY: InventoryScreen,
    ScreenID.CRAFTING: CraftingScreen,
    ScreenID.SMELTING: SmeltingScreen,
    ScreenID.ENCHANTING: EnchantingScreen,
    ScreenID.COMPRESSING: CompressingScreen,
    ScreenID.GRINDSTONE: GrindstoneScreen,
    ScreenID.OVERWORLD_GENERATING: OverworldGeneratingScreen,
    ScreenID.UNDERGROUND_GENERATING: UndergroundGeneratingScreen,
    ScreenID.TITLE: TitleScreen,
    ScreenID.HOW_TO_PLAY: HowToPlayScreen,
    ScreenID.PATCH_NOTES: PatchNotesScreen,
    ScreenID.CREDITS: GameCreditsScreen,
    ScreenID.DEATH: DeathScreen,
}


def create_screen(screen_id: ScreenID, display: pygame.Surface, context: Context, game_state: GameState) -> Interface:
    """
        Creates a new screen for screen_id passing the parameters
    """

    try:
        screen_type = SCREEN_TYPES[screen_id]
    except KeyError:
        raise ValueError(f"Cannot create screen for {screen_id!r}") from None
    
    return screen_type(display, context, game_state)
