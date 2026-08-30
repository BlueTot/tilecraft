import tkinter  
import tkinter.font 
import random  
import pygame  
import math 
import sys 
from typing import Optional

from tilecraft import ASSETS_DIR , VERSION
from .cheats import print_cheats, give, enchant, teleport, experience
from .constants import ITEM_TYPES, Item, TILE_IMAGE_MAPPING, RandomNumberGenerator, Context, create_context
from .generation import Tile, OverworldGeneratedList, OverworldGenerate, SpawnOverworldGenerate, SpawnOverworldBoundGenerate, UndergroundGeneratedList, SpawnUndergroundGenerate, UndergroundGenerate, UndergroundGeneratePortal, OverworldGeneratePortal, NetherGeneratedList, SpawnNetherGenerate, SpawnNetherBoundGenerate, NetherGenerate
from .inventory import Inventory, Hotbar, Armour, SmallCraftingInterface, CraftingTableInterface, FurnaceInterface, EnchantingTable, Compressor, Grindstone, HoldingItem
from .player_info import HealthBar, HungerBar, Experience, ExperienceBar


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
    def __init__(self, rng: RandomNumberGenerator, player, world):
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
        self.player = player
        self.world = world

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
                        NumberLimit(number, self.typingText, self.rng, self, timer, self.player, self.world)
                    except ValueError:
                        self.print("Invalid integer")
                else:
                    number = 1  # Set number to 1 when number is not specified
                    NumberLimit(number, self.typingText, self.rng, self, timer, self.player, self.world)
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
    def generate_chunks(self, player_dimension: str):
        global hasGeneratedUnderground
        if player_dimension == 'Overworld':
            for i in self.render_list:
                if i not in self.overworld_generated_list:
                    self.village, self.ruined_portal, self.obsidian_counts, self.overworld_generated_list, \
                    self.bound_village, self.bound_village2, self.bound_village3, self.bound_village4, self.bound_ruined_portal, self.bound_ruined_portal2, self.UnderTiles, self.Tiles = \
                    OverworldGenerate(self.rng, i[0], i[1], self.village, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4,
                                                      self.bound_ruined_portal, self.bound_ruined_portal2, self.seed, self.UnderTiles, self.Tiles)
        elif player_dimension == "Underground":
            if not self.undergroundGenerated:
                hasGeneratedUnderground = 'Generating'
            if hasGeneratedUnderground == "Generated":
                for i in self.render_list:
                    if i not in self.UndergroundGeneratedList:
                        self.UndergroundUnderTiles, self.UndergroundTiles = UndergroundGenerate(self.rng, self.seed, i[0], i[1], self.UndergroundUnderTiles, self.UndergroundTiles, self.UndergroundGeneratedList)
        elif player_dimension == 'Nether':
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
    def generateNether(self, player_x: float, player_y: float):
        global netherGenerated 
        if not netherGenerated:
            netherGenerated = True

            # Initialise nether portal bounding box
            self.bound_nether_portal = []
            self.bastion, self.fortress = SpawnNetherGenerate(self.rng, self.seed)
            self.bound_bastion, self.bound_fortress = SpawnNetherBoundGenerate(self.bastion, self.fortress)
            self.nether_generated_list = NetherGeneratedList(player_x, player_y)

    def render(self, display, context: Context, player_dimension: str, player_left: int, player_top: int, player_rect: pygame.Rect, player_breaking_time: float, player_target: tuple[int, int]):
        global netherrack_tile, hotbar_imgs, slot, number_list, experience, pygame_enchant_imgs, enchant_name_list, player, hasGeneratedUnderground, bedrock_tile
        # player.health_hunger_update()

        def tile_image(tile_name: str) -> pygame.Surface:
            return context.TILE_IMAGES[TILE_IMAGE_MAPPING[tile_name].alpha_image_name]

        # DRAW OVERWORLD DIMENSION
        if player_dimension == "Overworld":
            for key, value in self.UnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                    else:
                        display.blit(context.TILE_IMAGES["bedrock_tile"], (value.x * 32 - player_left, value.y * 32 - player_top))
                    pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            for key, value in self.Tiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                        pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            # DRAWING OVERWORLD STRUCTURES
            for k in range(len(self.village)):
                if -32 <= (self.village[k][0] * 32 - player_left) <= 1032 and -32 <= (self.village[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (255, 165, 0), (self.village[k][0] * 32 - player_left, self.village[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.ruined_portal)):
                if -32 <= (self.ruined_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.ruined_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (56, 0, 89), (self.ruined_portal[k][0] * 32 - player_left, self.ruined_portal[k][1] * 32 - player_top), 10, 10)

            # DRAWING OVERWORLD EMPTY STRUCTURES
            for k in range(len(self.empty_vil_total)):
                if -32 <= (self.empty_vil_total[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_vil_total[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (153, 102, 0), (self.empty_vil_total[k][0] * 32 - player_left, self.empty_vil_total[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.empty_ruined_portal_total)):
                if -32 <= (self.empty_ruined_portal_total[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_ruined_portal_total[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (255, 255, 255), (self.empty_ruined_portal_total[k][0] * 32 - player_left, self.empty_ruined_portal_total[k][1] * 32 - player_top), 12, 12)
            # DRAWING OVERWORLD NETHER PORTALS
            for k in range(len(self.overworld_portal)):
                if -32 <= (self.overworld_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.overworld_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (128, 0, 128), (self.overworld_portal[k][0] * 32 - player_left, self.overworld_portal[k][1] * 32 - player_top), 10, 10)

        #DRAW UNDERGROUND DIMENSION
        elif player_dimension == "Underground" and hasGeneratedUnderground == "Generated":
            for key, value in self.UndergroundUnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                    else:
                        display.blit(context.ITEM_IMAGES["bedrock_tile"], (value.x * 32 - player_left, value.y * 32 - player_top))
                    pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline
            for key, value in self.UndergroundTiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player_left) <= 1032 and -32 <= (key[1] * 32 - player_top) <= 1032:
                    if value.tile != "Air":
                        display.blit(tile_image(value.tile), (value.x * 32 - player_left, value.y * 32 - player_top)) #Draw Image
                        pygame.draw.rect(display, (100, 100, 100), (value.x * 32 - player_left, value.y * 32 - player_top, 32, 32), 1) #Draw Border Outline

        # DRAW NETHER DIMENSION
        elif player_dimension == "Nether":
            # DRAWING NETHERRACK TEXTURES
            for k in range(player_rect.x - 384, player_rect.x + 384, 24):
                for j in range(player_rect.y - 384, player_rect.y + 384, 24):
                    display.blit(context.ITEM_IMAGES["netherrack_tile"], (k, j))
            # DRAWING NETHER NETHER PORTALS
            for k in range(len(self.nether_portal)):
                if -32 <= (self.nether_portal[k][0] * 32 - player_left) <= 1032 and -32 <= (self.nether_portal[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (128, 0, 128), (self.nether_portal[k][0] * 32 - player_left, self.nether_portal[k][1] * 32 - player_top), 10, 10)
            # DRAWING NETHER STRUCTURES
            for k in range(len(self.fortress)):
                if -32 <= (self.fortress[k][0] * 32 - player_left) <= 1032 and -32 <= (self.fortress[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (134, 71, 71), (self.fortress[k][0] * 32 - player_left, self.fortress[k][1] * 32 - player_top), 10, 10)
            for k in range(len(self.bastion)):
                if -32 <= (self.bastion[k][0] * 32 - player_left) <= 1032 and -32 <= (self.bastion[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (218, 165, 32), (self.bastion[k][0] * 32 - player_left, self.bastion[k][1] * 32 - player_top), 10, 10)
            # DRAWING NETHER EMPTY STRUCTURES
            for k in range(len(self.empty_bastion)):
                if -32 <= (self.empty_bastion[k][0] * 32 - player_left) <= 1032 and -32 <= (self.empty_bastion[k][1] * 32 - player_top) <= 1032:
                    pygame.draw.circle(display, (0, 0, 0), (self.empty_bastion[k][0] * 32 - player_left, self.empty_bastion[k][1] * 32 - player_top), 10, 10)

        # DRAW BREAKING ANIMATION
        if 1 <= math.floor(player_breaking_time) <= 6:
            display.blit(context.BREAKING_LIST[math.floor(player_breaking_time) - 1], (player_target[0] * 32 - player_left, player_target[1] * 32 - player_top))
        pygame.draw.rect(display, (50, 50, 50), (player_target[0] * 32 - player_left, player_target[1] * 32 - player_top, 32, 32), 1)  # Draw target block outline


# common screen interface
class Interface:
    def __init__(self, display: pygame.Surface, context: Context, screen: Screen, player, world: TilecraftWorld, timer: SpeedrunTimer, rng: RandomNumberGenerator) -> None:
        self.display = display
        self.context = context
        self.screen = screen
        self.player = player
        self.world = world
        self.timer = timer
        self.rng = rng
        self.next_screen: Optional[Interface] = None

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def render(self) -> None:
        pass


class GameScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if not self.screen.isTyping:
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
                    self.player.mode = 'inventory'
                # Advancements Key
                if event.key == pygame.K_f:
                    if not self.player.advancements:
                        self.screen.print("YOU HAVE NOT EARNED ANY ADVANCEMENTS")
                    else:
                        self.screen.print("Advancements: ")
                        for i in self.player.advancements:
                            self.screen.print(f"- {i}")
                # Input and chat key
                if event.key == pygame.K_t:
                    self.screen.start_typing('')
                # Eat key
                if event.key == pygame.K_q:
                    if self.player.inventory.hotbar_item is not None:
                        if self.player.inventory.hotbar_item.itemType == "Food":
                            if self.player.hunger < 20:
                                if self.player.inventory.hotbar_item.name == 'Bread':
                                    index = self.player.inventory.items.index(self.player.inventory.hotbar_item)
                                    self.player.inventory.items[index].number -= 1
                                    self.player.hunger += 5
                                # GOLDEN CARROT
                                elif self.player.inventory.hotbar_item.name == 'Golden Carrot':
                                    index = self.player.inventory.items.index(self.player.inventory.hotbar_item)
                                    self.player.inventory.items[index].number -= 1
                                    self.player.hunger += 6
                                # GOLDEN APPLE
                                elif self.player.inventory.hotbar_item.name == 'Golden Apple':
                                    index = self.player.inventory.items.index(self.player.inventory.hotbar_item)
                                    self.player.inventory.items[index].number -= 1
                                    self.player.hunger += 5
                                    self.player.regenerate_start_time = 0
                                    self.player.regenerate_val = True
                                else:
                                    self.screen.print("You are not holding a food item!")
                                # self.player.health_hunger_update()  # UPDATE HEALTH / HUNGER
                        else:
                            self.screen.print("You are not holding a food item!")
                    else:
                        self.screen.print("You are not holding a food item!")
                if event.key == pygame.K_1:
                    self.player.set_hotbar(0)
                if event.key == pygame.K_2:
                    self.player.set_hotbar(1)
                if event.key == pygame.K_3:
                    self.player.set_hotbar(2)
                if event.key == pygame.K_4:
                    self.player.set_hotbar(3)
                if event.key == pygame.K_5:
                    self.player.set_hotbar(4)
                if event.key == pygame.K_6:
                    self.player.set_hotbar(5)
                if event.key == pygame.K_7:
                    self.player.set_hotbar(6)
                if event.key == pygame.K_8:
                    self.player.set_hotbar(7)
                if event.key == pygame.K_9:
                    self.player.set_hotbar(8)
                if event.key == pygame.K_0:
                    self.player.debug_menu = not self.player.debug_menu
                if event.key == pygame.K_a:  # Turn Left
                    pos = self.player.direction_list.index(self.player.direction)
                    self.player.direction = self.player.direction_list[pos - 1]
                if event.key == pygame.K_d:  # Turn Right
                    pos = self.player.direction_list.index(self.player.direction)
                    if pos == 3:
                        self.player.direction = self.player.direction_list[0]
                    else:
                        self.player.direction = self.player.direction_list[pos + 1]
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                if pygame.mouse.get_pressed(3)[2]:  # Right Click
                    self.player.mouse_button = 2
                    if self.player.inventory.hotbar_item is not None:
                        if self.player.inventory.hotbar_item.name == 'Crafting Table': #Crafting Key
                            self.player.mode = 'crafting'
                        elif self.player.inventory.hotbar_item.name == 'Furnace': #Smelting Key
                            self.player.mode = 'smelting'
                        elif self.player.inventory.hotbar_item.name == 'Enchanting Table': #Enchanting Key
                            self.player.mode = 'enchanting'
                        elif self.player.inventory.hotbar_item.name == 'Compressor': #Compressing Key
                            self.player.mode = 'compressing'
                        elif self.player.inventory.hotbar_item.name == "Grindstone": #Repairing and Disenchanting Key
                            self.player.mode = 'repairing and disenchanting'
                        elif self.player.inventory.hotbar_item.name == "Bucket": #Picking up liquids
                            self.player.pick_up_liquid()
                        elif self.player.inventory.hotbar_item.name == "Water Bucket" or \
                                self.player.inventory.hotbar_item.name == "Lava Bucket":  #Placing liquids
                            self.player.place_liquid()
                        else:
                            self.player.place_tile()
                elif pygame.mouse.get_pressed(3)[0]:
                    self.player.mouse_button = 1
                    self.player.isBreaking = True
            if event.type == pygame.MOUSEBUTTONUP:
                if self.player.mouse_button == 1:
                    self.player.breaking_time = 0
                    self.player.isBreaking = False

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: #Type Space
                    self.screen.type(' ')
                elif event.key == pygame.K_RETURN: #Enter Key
                    self.screen.stop_typing(self.timer, self.player)
                elif event.key == pygame.K_BACKSPACE: #Delete
                    self.screen.delete()
                else:
                    char = str(pygame.key.name(event.key)) #Get Key name
                    if len(char) == 1: #Check to prevent non-alphabetical and non-number keys
                        self.screen.type(char)


    def render(self, world_map: pygame.Surface, fps: float, frame_count: int) -> Optional[str]:
        global true_play_time

        if not self.screen.isTyping:
            # Kill self.player
            if self.player.dead:
                minute = int(play_time_seconds // 60)
                seconds = int(round(play_time_seconds % 60))
                true_play_time = "Time Played:   " + str(minute) + "m " + str(seconds) + "s"
                pygame.quit()
                return 'death screen'
            if self.player.isBreaking:
                self.player.breaking(fps)
            self.player.move()  # Move self.player

        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]: #Scroll Up
                self.screen.scroll_up()
            elif keys[pygame.K_DOWN]: #Scroll Down
                self.screen.scroll_down()

        self.display.fill((0, 0, 0))  # Fill world_map border black
        world_map.fill(background)  # Fill world_map background colour
        self.player.health_update(frame_count)  # Update self.player Health
        self.world.render_chunks(self.player.left, self.player.right, self.player.top, self.player.bottom)  # Generate list of all chunks that are loaded
        self.world.generate_chunks(self.player.dimension)  # Generate Chunks that are loaded but have not been generated before
        self.world.render(world_map, self.context, self.player.dimension, self.player.left, self.player.top, self.player.rect, self.player.breaking_time, self.player.target)  # Render all world_map blocks to world_map
        self.player.remove_items() #Remove Items if their number is 0
        self.player.render(self.context, world_map, screen_width, screen_height, fps)  # Render self.player and self.player accessories to world_map
        self.timer.render(world_map, play_time_seconds)
        advancements_update(self.screen, self.timer, self.player.advancements, self.player.inventory.items, self.player.armour.items, self.player.dimension)  # Update Advancements
        self.screen.render(world_map) #Render Text self.screen

        # general rendering
        self.display.blit(world_map, (0, 0))  # Render map to display
        pygame.display.flip()  # Update Display


class InventoryScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.armour.handle_left_click(mouse, self.player.holding_item)
                self.player.craft_interface.handle_left_click(mouse, self.player.holding_item, self.player.inventory)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.craft_interface.handle_right_click(mouse, self.player.holding_item)

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.armour.render(world_map, self.context, mouse, is_holding) #Render Armour Grid for self.player
        self.player.craft_interface.render(world_map, self.context, mouse, is_holding) #Render Small Crafting Grid
        self.player.craft_interface.update() #Update Small 2x2 Crafting Grid

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


class CraftingScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.crafting_grid.handle_left_click(mouse, self.player.holding_item, self.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.crafting_grid.handle_right_click(mouse, self.player.holding_item) 

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.crafting_grid.render(world_map, self.context, mouse, is_holding) #Render 3x3 Crafting Grid
        self.player.crafting_grid.update()  #Update 3x3 Crafting Grid

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


class SmeltingScreen(Interface):
    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.furnace.handle_left_click(mouse, self.player.holding_item, self.player.inventory) 

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.furnace.handle_right_click(mouse, self.player.holding_item) 

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.furnace.render(world_map, self.context, mouse, fps, is_holding) #Render Furnace Interface
        self.player.furnace.smelt(self.context, fps, self.player.experience) #Furnace Smelting

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


class EnchantingScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.enchanting_table.handle_left_click(mouse, self.player.holding_item, self.player.experience, self.rng)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.enchanting_table.handle_right_click(mouse, self.player.holding_item)

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.enchanting_table.render(world_map, self.context, mouse, is_holding) #Render Enchanting Table Interface

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


class CompressingScreen(Interface):
    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.compressor.handle_left_click(mouse, self.player.holding_item, self.player.inventory)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.compressor.handle_right_click(mouse, self.player.holding_item)

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.compressor.render(world_map, self.context, mouse, fps, is_holding) #Render Compressor Interface
        self.player.compressor.compress(fps) #Compressing Process

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


class GrindstoneScreen(Interface):

    def handle_event(self, event: pygame.event.Event) -> None:
        mouse = pygame.mouse.get_pos()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e: # Exit 
                self.player.mode = "game"
                return
            elif event.key == pygame.K_1: #1
                self.player.inventory.hotbar_swap(mouse, 1)
            elif event.key == pygame.K_2: #2
                self.player.inventory.hotbar_swap(mouse, 2)
            elif event.key == pygame.K_3: #3
                self.player.inventory.hotbar_swap(mouse, 3)
            elif event.key == pygame.K_4: #4
                self.player.inventory.hotbar_swap(mouse, 4)
            elif event.key == pygame.K_5: #5
                self.player.inventory.hotbar_swap(mouse, 5)
            elif event.key == pygame.K_6: #6
                self.player.inventory.hotbar_swap(mouse, 6)
            elif event.key == pygame.K_7: #7
                self.player.inventory.hotbar_swap(mouse, 7)
            elif event.key == pygame.K_8: #8
                self.player.inventory.hotbar_swap(mouse, 8)
            elif event.key == pygame.K_9: #9
                self.player.inventory.hotbar_swap(mouse, 9)

        elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
            
            if pygame.mouse.get_pressed(3)[0]: #Left Click
                self.player.inventory.handle_left_click(mouse, self.player.holding_item)
                self.player.grindstone.handle_left_click(mouse, self.player.holding_item, self.player.inventory, self.player.experience)

            elif pygame.mouse.get_pressed(3)[2]: #Right Click
                self.player.inventory.handle_right_click(mouse, self.player.holding_item)
                self.player.grindstone.handle_right_click(mouse, self.player.holding_item)

    def render(self, world_map: pygame.Surface, fps: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.display.fill((0, 0, 0))
        world_map.fill((211, 211, 211))

        is_holding = self.player.holding_item.item is not None
        self.player.inventory.render(self.context, world_map, mouse, is_holding) #Render Inventory Grid
        self.player.grindstone.render(world_map, self.context, mouse, is_holding) #Render Grindstone Interface
        self.player.grindstone.repair_and_disenchant() #Update repaired/disenchanted item

        self.player.remove_items() #Remove all items with number of 0 or durability of 0
        self.player.holding_item.render(world_map, self.context) #Render the item the user is holding

        self.display.blit(world_map, (0, 0))  # Render map to self.display
        pygame.display.flip()  # Update self.display


# Game Loop
def main(display: pygame.Surface, clock: pygame.time.Clock, context: Context):
    global mode, val, comma, number, called, play_time, endTime, \
           minute, seconds, true_play_time, play_time_seconds, hasGeneratedOverworld, loading, hasGeneratedUnderground 

    world = pygame.Surface((750, 750))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    rng = RandomNumberGenerator(seed := GetSeed())
    timer: SpeedrunTimer = SpeedrunTimer(load)
    frame_count = 0
    World: Optional[TilecraftWorld] = None
    screen: Optional[Screen] = None
    player: Optional[Player] = None

    game_screen: Interface = GameScreen(display, context, screen, player, World, timer, rng)
    inventory_screen: Interface = InventoryScreen(display, context, screen, player, World, timer, rng)
    crafting_screen: Interface = CraftingScreen(display, context, screen, player, World, timer, rng)
    smelting_screen: Interface = SmeltingScreen(display, context, screen, player, World, timer, rng)
    enchanting_screen: Interface = EnchantingScreen(display, context, screen, player, World, timer, rng)
    compressing_screen: Interface = CompressingScreen(display, context, screen, player, World, timer, rng)
    grindstone_screen: Interface = GrindstoneScreen(display, context, screen, player, World, timer, rng)

    while True:

        clock.tick(60) # maximum FPS of 60
        frame_count += 1 # increment no. of frames
        fps = clock.get_fps()
        play_time_seconds = pygame.time.get_ticks() / 1000.0 # in seconds 

        events = pygame.event.get()
        if hasGeneratedOverworld and (hasGeneratedUnderground == "Not Loaded" or hasGeneratedUnderground == "Generated"):

            if player.mode == "game":
                for event in events:
                    ret = game_screen.handle_event(event)
                    if ret is not None:
                        return ret

                ret = game_screen.render(world, fps, frame_count)
                if ret is not None:
                    return ret

            elif player.mode == "inventory":
                for event in events:
                    inventory_screen.handle_event(event)
                inventory_screen.render(world, fps)

            elif player.mode == "crafting":
                for event in events:
                    crafting_screen.handle_event(event)
                crafting_screen.render(world, fps)

            elif player.mode == "smelting":
                for event in events:
                    smelting_screen.handle_event(event)
                smelting_screen.render(world, fps)

            elif player.mode == "enchanting":
                for event in events:
                    enchanting_screen.handle_event(event)
                enchanting_screen.render(world, fps)

            elif player.mode == "compressing":
                for event in events:
                    compressing_screen.handle_event(event)
                compressing_screen.render(world, fps)

            elif player.mode == "repairing and disenchanting":
                for event in events:
                    grindstone_screen.handle_event(event)
                grindstone_screen.render(world, fps)

        elif not hasGeneratedOverworld and hasGeneratedUnderground == "Not Loaded":
            display.fill((255, 255, 255))
            for i in range(0, 750, 32):
                for j in range(0, 750, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font(str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 37)
            display.blit(font.render("Generating Overworld", False, (255, 255, 255)), (180, 225))
            pygame.display.flip()
            World, screen, player = generate_world(context, rng, seed)

            game_screen.screen = screen # set screen
            game_screen.world = World # set world
            game_screen.player = player # set player

            inventory_screen.screen = screen
            inventory_screen.world = World
            inventory_screen.player = player

            crafting_screen.screen = screen
            crafting_screen.world = World
            crafting_screen.player = player

            smelting_screen.screen = screen
            smelting_screen.world = World
            smelting_screen.player = player

            enchanting_screen.screen = screen
            enchanting_screen.world = World
            enchanting_screen.player = player

            compressing_screen.screen = screen
            compressing_screen.world = World
            compressing_screen.player = player

            grindstone_screen.screen = screen
            grindstone_screen.world = World
            grindstone_screen.player = player

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
def NumberLimit(number, val, rng: RandomNumberGenerator, screen: Screen, timer: SpeedrunTimer, player, World: TilecraftWorld):
    if number > 16:
        screen.print("ERROR: Invalid Integer")
    elif number < 1:
        screen.print("ERROR: Invalid Integer")
    else:
        commands(number, val, rng, screen, timer, player, World)


#Player Class and Methods
class Player:
    def __init__(self, context: Context, rng: RandomNumberGenerator, world: TilecraftWorld):
        self.world = world

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
            if world.Tiles[(self.x, self.y)].tile != "Air": #If tile that player spawns in is not air
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
    def health_update(self, frame_count: int):
        if self.hunger >= 17 and self.health < 20 and frame_count % 16 == 0:
            self.hunger -= 1
            self.health += 1
        if self.hunger == 0 and frame_count % 16 == 0:
            self.health -= 1
        if self.health == 0:
            self.dead = True
        if self.regenerate_val and self.health < 20:
            if self.regenerate_start_time < 60:
                if frame_count % 5 == 0:
                    self.health += 1
                self.regenerate_start_time += 1
            else:
                self.regenerate_val = False

    # remove items that shouldn't be there
    def remove_items(self):
        all_lists = [self.enchanting_table.items, self.inventory.items, self.craft_interface.items,
                    self.crafting_grid.items, self.furnace.items, self.compressor.items, self.grindstone.items]
        for i in all_lists:
            for j in range(len(i)):
                if i[j] is not None:
                    if i[j].number <= 0:
                        i[j] = None
                    elif i[j].durability is not None:
                        if i[j].durability <= 0:
                            i[j] = None
        self.enchanting_table.items, self.inventory.items, self.craft_interface.items, \
        self.crafting_grid.items, self.furnace.items, self.compressor.items, self.grindstone.items = all_lists
        if self.holding_item.item is not None:
            if self.holding_item.item.number <= 0:
                self.holding_item.item = None
            elif self.holding_item.item.durability is not None:
                if self.holding_item.item.durability <= 0:
                    self.holding_item.item = None

    def collide(self): #Collisions with tiles
        global hasGeneratedUnderground
        self.canMove = True
        try:
            if self.dimension == "Overworld": #Overworld dimension
                call = False
                for key, value in self.world.Tiles.items():
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
                                        if self.world.UndergroundTiles[(round(self.x), round(self.y))].tile != "Mine Entrance":
                                            self.world.UndergroundTiles = UndergroundGeneratePortal(round(self.x), round(self.y), self.world.UndergroundTiles)
                                    except KeyError:
                                        self.world.generate_chunks(self.dimension)
                                        self.world.UndergroundTiles = UndergroundGeneratePortal(round(self.x), round(self.y), self.world.UndergroundTiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
            elif self.dimension == "Underground" and hasGeneratedUnderground == "Generated": #Underground dimension
                call = False
                for key, value in self.world.UndergroundTiles.items():
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
                                    if self.world.Tiles[(round(self.x), round(self.y))].tile != "Mine Entrance":
                                        self.world.Tiles = OverworldGeneratePortal(round(self.x), round(self.y), self.world.Tiles)
                                except KeyError:
                                    self.world.generate_chunks(self.dimension)
                                    self.world.Tiles = OverworldGeneratePortal(round(self.x), round(self.y), self.world.Tiles)
                            if value.tile == "Mine Entrance": #is colliding with portal
                                call = True
                                break
                if not call: #can re-enter portal
                    self.canEnterPortal = True
        except KeyError:
            self.world.generate_chunks(self.dimension)
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
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
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
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
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
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
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
                        self.hunger_mechanism()
                else:
                    self.distance += 1
                    self.hunger_mechanism()
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
                if self.world.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and self.world.Tiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    self.world.Tiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
            elif self.dimension == "Underground" and hasGeneratedUnderground == "Generated":
                if self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    self.world.UndergroundTiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y))
        except KeyError:
            self.world.generate_chunks(self.dimension)


    def place_tile(self): #Place tiles
        if self.isShifting: #is shifting = can edit background tiles
            if self.dimension == "Overworld": #Overworld background tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Open space to place tile
                        self.world.UnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1]) #Place tile
                        self.inventory.hotbar_item.number -= 1 #Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None #Remove from inventory
            elif self.dimension == "Underground": #Underground background tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
        else:
            if self.dimension == "Overworld": #Overworld Collision tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.Tiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.Tiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.Tiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.Tiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory
            elif self.dimension == "Underground": #Underground Collision Tiles
                if self.inventory.hotbar_item.hasTile:
                    if self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile(self.inventory.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.inventory.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.inventory.hotbar_item.number == 0:
                            self.inventory.hotbar_item = None  # Remove from inventory

    def breaking(self, fps: float): #Breaking process of tile
        if self.breaking_delay == 0:
            if self.isShifting: #can edit background tiles
                if self.dimension == "Overworld": #Overworld background tiles
                    tile = self.world.UnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None: #Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
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
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground background tiles
                    tile = self.world.UndergroundUnderTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
            else:
                if self.dimension == "Overworld": #Overworld collision tiles
                    tile = self.world.Tiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7
                elif self.dimension == "Underground": #Underground collision tiles
                    tile = self.world.UndergroundTiles[(self.target[0], self.target[1])]
                    if tile.breaking_time is not None:  # Can break tile, targeting correct tile
                        if math.floor(self.breaking_time) >= 7:
                            self.breaking_time = 0
                            self.break_tile(tile, fps)
                        else:
                            try:
                                CALLED = False
                                if self.inventory.hotbar_item is not None:  # not holding any item
                                    if self.inventory.hotbar_item.toolTier is not None:  # is holding item
                                        if self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.inventory.hotbar_item.mining_speed) / (tile.breaking_time * fps * 1.5) >= 1 / (fps/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / fps) / (tile.breaking_time * 1.5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.inventory.hotbar_item.itemType == tile.requireTool and self.inventory.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / fps) / (tile.breaking_time * 5)) * (1 + self.inventory.hotbar_item.mining_speed)
                                            CALLED = True
                                            self.isInstantMining = False
                                if not CALLED:  # code above didn't run
                                    if tile.requireToolTier == 0:  # no requirement
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 1.5)
                                        self.isInstantMining = False
                                    else:  # incorrect tool and tier
                                        self.breaking_time += (7 / fps) / (tile.breaking_time * 5)
                                        self.isInstantMining = False
                            except ZeroDivisionError:
                                self.breaking_time += 7

    def break_add_item(self, value, fps: float):
        if not self.isInstantMining:
            self.breaking_delay = fps * 3/10
        if self.dimension == "Overworld":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    self.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    self.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    self.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    self.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    self.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    self.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        self.inventory.add(Item("Flint", 1, None, None))
                    else:
                        self.inventory.add(Item("Gravel", 1, None, None))
                else:
                    self.inventory.add(Item(value.tile, 1, None, None))
        elif self.dimension == "Underground":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    self.inventory.add(Item("Oak Log", self.rng.next_random(1, 5), None, None))
                elif value.tile == "Stone":
                    self.inventory.add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    self.inventory.add(Item("Coal", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Lapis Ore":
                    self.inventory.add(Item("Lapis Lazuli", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Diamond Ore":
                    self.inventory.add(Item("Diamond", 1, None, None))
                    self.experience.add_points(12)
                elif value.tile == "Grass":
                    self.inventory.add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if self.rng.next_random(1, 10) == 1:
                        self.inventory.add(Item("Flint", 1, None, None))
                    else:
                        self.inventory.add(Item("Gravel", 1, None, None))
                else:
                    self.inventory.add(Item(value.tile, 1, None, None))
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

    def break_tile(self, value, fps: float):
        if self.isShifting:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UndergroundUnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
        else:
            if self.dimension == "Overworld":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.Tiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.inventory.hotbar_item is not None:
                    if self.inventory.hotbar_item.itemType == value.requireTool:
                        if self.inventory.hotbar_item.toolTier >= value.requireToolTier:
                            if self.inventory.hotbar_item.name == value.tile:
                                self.inventory.hotbar_item.number += 1
                            else:
                                self.break_add_item(value, fps)
                    elif value.requireToolTier == 0:
                        if self.inventory.hotbar_item.name == value.tile:
                            self.inventory.hotbar_item.number += 1
                        else:
                            self.break_add_item(value, fps)
                elif value.requireToolTier == 0:
                    self.break_add_item(value, fps)
                self.world.UndergroundTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])

    def pick_up_liquid(self): #Picking up liquids with a bucket
        if self.dimension == "Overworld": #Overworld
            if self.isShifting: #Background tiles
                if self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Water": #Wate
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision tiles
                if self.world.Tiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1],)
                elif self.world.Tiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
        elif self.dimension == "Underground": #Underground
            if self.isShifting: #Background Tiles
                if self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision Tiles
                if self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Water Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif self.world.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Lava Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])

    def place_liquid(self):
        if self.dimension == "Overworld":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.Tiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
        elif self.dimension == "Underground":
            if self.isShifting:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.inventory.hotbar_item.name == "Water Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.inventory.hotbar_item.name == "Lava Bucket":
                    self.inventory.hotbar_item.number -= 1
                    self.inventory.add(Item("Bucket", 1, None, None))
                    self.world.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])

    def render(self, context: Context, display: pygame.Surface, screen_width: int, screen_height: int, fps: float):

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
        elif self.direction == 'East':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (391, 375), width=4)
        elif self.direction == 'South':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (375, 391), width=4)
        elif self.direction == 'West':
            pygame.draw.line(display, (0, 0, 0), (375, 375), (359, 375), width=4)

        # render health and hunger bars
        self.health_bar.render(display, context, self.health)
        self.hunger_bar.render(display, context, self.hunger)

        # render experience bar
        self.experience_bar.render(display, self.experience.levels)

        # render hotbar
        self.hotbar.render(display, context, self.inventory.items[27:36], self.inventory.selected_hotbar)

        # RENDER DEBUG MENU
        if self.debug_menu:
            font9 = pygame.font.Font(
                str(ASSETS_DIR / "minecraft-font/MinecraftRegular-Bmg3.otf"), 25)
            version = font9.render(VERSION, True, (0, 0, 0), (255, 255, 255))
            display.blit(version, (0, 0))
            python_version = font9.render(f"Python {sys.version[0:6]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(python_version, (0, 25))
            pygame_version = font9.render("Graphics: pygame v2.1.2", True, (0, 0, 0), (255, 255, 255))
            display.blit(pygame_version, (0, 50))
            display_size = font9.render(f"Display Size: {screen_width}x{screen_height}", True, (0, 0, 0), (255, 255, 255))
            display.blit(display_size, (0, 75))
            SEEDs = font9.render(f"Seed: {self.world.seed}", True, (0, 0, 0), (255, 255, 255))
            display.blit(SEEDs, (0, 100))
            fps_font = font9.render(f"FPS: {fps:.2f}", True, (0, 0, 0), (255, 255, 255))
            display.blit(fps_font, (0, 125))
            Direction = font9.render(f"Facing: {self.direction}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Direction, (0, 150))
            Target = font9.render(f"Target Tile: {self.target[0]}, {self.target[1]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Target, (0, 175))
            Coords = font9.render(f"X: {round(self.x, 3)}, Y: {round(self.y, 3)}", True, (0, 0, 0), (255, 255, 255))
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


def generate_world(context: Context, rng: RandomNumberGenerator, seed: int) -> RandomNumberGenerator:
    global hasGeneratedOverworld

    # Play Minecraft Music (Sweden)
    pygame.mixer.init()
    pygame.mixer.music.load(str(ASSETS_DIR / "music/song") + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
    pygame.mixer.music.play()

    World = TilecraftWorld(rng, seed)  # Create World
    player = Player(context, rng, World)  # Create Player
    screen = Screen(rng, player, World)  # Create Text Screen
    hasGeneratedOverworld = True

    return World, screen, player 


def create_world():

    global hasGeneratedOverworld, hasGeneratedUnderground, netherGenerated, background, call, load, loading 
    hasGeneratedOverworld = False
    hasGeneratedUnderground = 'Not Loaded'

    pygame.init()  # Initialise Pygame Module
    display = pygame.display.set_mode((750, 750))  # Set display
    pygame.display.set_caption(VERSION)  # Set title
    clock = pygame.time.Clock()
    clock.get_time()
    context = create_context()

    netherGenerated = False
    background = (255, 255, 255)
    call = False
    load = optionData()
    Quit()
    loading = pygame.image.load(str(ASSETS_DIR / "loading.png")).convert()

    signal = main(display, clock, context)  #Start Game by Calling the Main Loop

    if signal == 'title screen':
        title_screen()
    elif signal == 'death screen':
        death_screen()


'''Function to handle all commands'''

#UP TO HERE
def commands(number, val, rng: RandomNumberGenerator, screen: Screen, timer: SpeedrunTimer, player: Player, World: TilecraftWorld):
    global cobblestone_index, obsidian_index, item_name_list, experience, inventory_list, hotbar_order, hotbar_index, mode, hotbar_item, item_val_list, background, enchantable_list, flint_val, gravel_val, blacksmith_book, bool_blacksmith_iron, bool_blacksmith_diamond, bool_blacksmith_bread, blacksmith_iron, blacksmith_diamond, blacksmith_bread, endTime, bound_overworld_portal, overworld_portal, diaval, call, actualX, actualY, dimension
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
                                empty_vil(World)
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
                        empty_vil(World)
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
                        empty_vil(World)
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
                        empty_vil(World)
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
                        empty_ruined_portals(World)
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
                            empty_ruined_portals(World)
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
def empty_vil(World: TilecraftWorld):
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
def empty_ruined_portals(World: TilecraftWorld):
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
