from __future__ import annotations
import random
import pygame

from tilecraft import ASSETS_DIR, VERSION
from .constants import create_context
from .game_state import GameState
from .interfaces import Interface, ScreenID, create_screen


def main() -> None:
    """
        Main event loop for the game, also the entry point for the program
    """

    pygame.init()  # Initialise Pygame Module

    display = pygame.display.set_mode((750, 750))  # Set display
    pygame.display.set_caption(f"Tilecraft {VERSION}")  # Set title
    clock = pygame.time.Clock()
    clock.get_time()
    context = create_context()

    world = pygame.Surface((750, 750))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    frame_count = 0

    game_state = GameState(
        screen=None, 
        player=None, 
        world=None, 
        timer=None, 
        rng=None, 
        seed=None, 
        background=(255, 255, 255), 
        load=None,
        start_ticks=0,
        play_time_seconds=0.0,
        debug_mode=False,
    )

    # start at the title screen
    current_screen: Interface = create_screen(ScreenID.TITLE, display, context, game_state)

    running = True

    while running:

        clock.tick(60) # maximum FPS of 60
        frame_count += 1 # increment no. of frames
        fps = clock.get_fps()

        # event loop
        for event in pygame.event.get():
            current_screen.handle_event(event)

        # exit loop if pygame is quit
        if current_screen.next_screen_id is ScreenID.QUIT:
            running = False
            continue

        # transition to next screen
        if current_screen.next_screen_id is not None:
            current_screen = create_screen(
                current_screen.next_screen_id,
                current_screen.display,
                current_screen.context,
                current_screen.game_state
            )

        # update screen
        current_screen.update(fps)

        # render screen
        current_screen.render(world, fps, frame_count)
        pygame.display.flip()

        if current_screen.game_state.rng is not None and not pygame.mixer.music.get_busy():
            if current_screen.game_state.rng.next_random(1, 500) == 1:
                pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()

    pygame.quit()
