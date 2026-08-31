from __future__ import annotations

import tkinter
import tkinter.font
import random
import math
from typing import Optional
from dataclasses import dataclass

import pygame

from tilecraft import ASSETS_DIR, VERSION
from .cheats import print_cheats, give, enchant, teleport, experience
from .constants import ITEM_TYPES, Item, RandomNumberGenerator, Context, create_context
from .generation import UndergroundGeneratePortal
from .player import Player
from .world import TilecraftWorld


class SpeedrunTimer:
    def __init__(self, load_val: str):
        self.font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 25)
        self.enabled = (load_val in ("Music Player", "God Gear"))
        self.running = True 
        self.latest_time_string = ""

    def render(self, display: pygame.Surface, play_time: float):
        if not self.enabled:
            return

        if self.running:
            if play_time // 3600 >= 10:  # HOURS 2 digits
                HourTime = str(int(play_time // 3600))
            else:  # HOURS 1 digit
                HourTime = f"0{int(play_time // 3600)}"
            if play_time // 60 >= 10:  # MINUTES 2 digits
                MinuteTime = str(int(play_time // 60))
            else:  # MINUTES 1 digit
                MinuteTime = f"0{int(play_time // 60)}"
            if play_time % 60 >= 10:  # SECONDS 2 digits
                SecondTime = str(round(play_time % 60))
            else:  # SECONDS 1 digit
                SecondTime = f"0{round(play_time % 60)}"
            MSecondTime = (round(play_time, 3) - math.floor(play_time)) * 1000  # Milliseconds
            if MSecondTime >= 100:  # 3 digits
                MSecondTime = str(int(MSecondTime))
            elif MSecondTime >= 10:  # 2 digits
                MSecondTime = f"0{int(MSecondTime)}"
            else:  # 1 digit
                MSecondTime = f"00{int(MSecondTime)}"
            self.latest_time_string = HourTime + ":" + MinuteTime + ":" + SecondTime + '.' + MSecondTime  # Current in-game time

        display.blit(
            self.font.render( self.latest_time_string, True, (0, 0, 0), (255, 255, 255)), 
            (504 - (13 * len(self.latest_time_string)), 0)
        ) #Render Speedrun Timer


#Check for completed advancements
def advancements_update(screen: Screen, timer: SpeedrunTimer, advancements, inventory_list, armour_list, dimension):
    name_list = []
    enchantments_list = []
    for i in inventory_list: #Compile list of item names and enchantments
        if i is not None:
            name_list.append(i.name)
            enchantments_list.append(i.enchantments)
        else:
            name_list.append(None)
            enchantments_list.append(None)
    armour_enchantment_list = []
    for i in armour_list: #Compile list of enchantments for armour list
        if i is not None:
            armour_enchantment_list.append(i.enchantments)
        else:
            armour_enchantment_list.append(None)

    if "Stone Age" not in advancements and "Cobblestone" in name_list: #Get Cobblestone
        advancements.append("Stone Age")
        screen.print("Advancement unlocked: Stone Age")
    if "Getting an Upgrade" not in advancements and "Stone Pickaxe" in name_list: #Get a Stone Pickaxe
        advancements.append("Getting an Upgrade")
        screen.print("Advancement unlocked: Getting an Upgrade")
    if "Into the Depths" not in advancements and dimension == "Underground": #Enter the underground
        screen.print("Advancement unlocked: Into the Depths")
        advancements.append("Into the Depths")
    if "Acquire Hardware" not in advancements and "Iron Ingot" in name_list: #Get an Iron Ingot
        advancements.append("Acquire Hardware")
        screen.print("Advancement unlocked: Acquire Hardware")
    if "Isn't it Iron Pick" not in advancements and "Iron Pickaxe" in name_list: #Get an Iron Pickaxe
        advancements.append("Isn't it Iron Pick")
        screen.print("Advancement unlocked: Isn't it Iron Pick")
    if ("Suit Up" not in advancements) and ("Tier 1 Iron Plate" in name_list or "Tier 2 Iron Plate" in name_list or "Tier 3 Iron Plate" in name_list): #Get Iron Armour
        advancements.append("Suit Up")
        screen.print("Advancement unlocked: Suit Up")
    if "Diamonds!" not in advancements and "Diamond" in name_list: #Get Diamonds
        advancements.append("Diamonds!")
        screen.print("Advancement unlocked: Diamonds!")
    if ("Cover Me with Diamonds" not in advancements) and ("Tier 1 Diamond Plate" in name_list or "Tier 2 Diamond Plate" in name_list or "Tier 3 Diamond Plate" in name_list): #Get Diamond Armour
        advancements.append("Cover Me with Diamonds")
        screen.print("Advancement unlocked: Cover Me with Diamonds")
    if "Ice Bucket Challenge" not in advancements and "Obsidian" in name_list: #Get Obsidian
        advancements.append("Ice Bucket Challenge")
        screen.print("Advancement unlocked: Ice Bucket Challenge")
    if "We Need to Go Deeper" not in advancements and dimension == 'Nether': #Go to the Nether
        screen.print("Advancement unlocked: We Need to Go Deeper")
        advancements.append("We Need to Go Deeper")
    for i in enchantments_list:
        if i is not None and "Enchanter" not in advancements: #Get an enchanted tool or armour piece
            advancements.append("Enchanter")
            screen.print("Advancement unlocked: Enchanter")
            break

    max_t1 = False
    max_t2 = False
    max_t3 = False

    if armour_list[0] is not None:
        if armour_list[0].enchantments is not None:
            if armour_list[0].name == 'Tier 1 Diamond Plate' and armour_list[0].enchantments == [['Protection', 5], ['Unbreaking', 3]]:
                max_t1 = True
    if armour_list[1] is not None:
        if armour_list[1].enchantments is not None:
            if armour_list[1].name == 'Tier 2 Diamond Plate' and armour_list[1].enchantments == [['Protection', 5], ['Unbreaking', 3]]:
                max_t2 = True
    if armour_list[2] is not None:
        if armour_list[2].enchantments is not None:
            if armour_list[2].name == 'Tier 3 Diamond Plate' and armour_list[2].enchantments == [['Protection', 5], ['Unbreaking', 3]]:
                max_t3 = True
    if max_t1 and max_t2 and max_t3 and 'God Gear' not in advancements: #Get a full set of Protection V Unbreaking III Diamond Armour
        advancements.append("God Gear")
        screen.print("Advancement unlocked: God Gear")
        timer.running = False

    return advancements

def MusicPlayer(screen: Screen, timer: SpeedrunTimer, advancements):
    if "Music Player" not in advancements:  # Music Player: Play Pigstep
        advancements.append("Music Player")
        screen.print("Advancement unlocked: Music Player")
        timer.running = False
    return advancements


class Screen:
    def __init__(self, game_state: GameState):
        self.x = 0
        self.y = 570
        self.input_line = 0
        self.print_list = []
        self.isTyping = False
        self.typingText = ''
        self.position = 0
        self.foretext = ''
        self.timer = 0

        self.game_state = game_state 

    def scroll_up(self):
        if self.position < len(self.print_list) - 15:
            self.position += 1

    def scroll_down(self):
        if self.position > 0:
            self.position -= 1

    def start_typing(self, text):
        self.input_line = 15
        self.isTyping = True
        self.foretext = text
        self.timer = 0

    def type(self, char):
        self.typingText += char

    def stop_typing(self):
        self.input_line = 0
        self.isTyping = False
        length = len(list(ITEM_TYPES.keys())) - 1
        if self.foretext == f'Item ID (0 - {length}): ':
            self.game_state.player.inventory.add(give(self, self.typingText))
            self.foretext = ''
        elif self.foretext == 'Coordinates (X,Y): ':
            self.game_state.player.x, self.game_state.player.y = teleport(self, self.game_state.player.x, self.game_state.player.y, self.typingText)
            self.foretext = ''
        elif self.foretext == "Enchantment (Name, Lvl): ":
            item = enchant(self, self.game_state.player.inventory, self.typingText)
            if item is not None:
                self.game_state.player.inventory.hotbar_item = item
            self.foretext = ''
        elif self.foretext == "Experience Level: ":
            experience(self, self.game_state.player.experience, self.typingText)
            self.foretext = ''
        else:
            self.text_validate()
        self.typingText = ''
        self.position = 0

    def delete(self):
        self.typingText = self.typingText[0:-1]

    def text_validate(self):
        if len(self.typingText) != 0:
            if self.typingText[0] == '/':
                self.typingText = self.typingText.replace(' ', '')  # REMOVE WHITESPACES
                if ',' in self.typingText and self.typingText[-1] != ',':
                    comma = self.typingText.index(',')
                    number = self.typingText[comma + 1:len(self.typingText)]
                    self.typingText = self.typingText[0: comma]
                    try:
                        number = int(number)
                        # Prevent crashes by limiting number size
                        commands(number, self.typingText, self.game_state)
                    except ValueError:
                        self.print("Invalid integer")
                else:
                    number = 1  # Set number to 1 when number is not specified
                    commands(number, self.typingText, self.game_state)
            # Regular text message
            else:
                self.print(f"<Player> {self.typingText}")

    def print(self, text):
        self.timer = 0
        self.print_list.append(text)

    def render(self, display: pygame.Surface):
        if self.timer == 600:
            return

        if len(self.print_list) <= 16:
            screen_list = self.print_list[:]
            height = len(self.print_list) * 15 + self.input_line
        else:
            if self.position == 0:
                screen_list = self.print_list[-16 - self.position:]
                height = 16 * 15 + self.input_line
            else:
                screen_list = self.print_list[-16 - self.position: 0 - self.position]
                height = 16 * 15 + self.input_line

        screen_list.reverse()
        width = 375
        x = self.x
        y = self.y - height
        surface = pygame.Surface((width, height))
        surface.fill((125, 125, 125))
        surface.set_alpha(200)
        display.blit(surface, (x, y))

        font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 18)
        for i in range(len(screen_list)):
            display.blit(font.render(screen_list[i], False, (255, 255, 255)), (x, y + height - (i + 1) * 15 - self.input_line))
        display.blit(font.render(self.foretext + self.typingText, True, (255, 255, 255)), (x, y + height - 15))

        self.timer += 1


@dataclass
class GameState:
    """
        Struct containing all game state fields
    """
    screen: Screen
    player: Player
    world: TilecraftWorld
    timer: SpeedrunTimer
    rng: RandomNumberGenerator
    seed: int
    background: tuple[int, int, int]
    load: str


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

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
            Handle an event, returning an optional signal to the title screen
        """

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
        """
            Render the screen, returning an optional signal to the title screen
        """


class GameScreen(Interface):
    """
        Main game window
    """

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if not self.game_state.screen.isTyping:
            # QUIT Key
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'title screen'
            # Specify key types (key down)
            elif event.type == pygame.KEYDOWN:
                # Escape key (QUIT)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return 'title screen'
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


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
        global true_play_time

        if self.game_state.player.dimension == "Underground" and not self.game_state.world.is_underground_generated:
            self.next_screen = UndergroundGeneratingScreen(self.display, self.context, self.game_state)
            return

        if not self.game_state.screen.isTyping:
            # Kill self.game_state.player
            if self.game_state.player.dead:
                minute = int(play_time_seconds // 60)
                seconds = int(round(play_time_seconds % 60))
                true_play_time = "Time Played:   " + str(minute) + "m " + str(seconds) + "s"
                pygame.quit()
                return 'death screen'
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
        self.game_state.player.render(self.context, world_map, screen_width, screen_height, fps)  # Render self.game_state.player and self.game_state.player accessories to world_map
        self.game_state.timer.render(world_map, play_time_seconds)
        advancements_update(self.game_state.screen, self.game_state.timer, self.game_state.player.advancements, self.game_state.player.inventory.items, self.game_state.player.armour.items, self.game_state.player.dimension)  # Update Advancements
        self.game_state.screen.render(world_map) #Render Text self.game_state.screen

        # general rendering
        self.display.blit(world_map, (0, 0))  # Render map to display
        pygame.display.flip()  # Update Display
        return


class InventoryScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
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

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
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
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        return super().handle_event(event)

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:

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
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        return super().handle_event(event)

    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:

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


# Game Loop
def main(display: pygame.Surface, clock: pygame.time.Clock, context: Context, load: str) -> Optional[str]:
    global play_time_seconds

    world = pygame.Surface((750, 750))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    rng = RandomNumberGenerator(seed := GetSeed())
    timer: SpeedrunTimer = SpeedrunTimer(load)
    frame_count = 0

    # start by generating the overworld
    current_screen: Interface = OverworldGeneratingScreen(
        display = display,
        context = context,
        game_state = GameState(screen=None, player=None, world=None, timer=timer, rng=rng, seed=seed, background=(255, 255, 255), load=load)
    )

    while True:

        clock.tick(60) # maximum FPS of 60
        frame_count += 1 # increment no. of frames
        fps = clock.get_fps()
        play_time_seconds = pygame.time.get_ticks() / 1000.0 # in seconds 

        # TODO:
        # furnace and compressor now do not update when user is not on the screen
        # separate update logic to rendering logic and make update a player method

        # event loop
        for event in pygame.event.get():
            ret = current_screen.handle_event(event)
            if ret is not None:
                return ret

        # render screen
        ret = current_screen.render(world, fps, frame_count)
        if ret is not None:
            return ret

        # screen transition
        if current_screen.next_screen is not current_screen:
            current_screen = current_screen.next_screen

        if not pygame.mixer.music.get_busy():
            if rng.next_random(1, 500) == 1:
                pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()


def create_world():
    global true_play_time

    pygame.init()  # Initialise Pygame Module
    display = pygame.display.set_mode((750, 750))  # Set display
    pygame.display.set_caption(VERSION)  # Set title
    clock = pygame.time.Clock()
    clock.get_time()
    context = create_context()

    load = optionData()
    Quit()
    true_play_time = ""

    signal = main(display, clock, context, load)  #Start Game by Calling the Main Loop

    if signal == 'title screen':
        title_screen()
    elif signal == 'death screen':
        death_screen()


def commands(number: int, val: str, game_state: GameState):
    """
        Legcay commands and cheat commands to play the game
        This is to be gradually deprecated in favour of new game mechanics
    """

    if number < 1 or number > 16:
        game_state.screen.print("ERROR: Invalid Integer")
        return

    for _ in range(number):

        # Loot Village Hay
        if val == "/lootvillagehay":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            if game_state.player.inventory.hotbar_item is None:
                game_state.screen.print("Require Stone Hoe")
                return
            if game_state.player.inventory.hotbar_item.name != "Stone Hoe":
                game_state.screen.print("Require Stone Hoe")
                return
            for j in range(len(game_state.world.bound_village)):
                if (game_state.world.bound_village[j][0][0] < game_state.player.x < game_state.world.bound_village[j][0][2]) and (
                        game_state.world.bound_village[j][1][0] < game_state.player.y < game_state.world.bound_village[j][1][2]):
                    hay = game_state.rng.next_random(25, 45)
                    game_state.player.inventory.add(Item("Hay Bale", hay, None, None))
                    game_state.screen.print("+" + str(hay) + " Hay Bale")
                    actualX = game_state.world.bound_village[j][0][1]
                    actualY = game_state.world.bound_village[j][1][1]
                    game_state.world.empty_vil1.append([actualX, actualY])
                    game_state.world.bound_village.remove(game_state.world.bound_village[j])
                    try_set_empty_village(game_state.world, actualX, actualY)
                    return
            else:
                game_state.screen.print("You are not at a village")

        # Loot Village Beds
        elif val == "/lootvillagebeds":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            for j in range(len(game_state.world.bound_village2)):
                if (game_state.world.bound_village2[j][0][0] < game_state.player.x < game_state.world.bound_village2[j][0][2]) and (
                        game_state.world.bound_village2[j][1][0] < game_state.player.y < game_state.world.bound_village2[j][1][2]):
                    beds = game_state.rng.next_random(2, 7)
                    game_state.player.inventory.add(Item("Bed", beds, None, None))
                    game_state.screen.print("+" + str(beds) + " Beds")
                    actualX = game_state.world.bound_village2[j][0][1]
                    actualY = game_state.world.bound_village2[j][1][1]
                    game_state.world.empty_vil2.append([actualX, actualY])
                    game_state.world.bound_village2.remove(game_state.world.bound_village2[j])
                    try_set_empty_village(game_state.world, actualX, actualY)
                    return
            else:
                game_state.screen.print("You are not at a village")

        # Loot Village Blacksmith
        elif val == "/lootvillageblacksmith":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            for j in range(len(game_state.world.bound_village3)):
                if (game_state.world.bound_village3[j][0][0] < game_state.player.x < game_state.world.bound_village3[j][0][2]) and (game_state.world.bound_village3[j][1][0] < game_state.player.y < game_state.world.bound_village3[j][1][2]):

                    # GENERATE IRON VALUES
                    for k in range(5):
                        if k == 1 or k == 2 or k == 3:
                            bool_blacksmith_iron = True
                            break
                        else:
                            bool_blacksmith_iron = False
                    if bool_blacksmith_iron:
                        blacksmith_iron = game_state.rng.next_random(1, 7)
                    else:
                        blacksmith_iron = 0

                    # GENERATE DIAMOND VALUES
                    for k in range(10):
                        if k == 1 or k == 2 or k == 3 or k == 4:
                            bool_blacksmith_diamond = True
                            break
                        else:
                            bool_blacksmith_diamond = False
                    if bool_blacksmith_diamond:
                        blacksmith_diamond = game_state.rng.next_random(1, 5)
                    else:
                        blacksmith_diamond = 0

                    # GENERATE BREAD VALUES
                    for k in range(3):
                        if k == 1 or k == 2:
                            bool_blacksmith_bread = True
                            break
                        else:
                            bool_blacksmith_bread = False
                    if bool_blacksmith_bread:
                        blacksmith_bread = game_state.rng.next_random(1, 14)
                    else:
                        blacksmith_bread = 0

                    # UPDATE AND PRINT INVENTORY VALUES
                    if blacksmith_iron > 0:
                        game_state.screen.print(f"+{blacksmith_iron} Iron Ingot")
                        game_state.player.inventory.add(Item("Iron Ingot", blacksmith_iron, None, None))
                    if blacksmith_diamond > 0:
                        game_state.screen.print(f"+{blacksmith_diamond} Diamond")
                        game_state.player.inventory.add(Item("Diamond", blacksmith_diamond, None, None))
                    if blacksmith_bread > 0:
                        game_state.screen.print(f"+{blacksmith_bread} Bread")
                        game_state.player.inventory.add(Item("Bread", blacksmith_bread, None, None))

                    actualX = game_state.world.bound_village3[j][0][1]
                    actualY = game_state.world.bound_village3[j][1][1]
                    game_state.world.empty_vil3.append([actualX, actualY])
                    game_state.world.bound_village3.remove(game_state.world.bound_village3[j])
                    try_set_empty_village(game_state.world, actualX, actualY)
                    return
            else:
                game_state.screen.print("You are not at a village")

        # Loot Village Library
        elif val == "/lootvillagelibrary":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            for j in range(len(game_state.world.bound_village4)):
                if (game_state.world.bound_village4[j][0][0] < game_state.player.x < game_state.world.bound_village4[j][0][2]) and (game_state.world.bound_village4[j][1][0] < game_state.player.y < game_state.world.bound_village4[j][1][2]):
                    library_bookshelf = game_state.rng.next_random(1, 3)
                    library_books = game_state.rng.next_random(7, 14)
                    game_state.screen.print(f"+{library_bookshelf} Bookshelf")
                    game_state.screen.print(f"+{library_books} Books")
                    game_state.player.inventory.add(Item("Bookshelf", library_bookshelf, None, None))
                    game_state.player.inventory.add(Item("Book", library_books, None, None))
                    actualX = game_state.world.bound_village4[j][0][1]
                    actualY = game_state.world.bound_village4[j][1][1]
                    game_state.world.empty_vil4.append([actualX, actualY])
                    game_state.world.bound_village4.remove(game_state.world.bound_village4[j])
                    try_set_empty_village(game_state.world, actualX, actualY)
                    return
            else:
                game_state.screen.print("You are not at a village")

        # Enter Nether Dimension
        elif val == "/dimensionnether":
            for j in range(len(game_state.world.bound_overworld_portal)):
                if (game_state.world.bound_overworld_portal[j][0][0] < game_state.player.x < game_state.world.bound_overworld_portal[j][0][2]) and (
                        game_state.world.bound_overworld_portal[j][1][0] < game_state.player.y < game_state.world.bound_overworld_portal[j][1][2]) and game_state.player.dimension == 'Overworld':
                    game_state.player.dimension = 'Nether'
                    game_state.screen.print("Entering Nether Dimension...")
                    actualX = game_state.world.bound_overworld_portal[j][0][1]
                    actualY = game_state.world.bound_overworld_portal[j][1][1]
                    game_state.background = (255, 153, 153)
                    game_state.player.x /= 8
                    game_state.player.y /= 8
                    game_state.world.generateNether(game_state.player.x, game_state.player.y)
                    if actualX / 8 not in game_state.world.nether_portal or actualY / 8 not in game_state.world.nether_portal:
                        # Generating Nether Portal coordinates (IN NETHER) and bounding box
                        game_state.world.nether_portal.append([actualX / 8, actualY / 8])
                        game_state.world.bound_nether_portal.append([
                            [actualX / 8 - 10 / 16, actualX / 8, actualX / 8 + 10 / 16],
                            [actualY / 8 - 10 / 16, actualY / 8, actualY / 8 + 10 / 16]
                        ])
                    return
            else:
                game_state.screen.print("You are not at a nether portal")

        # Enter Overworld Dimension
        elif val == "/dimensionoverworld":
            if game_state.player.dimension != 'Nether':
                game_state.screen.print("You are already in the overworld")
                return
            for j in range(len(game_state.world.bound_nether_portal)):
                if (game_state.world.bound_nether_portal[j][0][0] < game_state.player.x < game_state.world.bound_nether_portal[j][0][2]) and (
                        game_state.world.bound_nether_portal[j][1][0] < game_state.player.y < game_state.world.bound_nether_portal[j][1][2]):
                    game_state.player.dimension = 'Overworld'
                    game_state.screen.print("Entering Overworld Dimension...")
                    actualX = game_state.world.bound_nether_portal[j][0][1]
                    actualY = game_state.world.bound_nether_portal[j][1][1]
                    game_state.background = (255, 255, 255)
                    game_state.player.x *= 8
                    game_state.player.y *= 8
                    return
            else:
                game_state.screen.print("You are not at a nether portal")

        # Loot Bastion
        elif val == "/lootbastion":
            if game_state.player.dimension != 'Nether':
                game_state.screen.print("You are not in the nether")
                return
            for j in range(len(game_state.world.bound_bastion)):
                if (game_state.world.bound_bastion[j][0][0] < game_state.player.x < game_state.world.bound_bastion[j][0][2]) and (
                        game_state.world.bound_bastion[j][1][0] < game_state.player.y < game_state.world.bound_bastion[j][1][2]):
                    game_state.player.inventory.add(Item("Pigstep Disc", 1, None, None))
                    game_state.screen.print("+1 Pigstep Disc")
                    actualX = game_state.world.bound_bastion[j][0][1]
                    actualY = game_state.world.bound_bastion[j][1][1]
                    game_state.world.empty_bastion.append([actualX, actualY])
                    game_state.world.bound_bastion.remove(game_state.world.bound_bastion[j])
                    break
            else:
                game_state.screen.print("You are not at a bastion.")

        # Play Pigstep Music Disc
        elif val == "/playpigstep":

            # Declare Variables
            pigstep_disc_bool = False
            jukebox_bool = False

            for i in game_state.player.inventory.items:
                if i is not None:
                    if i.name == "Pigstep Disc":  # Pigstep Disc
                        pigstep_disc_bool = True
                        break
            for i in game_state.player.inventory.items:
                if i is not None:
                    if i.name == "Jukebox":  # Jukebox
                        jukebox_bool = True
                        break

            if pigstep_disc_bool and jukebox_bool:  # Play Pigstep
                pygame.mixer.init()
                pygame.mixer.music.load(str(ASSETS_DIR / "pigstep.mp3"))
                pygame.mixer.music.set_volume(10)
                pygame.mixer.music.play()
                MusicPlayer(game_state.screen, game_state.timer, game_state.player.advancements) #Update Advancement and Speedrun Details
            else:
                game_state.screen.print("Error: Not Enough Resources")

        # Loot Ruined Portal
        elif val == "/lootruinedportal":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            for j in range(len(game_state.world.bound_ruined_portal)):
                if (game_state.world.bound_ruined_portal[j][0][0] < game_state.player.x < game_state.world.bound_ruined_portal[j][0][2]) and (
                        game_state.world.bound_ruined_portal[j][1][0] < game_state.player.y < game_state.world.bound_ruined_portal[j][1][2]):
                    R_iron_val = game_state.rng.next_random(2, 7)
                    R_flint_val = game_state.rng.next_random(1, 3)
                    R_golden_carrot_val = game_state.rng.next_random(0, 6)
                    R_golden_apple_val = game_state.rng.next_random(0, 2)
                    R_obsidian_val = game_state.rng.next_random(0, 3)
                    game_state.player.inventory.add(Item("Iron Ingot", R_iron_val, None, None))  # Add Iron Ingot
                    game_state.screen.print(f"+{R_iron_val} Iron Ingot")
                    game_state.player.inventory.add(Item("Flint", R_flint_val, None, None))  # Add Flint
                    game_state.screen.print(f"+{R_flint_val} Flint")
                    if R_golden_carrot_val > 0:  # Add Golden Carrot
                        game_state.screen.print(f"+{R_golden_carrot_val} Golden Carrot")
                        game_state.player.inventory.add(Item("Golden Carrot", R_golden_carrot_val, None, None))
                    if R_golden_apple_val > 0:  # Add Golden Apple
                        game_state.screen.print(f"+{R_golden_apple_val} Golden Apple")
                        game_state.player.inventory.add(Item("Golden Apple", R_golden_apple_val, None, None))
                    if R_obsidian_val > 0:  # Add Obsidian
                        game_state.screen.print(f"+{R_obsidian_val} Obsidian")
                        game_state.player.inventory.add(Item("Obsidian", R_obsidian_val, None, None))
                    actualX = game_state.world.bound_ruined_portal[j][0][1]
                    actualY = game_state.world.bound_ruined_portal[j][1][1]
                    game_state.world.empty_ruined_portal1.append([actualX, actualY])
                    game_state.world.bound_ruined_portal.remove(game_state.world.bound_ruined_portal[j])
                    try_set_empty_ruined_portal(game_state.world, actualX, actualY)
                    break
            else:
                game_state.screen.print("You are not at a ruined portal")

        # Complete Ruined Portal
        elif val == "/portalcomplete":
            if game_state.player.dimension != "Overworld":
                game_state.screen.print("You are not in the overworld")
                return
            for j in range(len(game_state.world.bound_ruined_portal2)):
                if (game_state.world.bound_ruined_portal2[j][0][0] < game_state.player.x < game_state.world.bound_ruined_portal2[j][0][2]) and (
                        game_state.world.bound_ruined_portal2[j][1][0] < game_state.player.y < game_state.world.bound_ruined_portal2[j][1][2]):
                    obsidian_num = 10 - game_state.world.obsidian_counts[
                        j]  # Set number of obsidian remaining to complete the portal (max. 5)
                    flint_and_steel_bool = False
                    obsidian_bool = False

                    for i in game_state.player.inventory.items:
                        if i is not None:
                            if i.name == 'Flint and Steel':  # Test for flint and steel
                                flint_and_steel_bool = True
                                break
                    if obsidian_num == 0:
                        obsidian_bool = True
                    for i in game_state.player.inventory.items:
                        if i is not None:
                            if i.name == "Obsidian" and i.number >= obsidian_num:  # Test for enough obsidian
                                obsidian_index = game_state.player.inventory.items.index(i)
                                obsidian_bool = True
                                break

                    if flint_and_steel_bool and obsidian_bool:
                        if obsidian_num > 0:
                            game_state.player.inventory.items[obsidian_index].number -= obsidian_num
                            game_state.screen.print(f"-{obsidian_num} Obsidian")
                            game_state.screen.print("Ruined Portal has been completed")
                        else:
                            game_state.screen.print("Portal is already complete")
                        actualX = game_state.world.bound_ruined_portal2[j][0][1]
                        actualY = game_state.world.bound_ruined_portal2[j][1][1]
                        game_state.world.empty_ruined_portal2.append([actualX, actualY])
                        game_state.world.bound_ruined_portal2.remove(game_state.world.bound_ruined_portal2[j])
                        game_state.world.overworld_portal.append([actualX, actualY])
                        game_state.world.bound_overworld_portal.append([[actualX - 10 / 16, actualX, actualX + 10 / 16],
                                                        [actualY - 10 / 16, actualY, actualY + 10 / 16]])
                        try_set_empty_ruined_portal(game_state.world, actualX, actualY)
                        break
                    elif obsidian_bool and not flint_and_steel_bool:
                        game_state.screen.print("Require Flint and Steel")
                        break
                    elif flint_and_steel_bool and not obsidian_bool:
                        game_state.screen.print(f"Require {obsidian_num} Obsidian")
                        break
                    else:
                        game_state.screen.print(f"Require {obsidian_num} Obsidian")
                        game_state.screen.print("Require Flint and Steel")
                        break
            else:
                game_state.screen.print("You are not at a ruined portal")

        # cheats datapack - list items
        elif val == "/table":
            if game_state.load == "Cheats":
                print_cheats(game_state.screen, list(ITEM_TYPES.keys()))
            else:
                game_state.screen.print("REQUIRE CHEATS DATAPACK")

        # cheats datapack - give item
        elif val == "/give":
            if game_state.load == "Cheats":
                length = len(list(ITEM_TYPES.keys())) - 1
                game_state.screen.start_typing(f"Item ID (0 - {length}): ")
            else:
                game_state.screen.print("REQUIRE CHEATS DATAPACK")

        # cheats datapack - teleport
        elif val == "/tp":
            if game_state.load == "Cheats":
                game_state.screen.start_typing("Coordinates (X,Y): ")
            else:
                game_state.screen.print("REQUIRE CHEATS DATAPACK")

        # cheats datapack - enchant an item
        elif val == "/enchant":
            if game_state.load == "Cheats":
                game_state.screen.start_typing("Enchantment (Name, Lvl): ")
            else:
                game_state.screen.print("REQUIRE CHEATS DATAPACK")
        
        # cheats datapack - give player experience points 
        elif val == "/experience":
            if game_state.load == "Cheats":
                game_state.screen.start_typing("Experience Level: ")
            else:
                game_state.screen.print("REQUIRE CHEATS DATAPACK")

        # default case
        else:
            game_state.screen.print("Invalid Function")


def try_set_empty_village(world: TilecraftWorld, actualX: int, actualY: int):
    """
        Try to mark a villge structure as empty
        actualX, actualY are the coordinates of the village
    """

    bool_empty_vil1 = False
    bool_empty_vil2 = False
    bool_empty_vil3 = False
    bool_empty_vil4 = False

    for i in range(len(world.empty_vil1)):
        if (actualX in world.empty_vil1[i]) and (actualY in world.empty_vil1[i]):
            bool_empty_vil1 = True
    for i in range(len(world.empty_vil2)):
        if (actualX in world.empty_vil2[i]) and (actualY in world.empty_vil2[i]):
            bool_empty_vil2 = True
    for i in range(len(world.empty_vil3)):
        if (actualX in world.empty_vil3[i]) and (actualY in world.empty_vil3[i]):
            bool_empty_vil3 = True
    for i in range(len(world.empty_vil4)):
        if (actualX in world.empty_vil4[i]) and (actualY in world.empty_vil4[i]):
            bool_empty_vil4 = True

    if bool_empty_vil1 and bool_empty_vil2 and bool_empty_vil3 and bool_empty_vil4:
        world.empty_vil_total.append([actualX, actualY])


def try_set_empty_ruined_portal(world: TilecraftWorld, actualX: int, actualY: int):
    """
        Try to mark a ruined portal structure as empty
        actualX, actualY are the coordinates of the ruined portal
    """

    bool_empty_ruined_portal1 = False
    bool_empty_ruined_portal2 = False
    for i in range(len(world.empty_ruined_portal1)):
        if (actualX in world.empty_ruined_portal1[i]) and (actualY in world.empty_ruined_portal1[i]):
            bool_empty_ruined_portal1 = True
    for i in range(len(world.empty_ruined_portal2)):
        if (actualX in world.empty_ruined_portal2[i]) and (actualY in world.empty_ruined_portal2[i]):
            bool_empty_ruined_portal2 = True
    if bool_empty_ruined_portal1 and bool_empty_ruined_portal2:
        world.empty_ruined_portal_total.append([actualX, actualY])


# Select data pack
def optionData():
    global tkvar2
    if tkvar2.get() == '"Music Player" Speedrun Data Pack':
        return 'Music Player'
    elif tkvar2.get() == '"God Gear" Speedrun Data Pack':
        return 'God Gear'
    elif tkvar2.get() == 'Cheats Data Pack':
        return 'Cheats'
    else:
        return 'None'

#Get the world seed
def GetSeed():
    global tkvar3
    text = tkvar3.get()
    if text != '':
        try:
            return int(text)
        except ValueError:
            return random.randint(-1 * 2 ** 16, 2 ** 16 - 1)
    else:
        return random.randint(-1 * 2 ** 16, 2 ** 16 - 1)

#Get the user's first click on entry box
def get_first_click(event):
    global first_click, tkvar3
    if first_click:
        first_click = False
        tkvar3.set('')

# Quit screen
def Quit():
    global window
    window.destroy()

#Function to exit patch notes screen
def BackToTitleScreen():
    global window1
    window1.destroy()
    title_screen()

#Patch Notes Screen
def patchnotes():
    global window1
    Quit()
    window1 = tkinter.Tk()
    window1.title(VERSION)
    window1.geometry('750x750')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=60)
    font = tkinter.font.Font(family='Minecraft', size=36)
    font2 = tkinter.font.Font(family='Minecraft', size=15)

    title = tkinter.Label(window1, text='Patch Notes', font=bold_font, fg='black')
    title.place(x=215, y=0)

    with open("docs/patch_notes.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window1, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=82, y=75)

    back_to_title_screen = tkinter.Button(window1, text='Title Screen', fg='black', font=font, command=BackToTitleScreen)
    back_to_title_screen.place(x=225, y=637)

    window1.mainloop()

#Function to exit How to Play Screen
def BackToTitleScreen2():
    global window2
    window2.destroy()
    title_screen()

#How to Play Screen
def howtoplay():
    global window2
    Quit()
    window2 = tkinter.Tk()
    window2.title(VERSION)
    window2.geometry('750x750')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=60)
    font = tkinter.font.Font(family='Minecraft', size=36)
    font2 = tkinter.font.Font(family='Minecraft', size=15)

    title = tkinter.Label(window2, text='How To Play', font=bold_font, fg='black')
    title.place(x=215, y=0)

    with open("docs/how_to_play.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window2, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=82, y=75)

    back_to_title_screen = tkinter.Button(window2, text='Title Screen', fg='black', font=font, command=BackToTitleScreen2)
    back_to_title_screen.place(x=225, y=637)

    window2.mainloop()

#Function to exit Credits Screen
def BackToTitleScreen3():
    global window3
    window3.destroy()
    title_screen()

#Credits Screen
def game_credits():
    global window3
    Quit()
    window3 = tkinter.Tk()
    window3.title(VERSION)
    window3.geometry('750x750')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=60)
    font = tkinter.font.Font(family='Minecraft', size=36)
    font2 = tkinter.font.Font(family='Minecraft', size=15)

    title = tkinter.Label(window3, text='Credits', font=bold_font, fg='black')
    title.place(x=262, y=0)

    with open("docs/credits.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window3, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=82, y=75)

    back_to_title_screen = tkinter.Button(window3, text='Title Screen', fg='black', font=font, command=BackToTitleScreen3)
    back_to_title_screen.place(x=225, y=637)

    window3.mainloop()

# Title Screen Function
def title_screen():
    global window, tkvar2, fontStyle2, fileMenu, startWorld, bg, bold_font, regular_font, fontStyle2, font4, tkvar3, first_click

    first_click = True #Set Variable to track when the user first clicked on the seed box

    # Play Minecraft Music
    pygame.mixer.init()
    pygame.mixer.music.load(random.choice([str(ASSETS_DIR / "music/song6.mp3"), str(ASSETS_DIR / "music/song8.mp3")]))
    pygame.mixer.music.play()

    # Create tkinter window
    window = tkinter.Tk()
    window.title(VERSION)
    window.geometry('750x750')

    global screen_width, screen_height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Create background image
    bg = tkinter.PhotoImage(file=str(ASSETS_DIR / "background_vB1_0_pre3.png"))

    # Create fonts
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=60)
    regular_font = tkinter.font.Font(family='Minecraft Regular', size=27)
    warning_font = tkinter.font.Font(family='Minecraft Regular', size=17)
    fontStyle2 = tkinter.font.Font(size=35, family='Minecraft Regular')
    font4 = tkinter.font.Font(size=20, family='Minecraft Regular')

    # Create canvas
    canvas1 = tkinter.Canvas(window, width=750, height=750)
    canvas1.create_image(0, 0, image=bg, anchor="nw")
    canvas1.create_text(375, 40, fill="black", font=bold_font, text="Tilecraft")
    canvas1.create_text(375, 75, fill="black", font=regular_font, text="Beta 1.0 Pre-Release 4")
    canvas1.create_text(375, 110, fill="red", font=warning_font, text="Warning! This is a pre-release version and contains many bugs.")
    canvas1.place(x=0, y=0)

    #Create Seed Box Entry Widget
    tkvar3 = tkinter.StringVar(window)
    tkvar3.set('World Seed: ')
    SeedBox = tkinter.Entry(window, textvariable=tkvar3)
    SeedBox.configure(width=39, fg='white', font=font4)
    SeedBox.place(x=120, y=150)

    # Create a tkinter variable
    tkvar2 = tkinter.StringVar(window)
    tkvar2.set('None')

    # Set choices for option menu
    choices = ['"Music Player" Speedrun Data Pack', '"God Gear" Speedrun Data Pack', 'Cheats Data Pack', 'None']

    # Option menu for datapacks
    fileMenu = tkinter.OptionMenu(window, tkvar2, *choices)
    fileMenu.configure(width=36, foreground='black', font=font4)
    fileMenu.place(x=120, y=187)

    # New World button
    startWorld = tkinter.Button(window, text="New World", command=create_world, width="20", height="2", font=fontStyle2,
                                foreground='black')
    startWorld.place(x=120, y=217)

    # How to play button
    htp = tkinter.Button(window, text="How to Play", width="20", height="2", font=fontStyle2, foreground='black', command=howtoplay)
    htp.place(x=120, y=292)

    # Patch Notes
    patch_notes = tkinter.Button(window, text="Patch Notes", width="20", height="2", font=fontStyle2, foreground='black', command=patchnotes)
    patch_notes.place(x=120, y=367)

    #Credits
    Credits = tkinter.Button(window, text="Credits", width="20", height="2", font=fontStyle2, foreground='black', command=game_credits)
    Credits.place(x=120, y=442)

    # Quit Button
    quit_button = tkinter.Button(window, text="Quit", command=Quit, width="20", height="2", font=fontStyle2, foreground='black')
    quit_button.place(x=120, y=517)

    #Clicking on Seedbox entry widget
    SeedBox.bind('<FocusIn>', get_first_click)

    # Tkinter main loop
    window.mainloop()


def exit_death_screen():
    global death_window
    death_window.destroy()
    title_screen()


def death_screen():
    global death_window, true_play_time
    death_window = tkinter.Tk()
    death_window.title("Tilecraft Beta 1.0 Pre-Release 3")
    death_window.geometry("500x500")
    death_window.configure(bg='#FFCCCB')

    font = tkinter.font.Font(size=45, family='Minecraft')
    font2 = tkinter.font.Font(size=30, family='Minecraft')
    font3 = tkinter.font.Font(size=30, family='Avenir')

    death_title = tkinter.Label(death_window, text="You Died!", fg='black', font=font, bg='#FFCCCB')
    death_title.place(x=150, y=0)

    death_reason = tkinter.Label(death_window, text="Death reason:   Starvation", fg='black', font=font3, bg='#FFCCCB')
    death_reason.place(x=50, y=150)

    time_played = tkinter.Label(death_window, text=true_play_time, fg='black', font=font3, bg='#FFCCCB')
    time_played.place(x=50, y=200)

    back_to_title_screen = tkinter.Button(death_window, font=font2, text="Back to Title Screen", width=20, height=3,
                                          fg='black', command=exit_death_screen)
    back_to_title_screen.place(x=50, y=300)

    death_window.mainloop()