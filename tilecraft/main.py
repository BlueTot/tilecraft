from __future__ import annotations

import tkinter
import tkinter.font
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

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.game_state.screen.isTyping:
            # QUIT Key
            if event.type == pygame.QUIT:
                self.next_screen = TitleScreen(self.display, self.context, self.game_state)
                return
            # Specify key types (key down)
            elif event.type == pygame.KEYDOWN:
                # Escape key (QUIT)
                if event.key == pygame.K_ESCAPE:
                    self.next_screen = TitleScreen(self.display, self.context, self.game_state)
                    return
                # Inventory key
                if event.key == pygame.K_e:
                    self.next_screen = InventoryScreen(self.display, self.context, self.game_state)
                # Advancements Key
                if event.key == pygame.K_f:
                    if not self.game_state.player.advancements:
                        self.game_state.screen.print("YOU HAVE NOT EARNED ANY ADVANCEMENTS")
                    else:
                        self.game_state.screen.print("Advancements: ")
                        for i in self.game_state.player.advancements:
                            self.game_state.screen.print(f"- {i}")
                # Input and chat key
                if event.key == pygame.K_t:
                    self.game_state.screen.start_typing('')
                # Eat key
                if event.key == pygame.K_q:
                    if self.game_state.player.inventory.hotbar_item is not None:
                        if self.game_state.player.inventory.hotbar_item.itemType == "Food":
                            if self.game_state.player.hunger < 20:
                                if self.game_state.player.inventory.hotbar_item.name == 'Bread':
                                    index = self.game_state.player.inventory.items.index(self.game_state.player.inventory.hotbar_item)
                                    self.game_state.player.inventory.items[index].number -= 1
                                    self.game_state.player.hunger += 5
                                # GOLDEN CARROT
                                elif self.game_state.player.inventory.hotbar_item.name == 'Golden Carrot':
                                    index = self.game_state.player.inventory.items.index(self.game_state.player.inventory.hotbar_item)
                                    self.game_state.player.inventory.items[index].number -= 1
                                    self.game_state.player.hunger += 6
                                # GOLDEN APPLE
                                elif self.game_state.player.inventory.hotbar_item.name == 'Golden Apple':
                                    index = self.game_state.player.inventory.items.index(self.game_state.player.inventory.hotbar_item)
                                    self.game_state.player.inventory.items[index].number -= 1
                                    self.game_state.player.hunger += 5
                                    self.game_state.player.regenerate_start_time = 0
                                    self.game_state.player.regenerate_val = True
                                else:
                                    self.game_state.screen.print("You are not holding a food item!")
                                # self.game_state.player.health_hunger_update()  # UPDATE HEALTH / HUNGER
                        else:
                            self.game_state.screen.print("You are not holding a food item!")
                    else:
                        self.game_state.screen.print("You are not holding a food item!")
                if event.key == pygame.K_1:
                    self.game_state.player.set_hotbar(0)
                if event.key == pygame.K_2:
                    self.game_state.player.set_hotbar(1)
                if event.key == pygame.K_3:
                    self.game_state.player.set_hotbar(2)
                if event.key == pygame.K_4:
                    self.game_state.player.set_hotbar(3)
                if event.key == pygame.K_5:
                    self.game_state.player.set_hotbar(4)
                if event.key == pygame.K_6:
                    self.game_state.player.set_hotbar(5)
                if event.key == pygame.K_7:
                    self.game_state.player.set_hotbar(6)
                if event.key == pygame.K_8:
                    self.game_state.player.set_hotbar(7)
                if event.key == pygame.K_9:
                    self.game_state.player.set_hotbar(8)
                if event.key == pygame.K_0:
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
        global true_play_time

        if self.game_state.player.dimension == "Underground" and not self.game_state.world.is_underground_generated:
            self.next_screen = UndergroundGeneratingScreen(self.display, self.context, self.game_state)
            return

        if not self.game_state.screen.isTyping:

            if self.game_state.player.dead: # kill player
                minute = int(play_time_seconds // 60)
                seconds = int(round(play_time_seconds % 60))
                true_play_time = "Time Played:   " + str(minute) + "m " + str(seconds) + "s"
                pygame.quit()
                self.next_screen = None # stop the loop
                # TODO: go to death screen
                return

            if self.game_state.player.isBreaking:
                self.game_state.player.breaking(fps)

            self.game_state.player.move()  # Move self.game_state.player

        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]: #Scroll Up
                self.game_state.screen.scroll_up()
            elif keys[pygame.K_DOWN]: #Scroll Down
                self.game_state.screen.scroll_down()

        self.display.fill((0, 0, 0))  # Fill world_map border black
        world_map.fill(self.game_state.background)  # Fill world_map background colour
        self.game_state.player.health_update(frame_count)  # Update self.game_state.player Health
        self.game_state.world.render_chunks(self.game_state.player.left, self.game_state.player.right, self.game_state.player.top, self.game_state.player.bottom)  # Generate list of all chunks that are loaded
        self.game_state.world.generate_chunks(self.game_state.player.dimension)  # Generate Chunks that are loaded but have not been generated before
        self.game_state.world.render(world_map, self.context, self.game_state.player.dimension, self.game_state.player.left, self.game_state.player.top, self.game_state.player.rect, self.game_state.player.breaking_time, self.game_state.player.target)  # Render all world_map blocks to world_map
        self.game_state.player.remove_items() #Remove Items if their number is 0
        self.game_state.player.render(self.context, world_map, SCREEN_WIDTH, SCREEN_HEIGHT, fps)  # Render self.game_state.player and self.game_state.player accessories to world_map
        self.game_state.timer.render(world_map, play_time_seconds)
        advancements_update(self.game_state.screen, self.game_state.timer, self.game_state.player.advancements, self.game_state.player.inventory.items, self.game_state.player.armour.items, self.game_state.player.dimension)  # Update Advancements
        self.game_state.screen.render(world_map) #Render Text self.game_state.screen

        # general rendering
        self.display.blit(world_map, (0, 0))  # Render map to display
        pygame.display.flip()  # Update Display
        return


class InventoryScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.armour.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.craft_interface.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.craft_interface.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.armour.render(world_map, self.context, mouse, is_holding) #Render Armour Grid for self.game_state.player
        self.game_state.player.craft_interface.render(world_map, self.context, mouse, is_holding) #Render Small Crafting Grid
        self.game_state.player.craft_interface.update() #Update Small 2x2 Crafting Grid

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class CraftingScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.crafting_grid.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.crafting_grid.handle_right_click(mouse, self.game_state.player.holding_item) 

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.crafting_grid.render(world_map, self.context, mouse, is_holding) #Render 3x3 Crafting Grid
        self.game_state.player.crafting_grid.update()  #Update 3x3 Crafting Grid

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class SmeltingScreen(Interface):
    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.furnace.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.furnace.handle_right_click(mouse, self.game_state.player.holding_item) 

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.furnace.render(world_map, self.context, mouse, fps, is_holding) #Render Furnace Interface
        self.game_state.player.furnace.smelt(self.context, fps, self.game_state.player.experience) #Furnace Smelting

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class EnchantingScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.enchanting_table.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.experience, self.game_state.rng)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.enchanting_table.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.enchanting_table.render(world_map, self.context, mouse, is_holding) #Render Enchanting Table Interface

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class CompressingScreen(Interface):
    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.compressor.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.compressor.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.compressor.render(world_map, self.context, mouse, fps, is_holding) #Render Compressor Interface
        self.game_state.player.compressor.compress(fps) #Compressing Process

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class GrindstoneScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.next_screen = GameScreen(self.display, self.context, self.game_state)
            elif event.key == pygame.K_1: #1
                self.game_state.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.game_state.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.game_state.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.game_state.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.game_state.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.game_state.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.game_state.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.game_state.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.game_state.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.game_state.player.inventory.handle_left_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.grindstone.handle_left_click(mouse, self.game_state.player.holding_item, self.game_state.player.inventory, self.game_state.player.experience)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.game_state.player.inventory.handle_right_click(mouse, self.game_state.player.holding_item)
                self.game_state.player.grindstone.handle_right_click(mouse, self.game_state.player.holding_item)

        return

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.game_state.player.holding_item.item is not None
        self.game_state.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.game_state.player.grindstone.render(world_map, self.context, mouse, is_holding) #Render Grindstone Interface
        self.game_state.player.grindstone.repair_and_disenchant() #Update repaired/disenchanted item

        self.game_state.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.game_state.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display
        return


class OverworldGeneratingScreen(Interface):
    """
        Screen shown when the overworld is first generated upon world startup
    """
    def handle_event(self, event: pygame.event.Event) -> None:
        return super().handle_event(event)

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

        # go to game screen
        self.next_screen = GameScreen(self.display, self.context, self.game_state)
        return


class UndergroundGeneratingScreen(Interface):
    """
        Screen shown when user first enters the underground dimension
    """
    def handle_event(self, event: pygame.event.Event) -> None:
        return super().handle_event(event)

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
        game_version_surface = game_version_font.render("v0.9.0a4", False, (0, 0, 0))
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

        pygame.display.flip()


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

        pygame.display.flip()


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

        pygame.display.flip()


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

        pygame.display.flip()


def main() -> None:
    """
        Main event loop for the game, also the entry point for the program
    """
    global play_time_seconds, true_play_time

    pygame.init()  # Initialise Pygame Module

    display = pygame.display.set_mode((750, 750))  # Set display
    pygame.display.set_caption(VERSION)  # Set title
    clock = pygame.time.Clock()
    clock.get_time()
    context = create_context()

    true_play_time = ""

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
        )
    )

    while current_screen is not None:

        clock.tick(60) # maximum FPS of 60
        frame_count += 1 # increment no. of frames
        fps = clock.get_fps()
        play_time_seconds = pygame.time.get_ticks() / 1000.0 # in seconds 

        # TODO:
        # furnace and compressor now do not update when user is not on the screen
        # separate update logic to rendering logic and make update a player method

        # TODO:
        # fix speedrun timer start point to be when game loads

        # TODO:
        # add death screen

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

        if current_screen.game_state.rng is not None and not pygame.mixer.music.get_busy():
            if current_screen.game_state.rng.next_random(1, 500) == 1:
                pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()

# def exit_death_screen():
#     global death_window
#     death_window.destroy()
#     title_screen()


# def death_screen():
#     global death_window, true_play_time
#     death_window = tkinter.Tk()
#     death_window.title("Tilecraft Beta 1.0 Pre-Release 3")
#     death_window.geometry("500x500")
#     death_window.configure(bg='#FFCCCB')

#     font = tkinter.font.Font(size=45, family='Minecraft')
#     font2 = tkinter.font.Font(size=30, family='Minecraft')
#     font3 = tkinter.font.Font(size=30, family='Avenir')

#     death_title = tkinter.Label(death_window, text="You Died!", fg='black', font=font, bg='#FFCCCB')
#     death_title.place(x=150, y=0)

#     death_reason = tkinter.Label(death_window, text="Death reason:   Starvation", fg='black', font=font3, bg='#FFCCCB')
#     death_reason.place(x=50, y=150)

#     time_played = tkinter.Label(death_window, text=true_play_time, fg='black', font=font3, bg='#FFCCCB')
#     time_played.place(x=50, y=200)

#     back_to_title_screen = tkinter.Button(death_window, font=font2, text="Back to Title Screen", width=20, height=3,
#                                           fg='black', command=exit_death_screen)
#     back_to_title_screen.place(x=50, y=300)

#     death_window.mainloop()
