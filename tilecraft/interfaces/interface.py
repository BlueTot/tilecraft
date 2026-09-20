from enum import Enum, auto
from typing import Optional
from abc import abstractmethod, ABC
import pygame

from tilecraft.constants import Context 
from tilecraft.game_state import GameState


class ScreenID(Enum):
    """
        Identifiers for all the different screens
    """
    TITLE = auto()
    GAME = auto()
    INVENTORY = auto()
    CRAFTING = auto()
    SMELTING = auto()
    ENCHANTING = auto()
    COMPRESSING = auto()
    GRINDSTONE = auto()
    OVERWORLD_GENERATING = auto()
    UNDERGROUND_GENERATING = auto()
    HOW_TO_PLAY = auto()
    PATCH_NOTES = auto()
    CREDITS = auto()
    DEATH = auto()
    QUIT = auto()


class Interface(ABC):
    """
        Interface is a screen to be rendered onto the pygame display
    """

    def __init__(self, display: pygame.Surface, context: Context, game_state: GameState) -> None:
        self.display = display
        self.context = context
        self.game_state: GameState = game_state

        # None means that no transition has been requested
        self.next_screen_id: Optional[ScreenID] = None

    def request_screen(self, screen_id: ScreenID) -> None:
        """
            Request a screen transition to screen_id
        """
        self.next_screen_id = screen_id

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
            Handle an event
        """

    @abstractmethod
    def update(self, fps: float) -> None:
        """
            One frame update of the interface 
        """

    @abstractmethod
    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        """
            Render the screen to its display
        """


class GameRunningScreen(Interface):
    """
        GameRunningScreen is an interface that is running while the player's game is active
    """

    def update(self, fps: float) -> None:
        # In all game screens, furnace and compressor run in the background even when the interface isn't open
        self.game_state.player.furnace.smelt(self.context, fps, self.game_state.player.experience)
        self.game_state.player.compressor.compress(fps)
        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
