from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from tilecraft import ASSETS_DIR
from .cheats import print_cheats, give, enchant, teleport, experience
from .constants import ITEM_TYPES, Item, RandomNumberGenerator
from .player import Player
from .world import TilecraftWorld


class SpeedrunTimer:
    """
        Timer to log how long the user has been playing
    """

    def __init__(self, load_val: str):
        self.font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 25)
        self.enabled = (load_val in ("Music Player", "God Gear"))
        self.running = True 
        self.latest_time_string = ""

    def render(self, display: pygame.Surface, play_time_seconds: float):
        """
            Render the speedrun timer to the display
            If not enabled, it will not render
        """

        if not self.enabled:
            return

        if self.running:
            if play_time_seconds // 3600 >= 10:  # HOURS 2 digits
                hour_time = str(int(play_time_seconds // 3600))
            else:  # HOURS 1 digit
                hour_time = f"0{int(play_time_seconds // 3600)}"
            if play_time_seconds // 60 >= 10:  # MINUTES 2 digits
                minute_time = str(int(play_time_seconds // 60))
            else:  # MINUTES 1 digit
                minute_time = f"0{int(play_time_seconds // 60)}"
            if play_time_seconds % 60 >= 10:  # SECONDS 2 digits
                second_time = str(round(play_time_seconds % 60))
            else:  # SECONDS 1 digit
                second_time = f"0{round(play_time_seconds % 60)}"
            millisecond_time = (round(play_time_seconds, 3) - math.floor(play_time_seconds)) * 1000  # Milliseconds
            if millisecond_time >= 100:  # 3 digits
                millisecond_time = str(int(millisecond_time))
            elif millisecond_time >= 10:  # 2 digits
                millisecond_time = f"0{int(millisecond_time)}"
            else:  # 1 digit
                millisecond_time = f"00{int(millisecond_time)}"
            self.latest_time_string = hour_time + ":" + minute_time + ":" + second_time + '.' + millisecond_time  # Current in-game time

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
    start_ticks: int 
    play_time_seconds: float


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
