import pygame

from tilecraft import ASSETS_DIR
from tilecraft.constants import SCREEN_WIDTH
from tilecraft.interfaces.interface import Interface, GameRunningScreen, ScreenID
from tilecraft.game_state import advancements_update
from tilecraft.ui.game import (
    DebugWidget,
    ExperienceBarWidget,
    HealthBarWidget,
    HotbarWidget,
    HungerBarWidget,
)


class GameScreen(GameRunningScreen):
    """
        Main game window
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        self.health_bar_widget = HealthBarWidget(self.game_state.player.health)
        self.hunger_bar_widget = HungerBarWidget(self.game_state.player.hunger)
        self.experience_bar_widget = ExperienceBarWidget(self.game_state.player.experience)
        self.hotbar_widget = HotbarWidget(self.game_state.player.inventory)
        self.debug_widget = DebugWidget(self.game_state)


    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.game_state.screen.isTyping:

            if event.type == pygame.QUIT:
                self.request_screen(ScreenID.TITLE)
                return

            elif event.type == pygame.KEYDOWN:

                # handle switch to hotbar events
                self.hotbar_widget.handle_event(event)

                if event.key == pygame.K_ESCAPE: # escape key (quit)
                    self.request_screen(ScreenID.TITLE)
                    return

                if event.key == pygame.K_e: # inventory key
                    self.request_screen(ScreenID.INVENTORY)

                if event.key == pygame.K_f: # advancements key
                    if not self.game_state.player.advancements:
                        self.game_state.screen.print("YOU HAVE NOT EARNED ANY ADVANCEMENTS")
                    else:
                        self.game_state.screen.print("Advancements: ")
                        for i in self.game_state.player.advancements:
                            self.game_state.screen.print(f"- {i}")

                if event.key == pygame.K_t: # input and chat key
                    self.game_state.screen.start_typing('')

                if event.key == pygame.K_q: # eat key
                    if self.game_state.player.inventory.hotbar_item is None:
                        self.game_state.screen.print("You are not holding a food item!")
                        return

                    if self.game_state.player.inventory.hotbar_item.itemType != "Food":
                        self.game_state.screen.print("You are not holding a food item!")
                        return

                    if not self.game_state.player.eat(): # try to eat
                        self.game_state.screen.print("You are not holding a food item!")
                        return

                if event.key == pygame.K_0: # debug key
                    self.game_state.debug_mode = not self.game_state.debug_mode

                if event.key == pygame.K_a:  # Turn Left
                    pos = self.game_state.player.direction_list.index(self.game_state.player.direction)
                    self.game_state.player.direction = self.game_state.player.direction_list[pos - 1]

                if event.key == pygame.K_d:  # Turn Right
                    pos = self.game_state.player.direction_list.index(self.game_state.player.direction)
                    if pos == 3:
                        self.game_state.player.direction = self.game_state.player.direction_list[0]
                    else:
                        self.game_state.player.direction = self.game_state.player.direction_list[pos + 1]

            elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event

                if pygame.mouse.get_pressed(3)[2]:  # Right Click
                    self.game_state.player.mouse_button = 2
                    if self.game_state.player.inventory.hotbar_item is not None:
                        if self.game_state.player.inventory.hotbar_item.name == 'Crafting Table': #Crafting Key
                            self.request_screen(ScreenID.CRAFTING)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Furnace': #Smelting Key
                            self.request_screen(ScreenID.SMELTING)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Enchanting Table': #Enchanting Key
                            self.request_screen(ScreenID.ENCHANTING)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Compressor': #Compressing Key
                            self.request_screen(ScreenID.COMPRESSING)
                        elif self.game_state.player.inventory.hotbar_item.name == "Grindstone": #Repairing and Disenchanting Key
                            self.request_screen(ScreenID.GRINDSTONE)
                        elif self.game_state.player.inventory.hotbar_item.name == "Bucket": #Picking up liquids
                            self.game_state.player.pick_up_liquid()
                        elif self.game_state.player.inventory.hotbar_item.name == "Water Bucket" or \
                                self.game_state.player.inventory.hotbar_item.name == "Lava Bucket":  #Placing liquids
                            self.game_state.player.place_liquid()
                        else:
                            self.game_state.player.place_tile()

                elif pygame.mouse.get_pressed(3)[0]:
                    self.game_state.player.mouse_button = 1
                    self.game_state.player.isBreaking = True

            if event.type == pygame.MOUSEBUTTONUP:
                if self.game_state.player.mouse_button == 1:
                    self.game_state.player.breaking_time = 0
                    self.game_state.player.isBreaking = False

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: #Type Space
                    self.game_state.screen.type(' ')
                elif event.key == pygame.K_RETURN: #Enter Key
                    self.game_state.screen.stop_typing()
                elif event.key == pygame.K_BACKSPACE: #Delete
                    self.game_state.screen.delete()
                else:
                    char = str(pygame.key.name(event.key)) #Get Key name
                    if len(char) == 1: #Check to prevent non-alphabetical and non-number keys
                        self.game_state.screen.type(char)

        return


    def update(self, fps: float) -> None:
        super().update(fps)
        self.debug_widget.update(fps)
        self.game_state.play_time_seconds = (
            pygame.time.get_ticks() - self.game_state.start_ticks
        ) / 1000.0


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:


        if self.game_state.player.dimension == "Underground" and not self.game_state.world.is_underground_generated:
            self.request_screen(ScreenID.UNDERGROUND_GENERATING)
            return

        if not self.game_state.screen.isTyping:

            if self.game_state.player.dead: # kill player
                self.request_screen(ScreenID.DEATH)
                return

            if self.game_state.player.isBreaking:
                self.game_state.player.breaking(fps)

            self.game_state.player.move()  # Move self.game_state.player

        else:

            # handle screen up/down arrow movements
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]: # scroll up
                self.game_state.screen.scroll_up()
            elif keys[pygame.K_DOWN]: # scroll down
                self.game_state.screen.scroll_down()

        self.display.fill((0, 0, 0))  # Fill world_map border black
        world_map.fill(self.game_state.background)  # Fill world_map background colour

        self.game_state.player.health_update(frame_count)  # Update self.game_state.player Health
        self.game_state.world.render_chunks(self.game_state.player.left, self.game_state.player.right, self.game_state.player.top, self.game_state.player.bottom)  # Generate list of all chunks that are loaded
        self.game_state.world.generate_chunks(self.game_state.player.dimension)  # Generate Chunks that are loaded but have not been generated before
        self.game_state.world.render(world_map, self.context, self.game_state.player.dimension, self.game_state.player.left, self.game_state.player.top, self.game_state.player.rect, self.game_state.player.breaking_time, self.game_state.player.target)  # Render all world_map blocks to world_map
        self.game_state.player.remove_items() #Remove Items if their number is 0
        self.game_state.player.render(world_map)

        if self.game_state.debug_mode:
            self.debug_widget.render(world_map, self.context)

        self.health_bar_widget.render(world_map, self.context)
        self.hunger_bar_widget.render(world_map, self.context)
        self.experience_bar_widget.render(world_map, self.context) # render experience bar
        self.hotbar_widget.render(world_map, self.context) # render hotbar

        self.game_state.timer.render(world_map, self.game_state.play_time_seconds)
        advancements_update(self.game_state.screen, self.game_state.timer, self.game_state.player.advancements, self.game_state.player.inventory.items, self.game_state.player.armour.items, self.game_state.player.dimension)  # Update Advancements
        self.game_state.screen.render(world_map) #Render Text self.game_state.screen

        # general rendering
        self.display.blit(world_map, (0, 0))  # Render map to display
        return


class DeathScreen(Interface):
    """
        Screen shown when the player dies
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        minute = int(self.game_state.play_time_seconds // 60)
        seconds = int(round(self.game_state.play_time_seconds % 60))
        self.true_play_time = "Time Played:   " + str(minute) + "m " + str(seconds) + "s"


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.request_screen(ScreenID.QUIT)
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.request_screen(ScreenID.TITLE)
                return


    def update(self, fps: float) -> None:
        pass


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        self.display.fill("#FFCCCB")

        # render game title
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        surface = font.render("You Died!", False, (0, 0, 0))
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.display.blit(surface, (rect.x, rect.y))

        # render time played
        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 50)
        surface = font.render(self.true_play_time, False, (0, 0, 0))
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.display.blit(surface, (rect.x, rect.y))
