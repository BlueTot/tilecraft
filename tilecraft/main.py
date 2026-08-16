import tkinter  # Tkinter module
import tkinter.font  # Fonts module
import random  # Random module
import pygame  # Pygame module
import time  # Time module
import math #Math module
import os #OS module
import sys #SYS module

from tilecraft import ASSETS_DIR
from .cheats import print_cheats, give, enchant, teleport, experience
from .constants import ITEM_TYPES, Item, TILE_IMAGE_MAPPING, RandomNumberGenerator, Context
from .generation import Tile, OverworldGeneratedList, OverworldGenerate, SpawnOverworldGenerate, SpawnOverworldBoundGenerate, UndergroundGeneratedList, SpawnUndergroundGenerate, UndergroundGenerate, UndergroundGeneratePortal, OverworldGeneratePortal, NetherGeneratedList, SpawnNetherGenerate, SpawnNetherBoundGenerate, NetherGenerate
from .inventory import Inventory, Hotbar, Armour, SmallCraftingInterface, CraftingTableInterface, FurnaceInterface, EnchantingTable, Compressor, Grindstone, HoldingItem
from .player_info import HealthBar, HungerBar, Experience, ExperienceBar

title_screen_mode = 'normal'


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


class Screen:
    def __init__(self, rng: RandomNumberGenerator):
        self.x = 0
        self.y = 570
        self.input_line = 0
        self.print_list = []
        self.isTyping = False
        self.typingText = ''
        self.position = 0
        self.foretext = ''
        self.timer = 0
        self.rng = rng

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

    def stop_typing(self, timer: SpeedrunTimer, player):
        self.input_line = 0
        self.isTyping = False
        length = len(list(ITEM_TYPES.keys())) - 1
        if self.foretext == f'Item ID (0 - {length}): ':
            player.inventory.add(give(self, self.typingText))
            self.foretext = ''
        elif self.foretext == 'Coordinates (X,Y): ':
            player.x, player.y = teleport(self, player.x, player.y, self.typingText)
            self.foretext = ''
        elif self.foretext == "Enchantment (Name, Lvl): ":
            item = enchant(self, player.inventory, self.typingText)
            if item is not None:
                player.inventory.hotbar_item = item
            self.foretext = ''
        elif self.foretext == "Experience Level: ":
            experience(self, player.experience, self.typingText)
            self.foretext = ''
        else:
            self.text_validate(timer)
        self.typingText = ''
        self.position = 0

    def delete(self):
        self.typingText = self.typingText[0:-1]

    def text_validate(self, timer: SpeedrunTimer):
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
                        NumberLimit(number, self.typingText, self.rng, self, timer)
                    except ValueError:
                        self.print("Invalid integer")
                else:
                    number = 1  # Set number to 1 when number is not specified
                    NumberLimit(number, self.typingText, self.rng, self, timer)
            # Regular text message
            else:
                self.print(f"<Player> {self.typingText}")

    def print(self, text):
        self.timer = 0
        self.print_list.append(text)

    def render(self, display: pygame.Surface):
        if self.timer != 600:
            if len(self.print_list) <= 16:
                self.screen_list = self.print_list[:]
                height = len(self.print_list) * 15 + self.input_line
            else:
                if self.position == 0:
                    self.screen_list = self.print_list[-16 - self.position:]
                    height = 16 * 15 + self.input_line
                else:
                    self.screen_list = self.print_list[-16 - self.position: 0 - self.position]
                    height = 16 * 15 + self.input_line
            self.screen_list.reverse()
            width = 375
            x = self.x
            y = self.y - height
            surface = pygame.Surface((width, height))
            surface.fill((125, 125, 125))
            surface.set_alpha(200)
            display.blit(surface, (x, y))
            font = pygame.font.Font(str(ASSETS_DIR / "monofur/monof55.ttf"), 18)
            for i in range(len(self.screen_list)):
                display.blit(font.render(self.screen_list[i], False, (255, 255, 255)), (x, y + height - (i + 1) * 15 - self.input_line))
            display.blit(font.render(self.foretext + self.typingText, True, (255, 255, 255)), (x, y + height - 15))
            self.timer += 1


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


'''Main Part of Game Code'''

class TilecraftWorld:
    def __init__(self, rng: RandomNumberGenerator, seed):
        self.empty_vil1 = []
        self.empty_vil2 = []
        self.empty_vil3 = []
        self.empty_vil4 = []
        self.empty_vil_total = []
        self.bastion = []
        self.bound_bastion = []
        self.fortress = []
        self.bound_fortress = []
        self.empty_bastion = []
        self.overworld_portal = []
        self.bound_overworld_portal = []
        self.nether_portal = []
        self.bound_nether_portal = []
        self.empty_ruined_portal1 = []
        self.empty_ruined_portal2 = []
        self.empty_ruined_portal_total = []
        self.seed = seed #World Seed
        self.undergroundGenerated = False
        self.rng = rng

        self.village, self.ruined_portal, self.obsidian_counts, \
        self.UnderTiles, self.Tiles = SpawnOverworldGenerate(self.rng, self.seed)  # Spawn Generation for Structures and Biomes
        self.bound_village, self.bound_ruined_portal = SpawnOverworldBoundGenerate(self.village, self.ruined_portal)  # Spawn Bounding Box Generation
        self.bound_village2 = self.bound_village.copy()
        self.bound_village3 = self.bound_village.copy()
        self.bound_village4 = self.bound_village.copy()
        self.bound_ruined_portal2 = self.bound_ruined_portal.copy()
        self.overworld_generated_list = OverworldGeneratedList()

    #Generate Chunks Per Frame
    def generate_chunks(self):
        global hasGeneratedUnderground
        if player.dimension == 'Overworld':
            for i in self.render_list:
                if i not in self.overworld_generated_list:
                    self.village, self.ruined_portal, self.obsidian_counts, self.overworld_generated_list, \
                    self.bound_village, self.bound_village2, self.bound_village3, self.bound_village4, self.bound_ruined_portal, self.bound_ruined_portal2, self.UnderTiles, self.Tiles = \
                    OverworldGenerate(self.rng, i[0], i[1], self.village, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4,
                                                      self.bound_ruined_portal, self.bound_ruined_portal2, self.seed, self.UnderTiles, self.Tiles)
        elif player.dimension == "Underground":
            if not self.undergroundGenerated:
                hasGeneratedUnderground = 'Generating'
            if hasGeneratedUnderground == "Generated":
                for i in self.render_list:
                    if i not in self.UndergroundGeneratedList:
                        self.UndergroundUnderTiles, self.UndergroundTiles = UndergroundGenerate(self.rng, self.seed, i[0], i[1], self.UndergroundUnderTiles, self.UndergroundTiles, self.UndergroundGeneratedList)
        elif player.dimension == 'Nether':
            for i in self.render_list:
                if i not in self.nether_generated_list:
                    self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion = NetherGenerate(self.rng, i[0], i[1], self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion, self.seed)

    #Calculate Render List Per Frame
    def render_chunks(self, left, right, top, bottom):
        global render_list
        self.render_list = []
        self.render_blocks_list = []
        left_chunk = math.floor(left / 32) // 16 * 16
        right_chunk = math.floor(right / 32) // 16 * 16
        top_chunk = math.floor(top / 32) // 16 * 16
        bottom_chunk = math.floor(bottom / 32) // 16 * 16
        for i in range(left_chunk, right_chunk + 1, 16):
            for j in range(top_chunk, bottom_chunk + 1, 16):
                self.render_list.append([i, j])
        for i in range(left_chunk, right_chunk + 1):
            for j in range(top_chunk, bottom_chunk + 1):
                self.render_blocks_list.append([i, j])

    #Generate Underground for the first time
    def generateUnderground(self):
        self.UndergroundUnderTiles, self.UndergroundTiles = SpawnUndergroundGenerate(self.rng, self.seed)
        self.UndergroundGeneratedList = UndergroundGeneratedList()

    # Generate nether for the first time
    def generateNether(self):
        global netherGenerated, player
        if not netherGenerated:
            netherGenerated = True

            # Initialise nether portal bounding box
            self.bound_nether_portal = []
            self.bastion, self.fortress = SpawnNetherGenerate(self.rng, self.seed)
            self.bound_bastion, self.bound_fortress = SpawnNetherBoundGenerate(self.bastion, self.fortress)
            self.nether_generated_list = NetherGeneratedList(player.x, player.y)

    def render(self, display, context: Context):
        global netherrack_tile, hotbar_imgs, slot, number_list, experience, pygame_enchant_imgs, enchant_name_list, player, hasGeneratedUnderground, bedrock_tile
        # player.health_hunger_update()

        def tile_image(tile_name: str) -> pygame.Surface:
            return context.TILE_IMAGES[TILE_IMAGE_MAPPING[tile_name].alpha_image_name]

        # DRAW OVERWORLD DIMENSION
        if player.dimension == "Overworld":
            for key, value in self.UnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                    else:
                        display.blit(context.TILE_IMAGES["bedrock_tile"], (value.x * 32 - player.left, value.y * 32 - player.top))
                    pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            for key, value in self.Tiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                        pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            # DRAWING OVERWORLD STRUCTURES
            for k in range(len(self.village)):
                if -32 <= (self.village[k][0] * 32 - player.left) <= 1032 and -32 <= (self.village[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (255, 165, 0), (self.village[k][0] * 32 - player.left, self.village[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.ruined_portal)):
                if -32 <= (self.ruined_portal[k][0] * 32 - player.left) <= 1032 and -32 <= (self.ruined_portal[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (56, 0, 89), (self.ruined_portal[k][0] * 32 - player.left, self.ruined_portal[k][1] * 32 - player.top), 10, 10)

            # DRAWING OVERWORLD EMPTY STRUCTURES
            for k in range(len(self.empty_vil_total)):
                if -32 <= (self.empty_vil_total[k][0] * 32 - player.left) <= 1032 and -32 <= (self.empty_vil_total[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (153, 102, 0), (self.empty_vil_total[k][0] * 32 - player.left, self.empty_vil_total[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.empty_ruined_portal_total)):
                if -32 <= (self.empty_ruined_portal_total[k][0] * 32 - player.left) <= 1032 and -32 <= (self.empty_ruined_portal_total[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (255, 255, 255), (self.empty_ruined_portal_total[k][0] * 32 - player.left, self.empty_ruined_portal_total[k][1] * 32 - player.top), 12, 12)
            # DRAWING OVERWORLD NETHER PORTALS
            for k in range(len(self.overworld_portal)):
                if -32 <= (self.overworld_portal[k][0] * 32 - player.left) <= 1032 and -32 <= (self.overworld_portal[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (128, 0, 128), (self.overworld_portal[k][0] * 32 - player.left, self.overworld_portal[k][1] * 32 - player.top), 10, 10)

        #DRAW UNDERGROUND DIMENSION
        elif player.dimension == "Underground" and hasGeneratedUnderground == "Generated":
            for key, value in self.UndergroundUnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                    else:
                        display.blit(context.ITEM_IMAGES["bedrock_tile"], (value.x * 32 - player.left, value.y * 32 - player.top))
                    pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            for key, value in self.UndergroundTiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                        pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline

        # DRAW NETHER DIMENSION
        elif player.dimension == "Nether":
            # DRAWING NETHERRACK TEXTURES
            for k in range(player.rect.x - 384, player.rect.x + 384, 24):
                for j in range(player.rect.y - 384, player.rect.y + 384, 24):
                    display.blit(context.ITEM_IMAGES["netherrack_tile"], (k, j))
            # DRAWING NETHER NETHER PORTALS
            for k in range(len(self.nether_portal)):
                if -32 <= (self.nether_portal[k][0] * 32 - player.left) <= 1032 and -32 <= (self.nether_portal[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (128, 0, 128), (self.nether_portal[k][0] * 32 - player.left, self.nether_portal[k][1] * 32 - player.top), 10, 10)
            # DRAWING NETHER STRUCTURES
            for k in range(len(self.fortress)):
                if -32 <= (self.fortress[k][0] * 32 - player.left) <= 1032 and -32 <= (self.fortress[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (134, 71, 71), (self.fortress[k][0] * 32 - player.left, self.fortress[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.bastion)):
                if -32 <= (self.bastion[k][0] * 32 - player.left) <= 1032 and -32 <= (self.bastion[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (218, 165, 32), (self.bastion[k][0] * 32 - player.left, self.bastion[k][1] * 32 - player.top), 10, 10)
            # DRAWING NETHER EMPTY STRUCTURES
            for k in range(len(self.empty_bastion)):
                if -32 <= (self.empty_bastion[k][0] * 32 - player.left) <= 1032 and -32 <= (self.empty_bastion[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (0, 0, 0), (self.empty_bastion[k][0] * 32 - player.left, self.empty_bastion[k][1] * 32 - player.top), 10, 10)

        # DRAW BREAKING ANIMATION
        if 1 <= math.floor(player.breaking_time) <= 6:
            display.blit(context.BREAKING_LIST[math.floor(player.breaking_time) - 1], (player.target[0] * 32 - player.left, player.target[1] * 32 - player.top))
        pygame.draw.rect(world, (50, 50, 50), (player.target[0] * 32 - player.left, player.target[1] * 32 - player.top, 32, 32), 1)  # Draw target block outline


# Game Loop
def Main():
    global TimerRunning, screen, furnace_interface, crafting_grid, small_crafting_grid, inventory_grid, World, player, difference, individual_frame, FPS, mode, val, comma, number, called, world, frame, play_time, endTime, minute, seconds, true_play_time, PlayTime, hotbar_backgrounds, selected_hotbar
    global hasGeneratedOverworld, display, clock, loading, hasGeneratedUnderground, previous_frame

    context: Context = None
    rng: RandomNumberGenerator = None
    timer: SpeedrunTimer = SpeedrunTimer(load)

    while True:
        clock.tick()

        # Calculate FPS
        frame += 1  # Update frame
        individual_frame += 1  # Update individual frame for each second
        end = time.time()  # Calculate current time
        PlayTime = end - start  # Calculate current playtime
        if (end - start - difference) > 1:  # Reset every second
            previous_frame = individual_frame
            individual_frame = 0
            difference += 1
        FPS = previous_frame
        events = pygame.event.get()
        if hasGeneratedOverworld and (hasGeneratedUnderground == "Not Loaded" or hasGeneratedUnderground == "Generated"):
            if player.mode == "game":
                if not screen.isTyping:
                    # Kill Player
                    if player.dead:
                        minute = int(PlayTime // 60)
                        seconds = int(round(PlayTime % 60))
                        true_play_time = "Time Played:   " + str(minute) + "m " + str(seconds) + "s"
                        pygame.quit()
                        return 'death screen'
                    # Single-key binds
                    for event in events:
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
                                player.mode = 'inventory'
                            # Advancements Key
                            if event.key == pygame.K_f:
                                if not player.advancements:
                                    screen.print("YOU HAVE NOT EARNED ANY ADVANCEMENTS")
                                else:
                                    screen.print("Advancements: ")
                                    for i in player.advancements:
                                        screen.print(f"- {i}")
                            # Input and chat key
                            if event.key == pygame.K_t:
                                screen.start_typing('')
                            # Eat key
                            if event.key == pygame.K_q:
                                if player.inventory.hotbar_item is not None:
                                    if player.inventory.hotbar_item.itemType == "Food":
                                        if player.hunger < 20:
                                            if player.inventory.hotbar_item.name == 'Bread':
                                                index = player.inventory.items.index(player.inventory.hotbar_item)
                                                player.inventory.items[index].number -= 1
                                                player.hunger += 5
                                            # GOLDEN CARROT
                                            elif player.inventory.hotbar_item.name == 'Golden Carrot':
                                                index = player.inventory.items.index(player.inventory.hotbar_item)
                                                player.inventory.items[index].number -= 1
                                                player.hunger += 6
                                            # GOLDEN APPLE
                                            elif player.inventory.hotbar_item.name == 'Golden Apple':
                                                index = player.inventory.items.index(player.inventory.hotbar_item)
                                                player.inventory.items[index].number -= 1
                                                player.hunger += 5
                                                player.regenerate_start_time = 0
                                                player.regenerate_val = True
                                            else:
                                                screen.print("You are not holding a food item!")
                                            # player.health_hunger_update()  # UPDATE HEALTH / HUNGER
                                    else:
                                        screen.print("You are not holding a food item!")
                                else:
                                    screen.print("You are not holding a food item!")
                            if event.key == pygame.K_1:
                                player.set_hotbar(0)
                            if event.key == pygame.K_2:
                                player.set_hotbar(1)
                            if event.key == pygame.K_3:
                                player.set_hotbar(2)
                            if event.key == pygame.K_4:
                                player.set_hotbar(3)
                            if event.key == pygame.K_5:
                                player.set_hotbar(4)
                            if event.key == pygame.K_6:
                                player.set_hotbar(5)
                            if event.key == pygame.K_7:
                                player.set_hotbar(6)
                            if event.key == pygame.K_8:
                                player.set_hotbar(7)
                            if event.key == pygame.K_9:
                                player.set_hotbar(8)
                            if event.key == pygame.K_0:
                                player.debug_menu = not player.debug_menu
                            if event.key == pygame.K_a:  # Turn Left
                                pos = player.direction_list.index(player.direction)
                                player.direction = player.direction_list[pos - 1]
                            if event.key == pygame.K_d:  # Turn Right
                                pos = player.direction_list.index(player.direction)
                                if pos == 3:
                                    player.direction = player.direction_list[0]
                                else:
                                    player.direction = player.direction_list[pos + 1]
                        elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                            if pygame.mouse.get_pressed(3)[2]:  # Right Click
                                player.mouse_button = 2
                                if player.inventory.hotbar_item is not None:
                                    if player.inventory.hotbar_item.name == 'Crafting Table': #Crafting Key
                                        player.mode = 'crafting'
                                    elif player.inventory.hotbar_item.name == 'Furnace': #Smelting Key
                                        player.mode = 'smelting'
                                    elif player.inventory.hotbar_item.name == 'Enchanting Table': #Enchanting Key
                                        player.mode = 'enchanting'
                                    elif player.inventory.hotbar_item.name == 'Compressor': #Compressing Key
                                        player.mode = 'compressing'
                                    elif player.inventory.hotbar_item.name == "Grindstone": #Repairing and Disenchanting Key
                                        player.mode = 'repairing and disenchanting'
                                    elif player.inventory.hotbar_item.name == "Bucket": #Picking up liquids
                                        player.pick_up_liquid()
                                    elif player.inventory.hotbar_item.name == "Water Bucket" or \
                                            player.inventory.hotbar_item.name == "Lava Bucket":  #Placing liquids
                                        player.place_liquid()
                                    else:
                                        player.place_tile()
                            elif pygame.mouse.get_pressed(3)[0]:
                                player.mouse_button = 1
                                player.isBreaking = True
                        if event.type == pygame.MOUSEBUTTONUP:
                            if player.mouse_button == 1:
                                player.breaking_time = 0
                                player.isBreaking = False
                    if player.isBreaking:
                        player.breaking()
                    player.move()  # Move Player
                else:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP]: #Scroll Up
                        screen.scroll_up()
                    elif keys[pygame.K_DOWN]: #Scroll Down
                        screen.scroll_down()
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE: #Type Space
                                screen.type(' ')
                            elif event.key == pygame.K_RETURN: #Enter Key
                                screen.stop_typing(timer, player)
                            elif event.key == pygame.K_BACKSPACE: #Delete
                                screen.delete()
                            else:
                                char = str(pygame.key.name(event.key)) #Get Key name
                                if len(char) == 1: #Check to prevent non-alphabetical and non-number keys
                                    screen.type(char)

                display.fill((0, 0, 0))  # Fill world border black
                world.fill(background)  # Fill world background colour
                player.health_update()  # Update Player Health
                World.render_chunks(player.left, player.right, player.top, player.bottom)  # Generate list of all chunks that are loaded
                World.generate_chunks()  # Generate Chunks that are loaded but have not been generated before
                World.render(world, context)  # Render all world blocks to world
                RemoveItem() #Remove Items if their number is 0
                player.render(context, world, screen_width, screen_height)  # Render player and player accessories to world
                timer.render(world, PlayTime)
                advancements_update(screen, timer, player.advancements, player.inventory.items, player.armour.items, player.dimension)  # Update Advancements
                screen.render(world) #Render Text Screen

            elif player.mode in ("inventory", "crafting", "smelting", "enchanting", "compressing", "repairing and disenchanting"):

                mouse = pygame.mouse.get_pos()

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e: # Exit 
                            player.mode = "game"
                            break
                        elif event.key == pygame.K_1: #1
                            player.inventory.hotbar_swap(mouse, 1)
                        elif event.key == pygame.K_2: #2
                            player.inventory.hotbar_swap(mouse, 2)
                        elif event.key == pygame.K_3: #3
                            player.inventory.hotbar_swap(mouse, 3)
                        elif event.key == pygame.K_4: #4
                            player.inventory.hotbar_swap(mouse, 4)
                        elif event.key == pygame.K_5: #5
                            player.inventory.hotbar_swap(mouse, 5)
                        elif event.key == pygame.K_6: #6
                            player.inventory.hotbar_swap(mouse, 6)
                        elif event.key == pygame.K_7: #7
                            player.inventory.hotbar_swap(mouse, 7)
                        elif event.key == pygame.K_8: #8
                            player.inventory.hotbar_swap(mouse, 8)
                        elif event.key == pygame.K_9: #9
                            player.inventory.hotbar_swap(mouse, 9)

                    elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
                        
                        if pygame.mouse.get_pressed(3)[0]: #Left Click
                            player.inventory.handle_left_click(mouse, player.holding_item)

                            if player.mode == "inventory":
                                player.armour.handle_left_click(mouse, player.holding_item)
                                player.craft_interface.handle_left_click(mouse, player.holding_item, player.inventory)

                            elif player.mode == "crafting":
                                player.crafting_grid.handle_left_click(mouse, player.holding_item, player.inventory) 

                            elif player.mode == "smelting":
                                player.furnace.handle_left_click(mouse, player.holding_item, player.inventory) 

                            elif player.mode == "enchanting":
                                player.enchanting_table.handle_left_click(mouse, player.holding_item, player.experience, rng)

                            elif player.mode == "compressing":
                                player.compressor.handle_left_click(mouse, player.holding_item, player.inventory)

                            elif player.mode == "repairing and disenchanting":
                                player.grindstone.handle_left_click(mouse, player.holding_item, player.inventory, player.experience)

                        elif pygame.mouse.get_pressed(3)[2]: #Right Click
                            player.inventory.handle_right_click(mouse, player.holding_item)

                            if player.mode == "inventory":
                                player.craft_interface.handle_right_click(mouse, player.holding_item)

                            elif player.mode == "crafting":
                                player.crafting_grid.handle_right_click(mouse, player.holding_item) 

                            elif player.mode == "smelting":
                                player.furnace.handle_right_click(mouse, player.holding_item) 

                            elif player.mode == "enchanting":
                                player.enchanting_table.handle_right_click(mouse, player.holding_item)

                            elif player.mode == "compressing":
                                player.compressor.handle_right_click(mouse, player.holding_item)

                            elif player.mode == "repairing and disenchanting":
                                player.grindstone.handle_right_click(mouse, player.holding_item)

                display.fill((0, 0, 0))
                world.fill((211, 211, 211))

                is_holding = player.holding_item.item is not None
                player.inventory.render(context, world, mouse, is_holding) #Render Inventory Grid

                if player.mode == "inventory":
                    player.armour.render(world, context, mouse, is_holding) #Render Armour Grid for Player
                    player.craft_interface.render(world, context, mouse, is_holding) #Render Small Crafting Grid
                    player.craft_interface.update() #Update Small 2x2 Crafting Grid
                    
                elif player.mode == "crafting":
                    player.crafting_grid.render(world, context, mouse, is_holding) #Render 3x3 Crafting Grid
                    player.crafting_grid.update()  #Update 3x3 Crafting Grid

                elif player.mode == "smelting":
                    player.furnace.render(world, context, mouse, FPS, is_holding) #Render Furnace Interface
                    player.furnace.smelt(context, FPS, player.experience) #Furnace Smelting

                elif player.mode == "enchanting":
                    player.enchanting_table.render(world, context, mouse, is_holding) #Render Enchanting Table Interface

                elif player.mode == "compressing":
                    player.compressor.render(world, context, mouse, FPS, is_holding) #Render Compressor Interface
                    player.compressor.compress(FPS) #Compressing Process

                elif player.mode == "repairing and disenchanting":
                    player.grindstone.render(world, context, mouse, is_holding) #Render Grindstone Interface
                    player.grindstone.repair_and_disenchant() #Update repaired/disenchanted item

                RemoveItem() #Remove all items with number of 0 or durability of 0
                player.holding_item.render(world, context) #Render the item the user is holding

            display.blit(world, (0, 0))  # Render map to display
            pygame.display.flip()  # Update Display

        elif not hasGeneratedOverworld and hasGeneratedUnderground == "Not Loaded":
            display.fill((255, 255, 255))
            for i in range(0, 750, 32):
                for j in range(0, 750, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 37)
            display.blit(font.render("Generating Overworld", False, (255, 255, 255)), (180, 225))
            pygame.display.flip()
            context, rng = PygameInitialise()
            print("PYGAME INITIALISED")

        if hasGeneratedUnderground == "Generating":
            display.fill((255, 255, 255))
            for i in range(0, 750, 32):
                for j in range(0, 750, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 37)
            display.blit(font.render("Generating Underground", False, (255, 255, 255)), (180, 225))
            pygame.display.flip()
            World.undergroundGenerated = True
            World.generateUnderground()
            World.UndergroundTiles = UndergroundGeneratePortal(round(player.x), round(player.y), World.UndergroundTiles)
            hasGeneratedUnderground = "Generated"

        if not pygame.mixer.music.get_busy():
            if rng.next_random(1, 500) == 1:
                pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()


#Limit number of times a player can repeat a command
def NumberLimit(number, val, rng: RandomNumberGenerator, screen: Screen, timer: SpeedrunTimer):
    if number > 16:
        screen.print("ERROR: Invalid Integer")
    elif number < 1:
        screen.print("ERROR: Invalid Integer")
    else:
        commands(number, val, rng, screen, timer)


#Player Class and Methods
class Player:
    def __init__(self, context: Context, rng: RandomNumberGenerator):
        global World
        self.advancements = []
        self.image = pygame.Surface((32, 32))  # Create Player Image
        self.image.fill((255, 0, 0))  # Fill Player Red
        self.rect = pygame.Rect((359, 359), (32, 32))  # Create Player Rect
        self.x = 0  # Set Starting X Coordinate
        self.y = 0  # Set Starting Y Coordinate
        self.actualX = 0
        self.actualY = 0
        self.dimension = "Overworld"
        self.regenerate_val = False
        self.regenerate_start_time = 180
        self.debug_menu = False
        self.direction = 'East'
        self.direction_list = ['North', 'East', 'South', 'West']
        self.target = [1, 0]
        self.breaking_time = 0
        self.mouse_button = 1
        self.isBreaking = False
        self.canEnterPortal = True
        self.isShifting = False
        self.breaking_delay = 0
        self.isInstantMining = False

        self.rng = rng    

        #TO PREVENT PLAYERS FROM SPAWNING INSIDE A TREE OR BOULDER
        while True: #Infinite loop
            if World.Tiles[(self.x, self.y)].tile != "Air": #If tile that player spawns in is not air
                self.x += 1 #increase x by 1
            else:
                break #tile is air so the loop ends

        self.health = 20
        self.health_bar = HealthBar()
        
        self.hunger = 20
        self.hunger_bar = HungerBar()

        self.experience = Experience()
        self.experience_bar = ExperienceBar()

        self.distance = 0  # Set Distance Travelled
        self.dead = False
        self.hunger_subtracted = 0

        self.backdrop = pygame.Rect((30, 592), (697, 30))  # Set Background for Hunger and Health Bar

        # inventory
        self.inventory = Inventory()
        self.waiting_list = []
        self.selected_slot = 'slot1'

        self.hotbar = Hotbar() # hotbar
        self.armour = Armour() # armour
        self.craft_interface = SmallCraftingInterface() # small crafting grid
        self.crafting_grid = CraftingTableInterface() # crafting table
        self.furnace = FurnaceInterface(context) # furnace interface
        self.enchanting_table = EnchantingTable() # enchanting table interface
        self.compressor = Compressor() # compressor interface
        self.grindstone = Grindstone() # grindstone interface
        self.holding_item = HoldingItem()

        self.mode = 'game'

    # set player hotbar index and item
    def set_hotbar(self, index: int):
        self.inventory.selected_hotbar = index

    # Hunger mechanism to decrease hunger as distance travelled increases
    def hunger_mechanism(self):
        if self.hunger > 0 and self.distance != 0 and self.distance // 512 != self.hunger_subtracted:
            self.hunger -= 1
            self.hunger_subtracted += 1

    #Update Health and Regeneration
    def health_update(self):
        if self.hunger >= 17 and self.health < 20 and frame % 16 == 0:
            self.hunger -= 1
            self.health += 1
        if self.hunger == 0 and frame % 16 == 0:
            self.health -= 1
        if self.health == 0:
            self.dead = True
        if self.regenerate_val and self.health < 20:
            if self.regenerate_start_time < 60:
                if frame % 5 == 0:
                    self.health += 1
                self.regenerate_start_time += 1
            else:
                self.regenerate_val = False

    def collide(self): #Collisions with tiles
        global hasGeneratedUnderground
        self.canMove = True
        try:
            if self.dimension == "Overworld": #Overworld dimension
                call = False
                for key, value in World.Tiles.items():
                    if -32 <= (key[0] * 32 - self.left) <= 1032 and -32 <= (key[1] * 32 - self.top) <= 1032: #in render distance
                        if pygame.Rect((self.x * 32, self.y * 32, 32, 32)).colliderect(pygame.Rect((key[0] * 32, key[1] * 32, 32, 32))): #collision
                            if not (value.tile == "Air" or value.tile == "Mine Entrance"): #collision with tile
                                self.canMove = False
                            elif value.tile == "Mine Entrance" and self.canEnterPortal: #enter portal
                                self.canEnterPortal = False
                                self.dimension = "Underground"
                                self.x = value.x
                                self.y = value.y
                                if hasGeneratedUnderground == "Generated":
                                    try:
                                        if World.UndergroundTiles[(round(player.x), round(player.y))].tile != "Mine Entrance":
                                            World.UndergroundTiles = UndergroundGeneratePortal(round(player.x), round(player.y), World.UndergroundTiles)
                                    except KeyError:
                                        World.generate_chunks()
                                        World.UndergroundTiles = UndergroundGeneratePortal(round(player.x), round(player.y), World.UndergroundTiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
            elif self.dimension == "Underground" and hasGeneratedUnderground == "Generated": #Underground dimension
                call = False
                for key, value in World.UndergroundTiles.items():
                    if -32 <= (key[0] * 32 - self.left) <= 1032 and -32 <= (key[1] * 32 - self.top) <= 1032: #in render distance
                        if pygame.Rect((self.x * 32, self.y * 32, 32, 32)).colliderect(pygame.Rect((key[0] * 32, key[1] * 32, 32, 32))): #collision
                            if not (value.tile == "Air" or value.tile == "Mine Entrance"): #collision with tile
                                self.canMove = False
                            elif value.tile == "Mine Entrance" and self.canEnterPortal: #enter portal
                                self.canEnterPortal = False
                                self.dimension = "Overworld"
                                self.x = value.x
                                self.y = value.y
                                try:
                                    if World.Tiles[(round(player.x), round(player.y))].tile != "Mine Entrance":
                                        World.Tiles = OverworldGeneratePortal(round(player.x), round(player.y), World.Tiles)
                                except KeyError:
                                    World.generate_chunks()
                                    World.Tiles = OverworldGeneratePortal(round(player.x), round(player.y), World.Tiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
        except KeyError:
            World.generate_chunks()
        return self.canMove

    #Player Move Keybinds
    def move(self):
        global hasGeneratedUnderground
        # Position calculation
        self.left = self.x * 32 - 359
        self.right = self.x * 32 + 391
        self.bottom = self.y * 32 + 391
        self.top = self.y * 32 - 359
        self.ScreenLeft = self.x * 32 - 359
        self.ScreenRight = self.x * 32 + 391
        self.ScreenBottom = self.y * 32 + 391
        self.ScreenTop = self.y * 32 - 359

        key = pygame.key.get_pressed() #Get Keyboard Input (Press Key)
        mods = pygame.key.get_mods()
        self.pastX = self.x
        self.pastY = self.y
        if mods & pygame.KMOD_SHIFT:
            self.isShifting = True
        else:
            self.isShifting = False

        if key[pygame.K_w]: #Forwards
            if key[pygame.K_r]: #Sprinting
                if self.direction == 'North':
                    self.y -= 5 / 16
                elif self.direction == 'East':
                    self.x += 5 / 16
                elif self.direction == 'South':
                    self.y += 5 / 16
                elif self.direction == 'West':
                    self.x -= 5 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y -= 1 / 16
                    elif self.direction == 'East':
                        self.x += 1 / 16
                    elif self.direction == 'South':
                        self.y += 1 / 16
                    elif self.direction == 'West':
                        self.x -= 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        player.hunger_mechanism()
                else:
                    self.distance += 1
                    player.hunger_mechanism()
            else: #Not Sprinting
                if self.direction == 'North':
                    self.y -= 3 / 16
                elif self.direction == 'East':
                    self.x += 3 / 16
                elif self.direction == 'South':
                    self.y += 3 / 16
                elif self.direction == 'West':
                    self.x -= 3 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y -= 1 / 16
                    elif self.direction == 'East':
                        self.x += 1 / 16
                    elif self.direction == 'South':
                        self.y += 1 / 16
                    elif self.direction == 'West':
                        self.x -= 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        player.hunger_mechanism()
                else:
                    self.distance += 1
                    player.hunger_mechanism()
        elif key[pygame.K_s]: #Backwards
            if key[pygame.K_r]: #Sprinting
                if self.direction == 'North':
                    self.y += 5 / 16
                elif self.direction == 'East':
                    self.x -= 5 / 16
                elif self.direction == 'South':
                    self.y -= 5 / 16
                elif self.direction == 'West':
                    self.x += 5 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y += 1 / 16
                    elif self.direction == 'East':
                        self.x -= 1 / 16
                    elif self.direction == 'South':
                        self.y -= 1 / 16
                    elif self.direction == 'West':
                        self.x += 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        player.hunger_mechanism()
                else:
                    self.distance += 1
                    player.hunger_mechanism()
            else: #Not Sprinting
                if self.direction == 'North':
                    self.y += 3 / 16
                elif self.direction == 'East':
                    self.x -= 3 / 16
                elif self.direction == 'South':
                    self.y -= 3 / 16
                elif self.direction == 'West':
                    self.x += 3 / 16
                if not self.collide():
                    self.x = self.pastX
                    self.y = self.pastY
                    if self.direction == 'North':
                        self.y += 1 / 16
                    elif self.direction == 'East':
                        self.x -= 1 / 16
                    elif self.direction == 'South':
                        self.y -= 1 / 16
                    elif self.direction == 'West':
                        self.x += 1 / 16
                    if not self.collide():
                        self.x = self.pastX
                        self.y = self.pastY
                    else:
                        self.distance += 1
                        player.hunger_mechanism()
                else:
                    self.distance += 1
                    player.hunger_mechanism()
        if self.direction == 'North':
            self.target = [math.floor(self.x + 0.5), math.floor(self.y) - 1] #Target tile in north direction
        elif self.direction == 'East':
            self.target = [math.ceil(self.x) + 1, math.floor(self.y + 0.5)] #Target tile in east direction
        elif self.direction == 'South':
            self.target = [math.floor(self.x + 0.5), math.ceil(self.y) + 1] #Target tile in south direction
        elif self.direction == 'West':
            self.target = [math.floor(self.x) - 1, math.floor(self.y + 0.5)] #Target tile in west direction
        try:
            if self.dimension == "Overworld":
                if World.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and World.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    World.Tiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
            elif self.dimension == "Underground" and hasGeneratedUnderground == "Generated":
                if World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
        except KeyError:
            World.generate_chunks()


    def place_tile(self): #Place tiles
        if self.isShifting: #is shifting = can edit background tiles
            if self.dimension == "Overworld": #Overworld background tiles
                if self.inventory.hotbar_item.hasTile:
                    if World.UnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Open space to place tile
                        World.UnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1]) #Place tile
                        self.inventory.hotbar_item.number -= 1 #Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None #Remove from inventory
            elif self.dimension == "Underground": #Underground background tiles
                if self.inventory.hotbar_item.hasTile:
                    if World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
        else:
            if self.dimension == "Overworld": #Overworld Collision tiles
                if self.inventory.hotbar_item.hasTile:
                    if World.Tiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.Tiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.Tiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.Tiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
            elif self.dimension == "Underground": #Underground Collision Tiles
                if self.inventory.hotbar_item.hasTile:
                    if World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.UndergroundTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory

    def breaking(self): #Breaking process of tile
        global frame, FPS
        if self.breaking_delay == 0:
            if self.isShifting: #can edit background tiles
                if self.dimension == "Overworld": #Overworld background tiles
                    tile = World.UnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None: #Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * 30) >= 1:
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground background tiles
                    tile = World.UndergroundUnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
            else:
                if self.dimension == "Overworld": #Overworld collision tiles
                    tile = World.Tiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground collision tiles
                    tile = World.UndergroundTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / FPS) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7

    def break_add_item(self, value):
        if not self.isInstantMining:
            self.breaking_delay = FPS * 3/10
        if self.dimension == "Overworld":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    player.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    player.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    player.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    player.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    player.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    player.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        player.inventory.add(Item("Flint", 1, None, None))
                    else:
                        player.inventory.add(Item("Gravel", 1, None, None))
                else:
                    player.inventory.add(Item(value.tile, 1, None, None))
        elif self.dimension == "Underground":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    player.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    player.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    player.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    player.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    player.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    player.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        player.inventory.add(Item("Flint", 1, None, None))
                    else:
                        player.inventory.add(Item("Gravel", 1, None, None))
                else:
                    player.inventory.add(Item(value.tile, 1, None, None))
        if self.inventory.hotbar_item is not None:
            if self.inventory.hotbar_item.durability is not None:
                if self.inventory.hotbar_item.enchantments is not None:
                    for i in self.inventory.hotbar_item.enchantments:
                        if i[0] == "Unbreaking":
                            if self.rng.next_random(1, i[1] + 1) == 1:
                                self.inventory.hotbar_item.durability -= 1
                            break
                    else:
                        self.inventory.hotbar_item.durability -= 1
                else:
                    self.inventory.hotbar_item.durability -= 1

    def break_tile(self, value):
        if self.isShifting:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UndergroundUnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
        else:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.Tiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UndergroundTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])

    def pick_up_liquid(self): #Picking up liquids with a bucket
        if self.dimension == "Overworld": #Overworld
            if self.isShifting: #Background tiles
                if World.UnderTiles[(self.target[0], self.target[1])].tile == "Water": #Wate
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Water Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Lava Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision tiles
                if World.Tiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Water Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1],)
                elif World.Tiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Lava Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
        elif self.dimension == "Underground": #Underground
            if self.isShifting: #Background Tiles
                if World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Water Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Lava Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision Tiles
                if World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Water Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Lava Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])

    def place_liquid(self):
        if self.dimension == "Overworld":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
        elif self.dimension == "Underground":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    player.inventory.add(Item("Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])

    def render(self, context: Context, display: pygame.Surface, screen_width: int, screen_height: int):
        global FPS 

        if self.breaking_delay > 0:
            self.breaking_delay -= 1
        else:
            self.breaking_delay = 0

        # DRAW BACKDROP FOR HUNGER AND HEALTH BARS
        pygame.draw.rect(display, (255, 255, 255), self.backdrop)

        # DRAW PLAYER
        display.blit(self.image, (self.rect.x, self.rect.y))
        if self.direction == 'North':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (375, 359), width=4)
        elif player.direction == 'East':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (391, 375), width=4)
        elif player.direction == 'South':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (375, 391), width=4)
        elif player.direction == 'West':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (359, 375), width=4)

        # render health and hunger bars
        self.health_bar.render(display, context, self.health)
        self.hunger_bar.render(display, context, self.hunger)

        # render experience bar
        self.experience_bar.render(display, self.experience.levels)

        # render hotbar
        self.hotbar.render(display, context, self.inventory.items[27:36], self.inventory.selected_hotbar)

        # RENDER DEBUG MENU
        if player.debug_menu:
            font9 = pygame.font.Font(
                str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
            version = font9.render("Tilecraft vBeta 1.0 Pre-Release 3", True, (0, 0, 0), (255, 255, 255))
            display.blit(version, (0, 0))
            python_version = font9.render(f"Python {sys.version[0:6]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(python_version, (0, 25))
            pygame_version = font9.render("Graphics: pygame v2.1.2", True, (0, 0, 0), (255, 255, 255))
            display.blit(pygame_version, (0, 50))
            display_size = font9.render(f"Display Size: {screen_width}x{screen_height}", True, (0, 0, 0), (255, 255, 255))
            display.blit(display_size, (0, 75))
            SEEDs = font9.render(f"Seed: {World.seed}", True, (0, 0, 0), (255, 255, 255))
            display.blit(SEEDs, (0, 100))
            FPS = font9.render(f"FPS: {FPS}", True, (0, 0, 0), (255, 255, 255))
            display.blit(FPS, (0, 125))
            Direction = font9.render(f"Facing: {self.direction}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Direction, (0, 150))
            Target = font9.render(f"Target Tile: {self.target[0]}, {self.target[1]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Target, (0, 175))
            Coords = font9.render(f"X: {round(player.x, 3)}, Y: {round(player.y, 3)}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Coords, (0, 200))

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


def PygameInitialise() -> tuple[Context, RandomNumberGenerator]:
    global hasGeneratedOverworld, display, clock
    global netherGenerated, background, numList, call, difference, FPS, individual_frame, second_time, start, load, frame
    global hotbar_imgs, pygame_enchant_imgs, hotbar_order

    # Play Minecraft Music (Sweden)
    pygame.mixer.init()
    pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
    pygame.mixer.music.play()

    # [EXPORT] Create PYGAME inventory images for hotbar
    ITEM_IMAGES = {
        "wood": pygame.image.load(str(ASSETS_DIR / "item_imgs/oak_log.png")).convert_alpha(), #0
        "planks": pygame.image.load(str(ASSETS_DIR / "item_imgs/oak_planks.png")).convert_alpha(), #1
        "stick": pygame.image.load(str(ASSETS_DIR / "item_imgs/stick.png")).convert_alpha(), #2
        "crafting_table": pygame.image.load(str(ASSETS_DIR / "item_imgs/crafting_table.png")).convert_alpha(), #3
        "wooden_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_pickaxe.png")).convert_alpha(), #4
        "wooden_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_axe.png")).convert_alpha(), #5
        "wooden_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_shovel.png")).convert_alpha(), #6
        "wooden_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/wooden_hoe.png")).convert_alpha(), #7
        "cobblestone": pygame.image.load(str(ASSETS_DIR / "item_imgs/cobblestone.png")).convert_alpha(), #8
        "mine_entrance": pygame.image.load(str(ASSETS_DIR / "item_imgs/mine_entrance.png")).convert_alpha(), #9
        "stone_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_pickaxe.png")).convert_alpha(), #10
        "stone_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_axe.png")).convert_alpha(), #11
        "stone_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_shovel.png")).convert_alpha(), #12
        "stone_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/stone_hoe.png")).convert_alpha(), #13
        "furnace": pygame.image.load(str(ASSETS_DIR / "item_imgs/furnace.png")).convert_alpha(), #14
        "compressor": pygame.image.load(str(ASSETS_DIR / "item_imgs/compressor.png")).convert_alpha(), #15
        "grindstone": pygame.image.load(str(ASSETS_DIR / "item_imgs/grindstone.png")).convert_alpha(), #16
        "coal": pygame.image.load(str(ASSETS_DIR / "item_imgs/coal.png")).convert_alpha(), #17
        "iron_ore": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_ore.png")).convert_alpha(), #18
        "iron_ingot": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_ingot.png")).convert_alpha(), #19
        "iron_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_pickaxe.png")).convert_alpha(), #20
        "iron_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_axe.png")).convert_alpha(), #21
        "iron_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_shovel.png")).convert_alpha(), #22
        "iron_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_hoe.png")).convert_alpha(), #23
        "bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/bucket.png")).convert_alpha(), #24
        "water_bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/water_bucket.png")).convert_alpha(), #25
        "lava_bucket": pygame.image.load(str(ASSETS_DIR / "item_imgs/lava_bucket.png")).convert_alpha(), #26
        "shield": pygame.image.load(str(ASSETS_DIR / "item_imgs/shield.png")).convert_alpha(), #27
        "flint_and_steel": pygame.image.load(str(ASSETS_DIR / "item_imgs/flint_and_steel.png")).convert_alpha(), #28
        "iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/iron_plate.png")).convert_alpha(), #29
        "tier1_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier1_iron_plate.png")).convert_alpha(), #30
        "tier2_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier2_iron_plate.png")).convert_alpha(), #31
        "tier3_iron_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier3_iron_plate.png")).convert_alpha(), #32
        "diamond": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond.png")).convert_alpha(), #33
        "diamond_pickaxe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_pickaxe.png")).convert_alpha(), #34
        "diamond_axe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_axe.png")).convert_alpha(), #35
        "diamond_shovel": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_shovel.png")).convert_alpha(), #36
        "diamond_hoe": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_hoe.png")).convert_alpha(), #37
        "diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/diamond_plate.png")).convert_alpha(), #38
        "tier1_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier1_diamond_plate.png")).convert_alpha(), #39
        "tier2_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier2_diamond_plate.png")).convert_alpha(), #40
        "tier3_diamond_plate": pygame.image.load(str(ASSETS_DIR / "item_imgs/tier3_diamond_plate.png")).convert_alpha(), #41
        "jukebox": pygame.image.load(str(ASSETS_DIR / "item_imgs/jukebox.png")).convert_alpha(), #42
        "pigstep_disc": pygame.image.load(str(ASSETS_DIR / "item_imgs/pigstep_disc.png")).convert_alpha(), #43
        "obsidian": pygame.image.load(str(ASSETS_DIR / "item_imgs/obsidian.png")).convert_alpha(), #44
        "enchanting_table": pygame.image.load(str(ASSETS_DIR / "item_imgs/enchanting_table.png")).convert_alpha(), #45
        "book": pygame.image.load(str(ASSETS_DIR / "item_imgs/book.png")).convert_alpha(), #46
        "bookshelf": pygame.image.load(str(ASSETS_DIR / "item_imgs/bookshelf.png")).convert_alpha(), #47
        "lapis": pygame.image.load(str(ASSETS_DIR / "item_imgs/lapis_lazuli.png")).convert_alpha(), #48
        "bread": pygame.image.load(str(ASSETS_DIR / "item_imgs/bread.png")).convert_alpha(), #49
        "golden_carrot": pygame.image.load(str(ASSETS_DIR / "item_imgs/golden_carrot.png")).convert_alpha(), #50
        "golden_apple": pygame.image.load(str(ASSETS_DIR / "item_imgs/golden_apple.png")), #51
        "dirt": pygame.image.load(str(ASSETS_DIR / "item_imgs/dirt.png")).convert_alpha(), #52
        "sand": pygame.image.load(str(ASSETS_DIR / "item_imgs/sand.png")).convert_alpha(), #53
        "snow": pygame.image.load(str(ASSETS_DIR / "item_imgs/snow.png")).convert_alpha(), #54
        "gravel": pygame.image.load(str(ASSETS_DIR / "item_imgs/gravel.png")).convert_alpha(), #55
        "flint": pygame.image.load(str(ASSETS_DIR / "item_imgs/flint.png")).convert_alpha(), #56
        "bed": pygame.image.load(str(ASSETS_DIR / "item_imgs/bed.png")).convert_alpha(), #57
        "hay": pygame.image.load(str(ASSETS_DIR / "item_imgs/hay_bale.png")).convert_alpha(), #58
        "none_img": pygame.image.load(str(ASSETS_DIR / "item_imgs/slot.png")).convert_alpha(),  # White Space
        "fire": pygame.image.load(str(ASSETS_DIR / "item_imgs/fire.png")).convert_alpha(),  # Fire when smelting
        "no_fire": pygame.image.load(str(ASSETS_DIR / "item_imgs/no_fire.png")).convert_alpha(),  # No fire when smelting
    }

    # Create GLINT images for enchanted items
    glint_list = []
    glint_fullname_list = []
    glint_num_list = []
    new_glint_name_list = []
    int_glint_num_list = []
    item_names = []
    for filename in os.listdir(str(ASSETS_DIR / "glints")):
        glint_num_list.append(filename[5:-4])
        glint_fullname_list.append(filename[:-4])
    for i in glint_num_list:
        int_glint_num_list.append(int(i))
    new_glint_num_list = sorted(int_glint_num_list)
    for i in new_glint_num_list:
        index = glint_num_list.index(str(i))
        new_glint_name_list.append(glint_fullname_list[index])
    for i in new_glint_name_list:
        image = pygame.image.load(str(ASSETS_DIR / f"glints/{i}.png")).convert_alpha()
        glint_list.append(image)
    for key in ITEM_TYPES.keys():
        item_names.append(key)

    # [EXPORT]
    TC_GLINTS = dict(zip(item_names, glint_list))

    def set_alpha(path: str) -> pygame.Surface:
        image = pygame.image.load(path).convert()
        image.set_alpha(200)
        return image

    # [EXPORT] Create Tile Images
    TILE_IMAGES = {
        "grass_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/grass.png")).convert(),  # Grass
        "netherrack_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/netherrack.png")).convert(),  # Netherrack
        "sand_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/sand.png")).convert(),  # Sand
        "snow_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/snow.png")).convert(),  # Snow
        "bookshelf_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/bookshelf_tile.png")).convert(),
        "coal_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/coal_ore_tile.png")).convert(),
        "cobblestone_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/cobblestone_tile.png")).convert(),
        "diamond_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/diamond_ore_tile.png")).convert(),
        "dirt_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/dirt_tile.png")).convert(),
        "gravel_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/gravel_tile.png")).convert(),
        "hay_bale_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/hay_bale_tile.png")).convert(),
        "iron_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/iron_ore_tile.png")).convert(),
        "lapis_ore_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/lapis_ore_tile.png")).convert(),
        "lava_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/lava_tile.png")).convert(),
        "leaf_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/leaf.png")).convert_alpha(),
        "mine_entrance_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/mine_entrance_tile.png")).convert(),
        "oak_log_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")).convert(),
        "oak_planks_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_planks_tile.png")).convert(),
        "obsidian_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/obsidian_tile.png")).convert(),
        "stone_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/stone_tile.png")).convert(),
        "tree_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "water_tile": pygame.image.load(str(ASSETS_DIR / "tile_imgs/water_tile.png")).convert(),
        "alpha_grass_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/grass.png")),  # Grass
        "alpha_netherrack_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/netherrack.png")),  # Netherrack
        "alpha_sand_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/sand.png")),  # Sand
        "alpha_snow_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/snow.png")),  # Snow
        "alpha_bookshelf_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/bookshelf_tile.png")),
        "alpha_coal_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/coal_ore_tile.png")),
        "alpha_cobblestone_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/cobblestone_tile.png")),
        "alpha_diamond_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/diamond_ore_tile.png")),
        "alpha_dirt_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/dirt_tile.png")),
        "alpha_gravel_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/gravel_tile.png")),
        "alpha_hay_bale_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/hay_bale_tile.png")),
        "alpha_iron_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/iron_ore_tile.png")),
        "alpha_lapis_ore_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/lapis_ore_tile.png")),
        "alpha_lava_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/lava_tile.png")),
        "alpha_leaf_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/leaf.png")),
        "alpha_mine_entrance_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/mine_entrance_tile.png")),
        "alpha_oak_log_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "alpha_oak_planks_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_planks_tile.png")),
        "alpha_obsidian_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/obsidian_tile.png")),
        "alpha_stone_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/stone_tile.png")),
        "alpha_tree_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/oak_log_tile.png")),
        "alpha_water_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/water_tile.png")),
        "bedrock_tile": set_alpha(str(ASSETS_DIR / "tile_imgs/bedrock.png")),
    }

    # [EXPORT] Create Breaking Images
    BREAKING_LIST = [
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking1.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking2.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking3.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking4.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking5.png")).convert_alpha(),
        pygame.image.load(str(ASSETS_DIR / "breaking/breaking6.png")).convert_alpha()
    ]

    # [EXPORT]
    INFOBAR_IMAGES = {
        "full_heart" : pygame.image.load(str(ASSETS_DIR / "FullHeart_20x20.png")).convert(),  # Full Heart (2)
        "half_heart" : pygame.image.load(str(ASSETS_DIR / "half_heart_20x20.png")).convert(),  # Half Heart (1)
        "empty_heart" : pygame.image.load(str(ASSETS_DIR / "empty_heart_20x20.png")).convert(),  # Empty Heart (0)
        "full_hunger" : pygame.image.load(str(ASSETS_DIR / "hunger_20x20.png")),  # Full Hunger (2)
        "half_hunger" : pygame.image.load(str(ASSETS_DIR / "half_hunger_20x20.png")),  # Half Hunger (1)
        "empty_hunger" : pygame.image.load(str(ASSETS_DIR / "empty_hunger_20x20.png")),  # Empty Hunger (0)
        "slot": pygame.image.load(str(ASSETS_DIR / "item_imgs/slot.png")).convert(),
        "experience_bar": pygame.image.load(str(ASSETS_DIR / "item_imgs/experience.png")).convert(),
    }

    context = Context(
        ITEM_IMAGES = ITEM_IMAGES,
        TC_GLINTS = TC_GLINTS,
        TILE_IMAGES = TILE_IMAGES,
        BREAKING_LIST = BREAKING_LIST,
        INFOBAR_IMAGES = INFOBAR_IMAGES
    )

    global player, World, screen, TimerRunning, world
    world = pygame.Surface((750, 750))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    rng = RandomNumberGenerator(seed := GetSeed())
    World = TilecraftWorld(rng, seed)  # Create World
    player = Player(context, rng)  # Create Player
    screen = Screen(rng)  # Create Text Screen
    TimerRunning = True
    hasGeneratedOverworld = True

    # return context to be passed around
    return context, rng

def create_world():
    global hasGeneratedOverworld, hasGeneratedUnderground
    hasGeneratedOverworld = False
    hasGeneratedUnderground = 'Not Loaded'
    global display, clock, world, netherGenerated, background, numList, call, difference, FPS, individual_frame, start, load, frame, loading, previous_frame
    pygame.init()  # Initialise Pygame Module
    display = pygame.display.set_mode((750, 750))  # Set display
    pygame.display.set_caption("Tilecraft Beta 1.0 Pre-Release 3")  # Set title
    clock = pygame.time.Clock()
    netherGenerated = False
    background = (255, 255, 255)
    numList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ']
    call = False
    load = optionData()
    Quit()
    start = time.time()
    individual_frame = 0
    previous_frame = 0
    difference = 0
    frame = 0
    loading = pygame.image.load(str(ASSETS_DIR / "loading.png")).convert()
    signal = Main()  #Start Game by Calling the Main Loop
    if signal == 'title screen':
        title_screen()
    elif signal == 'death screen':
        death_screen()

'''Function to handle all commands'''

#UP TO HERE
def commands(number, val, rng: RandomNumberGenerator, screen: Screen, timer: SpeedrunTimer):
    global player, cobblestone_index, obsidian_index, item_name_list, FPS, experience, inventory_list, hotbar_order, hotbar_index, mode, hotbar_item, item_val_list, background, enchantable_list, flint_val, gravel_val, blacksmith_book, bool_blacksmith_iron, bool_blacksmith_diamond, bool_blacksmith_bread, blacksmith_iron, blacksmith_diamond, blacksmith_bread, endTime, bound_overworld_portal, overworld_portal, diaval, call, actualX, actualY, dimension
    for o in range(number):
        if val == "/lootvillagehay":  # Loot Village Hay
            if player.dimension == 'Overworld':
                if player.inventory.hotbar_item is not None:
                    if player.inventory.hotbar_item.name == "Stone Hoe":
                        for j in range(len(World.bound_village)):
                            if (World.bound_village[j][0][0] < player.x < World.bound_village[j][0][2]) and (
                                    World.bound_village[j][1][0] < player.y < World.bound_village[j][1][2]):
                                hay = rng.next_random(25, 45)
                                player.inventory.add(Item("Hay Bale", hay, None, None))
                                screen.print("+" + str(hay) + " Hay Bale")
                                actualX = World.bound_village[j][0][1]
                                actualY = World.bound_village[j][1][1]
                                World.empty_vil1.append([actualX, actualY])
                                World.bound_village.remove(World.bound_village[j])
                                call = True
                                empty_vil()
                                break
                    else:
                        screen.print("Require Stone Hoe")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a village")
                else:
                    screen.print("Require Stone Hoe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/lootvillagebeds":  # Loot Village Beds
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_village2)):
                    if (World.bound_village2[j][0][0] < player.x < World.bound_village2[j][0][2]) and (
                            World.bound_village2[j][1][0] < player.y < World.bound_village2[j][1][2]):
                        beds = rng.next_random(2, 7)
                        player.inventory.add(Item("Bed", beds, None, None))
                        screen.print("+" + str(beds) + " Beds")
                        actualX = World.bound_village2[j][0][1]
                        actualY = World.bound_village2[j][1][1]
                        World.empty_vil2.append([actualX, actualY])
                        World.bound_village2.remove(World.bound_village2[j])
                        call = True
                        empty_vil()
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a village")
            else:
                screen.print("You are not in the overworld")
        elif val == "/lootvillageblacksmith":  # Loot Village Blacksmith
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_village3)):
                    if (World.bound_village3[j][0][0] < player.x < World.bound_village3[j][0][2]) and (World.bound_village3[j][1][0] < player.y < World.bound_village3[j][1][2]):

                        # GENERATE IRON VALUES
                        for k in range(5):
                            if k == 1 or k == 2 or k == 3:
                                bool_blacksmith_iron = True
                                break
                            else:
                                bool_blacksmith_iron = False
                        if bool_blacksmith_iron:
                            blacksmith_iron = rng.next_random(1, 7)
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
                            blacksmith_diamond = rng.next_random(1, 5)
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
                            blacksmith_bread = rng.next_random(1, 14)
                        else:
                            blacksmith_bread = 0

                        # UPDATE AND PRINT INVENTORY VALUES
                        if blacksmith_iron > 0:
                            screen.print(f"+{blacksmith_iron} Iron Ingot")
                            player.inventory.add(Item("Iron Ingot", blacksmith_iron, None, None))
                        if blacksmith_diamond > 0:
                            screen.print(f"+{blacksmith_diamond} Diamond")
                            player.inventory.add(Item("Diamond", blacksmith_diamond, None, None))
                        if blacksmith_bread > 0:
                            screen.print(f"+{blacksmith_bread} Bread")
                            player.inventory.add(Item("Bread", blacksmith_bread, None, None))

                        actualX = World.bound_village3[j][0][1]
                        actualY = World.bound_village3[j][1][1]
                        World.empty_vil3.append([actualX, actualY])
                        World.bound_village3.remove(World.bound_village3[j])
                        call = True
                        empty_vil()
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a village")
            else:
                screen.print("You are not in the overworld")
        elif val == '/lootvillagelibrary':
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_village4)):
                    if (World.bound_village4[j][0][0] < player.x < World.bound_village4[j][0][2]) and (World.bound_village4[j][1][0] < player.y < World.bound_village4[j][1][2]):
                        library_bookshelf = rng.next_random(1, 3)
                        library_books = rng.next_random(7, 14)
                        screen.print(f"+{library_bookshelf} Bookshelf")
                        screen.print(f"+{library_books} Books")
                        player.inventory.add(Item("Bookshelf", library_bookshelf, None, None))
                        player.inventory.add(Item("Book", library_books, None, None))
                        actualX = World.bound_village4[j][0][1]
                        actualY = World.bound_village4[j][1][1]
                        World.empty_vil4.append([actualX, actualY])
                        World.bound_village4.remove(World.bound_village4[j])
                        call = True
                        empty_vil()
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a village")
            else:
                screen.print("You are not in the overworld")
        elif val == "/dimensionnether":  # Enter Nether dimension
            for j in range(len(World.bound_overworld_portal)):
                if (World.bound_overworld_portal[j][0][0] < player.x < World.bound_overworld_portal[j][0][2]) and (
                        World.bound_overworld_portal[j][1][0] < player.y < World.bound_overworld_portal[j][1][2]) and player.dimension == 'Overworld':
                    player.dimension = 'Nether'
                    screen.print("Entering Nether Dimension...")
                    actualX = World.bound_overworld_portal[j][0][1]
                    actualY = World.bound_overworld_portal[j][1][1]
                    background = (255, 153, 153)
                    player.x /= 8
                    player.y /= 8
                    call = True
                    World.generateNether()
                    if actualX / 8 not in World.nether_portal or actualY / 8 not in World.nether_portal:
                        # Generating Nether Portal coordinates (IN NETHER) and bounding box
                        World.nether_portal.append([actualX / 8, actualY / 8])
                        World.bound_nether_portal.append([[actualX / 8 - 10 / 16, actualX / 8, actualX / 8 + 10 / 16],
                                                    [actualY / 8 - 10 / 16, actualY / 8, actualY / 8 + 10 / 16]])
                    break
            if call:
                call = False
            else:
                screen.print("You are not at a nether portal")
        elif val == "/dimensionoverworld":  # Enter overworld dimension
            if player.dimension == 'Nether':
                for j in range(len(World.bound_nether_portal)):
                    if (World.bound_nether_portal[j][0][0] < player.x < World.bound_nether_portal[j][0][2]) and (
                            World.bound_nether_portal[j][1][0] < player.y < World.bound_nether_portal[j][1][2]):
                        player.dimension = 'Overworld'
                        screen.print("Entering Overworld Dimension...")
                        actualX = World.bound_nether_portal[j][0][1]
                        actualY = World.bound_nether_portal[j][1][1]
                        background = (255, 255, 255)
                        player.x *= 8
                        player.y *= 8
                        call = True
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a nether portal")
            else:
                screen.print("You are already in the overworld")
        elif val == "/lootbastion":
            if player.dimension == 'Nether':
                for j in range(len(World.bound_bastion)):
                    if (World.bound_bastion[j][0][0] < player.x < World.bound_bastion[j][0][2]) and (
                            World.bound_bastion[j][1][0] < player.y < World.bound_bastion[j][1][2]):
                        player.inventory.add(Item("Pigstep Disc", 1, None, None))
                        screen.print("+1 Pigstep Disc")
                        actualX = World.bound_bastion[j][0][1]
                        actualY = World.bound_bastion[j][1][1]
                        World.empty_bastion.append([actualX, actualY])
                        World.bound_bastion.remove(World.bound_bastion[j])
                        call = True
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a bastion.")
            else:
                screen.print("You are not in the nether")
        elif val == "/playpigstep":

            # Declare Variables
            pigstep_disc_bool = False
            jukebox_bool = False

            for i in player.inventory.items:
                if i is not None:
                    if i.name == "Pigstep Disc":  # Pigstep Disc
                        pigstep_disc_bool = True
                        break
            for i in player.inventory.items:
                if i is not None:
                    if i.name == "Jukebox":  # Jukebox
                        jukebox_bool = True
                        break

            if pigstep_disc_bool and jukebox_bool:  # Play Pigstep
                pygame.mixer.init()
                pygame.mixer.music.load(str(ASSETS_DIR / "pigstep.mp3"))
                pygame.mixer.music.set_volume(10)
                pygame.mixer.music.play()
                MusicPlayer(screen, timer, player.advancements) #Update Advancement and Speedrun Details
            else:
                screen.print("Error: Not Enough Resources")
        elif val == '/lootruinedportal':  # Loot Ruined Portal
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_ruined_portal)):
                    if (World.bound_ruined_portal[j][0][0] < player.x < World.bound_ruined_portal[j][0][2]) and (
                            World.bound_ruined_portal[j][1][0] < player.y < World.bound_ruined_portal[j][1][2]):
                        R_iron_val = rng.next_random(2, 7)
                        R_flint_val = rng.next_random(1, 3)
                        R_golden_carrot_val = rng.next_random(0, 6)
                        R_golden_apple_val = rng.next_random(0, 2)
                        R_obsidian_val = rng.next_random(0, 3)
                        player.inventory.add(Item("Iron Ingot", R_iron_val, None, None))  # Add Iron Ingot
                        screen.print(f"+{R_iron_val} Iron Ingot")
                        player.inventory.add(Item("Flint", R_flint_val, None, None))  # Add Flint
                        screen.print(f"+{R_flint_val} Flint")
                        if R_golden_carrot_val > 0:  # Add Golden Carrot
                            screen.print(f"+{R_golden_carrot_val} Golden Carrot")
                            player.inventory.add(Item("Golden Carrot", R_golden_carrot_val, None, None))
                        if R_golden_apple_val > 0:  # Add Golden Apple
                            screen.print(f"+{R_golden_apple_val} Golden Apple")
                            player.inventory.add(Item("Golden Apple", R_golden_apple_val, None, None))
                        if R_obsidian_val > 0:  # Add Obsidian
                            screen.print(f"+{R_obsidian_val} Obsidian")
                            player.inventory.add(Item("Obsidian", R_obsidian_val, None, None))
                        actualX = World.bound_ruined_portal[j][0][1]
                        actualY = World.bound_ruined_portal[j][1][1]
                        World.empty_ruined_portal1.append([actualX, actualY])
                        World.bound_ruined_portal.remove(World.bound_ruined_portal[j])
                        call = True
                        empty_ruined_portals()
                        break
                if call:
                    call = False
                else:
                    screen.print("You are not at a ruined portal")
            else:
                screen.print("You are not in the overworld")
        elif val == '/portalcomplete':  # Complete Ruined Portal
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_ruined_portal2)):
                    if (World.bound_ruined_portal2[j][0][0] < player.x < World.bound_ruined_portal2[j][0][2]) and (
                            World.bound_ruined_portal2[j][1][0] < player.y < World.bound_ruined_portal2[j][1][2]):
                        obsidian_num = 10 - World.obsidian_counts[
                            j]  # Set number of obsidian remaining to complete the portal (max. 5)
                        flint_and_steel_bool = False
                        obsidian_bool = False

                        for i in player.inventory.items:
                            if i is not None:
                                if i.name == 'Flint and Steel':  # Test for flint and steel
                                    flint_and_steel_bool = True
                                    break
                        if obsidian_num == 0:
                            obsidian_bool = True
                        for i in player.inventory.items:
                            if i is not None:
                                if i.name == "Obsidian" and i.number >= obsidian_num:  # Test for enough obsidian
                                    obsidian_index = player.inventory.items.index(i)
                                    obsidian_bool = True
                                    break

                        if flint_and_steel_bool and obsidian_bool:
                            if obsidian_num > 0:
                                player.inventory.items[obsidian_index].number -= obsidian_num
                                screen.print(f"-{obsidian_num} Obsidian")
                                screen.print("Ruined Portal has been completed")
                            else:
                                screen.print("Portal is already complete")
                            actualX = World.bound_ruined_portal2[j][0][1]
                            actualY = World.bound_ruined_portal2[j][1][1]
                            World.empty_ruined_portal2.append([actualX, actualY])
                            World.bound_ruined_portal2.remove(World.bound_ruined_portal2[j])
                            World.overworld_portal.append([actualX, actualY])
                            World.bound_overworld_portal.append([[actualX - 10 / 16, actualX, actualX + 10 / 16],
                                                           [actualY - 10 / 16, actualY, actualY + 10 / 16]])
                            call = True
                            empty_ruined_portals()
                            break
                        elif obsidian_bool and not flint_and_steel_bool:
                            screen.print("Require Flint and Steel")
                            break
                        elif flint_and_steel_bool and not obsidian_bool:
                            screen.print(f"Require {obsidian_num} Obsidian")
                            break
                        else:
                            screen.print(f"Require {obsidian_num} Obsidian")
                            screen.print("Require Flint and Steel")
                            break
                if call:
                    call = False
                else:
                    screen.print("You are not at a ruined portal")
            else:
                screen.print("You are not in the overworld")
        elif val == '/table':
            if load == 'Cheats':
                print_cheats(screen, list(ITEM_TYPES.keys()))
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == '/give':
            if load == 'Cheats':
                length = len(list(ITEM_TYPES.keys())) - 1
                screen.start_typing(f"Item ID (0 - {length}): ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == '/tp':
            if load == 'Cheats':
                screen.start_typing("Coordinates (X,Y): ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == "/enchant":
            if load == "Cheats":
                screen.start_typing("Enchantment (Name, Lvl): ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == "/experience":
            if load == "Cheats":
                screen.start_typing("Experience Level: ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        else:
            screen.print("Invalid Function")


'''Empty Structures'''

# Displays empty village
def empty_vil():
    global actualX, actualY, bool_empty_vil1, bool_empty_vil2, empty_vil_total, bool_empty_vil3, bool_empty_vil4
    bool_empty_vil1 = False
    bool_empty_vil2 = False
    bool_empty_vil3 = False
    bool_empty_vil4 = False
    for i in range(len(World.empty_vil1)):
        if (actualX in World.empty_vil1[i]) and (actualY in World.empty_vil1[i]):
            bool_empty_vil1 = True
    for i in range(len(World.empty_vil2)):
        if (actualX in World.empty_vil2[i]) and (actualY in World.empty_vil2[i]):
            bool_empty_vil2 = True
    for i in range(len(World.empty_vil3)):
        if (actualX in World.empty_vil3[i]) and (actualY in World.empty_vil3[i]):
            bool_empty_vil3 = True
    for i in range(len(World.empty_vil4)):
        if (actualX in World.empty_vil4[i]) and (actualY in World.empty_vil4[i]):
            bool_empty_vil4 = True
    if bool_empty_vil1 and bool_empty_vil2 and bool_empty_vil3 and bool_empty_vil4:
        World.empty_vil_total.append([actualX, actualY])

# Displays empty ruined portal
def empty_ruined_portals():
    global actualX, actualY, empty_ruined_portal_total
    bool_empty_ruined_portal1 = False
    bool_empty_ruined_portal2 = False
    for i in range(len(World.empty_ruined_portal1)):
        if (actualX in World.empty_ruined_portal1[i]) and (actualY in World.empty_ruined_portal1[i]):
            bool_empty_ruined_portal1 = True
    for i in range(len(World.empty_ruined_portal2)):
        if (actualX in World.empty_ruined_portal2[i]) and (actualY in World.empty_ruined_portal2[i]):
            bool_empty_ruined_portal2 = True
    if bool_empty_ruined_portal1 and bool_empty_ruined_portal2:
        World.empty_ruined_portal_total.append([actualX, actualY])


'''Title Screen Accessory Functions'''


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
    window1.title('Tilecraft Beta 1.0 Pre-Release 3')
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
    window2.title('Tilecraft Beta 1.0 Pre-Release 3')
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
    window3.title('Tilecraft Beta 1.0 Pre-Release 3')
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
    window.title('Tilecraft Beta 1.0 Pre-Release 3')
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
    canvas1.create_text(375, 75, fill="black", font=regular_font, text="Beta 1.0 Pre-Release 3")
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

def RemoveItem():
    global player
    all_lists = [player.enchanting_table.items, player.inventory.items, player.craft_interface.items,
                 player.crafting_grid.items, player.furnace.items, player.compressor.items, player.grindstone.items]
    for i in all_lists:
        for j in range(len(i)):
            if i[j] is not None:
                if i[j].number <= 0:
                    i[j] = None
                elif i[j].durability is not None:
                    if i[j].durability <= 0:
                        i[j] = None
    player.enchanting_table.items, player.inventory.items, player.craft_interface.items, \
    player.crafting_grid.items, player.furnace.items, player.compressor.items, player.grindstone.items = all_lists
    if player.holding_item.item is not None:
        if player.holding_item.item.number <= 0:
            player.holding_item.item = None
        elif player.holding_item.item.durability is not None:
            if player.holding_item.item.durability <= 0:
                player.holding_item.item = None
