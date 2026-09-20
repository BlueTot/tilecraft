import random
import pygame

from tilecraft import ASSETS_DIR 
from tilecraft.game_state import Screen 
from tilecraft.generation import UndergroundGeneratePortal
from tilecraft.interfaces.interface import Interface, ScreenID
from tilecraft.player import Player
from tilecraft.world import TilecraftWorld


class OverworldGeneratingScreen(Interface):
    """
        Screen shown when the overworld is first generated upon world startup
    """


    def handle_event(self, event: pygame.event.Event) -> None:
        pass


    def update(self, fps: float) -> None:
        pass


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        self.display.fill((255, 255, 255))
        for i in range(0, 750, 32):
            for j in range(0, 750, 32):
                self.display.blit(self.context.LOADING_IMAGE, (i, j))
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 37)
        self.display.blit(font.render("Generating Overworld", False, (255, 255, 255)), (180, 225))
        pygame.display.flip()

        # play music
        pygame.mixer.init()
        pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
        pygame.mixer.music.play()

        # generate world
        self.game_state.world = TilecraftWorld(self.game_state.rng, self.game_state.seed)  # Create World
        self.game_state.player = Player(self.context, self.game_state.rng, self.game_state.world)  # Create Player
        self.game_state.screen = Screen(self.game_state) # Create Text Screen

        # set start ticks from when world finished generating
        self.game_state.start_ticks = pygame.time.get_ticks()

        # go to game screen
        self.request_screen(ScreenID.GAME)
        return


class UndergroundGeneratingScreen(Interface):
    """
        Screen shown when user first enters the underground dimension
    """

    def handle_event(self, event: pygame.event.Event) -> None:
        pass


    def update(self, fps: float) -> None:
        pass


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        self.display.fill((255, 255, 255))
        for i in range(0, 750, 32):
            for j in range(0, 750, 32):
                self.display.blit(self.context.LOADING_IMAGE, (i, j))
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 37)
        self.display.blit(font.render("Generating Underground", False, (255, 255, 255)), (180, 225))

        pygame.display.flip()

        self.game_state.world.generateUnderground()
        self.game_state.world.UndergroundTiles = UndergroundGeneratePortal(round(self.game_state.player.x), round(self.game_state.player.y), self.game_state.world.UndergroundTiles)

        # mark underground as generated
        self.game_state.world.is_underground_generated = True

        # go to game screen
        self.request_screen(ScreenID.GAME)
        return
