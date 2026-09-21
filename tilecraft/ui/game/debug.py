import sys
import pygame

from tilecraft import ASSETS_DIR, VERSION
from tilecraft.constants import Context, SCREEN_HEIGHT, SCREEN_WIDTH
from tilecraft.ui.widget import Widget
from tilecraft.game_state import GameState


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
