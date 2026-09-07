from __future__ import annotations

import random
from typing import Optional

import pygame

from tilecraft import ASSETS_DIR, VERSION
from .constants import RandomNumberGenerator, Context, create_context
from .game_state import GameState, advancements_update, Screen, SpeedrunTimer
from .generation import UndergroundGeneratePortal
from .player import Player
from .ui.text_input import TextInput
from .ui.drop_down_menu import Dropdown
from .ui.button import Button
from .ui.scrollable_text_box import ScrollableTextBox
from .widgets import InventoryWidget, ArmourWidget, SmallCraftingWidget, HotbarWidget, ExperienceBarWidget, HealthBarWidget, HungerBarWidget
from .world import TilecraftWorld

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 750


# common screen interface
class Interface:
    """
        Interface is a screen to be rendered onto the pygame display
    """

    def __init__(self, display: pygame.Surface, context: Context, game_state: GameState) -> None:
        self.display = display
        self.context = context
        self.game_state: GameState = game_state
        self.next_screen: Optional[Interface] = self

    def handle_event(self, event: pygame.event.Event) -> None:
        """
            Handle an event, returning an optional signal to the title screen
        """

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        """
            Render the screen, returning an optional signal to the title screen
        """


class GameScreen(Interface):
    """
        Main game window
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.health_bar_widget = HealthBarWidget(self.game_state.player.health)
        self.hunger_bar_widget = HungerBarWidget(self.game_state.player.hunger)
        self.experience_bar_widget = ExperienceBarWidget(self.game_state.player.experience)
        self.hotbar_widget = HotbarWidget(self.game_state.player.inventory)

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.game_state.screen.isTyping:

            if event.type == pygame.QUIT:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state)
                return

            elif event.type == pygame.KEYDOWN:

                # handle switch to hotbar events
                self.hotbar_widget.handle_event(event)

                if event.key == pygame.K_ESCAPE: # escape key (quit)
                    self.next_screen = TitleScreen(self.display, self.context, self.game_state)
                    return

                if event.key == pygame.K_e: # inventory key
                    self.next_screen = InventoryScreen(self.display, self.context, self.game_state)

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
                    self.game_state.player.debug_menu = not self.game_state.player.debug_menu

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
                            self.next_screen = CraftingScreen(self.display, self.context, self.game_state)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Furnace': #Smelting Key
                            self.next_screen = SmeltingScreen(self.display, self.context, self.game_state)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Enchanting Table': #Enchanting Key
                            self.next_screen = EnchantingScreen(self.display, self.context, self.game_state)
                        elif self.game_state.player.inventory.hotbar_item.name == 'Compressor': #Compressing Key
                            self.next_screen = CompressingScreen(self.display, self.context, self.game_state)
                        elif self.game_state.player.inventory.hotbar_item.name == "Grindstone": #Repairing and Disenchanting Key
                            self.next_screen = GrindstoneScreen(self.display, self.context, self.game_state)
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


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # update play time
        self.game_state.play_time_seconds = (pygame.time.get_ticks() - self.game_state.start_ticks) / 1000.0

        if self.game_state.player.dimension == "Underground" and not self.game_state.world.is_underground_generated:
            self.next_screen = UndergroundGeneratingScreen(self.display, self.context, self.game_state)
            return

        if not self.game_state.screen.isTyping:

            if self.game_state.player.dead: # kill player
                self.next_screen = DeathScreen(self.display, self.context, self.game_state) # go to death screen
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
        self.game_state.player.render(self.context, world_map, SCREEN_WIDTH, SCREEN_HEIGHT, fps)  # Render self.game_state.player and self.game_state.player accessories to world_map

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


class InventoryScreen(Interface):
    """
        Screen containing the inventory, armour, and small crafting grid widgets
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(
            0, 390, 
            self.game_state.player.inventory, 
            self.game_state.player.holding_item
        )
        self.armour_widget = ArmourWidget(
            0, 0, 
            self.game_state.player.armour, 
            self.game_state.player.holding_item
        )
        self.small_crafting_widget = SmallCraftingWidget(
            390, 75, 
            self.game_state.player.inventory, 
            self.game_state.player.craft_interface, 
            self.game_state.player.holding_item
        )


    def handle_event(self, event: pygame.event.Event) -> None:

        self.inventory_widget.handle_event(event)
        self.armour_widget.handle_event(event)
        self.small_crafting_widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # update logic
        self.game_state.player.craft_interface.update() #Update Small 2x2 Crafting Grid
        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0

        # render logic
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        self.inventory_widget.render(world_map, self.context)
        self.armour_widget.render(world_map, self.context)
        self.small_crafting_widget.render(world_map, self.context)
        self.game_state.player.holding_item.render(world_map, self.context)

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class CraftingScreen(Interface):
    """
        Screen showing the 3x3 crafting grid and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(0, 390, self.game_state.player.inventory, self.game_state.player.holding_item)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        self.inventory_widget.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.crafting_grid.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.crafting_grid.handle_right_click(mouse, self.game_state.player.holding_item) 


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.inventory_widget.render(world_map, self.context)
        self.game_state.player.crafting_grid.render(world_map, self.context, mouse, is_holding) #Render 3x3 Crafting Grid
        self.game_state.player.crafting_grid.update()  #Update 3x3 Crafting Grid

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class SmeltingScreen(Interface):
    """
        Screen showing the furance interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(0, 390, self.game_state.player.inventory, self.game_state.player.holding_item)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        self.inventory_widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.furnace.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.furnace.handle_right_click(mouse, self.game_state.player.holding_item) 


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.inventory_widget.render(world_map, self.context)
        self.game_state.player.furnace.render(world_map, self.context, mouse, fps, is_holding) #Render Furnace Interface
        self.game_state.player.furnace.smelt(self.context, fps, self.game_state.player.experience) #Furnace Smelting

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class EnchantingScreen(Interface):
    """
        Screen showing the enchanting table interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(0, 390, self.game_state.player.inventory, self.game_state.player.holding_item)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        self.inventory_widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.enchanting_table.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.experience, self.game_state.rng)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.enchanting_table.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.inventory_widget.render(world_map, self.context)
        self.game_state.player.enchanting_table.render(world_map, self.context, mouse, is_holding) #Render Enchanting Table Interface

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class CompressingScreen(Interface):
    """
        Screen showing the compressor interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(0, 390, self.game_state.player.inventory, self.game_state.player.holding_item)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        self.inventory_widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.compressor.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.compressor.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.inventory_widget.render(world_map, self.context)
        self.game_state.player.compressor.render(world_map, self.context, mouse, fps, is_holding) #Render Compressor Interface
        self.game_state.player.compressor.compress(fps) #Compressing Process

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class GrindstoneScreen(Interface):
    """
        Screen showing the grindstone interface and the inventory
    """

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)
        self.inventory_widget = InventoryWidget(0, 390, self.game_state.player.inventory, self.game_state.player.holding_item)


    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        self.inventory_widget.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.grindstone.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory, self.game_state.player.experience)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.grindstone.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.inventory_widget.render(world_map, self.context)
        self.game_state.player.grindstone.render(world_map, self.context, mouse, is_holding) #Render Grindstone Interface
        self.game_state.player.grindstone.repair_and_disenchant() #Update repaired/disenchanted item

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display


class OverworldGeneratingScreen(Interface):
    """
        Screen shown when the overworld is first generated upon world startup
    """

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
        self.next_screen = GameScreen(self.display, self.context, self.game_state)
        return


class UndergroundGeneratingScreen(Interface):
    """
        Screen shown when user first enters the underground dimension
    """

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
        self.next_screen = GameScreen(self.display, self.context, self.game_state)
        return


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

        button_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 30)

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
            pygame.quit()
            self.next_screen = None # stop the loop
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                self.next_screen = None # stop the loop
                return

        self.text_input.handle_event(event)

        if self.drop_down.handle_event(event): # if we handle a drop down event, do not handle any others
            return

        if self.play_button.handle_event(event): # create new world

            self.game_state.load = self.get_load() # extract datapack option
            self.game_state.seed = self.get_seed() # extract seed
            self.game_state.rng = RandomNumberGenerator(self.game_state.seed)
            self.game_state.timer = SpeedrunTimer(self.game_state.load)

            self.next_screen = OverworldGeneratingScreen(self.display, self.context, self.game_state)
            return

        if self.how_to_play_button.handle_event(event): # go to how to play screen
            self.next_screen = HowToPlayScreen(self.display, self.context, self.game_state)
            return

        if self.patch_notes_button.handle_event(event): # go to patch notes screen
            self.next_screen = PatchNotesScreen(self.display, self.context, self.game_state)
            return

        if self.credits_button.handle_event(event): # go to credits screen
            self.next_screen = GameCreditsScreen(self.display, self.context, self.game_state)
            return

        if self.quit_button.handle_event(event): # quit the game
            pygame.quit()
            self.next_screen = None # stop the loop
            return

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
        
        # update and render text input box
        self.text_input.update()
        self.text_input.render(self.display)

        # update and render play button
        self.play_button.update()
        self.play_button.render(self.display)

        # update and render how to play button
        self.how_to_play_button.update()
        self.how_to_play_button.render(self.display)

        # update and render patch notes button
        self.patch_notes_button.update()
        self.patch_notes_button.render(self.display)

        # update and render credits button
        self.credits_button.update()
        self.credits_button.render(self.display)

        # update and render quit button
        self.quit_button.update()
        self.quit_button.render(self.display)

        # update and render drop down box
        self.drop_down.update()
        self.drop_down.render(self.display)


class HowToPlayScreen(Interface):
    """
        Screen to see how to play instructions
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)

        with open("docs/how_to_play.txt") as f:
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
            pygame.quit()
            self.next_screen = None # stop the loop
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state) # go back to title screen
                return

        self.instructions.handle_event(event)

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("How to Play", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render game instructions scrollable text box
        self.instructions.update()
        self.instructions.render(self.display)


class PatchNotesScreen(Interface):
    """
        Screen to see patch notes for the game
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)

        with open("docs/patch_notes.txt") as f:
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
            pygame.quit()
            self.next_screen = None # stop the loop
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state) # go back to title screen
                return

        self.patch_notes.handle_event(event)

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("Patch Notes", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render patch notes scrollable text box
        self.patch_notes.update()
        self.patch_notes.render(self.display)


class GameCreditsScreen(Interface):
    """
        Screen to see credits for the game
    """

    TEXT_INPUT_WIDTH = 600
    TEXT_INPUT_HEIGHT = 570

    def __init__(self, display, context, game_state):
        super().__init__(display, context, game_state)

        font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 18)
        
        with open("docs/credits.txt") as f:
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
            pygame.quit()
            self.next_screen = None # stop the loop
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state) # go back to title screen
                return

        self.game_credits.handle_event(event)

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:

        # render background
        self.display.blit(self.context.TITLE_SCREEN_IMAGE, (0, 0))

        # render game title
        title_screen_font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftBold-nMK1.otf"), 50)
        title_screen_surface = title_screen_font.render("Game Credits", False, (0, 0, 0))
        text_rect = title_screen_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.display.blit(title_screen_surface, (text_rect.x, text_rect.y))
        
        # render game credits scrollable text box
        self.game_credits.update()
        self.game_credits.render(self.display)


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
            pygame.quit()
            self.next_screen = None # stop the loop
            return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state) # go back to title screen
                return

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

    # start by generating the overworld
    current_screen: Interface = TitleScreen(
        display = display,
        context = context,
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
        )
    )

    while current_screen is not None:

        clock.tick(60) # maximum FPS of 60
        frame_count += 1 # increment no. of frames
        fps = clock.get_fps()

        # TODO:
        # furnace and compressor now do not update when user is not on the screen
        # separate update logic to rendering logic and make update a player method

        # event loop
        for event in pygame.event.get():
            current_screen.handle_event(event)

        # screen transition
        if current_screen.next_screen is not current_screen:
            current_screen = current_screen.next_screen

        # exit loop if pygame is quit
        if current_screen is None:
            return

        # render screen
        current_screen.render(world, fps, frame_count)
        pygame.display.flip()

        if current_screen.game_state.rng is not None and not pygame.mixer.music.get_busy():
            if current_screen.game_state.rng.next_random(1, 500) == 1:
                pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()
