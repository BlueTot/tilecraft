import random
import pygame

from tilecraft import ASSETS_DIR, VERSION
from tilecraft.constants import RandomNumberGenerator, SCREEN_WIDTH 
from tilecraft.interfaces.interface import Interface, ScreenID
from tilecraft.game_state import SpeedrunTimer
from tilecraft.ui.general import Button, Dropdown, ScrollableTextBox, TextInput


class TitleScreen(Interface):
    """
        Menu screen the user is first greeted by
    """

    TEXT_INPUT_WIDTH = 500
    TEXT_INPUT_HEIGHT = 40
    BUTTON_HEIGHT = 70

    LOAD_OPTIONS = ['"Music Player" Speedrun Data Pack', '"God Gear" Speedrun Data Pack', 'Cheats Data Pack', 'None']

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        text_input_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 20)
        button_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 30)

        self.text_input = TextInput(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 225, 
                self.TEXT_INPUT_WIDTH, self.TEXT_INPUT_HEIGHT
            ), 
            font = text_input_font,
            placeholder="World Seed: "
        )

        self.drop_down = Dropdown(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 265, 
                self.TEXT_INPUT_WIDTH, self.TEXT_INPUT_HEIGHT
            ), 
            options = self.LOAD_OPTIONS, 
            font = text_input_font, 
           starting_option = "None" 
        )

        self.play_button = Button(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 305,
                self.TEXT_INPUT_WIDTH, self.BUTTON_HEIGHT
            ),
            text = "New World",
            font = button_font,
        )

        self.how_to_play_button = Button(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 375,
                self.TEXT_INPUT_WIDTH, self.BUTTON_HEIGHT
            ),
            text = "How to Play",
            font = button_font,
        )

        self.patch_notes_button = Button(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 445,
                self.TEXT_INPUT_WIDTH, self.BUTTON_HEIGHT
            ),
            text = "Patch Notes",
            font = button_font,
        )

        self.credits_button = Button(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 515,
                self.TEXT_INPUT_WIDTH, self.BUTTON_HEIGHT
            ),
            text = "Credits",
            font = button_font,
        )

        self.quit_button = Button(
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 585,
                self.TEXT_INPUT_WIDTH, self.BUTTON_HEIGHT
            ),
            text = "Quit",
            font = button_font,
        )

        # play minecraft music upon startup
        pygame.mixer.init()
        pygame.mixer.music.load(random.choice([str(ASSETS_DIR / "music/song6.mp3"), str(ASSETS_DIR / "music/song8.mp3")]))
        pygame.mixer.music.play()


    def get_seed(self) -> int:
        """
            Extract the seed from the text input if possible, otherwise return a random seed
        """
        try:
            return int(self.text_input.text)
        except ValueError:
            return random.randint(-1 * 2 ** 16, 2 ** 16 - 1)


    def get_load(self) -> str:
        """
            Get the datapack selected by the user on the title screen
        """
        match self.drop_down.selected:
            case '"Music Player" Speedrun Data Pack':
                return "Music Player"
            case '"God Gear" Speedrun Data Pack':
                return "God Gear"
            case 'Cheats Data Pack':
                return "Cheats"
        return "None"


    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type == pygame.QUIT:
            self.request_screen(ScreenID.QUIT)
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_screen(ScreenID.QUIT)
                return

        self.text_input.handle_event(event)

        if self.drop_down.handle_event(event): # if we handle a drop down event, do not handle any others
            return

        if self.play_button.handle_event(event): # create new world

            self.game_state.load = self.get_load() # extract datapack option
            self.game_state.seed = self.get_seed() # extract seed
            self.game_state.rng = RandomNumberGenerator(self.game_state.seed)
            self.game_state.timer = SpeedrunTimer(self.game_state.load)

            self.request_screen(ScreenID.OVERWORLD_GENERATING)
            return

        if self.how_to_play_button.handle_event(event): # go to how to play screen
            self.request_screen(ScreenID.HOW_TO_PLAY)
            return

        if self.patch_notes_button.handle_event(event): # go to patch notes screen
            self.request_screen(ScreenID.PATCH_NOTES)
            return

        if self.credits_button.handle_event(event): # go to credits screen
            self.request_screen(ScreenID.CREDITS)
            return

        if self.quit_button.handle_event(event): # quit the game
            self.request_screen(ScreenID.QUIT)
            return


    def update(self, fps: float) -> None:
        self.text_input.update(fps)
        self.play_button.update(fps)
        self.how_to_play_button.update(fps)
        self.patch_notes_button.update(fps)
        self.credits_button.update(fps)
        self.quit_button.update(fps)
        self.drop_down.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 75)
        title_screen_surface = title_screen_font.render("TILECRAFT", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))

        # render game version
        game_version_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftItalic-R8Mo.otf"), 30)
        game_version_surface = game_version_font.render(VERSION, False, (0, 0, 0))
        text_rect = game_version_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.display.blit(game_version_surface, (text_rect.x, text_rect.y))
        
        self.text_input.render(self.display, self.context)
        self.play_button.render(self.display, self.context)
        self.how_to_play_button.render(self.display, self.context)
        self.patch_notes_button.render(self.display, self.context)
        self.credits_button.render(self.display, self.context)
        self.quit_button.render(self.display, self.context)
        self.drop_down.render(self.display, self.context)


class HowToPlayScreen(Interface):
    """
        Screen to see how to play instructions
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)

        with open("docs/how_to_play.txt", encoding="utf-8") as f:
            instructions = f.read()

        self.instructions = ScrollableTextBox(
            rect=pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 130, 
                self.TEXT_INPUT_WIDTH, self.TEXT_INPUT_HEIGHT
            ),
            text=instructions,
            font=font,
        )


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.request_screen(ScreenID.QUIT)
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_screen(ScreenID.TITLE)
                return

        self.instructions.handle_event(event)


    def update(self, fps: float) -> None:
        self.instructions.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("How to Play", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render game instructions scrollable text box
        self.instructions.render(self.display, self.context)


class PatchNotesScreen(Interface):
    """
        Screen to see patch notes for the game
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)

        with open("docs/patch_notes.txt", encoding="utf-8") as f:
            patch_notes = f.read()

        self.patch_notes = ScrollableTextBox(
            rect=pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 130, 
                self.TEXT_INPUT_WIDTH, self.TEXT_INPUT_HEIGHT
            ),
            text=patch_notes,
            font=font,
        )


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.request_screen(ScreenID.QUIT)
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_screen(ScreenID.TITLE)
                return

        self.patch_notes.handle_event(event)


    def update(self, fps: float) -> None:
        self.patch_notes.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("Patch Notes", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render patch notes scrollable text box
        self.patch_notes.render(self.display, self.context)


class GameCreditsScreen(Interface):
    """
        Screen to see credits for the game
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)
        
        with open("docs/credits.txt", encoding="utf-8") as f:
            game_credits = f.read()

        self.game_credits = ScrollableTextBox(
            rect=pygame.Rect(
                (SCREEN_WIDTH - self.TEXT_INPUT_WIDTH) // 2, 130, 
                self.TEXT_INPUT_WIDTH, self.TEXT_INPUT_HEIGHT
            ),
            text=game_credits,
            font=font,
        )


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.request_screen(ScreenID.QUIT)
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_screen(ScreenID.TITLE)
                return

        self.game_credits.handle_event(event)


    def update(self, fps: float) -> None:
        self.game_credits.update(fps)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("Game Credits", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render game credits scrollable text box
        self.game_credits.render(self.display, self.context)
