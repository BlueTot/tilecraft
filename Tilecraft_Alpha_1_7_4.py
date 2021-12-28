import tkinter  # Tkinter module
import tkinter.font  # Fonts module
import random  # Random module
import pygame  # Pygame module
import time  # Time module
import math #Math module
import noise #Perlin Noise module
import os #OS module

title_screen_mode = 'normal'

'''Cheats Datapack Section'''

# PRINT CHEATS TABLE
def print_cheats(name):
    global screen
    screen.print("CODE   ITEM NAME")
    screen.print('-' * 25)
    for i in range(len(name)):
        screen.print((str(i) + ' ' * (7 - len(str(i))) + str(name[i])))

# /GIVE COMMAND
def give(name, stack, Type, item_id):
    global screen
    item_id = item_id.replace(' ', '') #REMOVE WHITESPACES
    # CALCULATE CODE AND AMOUNT
    if ',' in item_id and item_id[-1] != ',':
        comma = item_id.index(',')
        code = item_id[0:comma]
        amount = item_id[comma + 1:len(item_id)]
    else:
        code = item_id
        amount = 1
    try:
        code = int(code)
        amount = int(amount)
        if 0 <= code <= 45:
            add_item = [name[code], amount, stack[code], Type[code], None]
            return add_item
        else:
            screen.print("Please enter a number between 0 and 45.")
            return None
    except ValueError:
        screen.print("Invalid Input")

#/TELEPORT COMMAND
def teleport(internalX, internalY, coords):
    global screen
    if ',' in coords:
        try:
            x = coords[0:coords.index(',')]
            y = coords[coords.index(',') + 1:]
            x = int(x)
            y = int(y)
            internalX = x
            internalY = y
        except ValueError:
            screen.print("Invalid input")
    else:
        screen.print("Invalid input")
    return internalX, internalY

'''Advancements Section'''

def advancements_update(advancements, inventory_list, armour_list, dimension, load, start):
    global screen, TimerRunning
    name_list = []
    enchantments_list = []
    for i in inventory_list: #Compile list of item names and enchantments
        if i is not None:
            name_list.append(i[0])
            enchantments_list.append(i[4])
        else:
            name_list.append(None)
            enchantments_list.append(None)
    armour_enchantment_list = []
    for i in armour_list: #Compile list of enchantments for armour list
        if i is not None:
            armour_enchantment_list.append(i[4])
        else:
            armour_enchantment_list.append(None)

    if "Stone Age" not in advancements and "Cobblestone" in name_list: #Get Cobblestone
        advancements.append("Stone Age")
        screen.print("Advancement unlocked: Stone Age")
    if "Getting an Upgrade" not in advancements and "Stone Pickaxe" in name_list: #Get a Stone Pickaxe
        advancements.append("Getting an Upgrade")
        screen.print("Advancement unlocked: Getting an Upgrade")
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
        if armour_list[0][4] is not None:
            if armour_list[0][0] == 'Tier 1 Diamond Plate' and armour_list[0][4] == [['Protection', 5], ['Unbreaking', 3]]:
                max_t1 = True
    if armour_list[1] is not None:
        if armour_list[1][4] is not None:
            if armour_list[1][0] == 'Tier 2 Diamond Plate' and armour_list[1][4] == [['Protection', 5], ['Unbreaking', 3]]:
                max_t2 = True
    if armour_list[2] is not None:
        if armour_list[2][4] is not None:
            if armour_list[2][0] == 'Tier 3 Diamond Plate' and armour_list[2][4] == [['Protection', 5], ['Unbreaking', 3]]:
                max_t3 = True
    if max_t1 and max_t2 and max_t3 and 'God Gear' not in advancements: #Get a full set of Protection V Unbreaking III Diamond Armour
        advancements.append("God Gear")
        screen.print("Advancement unlocked: God Gear")
        TimerRunning = False

    return advancements

def MusicPlayer(advancements):
    global screen, speedrun_timer, TimerRunning
    if "Music Player" not in advancements:  # Music Player: Play Pigstep
        advancements.append("Music Player")
        screen.print("Advancement unlocked: Music Player")
        TimerRunning = False

        return advancements

def SpeedrunTimer(display, PlayTime):
    global speedrun_time, TimerRunning
    font = pygame.font.Font('images_vA1_7_4/monofur/monof55.ttf', 25)
    if load == 'Music Player' or load == 'God Gear':
        if TimerRunning:
            if PlayTime // 3600 >= 10:  # HOURS 2 digits
                HourTime = str(int(PlayTime // 3600))
            else:  # HOURS 1 digit
                HourTime = f"0{int(PlayTime // 3600)}"
            if PlayTime // 60 >= 10:  # MINUTES 2 digits
                MinuteTime = str(int(PlayTime // 60))
            else:  # MINUTES 1 digit
                MinuteTime = f"0{int(PlayTime // 60)}"
            if PlayTime % 60 >= 10:  # SECONDS 2 digits
                SecondTime = str(round(PlayTime % 60))
            else:  # SECONDS 1 digit
                SecondTime = f"0{round(PlayTime % 60)}"
            MSecondTime = (round(PlayTime, 3) - math.floor(PlayTime)) * 1000  # Milliseconds
            if MSecondTime >= 100:  # 3 digits
                MSecondTime = str(int(MSecondTime))
            elif MSecondTime >= 10:  # 2 digits
                MSecondTime = f"0{int(MSecondTime)}"
            else:  # 1 digit
                MSecondTime = f"00{int(MSecondTime)}"
            speedrun_time = HourTime + ":" + MinuteTime + ":" + SecondTime + '.' + MSecondTime  # Current in-game time
        display.blit(font.render(speedrun_time, True, (0, 0, 0), (255, 255, 255)), (504 - (13 * len(speedrun_time)), 0)) #Render Speedrun Timer

'''World Generation Classes and Functions'''

class Block:
    def __init__(self, block, x, y):
        global grass, stone
        self.block = block
        self.x = x
        self.y = y
        if self.block == 'Grass':
            self.image = grass
        elif self.block == 'Stone':
            self.image = stone

class Chunk:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.biome = None

def Random(seed, pos, Range):
    start, stop = Range
    mod = stop - start + 1
    x, y = pos
    v1 = abs((seed * math.sin(x) + x * seed + x % 12 + seed) % mod)
    v2 = abs((seed * math.sin(y) + y * seed + y % 12 + seed) % mod)
    return (v1 + v2) // 2 + start

def OverworldGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list


def OverworldGenerate(ChunkX, ChunkY, villages, caves, waters, deep_caves, lavas, ruined_portals, obsidian_counts,
                      generated_list, bound_village, bound_village2, bound_village3, bound_village4, bound_cave, bound_cave2,
                      bound_water, bound_water2, bound_lava, bound_deep_cave, bound_deep_cave2, bound_ruined_portal,
                      bound_ruined_portal2, seed, biomes, BlockList):
    num = Random(seed, (ChunkX, ChunkY), (1, 25))
    if num == 1 or num == 2:
        villages.append([ChunkX - 12, ChunkY - 12])  # Village
        bound_village.append([[ChunkX - 12 - 10 / 24, ChunkX - 12, ChunkX - 12 + 10 / 24], [ChunkY - 12 - 10 / 24, ChunkY - 12, ChunkY - 12 + 10 / 24]])  # Bounding box for village 1
        bound_village2.append([[ChunkX - 12 - 10 / 24, ChunkX - 12, ChunkX - 12 + 10 / 24], [ChunkY - 12 - 10 / 24, ChunkY - 12, ChunkY - 12 + 10 / 24]])  # Bounding box for village 2
        bound_village3.append([[ChunkX - 12 - 10 / 24, ChunkX - 12, ChunkX - 12 + 10 / 24], [ChunkY - 12 - 10 / 24, ChunkY - 12, ChunkY - 12 + 10 / 24]])  # Bounding box for village 3
        bound_village4.append([[ChunkX - 12 - 10 / 24, ChunkX - 12, ChunkX - 12 + 10 / 24], [ChunkY - 12 - 10 / 24, ChunkY - 12, ChunkY - 12 + 10 / 24]])  # Bounding box for village 4
    elif num == 3 or num == 4 or num == 5 or num == 6:
        caves.append([ChunkX - 10, ChunkY - 10])  # Cave
        bound_cave.append([[ChunkX - 10 - 10 / 24, ChunkX - 10, ChunkX - 10 + 10 / 24], [ChunkY - 10 - 10 / 24, ChunkY - 10, ChunkY - 10 + 10 / 24]])  # Bounding box for cave 1
        bound_cave2.append([[ChunkX - 10 - 10 / 24, ChunkX - 10, ChunkX - 10 + 10 / 24], [ChunkY - 10 - 10 / 24, ChunkY - 10, ChunkY - 10 + 10 / 24]])  # Bounding box for cave 2
    elif num == 7 or num == 8 or num == 9:
        waters.append([ChunkX - 14, ChunkY - 14])  # Water Pool
        bound_water.append([[ChunkX - 14 - 10 / 24, ChunkX - 14, ChunkX - 14 + 10 / 24], [ChunkY - 14 - 10 / 24, ChunkY - 14, ChunkY - 14 + 10 / 24]])  # Bounding box for water pool 1
        bound_water2.append([[ChunkX - 14 - 10 / 24, ChunkX - 14, ChunkX - 14 + 10 / 24], [ChunkY - 14 - 10 / 24, ChunkY - 14, ChunkY - 14 + 10 / 24]])  # Bounding box for water pool 2
    elif num == 10 or num == 11 or num == 12:
        lavas.append([ChunkX - 8, ChunkY - 8])  # Lava Pool
        bound_lava.append([[ChunkX - 8 - 10 / 24, ChunkX - 8, ChunkX - 8 + 10 / 24], [ChunkY - 8 - 10 / 24, ChunkY - 8, ChunkY - 8 + 10 / 24]])  # bounding box for lava pool
    elif num == 13 or num == 14:
        deep_caves.append([ChunkX - 6, ChunkY - 6])  # Deep Cave
        bound_deep_cave.append([[ChunkX - 6 - 10 / 24, ChunkX - 6, ChunkX - 6 + 10 / 24], [ChunkY - 6 - 10 / 24, ChunkY - 6, ChunkY - 6 + 10 / 24]])  # Bounding box for deep cave 1
        bound_deep_cave2.append([[ChunkX - 6 - 10 / 24, ChunkX - 6, ChunkX - 6 + 10 / 24], [ChunkY - 6 - 10 / 24, ChunkY - 6, ChunkY - 6 + 10 / 24]])  # Bounding box for deep cave 2
    elif num == 15 or num == 16 or num == 17:
        ruined_portals.append([ChunkX - 1, ChunkY - 1])  # Ruined Portal
        obsidian_counts.append(int(Random(seed, (ChunkX, ChunkY), (5, 10))))  # Obsidian remaining in ruined portal
        bound_ruined_portal.append([[ChunkX - 1 - 10 / 24, ChunkX - 1, ChunkX - 1 + 10 / 24], [ChunkY - 1 - 10 / 24, ChunkY - 1, ChunkY - 1 + 10 / 24]])  # Bounding box for ruined portal 1
        bound_ruined_portal2.append([[ChunkX - 1 - 10 / 24, ChunkX - 1, ChunkX - 1 + 10 / 24], [ChunkY - 1 - 10 / 24, ChunkY - 1, ChunkY - 1 + 10 / 24]])  # Bounding box for ruined portal 2
    generated_list.append([ChunkX, ChunkY])  # Chunk is now generated and cannot generate again

    #Generate Biome for Chunk
    value = noise.pnoise2(ChunkX / 100.0,
                            ChunkY / 100.0,
                            octaves=6,
                            persistence=0.5,
                            lacunarity=0.5,
                            repeatx=1024,
                            repeaty=1024,
                            base=seed)  # Perlin Noise Generation
    chunk = Chunk(ChunkX, ChunkY, value)

    #Convert Chunk to Blocks
    if chunk.value < 0:
        chunk.biome = 'Stone'
    else:
        chunk.biome = 'Plains'
    biomes.append(chunk)
    for j in range(16):
        for k in range(16):
            if chunk.biome == 'Plains':
                BlockList.append(Block('Grass', chunk.x + j, chunk.y + k))
            elif chunk.biome == 'Stone':
                BlockList.append(Block('Stone', chunk.x + j, chunk.y + k))

    return villages, caves, waters, deep_caves, lavas, ruined_portals, obsidian_counts, generated_list, \
           bound_village, bound_village2, bound_village3, bound_village4, bound_cave, bound_cave2, bound_water, \
           bound_water2, bound_lava, bound_deep_cave, bound_deep_cave2, bound_ruined_portal, bound_ruined_portal2, biomes, BlockList


def SpawnOverworldGenerate(seed):
    li_vil = []
    li_c = []
    li_w = []
    li_l = []
    li_dc = []
    li_ruined_portal = []
    villages = []
    caves = []
    waters = []
    lavas = []
    deep_caves = []
    ruined_portals = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = Random(seed, (i, j), (1, 25))
            if num == 1 or num == 2:
                li_vil.append([i, j])
            elif num == 3 or num == 4 or num == 5 or num == 6:
                li_c.append([i, j])
            elif num == 7 or num == 8 or num == 9:
                li_w.append([i, j])
            elif num == 10 or num == 11 or num == 12:
                li_l.append([i, j])
            elif num == 13 or num == 14:
                li_dc.append([i, j])
            elif num == 15 or num == 16 or num == 17:
                li_ruined_portal.append([i, j])

    # Village (Chunk Code: 4, 4)
    for i in li_vil:
        villages.append([i[0] - 12, i[1] - 12])

    # Cave (Chunk Code: 6, 6)
    for i in li_c:
        caves.append([i[0] - 10, i[1] - 10])

    # Water Pool (Chunk Code: 2, 2)
    for i in li_w:
        waters.append([i[0] - 14, i[1] - 14])

    # Lava Pool (Chunk Code: 8, 8)
    for i in li_l:
        lavas.append([i[0] - 8, i[1] - 8])

    # Deep Cave (Chunk Code: 10, 10)
    for i in li_dc:
        deep_caves.append([i[0] - 6, i[1] - 6])

    # Ruined Portal (Chunk Code: 15, 15)
    for i in li_ruined_portal:
        ruined_portals.append([i[0] - 1, i[1] - 1])
    obsidian_counts = []
    for i in range(len(ruined_portals)):
        obsidian_counts.append(int(Random(seed, (ruined_portals[i][0] + 1, ruined_portals[i][1] + 1), (5, 10))))

    #Generate Biomes for Spawn Chunks
    biomes = []
    for i in range(-64, 65, 16):  # Spawn Chunks (-64 --> 64 x and y)
        for j in range(-64, 65, 16):
            value = noise.pnoise2(i / 100.0,
                                  j / 100.0,
                                  octaves=6,
                                  persistence=0.5,
                                  lacunarity=0.5,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed)  # Perlin Noise Generation
            biomes.append(Chunk(i, j, value))

    #Convert Chunks into Blocks
    BlockList = []
    for i in biomes:
        if i.value < 0:
            i.biome = 'Stone'
        else:
            i.biome = 'Plains'
        # print(i.value)
    for i in biomes:
        for j in range(16):
            for k in range(16):
                if i.biome == 'Plains':
                    BlockList.append(Block('Grass', i.x + j, i.y + k))
                elif i.biome == 'Stone':
                    BlockList.append(Block('Stone', i.x + j, i.y + k))

    return villages, caves, waters, lavas, deep_caves, ruined_portals, obsidian_counts, biomes, BlockList


def SpawnOverworldBoundGenerate(villages, caves, waters, lavas, deep_caves, ruined_portals):
    bound_village, bound_cave, bound_water, bound_lava, bound_deep_cave, bound_ruined_portal = [], [], [], [], [], []
    for i in range(len(villages)):
        bound_village.append([])
        for j in range(2):
            bound_village[i].append([villages[i][j] - 10 / 24, villages[i][j], villages[i][j] + 10 / 24])
    for i in range(len(caves)):
        bound_cave.append([])
        for j in range(2):
            bound_cave[i].append([caves[i][j] - 10 / 24, caves[i][j], caves[i][j] + 10 / 24])
    for i in range(len(waters)):
        bound_water.append([])
        for j in range(2):
            bound_water[i].append([waters[i][j] - 10 / 24, waters[i][j], waters[i][j] + 10 / 24])
    for i in range(len(lavas)):
        bound_lava.append([])
        for j in range(2):
            bound_lava[i].append([lavas[i][j] - 10 / 24, lavas[i][j], lavas[i][j] + 10 / 24])
    for i in range(len(deep_caves)):
        bound_deep_cave.append([])
        for j in range(2):
            bound_deep_cave[i].append([deep_caves[i][j] - 10 / 24, deep_caves[i][j], deep_caves[i][j] + 10 / 24])
    for i in range(len(ruined_portals)):
        bound_ruined_portal.append([])
        for j in range(2):
            bound_ruined_portal[i].append(
                [ruined_portals[i][j] - 10 / 24, ruined_portals[i][j], ruined_portals[i][j] + 10 / 24])
    return bound_village, bound_cave, bound_water, bound_lava, bound_deep_cave, bound_ruined_portal

def NetherGeneratedList(x, y):
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i + x, j + y])
    return generated_list


def SpawnNetherGenerate(seed):
    li_bastion = []
    li_fortress = []
    bastions = []
    fortresses = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = Random(seed, (i, j), (1, 15))
            if num == 1 or num == 2 or num == 3:
                li_bastion.append([i, j])
            elif num == 4 or num == 5 or num == 6:
                li_fortress.append([i, j])

    #Bastion (Chunk Code: 10, 10)
    for i in li_bastion:
        bastions.append([i[0] - 6, i[1] - 6])

    #Fortress (Chunk Code: 6, 6)
    for i in li_fortress:
        fortresses.append([i[0] - 10, i[1] - 10])

    return bastions, fortresses

def SpawnNetherBoundGenerate(bastions, fortresses):
    bound_bastion, bound_fortress = [], []
    for i in range(len(bastions)):
        bound_bastion.append([])
        for j in range(2):
            bound_bastion[i].append([bastions[i][j] - 10 / 24, bastions[i][j], bastions[i][j] + 10 / 24])
    for i in range(len(fortresses)):
        bound_fortress.append([])
        for j in range(2):
            bound_fortress[i].append([fortresses[i][j] - 10 / 24, fortresses[i][j], fortresses[i][j] + 10 / 24])
    return bound_bastion, bound_fortress

def NetherGenerate(ChunkX, ChunkY, bastions, fortresses, generated_list, bound_bastion, seed):
    num = Random(seed, (ChunkX, ChunkY), (1, 15))
    if num == 1 or num == 2 or num == 3:
        bastions.append([ChunkX - 6, ChunkY - 6])  # Bastion
        bound_bastion.append([[ChunkX - 6 - 10 / 24, ChunkX - 6, ChunkX - 6 + 10 / 24], [ChunkY - 6 - 10 / 24, ChunkY - 6, ChunkY - 6 + 10 / 24]])  # Bounding box
    elif num == 4 or num == 5 or num == 6:
        fortresses.append([ChunkX - 10, ChunkY - 10])  # Fortress
    generated_list.append([ChunkX, ChunkY])  # Chunk is now generated and cannot generate again

    return bastions, fortresses, generated_list, bound_bastion

'''Main Part of Game Code'''

class TilecraftWorld:
    def __init__(self, seed):

        self.empty_cave1 = []
        self.empty_cave2 = []
        self.empty_cave_total = []
        self.empty_vil1 = []
        self.empty_vil2 = []
        self.empty_vil3 = []
        self.empty_vil4 = []
        self.empty_vil_total = []
        self.empty_water = []
        self.empty_deep_cave1 = []
        self.empty_deep_cave2 = []
        self.empty_deep_cave_total = []
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

        self.village, self.cave, self.water, self.lava, \
        self.deep_cave, self.ruined_portal, self.obsidian_counts, \
        self.biomes, self.BlockList = SpawnOverworldGenerate(self.seed)  # Spawn Generation for Structures and Biomes
        self.bound_village, self.bound_cave, self.bound_water, \
        self.bound_lava, self.bound_deep_cave, self.bound_ruined_portal = SpawnOverworldBoundGenerate(
            self.village, self.cave, self.water, self.lava, self.deep_cave, self.ruined_portal)  # Spawn Bounding Box Generation
        self.bound_cave2 = self.bound_cave.copy()
        self.bound_village2 = self.bound_village.copy()
        self.bound_village3 = self.bound_village.copy()
        self.bound_village4 = self.bound_village.copy()
        self.bound_water2 = self.bound_water.copy()
        self.bound_deep_cave2 = self.bound_deep_cave.copy()
        self.bound_ruined_portal2 = self.bound_ruined_portal.copy()
        self.overworld_generated_list = OverworldGeneratedList()

    #Generate Chunks Per Frame
    def generate_chunks(self):
        if player.dimension == 'Overworld':
            for i in self.render_list:
                if i not in self.overworld_generated_list:
                    self.village, self.cave, self.water, self.deep_cave, self.lava, self.ruined_portal, self.obsidian_counts, self.overworld_generated_list, \
                    self.bound_village, self.bound_village2, self.bound_village3, self.bound_village4, self.bound_cave, self.bound_cave2, self.bound_water, \
                    self.bound_water2, self.bound_lava, self.bound_deep_cave, self.bound_deep_cave2, self.bound_ruined_portal, self.bound_ruined_portal2, self.biomes, self.BlockList = \
                    OverworldGenerate(i[0], i[1], self.village, self.cave, self.water, self.deep_cave, self.lava, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4, self.bound_cave, self.bound_cave2,
                                                      self.bound_water, self.bound_water2, self.bound_lava, self.bound_deep_cave,
                                                      self.bound_deep_cave2, self.bound_ruined_portal, self.bound_ruined_portal2, self.seed, self.biomes, self.BlockList)
        elif player.dimension == 'Nether':
            for i in self.render_list:
                if i not in self.nether_generated_list:
                    self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion = NetherGenerate(i[0], i[1], self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion, self.seed)

    #Calculate Render List Per Frame
    def render_chunks(self, left, right, top, bottom):
        global render_list
        self.render_list = []
        self.render_blocks_list = []
        left_chunk = math.floor(left / 24) // 16 * 16
        right_chunk = math.floor(right / 24) // 16 * 16
        top_chunk = math.floor(top / 24) // 16 * 16
        bottom_chunk = math.floor(bottom / 24) // 16 * 16
        for i in range(left_chunk, right_chunk + 1, 16):
            for j in range(top_chunk, bottom_chunk + 1, 16):
                self.render_list.append([i, j])
        for i in range(left_chunk, right_chunk + 1):
            for j in range(top_chunk, bottom_chunk + 1):
                self.render_blocks_list.append([i, j])
        # print(self.render_list)

    # Generate nether for the first time
    def generateNether(self):
        global netherGenerated, player
        if not netherGenerated:
            netherGenerated = True

            # Initialise nether portal bounding box
            self.bound_nether_portal = []
            self.bastion, self.fortress = SpawnNetherGenerate(self.seed)
            self.bound_bastion, self.bound_fortress = SpawnNetherBoundGenerate(self.bastion, self.fortress)
            self.nether_generated_list = NetherGeneratedList(player.x, player.y)

    def render(self, display):
        global hotbar_imgs, slot, number_list, experience, pygame_enchant_imgs, pygame_imgs, enchant_name_list, player
        player.health_hunger_update()

        # DRAW OVERWORLD DIMENSION
        if player.dimension == "Overworld":
            for block in self.BlockList:
                if -24 <= (block.x * 24 - player.left) <= 528 and -24 <= (block.y * 24 - player.top) <= 528:
                    display.blit(block.image, (block.x * 24 - player.left, block.y * 24 - player.top))
            # DRAWING OVERWORLD STRUCTURES
            for k in range(len(self.village)):
                if -24 <= (self.village[k][0] * 24 - player.left) <= 528 and -24 <= (self.village[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (255, 165, 0), (self.village[k][0] * 24 - player.left, self.village[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.lava)):
                if -24 <= (self.lava[k][0] * 24 - player.left) <= 528 and -24 <= (self.lava[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (255, 0, 0), (self.lava[k][0] * 24 - player.left, self.lava[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.cave)):
                if -24 <= (self.cave[k][0] * 24 - player.left) <= 528 and -24 <= (self.cave[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (211, 211, 211), (self.cave[k][0] * 24 - player.left, self.cave[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.water)):
                if -24 <= (self.water[k][0] * 24 - player.left) <= 528 and -24 <= (self.water[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (173, 216, 230), (self.water[k][0] * 24 - player.left, self.water[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.deep_cave)):
                if -24 <= (self.deep_cave[k][0] * 24 - player.left) <= 528 and -24 <= (self.deep_cave[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (160, 82, 45), (self.deep_cave[k][0] * 24 - player.left, self.deep_cave[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.ruined_portal)):
                if -24 <= (self.ruined_portal[k][0] * 24 - player.left) <= 528 and -24 <= (self.ruined_portal[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (56, 0, 89), (self.ruined_portal[k][0] * 24 - player.left, self.ruined_portal[k][1] * 24 - player.top), 10, 10)

            # DRAWING OVERWORLD EMPTY STRUCTURES
            for k in range(len(self.empty_vil_total)):
                if -24 <= (self.empty_vil_total[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_vil_total[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (153, 102, 0), (self.empty_vil_total[k][0] * 24 - player.left, self.empty_vil_total[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.empty_cave_total)):
                if -24 <= (self.empty_cave_total[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_cave_total[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (112, 112, 112), (self.empty_cave_total[k][0] * 24 - player.left, self.empty_cave_total[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.empty_water)):
                if -24 <= (self.empty_water[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_water[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (0, 0, 255), (self.empty_water[k][0] * 24 - player.left, self.empty_water[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.empty_deep_cave_total)):
                if -24 <= (self.empty_deep_cave_total[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_deep_cave_total[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (101, 67, 33), (self.empty_deep_cave_total[k][0] * 24 - player.left, self.empty_deep_cave_total[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.empty_ruined_portal_total)):
                if -24 <= (self.empty_ruined_portal_total[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_ruined_portal_total[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (255, 255, 255), (self.empty_ruined_portal_total[k][0] * 24 - player.left, self.empty_ruined_portal_total[k][1] * 24 - player.top), 12, 12)
            # DRAWING OVERWORLD NETHER PORTALS
            for k in range(len(self.overworld_portal)):
                if -24 <= (self.overworld_portal[k][0] * 24 - player.left) <= 528 and -24 <= (self.overworld_portal[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (128, 0, 128), (self.overworld_portal[k][0] * 24 - player.left, self.overworld_portal[k][1] * 24 - player.top), 10, 10)

        # DRAW NETHER DIMENSION
        elif player.dimension == "Nether":
            # DRAWING NETHERRACK TEXTURES
            for k in range(player.rect.x - 384, player.rect.x + 384, 24):
                for j in range(player.rect.y - 384, player.rect.y + 384, 24):
                    display.blit(netherrack, (k, j))
            # DRAWING NETHER NETHER PORTALS
            for k in range(len(self.nether_portal)):
                if -24 <= (self.nether_portal[k][0] * 24 - player.left) <= 528 and -24 <= (self.nether_portal[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (128, 0, 128), (self.nether_portal[k][0] * 24 - player.left, self.nether_portal[k][1] * 24 - player.top), 10, 10)
            # DRAWING NETHER STRUCTURES
            for k in range(len(self.fortress)):
                if -24 <= (self.fortress[k][0] * 24 - player.left) <= 528 and -24 <= (self.fortress[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (134, 71, 71), (self.fortress[k][0] * 24 - player.left, self.fortress[k][1] * 24 - player.top), 10, 10)
            for k in range(len(self.bastion)):
                if -24 <= (self.bastion[k][0] * 24 - player.left) <= 528 and -24 <= (self.bastion[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (218, 165, 32), (self.bastion[k][0] * 24 - player.left, self.bastion[k][1] * 24 - player.top), 10, 10)
            # DRAWING NETHER EMPTY STRUCTURES
            for k in range(len(self.empty_bastion)):
                if -24 <= (self.empty_bastion[k][0] * 24 - player.left) <= 528 and -24 <= (self.empty_bastion[k][1] * 24 - player.top) <= 528:
                    pygame.draw.circle(world, (0, 0, 0), (self.empty_bastion[k][0] * 24 - player.left, self.empty_bastion[k][1] * 24 - player.top), 10, 10)

class Grid:
    def __init__(self, colour, rect, width, img):
        self.colour = colour
        self.rect = rect
        self.width = width
        self.img = img

class Text:
    def __init__(self, surface, x, y):
        self.surface = surface
        self.x = x
        self.y = y

class Button:
    def __init__(self, length, width, x, y, colour):
        self.length = length
        self.width = width
        self.x = x
        self.y = y
        self.colour = colour
        self.rect = pygame.Rect((x, y), (length, width))

    def render(self, display, text, size):
        self.font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', size)
        self.text = self.font.render(text, False, (0, 0, 0))
        pygame.draw.rect(display, self.colour, self.rect)
        pygame.draw.rect(display, (255, 255, 255), self.rect, 3)
        self.text_x = (self.length - len(text) * size) // 2
        if self.text_x < 0:
            self.text_x = 0
        self.text_y = (self.width - size) // 2
        display.blit(self.text, (self.x + self.text_x, self.y + self.text_y))

#Inventory Grid (36 Slots)
def InventoryGrid(display):
    global glint_list, item_name_list
    image_render()
    inventory_slots = [
        Grid((83, 83, 83), pygame.Rect((0, 260), (55, 55)), 2, player.image_list[0]),
        Grid((83, 83, 83), pygame.Rect((55, 260), (55, 55)), 2, player.image_list[1]),
        Grid((83, 83, 83), pygame.Rect((110, 260), (55, 55)), 2, player.image_list[2]),
        Grid((83, 83, 83), pygame.Rect((165, 260), (55, 55)), 2, player.image_list[3]),
        Grid((83, 83, 83), pygame.Rect((220, 260), (55, 55)), 2, player.image_list[4]),
        Grid((83, 83, 83), pygame.Rect((275, 260), (55, 55)), 2, player.image_list[5]),
        Grid((83, 83, 83), pygame.Rect((330, 260), (55, 55)), 2, player.image_list[6]),
        Grid((83, 83, 83), pygame.Rect((385, 260), (55, 55)), 2, player.image_list[7]),
        Grid((83, 83, 83), pygame.Rect((440, 260), (55, 55)), 2, player.image_list[8]),
        Grid((83, 83, 83), pygame.Rect((0, 315), (55, 55)), 2, player.image_list[9]),
        Grid((83, 83, 83), pygame.Rect((55, 315), (55, 55)), 2, player.image_list[10]),
        Grid((83, 83, 83), pygame.Rect((110, 315), (55, 55)), 2, player.image_list[11]),
        Grid((83, 83, 83), pygame.Rect((165, 315), (55, 55)), 2, player.image_list[12]),
        Grid((83, 83, 83), pygame.Rect((220, 315), (55, 55)), 2, player.image_list[13]),
        Grid((83, 83, 83), pygame.Rect((275, 315), (55, 55)), 2, player.image_list[14]),
        Grid((83, 83, 83), pygame.Rect((330, 315), (55, 55)), 2, player.image_list[15]),
        Grid((83, 83, 83), pygame.Rect((385, 315), (55, 55)), 2, player.image_list[16]),
        Grid((83, 83, 83), pygame.Rect((440, 315), (55, 55)), 2, player.image_list[17]),
        Grid((83, 83, 83), pygame.Rect((0, 370), (55, 55)), 2, player.image_list[18]),
        Grid((83, 83, 83), pygame.Rect((55, 370), (55, 55)), 2, player.image_list[19]),
        Grid((83, 83, 83), pygame.Rect((110, 370), (55, 55)), 2, player.image_list[20]),
        Grid((83, 83, 83), pygame.Rect((165, 370), (55, 55)), 2, player.image_list[21]),
        Grid((83, 83, 83), pygame.Rect((220, 370), (55, 55)), 2, player.image_list[22]),
        Grid((83, 83, 83), pygame.Rect((275, 370), (55, 55)), 2, player.image_list[23]),
        Grid((83, 83, 83), pygame.Rect((330, 370), (55, 55)), 2, player.image_list[24]),
        Grid((83, 83, 83), pygame.Rect((385, 370), (55, 55)), 2, player.image_list[25]),
        Grid((83, 83, 83), pygame.Rect((440, 370), (55, 55)), 2, player.image_list[26]),
        Grid((83, 83, 83), pygame.Rect((0, 425), (55, 55)), 2, player.image_list[27]),
        Grid((83, 83, 83), pygame.Rect((55, 425), (55, 55)), 2, player.image_list[28]),
        Grid((83, 83, 83), pygame.Rect((110, 425), (55, 55)), 2, player.image_list[29]),
        Grid((83, 83, 83), pygame.Rect((165, 425), (55, 55)), 2, player.image_list[30]),
        Grid((83, 83, 83), pygame.Rect((220, 425), (55, 55)), 2, player.image_list[31]),
        Grid((83, 83, 83), pygame.Rect((275, 425), (55, 55)), 2, player.image_list[32]),
        Grid((83, 83, 83), pygame.Rect((330, 425), (55, 55)), 2, player.image_list[33]),
        Grid((83, 83, 83), pygame.Rect((385, 425), (55, 55)), 2, player.image_list[34]),
        Grid((83, 83, 83), pygame.Rect((440, 425), (55, 55)), 2, player.image_list[35])
    ]

    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    numbers = [
        Text(font.render(player.number_list[0], False, (255, 255, 255)), 35, 295),
        Text(font.render(player.number_list[1], False, (255, 255, 255)), 90, 295),
        Text(font.render(player.number_list[2], False, (255, 255, 255)), 145, 295),
        Text(font.render(player.number_list[3], False, (255, 255, 255)), 200, 295),
        Text(font.render(player.number_list[4], False, (255, 255, 255)), 255, 295),
        Text(font.render(player.number_list[5], False, (255, 255, 255)), 310, 295),
        Text(font.render(player.number_list[6], False, (255, 255, 255)), 365, 295),
        Text(font.render(player.number_list[7], False, (255, 255, 255)), 420, 295),
        Text(font.render(player.number_list[8], False, (255, 255, 255)), 475, 295),
        Text(font.render(player.number_list[9], False, (255, 255, 255)), 35, 350),
        Text(font.render(player.number_list[10], False, (255, 255, 255)), 90, 350),
        Text(font.render(player.number_list[11], False, (255, 255, 255)), 145, 350),
        Text(font.render(player.number_list[12], False, (255, 255, 255)), 200, 350),
        Text(font.render(player.number_list[13], False, (255, 255, 255)), 255, 350),
        Text(font.render(player.number_list[14], False, (255, 255, 255)), 310, 350),
        Text(font.render(player.number_list[15], False, (255, 255, 255)), 365, 350),
        Text(font.render(player.number_list[16], False, (255, 255, 255)), 420, 350),
        Text(font.render(player.number_list[17], False, (255, 255, 255)), 475, 350),
        Text(font.render(player.number_list[18], False, (255, 255, 255)), 35, 405),
        Text(font.render(player.number_list[19], False, (255, 255, 255)), 90, 405),
        Text(font.render(player.number_list[20], False, (255, 255, 255)), 145, 405),
        Text(font.render(player.number_list[21], False, (255, 255, 255)), 200, 405),
        Text(font.render(player.number_list[22], False, (255, 255, 255)), 255, 405),
        Text(font.render(player.number_list[23], False, (255, 255, 255)), 310, 405),
        Text(font.render(player.number_list[24], False, (255, 255, 255)), 365, 405),
        Text(font.render(player.number_list[25], False, (255, 255, 255)), 420, 405),
        Text(font.render(player.number_list[26], False, (255, 255, 255)), 475, 405),
        Text(font.render(player.number_list[27], False, (255, 255, 255)), 35, 460),
        Text(font.render(player.number_list[28], False, (255, 255, 255)), 90, 460),
        Text(font.render(player.number_list[29], False, (255, 255, 255)), 145, 460),
        Text(font.render(player.number_list[30], False, (255, 255, 255)), 200, 460),
        Text(font.render(player.number_list[31], False, (255, 255, 255)), 255, 460),
        Text(font.render(player.number_list[32], False, (255, 255, 255)), 310, 460),
        Text(font.render(player.number_list[33], False, (255, 255, 255)), 365, 460),
        Text(font.render(player.number_list[34], False, (255, 255, 255)), 420, 460),
        Text(font.render(player.number_list[35], False, (255, 255, 255)), 475, 460)
    ]
    for i in range(len(inventory_slots)):
        display.blit(inventory_slots[i].img, (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
        pygame.draw.rect(display, inventory_slots[i].colour, inventory_slots[i].rect, inventory_slots[i].width)
        if player.inventory_list[i] is not None:
            if player.inventory_list[i][4] is not None:
                index = item_name_list.index(player.inventory_list[i][0])
                display.blit(glint_list[index], (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
    for i in numbers:
        display.blit(i.surface, (i.x, i.y))



#Armour Grid for Player
def ArmourGrid(display):
    image_render()
    armour_grid = [
        Grid((83, 83, 83), pygame.Rect((0, 160), (55, 55)), 2, player.armour_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((55, 160), (55, 55)), 2, player.armour_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((110, 160), (55, 55)), 2, player.armour_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((165, 160), (55, 55)), 2, player.armour_image_list[3]),
    ]
    for i in range(len(armour_grid)):
        display.blit(armour_grid[i].img, (armour_grid[i].rect.x, armour_grid[i].rect.y))
        pygame.draw.rect(display, armour_grid[i].colour, armour_grid[i].rect, armour_grid[i].width)
        if player.armour_list[i] is not None:
            if player.armour_list[i][4] is not None:
                index = item_name_list.index(player.armour_list[i][0])
                display.blit(glint_list[index], (armour_grid[i].rect.x, armour_grid[i].rect.y))
    pygame.draw.rect(display, (0, 0, 0), (0, 0, 220, 160)) #Draw Black Background
    pygame.draw.rect(display, (255, 0, 0), (85, 55, 50, 50)) #Draw Player Icon
    for i in player.layer_list: #Draw Armour Layers
        if i is not None:
            if i[1] == 1: #Tier 1
                pygame.draw.rect(display, i[0], (75, 45, 70, 70), 8)
            elif i[1] == 2: #Tier 2
                pygame.draw.rect(display, i[0], (66, 36, 89, 89), 8)
            elif i[1] == 3: #Tier 3
                pygame.draw.rect(display, i[0], (56, 26, 110, 110), 8)

#2x2 Small Crafting Grid within Inventory
def SmallCraftGrid(display):
    image_render()
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((260, 50), (55, 55)), 2, player.craft_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((315, 50), (55, 55)), 2, player.craft_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((260, 105), (55, 55)), 2, player.craft_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((315, 105), (55, 55)), 2, player.craft_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((425, 78), (55, 55)), 2, player.craft_image_list[4]),
    ]
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    arrow_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftBold-nMK1.otf', 24)
    crafting_numbers = [
        Text(font.render(player.craft_number_list[0], False, (255, 255, 255)), 295, 85),
        Text(font.render(player.craft_number_list[1], False, (255, 255, 255)), 350, 85),
        Text(font.render(player.craft_number_list[2], False, (255, 255, 255)), 295, 140),
        Text(font.render(player.craft_number_list[3], False, (255, 255, 255)), 350, 140),
        Text(font.render(player.craft_number_list[4], False, (255, 255, 255)), 460, 113),
    ]

    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.craft_list[i] is not None:
            if player.craft_list[i][4] is not None:
                index = item_name_list.index(player.craft_list[i][0])
                display.blit(glint_list[index], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (375, 95))

def CraftGrid(display):
    image_render()
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((130, 50), (55, 55)), 2, player.grid_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((185, 50), (55, 55)), 2, player.grid_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((240, 50), (55, 55)), 2, player.grid_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((130, 105), (55, 55)), 2, player.grid_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((185, 105), (55, 55)), 2, player.grid_image_list[4]),
        Grid((83, 83, 83), pygame.Rect((240, 105), (55, 55)), 2, player.grid_image_list[5]),
        Grid((83, 83, 83), pygame.Rect((130, 160), (55, 55)), 2, player.grid_image_list[6]),
        Grid((83, 83, 83), pygame.Rect((185, 160), (55, 55)), 2, player.grid_image_list[7]),
        Grid((83, 83, 83), pygame.Rect((240, 160), (55, 55)), 2, player.grid_image_list[8]),
        Grid((83, 83, 83), pygame.Rect((380, 105), (55, 55)), 2, player.grid_image_list[9])
    ]
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    title_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 27)
    arrow_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftBold-nMK1.otf', 27)
    crafting_numbers = [
        Text(font.render(player.grid_number_list[0], False, (255, 255, 255)), 165, 85),
        Text(font.render(player.grid_number_list[1], False, (255, 255, 255)), 220, 85),
        Text(font.render(player.grid_number_list[2], False, (255, 255, 255)), 275, 85),
        Text(font.render(player.grid_number_list[3], False, (255, 255, 255)), 165, 140),
        Text(font.render(player.grid_number_list[4], False, (255, 255, 255)), 220, 140),
        Text(font.render(player.grid_number_list[5], False, (255, 255, 255)), 275, 140),
        Text(font.render(player.grid_number_list[6], False, (255, 255, 255)), 165, 195),
        Text(font.render(player.grid_number_list[7], False, (255, 255, 255)), 220, 195),
        Text(font.render(player.grid_number_list[8], False, (255, 255, 255)), 275, 195),
        Text(font.render(player.grid_number_list[9], False, (255, 255, 255)), 415, 140)
    ]

    display.blit(title_font.render('Crafting Table', False, (0, 0, 0)), (130, 0))
    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.grid_list[i] is not None:
            if player.grid_list[i][4] is not None:
                index = item_name_list.index(player.grid_list[i][0])
                display.blit(glint_list[index], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (310, 120))

def FurnaceInterface(display):
    image_render()
    smelting_grid = [
        Grid((83, 83, 83), pygame.Rect((150, 45), (55, 55)), 2, player.smelt_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((150, 175), (55, 55)), 2, player.smelt_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((300, 115), (55, 55)), 2, player.smelt_image_list[2]),
    ]
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    side_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 24)
    title_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 27)
    arrow_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftBold-nMK1.otf', 30)
    smelting_numbers = [
        Text(font.render(player.smelt_number_list[0], False, (255, 255, 255)), 185, 80),
        Text(font.render(player.smelt_number_list[1], False, (255, 255, 255)), 185, 210),
        Text(font.render(player.smelt_number_list[2], False, (255, 255, 255)), 335, 150)
    ]

    display.blit(title_font.render('Furnace', False, (0, 0, 0)), (200, 0))
    for i in range(len(smelting_grid)):
        display.blit(smelting_grid[i].img, (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
        pygame.draw.rect(display, smelting_grid[i].colour, smelting_grid[i].rect, smelting_grid[i].width)
        if player.smelting_list[i] is not None:
            if player.smelting_list[i][4] is not None:
                index = item_name_list.index(player.smelting_list[i][0])
                display.blit(glint_list[index], (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
    for i in smelting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(player.fuel_img, (150, 115)) #Render Fire Image
    display.blit(side_font.render(str(player.fuel_val), False, (255, 0, 0)), (125, 125)) #Render Power of Fuel Remaining
    display.blit(side_font.render(str(player.smelting_time // 60), False, (255, 0, 0)), (245, 105)) #Render Time to Smelt
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (225, 125)) #Render Arrow

def EnchantingInterface(display):
    global Option1, Option2, Option3, Upgrade
    image_render()
    enchanting_grid = [
        Grid((83, 83, 83), pygame.Rect((20, 150), (55, 55)), 2, player.enchanting_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((75, 150), (55, 55)), 2, player.enchanting_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((20, 95), (55, 55)), 2, player.enchanting_image_list[2])
    ]
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    enchanting_numbers = [
        Text(font.render(str(player.enchanting_number_list[0]), False, (255, 255, 255)), 55, 185),
        Text(font.render(str(player.enchanting_number_list[1]), False, (255, 255, 255)), 110, 185),
        Text(font.render(str(player.enchanting_number_list[2]), False, (255, 255, 255)), 55, 130)
    ]
    for i in range(len(enchanting_grid)):
        display.blit(enchanting_grid[i].img, (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
        pygame.draw.rect(display, enchanting_grid[i].colour, enchanting_grid[i].rect, enchanting_grid[i].width)
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i][4] is not None:
                index = item_name_list.index(player.enchanting_list[i][0])
                display.blit(glint_list[index], (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
    for i in enchanting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(font.render(f'Enchanting Table LEVEL {player.enchanting_level}', False, (0, 0, 0)), (0, 0))
    Upgrade.render(world, 'Upgrade', 14)
    Option1.render(world, player.option_list[0], 20)
    Option2.render(world, player.option_list[1], 20)
    Option3.render(world, player.option_list[2], 20)

def CompressorInterface(display):
    global player
    image_render()
    compressor_grid = [
        Grid((83, 83, 83), pygame.Rect((150, 95), (55, 55)), 2, player.compressor_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((300, 95), (55, 55)), 2, player.compressor_image_list[1])
    ]
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    title_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 27)
    arrow_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftBold-nMK1.otf', 30)
    side_font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 24)
    compressor_numbers = [
        Text(font.render(player.compressor_number_list[0], False, (255, 255, 255)), 185, 130),
        Text(font.render(player.compressor_number_list[1], False, (255, 255, 255)), 335, 130)
    ]
    display.blit(title_font.render('Compressor', False, (0, 0, 0)), (175, 0))
    for i in range(len(compressor_grid)):
        display.blit(compressor_grid[i].img, (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
        pygame.draw.rect(display, compressor_grid[i].colour, compressor_grid[i].rect, compressor_grid[i].width)
        if player.compressor_list[i] is not None:
            if player.compressor_list[i][4] is not None:
                index = item_name_list.index(player.compressor_list[i][0])
                display.blit(glint_list[index], (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
    for i in compressor_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (225, 115))  # Render Arrow
    display.blit(side_font.render(str(player.compressing_time // 60), False, (255, 0, 0)), (240, 95))  # Render Time to Compress


def hotbar_identify():
    global selected_hotbar, hotbar_item, hotbar_index
    hotbar_index = hotbar_order.index(player.selected_hotbar)
    player.hotbar_item = player.inventory_list[hotbar_index + 27]


def SetHotbarProperties(n):
    global player
    player.hotbar_backgrounds[n].colour = (255, 255, 255)
    player.hotbar_backgrounds[n].width = 3
    for i in range(9):
        if i != n:
            player.hotbar_backgrounds[i].colour = (83, 83, 83)
            player.hotbar_backgrounds[i].width = 2

# Game Loop
def Main(display, clock):
    global TimerRunning, screen, furnace_interface, crafting_grid, small_crafting_grid, inventory_grid, World, player, difference, individual_frame, previous_frame, second_time, mode, val, comma, number, called, world, frame, play_time, endTime, minute, seconds, true_play_time, PlayTime, hotbar_backgrounds, selected_hotbar

    while True:

        clock.tick(60) #60 Frames per Second

        # Calculate FPS
        frame += 1  # Update frame
        individual_frame += 1  # Update individual frame for each second
        end = time.time()  # Calculate current time
        PlayTime = end - start  # Calculate current playtime
        second_time = end - start - difference  # Time for one second
        if second_time > 1:  # Reset every second
            previous_frame = individual_frame
            individual_frame = 0
            difference += 1
        events = pygame.event.get()

        if player.mode == 'game':
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
                            if player.hotbar_item is not None:
                                if player.hotbar_item[3] == "Food":
                                    if player.hunger < 20:
                                        if player.hotbar_item[0] == 'Bread':
                                            index = player.inventory_list.index(player.hotbar_item)
                                            player.inventory_list[index][1] -= 1
                                            player.hunger += 5
                                        # GOLDEN CARROT
                                        elif player.hotbar_item[0] == 'Golden Carrot':
                                            index = player.inventory_list.index(player.hotbar_item)
                                            player.inventory_list[index][1] -= 1
                                            player.hunger += 6
                                        # GOLDEN APPLE
                                        elif player.hotbar_item[0] == 'Golden Apple':
                                            index = player.inventory_list.index(player.hotbar_item)
                                            player.inventory_list[index][1] -= 1
                                            player.hunger += 5
                                            player.regenerate_start_time = 0
                                            player.regenerate_val = True
                                        else:
                                            screen.print("You are not holding a food item!")
                                        player.health_hunger_update()  # UPDATE HEALTH / HUNGER
                                else:
                                    screen.print("You are not holding a food item!")
                            else:
                                screen.print("You are not holding a food item!")
                        if event.key == pygame.K_1:
                            SetHotbarProperties(0)
                            player.selected_hotbar = 'Hotbar1'
                            hotbar_identify()
                        if event.key == pygame.K_2:
                            SetHotbarProperties(1)
                            player.selected_hotbar = 'Hotbar2'
                            hotbar_identify()
                        if event.key == pygame.K_3:
                            SetHotbarProperties(2)
                            player.selected_hotbar = 'Hotbar3'
                            hotbar_identify()
                        if event.key == pygame.K_4:
                            SetHotbarProperties(3)
                            player.selected_hotbar = 'Hotbar4'
                            hotbar_identify()
                        if event.key == pygame.K_5:
                            SetHotbarProperties(4)
                            player.selected_hotbar = 'Hotbar5'
                            hotbar_identify()
                        if event.key == pygame.K_6:
                            SetHotbarProperties(5)
                            player.selected_hotbar = 'Hotbar6'
                            hotbar_identify()
                        if event.key == pygame.K_7:
                            SetHotbarProperties(6)
                            player.selected_hotbar = 'Hotbar7'
                            hotbar_identify()
                        if event.key == pygame.K_8:
                            SetHotbarProperties(7)
                            player.selected_hotbar = 'Hotbar8'
                            hotbar_identify()
                        if event.key == pygame.K_9:
                            SetHotbarProperties(8)
                            player.selected_hotbar = 'Hotbar9'
                            hotbar_identify()
                        if event.key == pygame.K_0:
                            player.F3 = not player.F3
                    elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                        if pygame.mouse.get_pressed(3)[2]:  # Right Click
                            if player.hotbar_item is not None:
                                if player.hotbar_item[0] == 'Crafting Table': #Crafting Key
                                    player.mode = 'crafting'
                                elif player.hotbar_item[0] == 'Furnace': #Smelting Key
                                    player.mode = 'smelting'
                                elif player.hotbar_item[0] == 'Enchanting Table': #Enchanting Key
                                    player.mode = 'enchanting'
                                elif player.hotbar_item[0] == 'Compressor': #Compressing Key
                                    player.mode = 'compressing'

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
                            screen.stop_typing()
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
            World.render(world)  # Render all world blocks to world
            player.render(world)  # Render player and player accessories to world
            SpeedrunTimer(world, PlayTime)
            advancements_update(player.advancements, player.inventory_list, player.armour_list, player.dimension, load, start)  # Update Advancements
            screen.render(world) #Render Text Screen

        elif player.mode == 'inventory':

            Type, box = SelectedBox()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e: #Exit Inventory
                        player.mode = 'game'
                        break
                    elif event.key == pygame.K_1: #1
                        SwitchToHotbar(Type, box, 1)
                    elif event.key == pygame.K_2: #2
                        SwitchToHotbar(Type, box, 2)
                    elif event.key == pygame.K_3: #3
                        SwitchToHotbar(Type, box, 3)
                    elif event.key == pygame.K_4: #4
                        SwitchToHotbar(Type, box, 4)
                    elif event.key == pygame.K_5: #5
                        SwitchToHotbar(Type, box, 5)
                    elif event.key == pygame.K_6: #6
                        SwitchToHotbar(Type, box, 6)
                    elif event.key == pygame.K_7: #7
                        SwitchToHotbar(Type, box, 7)
                    elif event.key == pygame.K_8: #8
                        SwitchToHotbar(Type, box, 8)
                    elif event.key == pygame.K_9: #9
                        SwitchToHotbar(Type, box, 9)
                elif event.type == pygame.MOUSEBUTTONDOWN: #Mouse Button Down Clicking Event
                    if pygame.mouse.get_pressed(3)[0]: #Left Click
                        ClickItem(Type, box)
                    elif pygame.mouse.get_pressed(3)[2]: #Right Click
                        DropItem(Type, box)

            display.fill((0, 0, 0))
            world.fill((211, 211, 211))
            InventoryGrid(world) #Render Inventory Grid
            ArmourGrid(world) #Render Armour Grid for Player
            SmallCraftGrid(world) #Render Small Crafting Grid
            Crafting() #Update Small 2x2 Crafting Grid
            RemoveItem() #Remove Items if their value is 0
            RenderHoldingItem(world) #Render the item the user is holding
            RenderHoveringItem(world, Type, box) #Render Item Name

        elif player.mode == 'crafting':

            Type, box = SelectedBox()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:  # Exit Inventory
                        player.mode = 'game'
                        break
                    elif event.key == pygame.K_1:  # 1
                        SwitchToHotbar(Type, box, 1)
                    elif event.key == pygame.K_2:  # 2
                        SwitchToHotbar(Type, box, 2)
                    elif event.key == pygame.K_3:  # 3
                        SwitchToHotbar(Type, box, 3)
                    elif event.key == pygame.K_4:  # 4
                        SwitchToHotbar(Type, box, 4)
                    elif event.key == pygame.K_5:  # 5
                        SwitchToHotbar(Type, box, 5)
                    elif event.key == pygame.K_6:  # 6
                        SwitchToHotbar(Type, box, 6)
                    elif event.key == pygame.K_7:  # 7
                        SwitchToHotbar(Type, box, 7)
                    elif event.key == pygame.K_8:  # 8
                        SwitchToHotbar(Type, box, 8)
                    elif event.key == pygame.K_9:  # 9
                        SwitchToHotbar(Type, box, 9)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                    if pygame.mouse.get_pressed(3)[0]:  # Left Click
                        ClickItem(Type, box)
                    elif pygame.mouse.get_pressed(3)[2]:  # Right Click
                        DropItem(Type, box)

            display.fill((0, 0, 0))
            world.fill((211, 211, 211))
            InventoryGrid(world) #Render Inventory Grid
            CraftGrid(world) #Render 3x3 Crafting Grid
            GridCraft()  # Update 3x3 Crafting Grid
            RemoveItem()  # Remove Items if their value is 0
            RenderHoldingItem(world)  # Render the item the user is holding
            RenderHoveringItem(world, Type, box) #Render Item Name

        elif player.mode == 'smelting':

            Type, box = SelectedBox()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:  # Exit Inventory
                        player.mode = 'game'
                        break
                    elif event.key == pygame.K_1:  # 1
                        SwitchToHotbar(Type, box, 1)
                    elif event.key == pygame.K_2:  # 2
                        SwitchToHotbar(Type, box, 2)
                    elif event.key == pygame.K_3:  # 3
                        SwitchToHotbar(Type, box, 3)
                    elif event.key == pygame.K_4:  # 4
                        SwitchToHotbar(Type, box, 4)
                    elif event.key == pygame.K_5:  # 5
                        SwitchToHotbar(Type, box, 5)
                    elif event.key == pygame.K_6:  # 6
                        SwitchToHotbar(Type, box, 6)
                    elif event.key == pygame.K_7:  # 7
                        SwitchToHotbar(Type, box, 7)
                    elif event.key == pygame.K_8:  # 8
                        SwitchToHotbar(Type, box, 8)
                    elif event.key == pygame.K_9:  # 9
                        SwitchToHotbar(Type, box, 9)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                    if pygame.mouse.get_pressed(3)[0]:  # Left Click
                        ClickItem(Type, box)
                    elif pygame.mouse.get_pressed(3)[2]:  # Right Click
                        DropItem(Type, box)

            display.fill((0, 0, 0))
            world.fill((211, 211, 211))
            InventoryGrid(world) #Render Inventory Grid
            FurnaceInterface(world) #Render Furnace Interface
            player.smelt() #Furnace Smelting
            RemoveItem()  # Remove Items if their value is 0
            RenderHoldingItem(world)  # Render the item the user is holding
            RenderHoveringItem(world, Type, box) #Render Item Name

        elif player.mode == 'enchanting':

            Type, box = SelectedBox()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:  # Exit Inventory
                        player.mode = 'game'
                        break
                    elif event.key == pygame.K_1:  # 1
                        SwitchToHotbar(Type, box, 1)
                    elif event.key == pygame.K_2:  # 2
                        SwitchToHotbar(Type, box, 2)
                    elif event.key == pygame.K_3:  # 3
                        SwitchToHotbar(Type, box, 3)
                    elif event.key == pygame.K_4:  # 4
                        SwitchToHotbar(Type, box, 4)
                    elif event.key == pygame.K_5:  # 5
                        SwitchToHotbar(Type, box, 5)
                    elif event.key == pygame.K_6:  # 6
                        SwitchToHotbar(Type, box, 6)
                    elif event.key == pygame.K_7:  # 7
                        SwitchToHotbar(Type, box, 7)
                    elif event.key == pygame.K_8:  # 8
                        SwitchToHotbar(Type, box, 8)
                    elif event.key == pygame.K_9:  # 9
                        SwitchToHotbar(Type, box, 9)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                    if pygame.mouse.get_pressed(3)[0]:  # Left Click
                        ClickItem(Type, box)
                    elif pygame.mouse.get_pressed(3)[2]:  # Right Click
                        DropItem(Type, box)

            display.fill((0, 0, 0))
            world.fill((211, 211, 211))
            InventoryGrid(world)  # Render Inventory Grid
            EnchantingInterface(world) #Render Enchanting Table Interface
            RemoveItem()  # Remove Items if their value is 0
            RenderHoldingItem(world)  # Render the item the user is holding
            RenderHoveringItem(world, Type, box) #Render Item Name

        elif player.mode == 'compressing':

            Type, box = SelectedBox()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:  # Exit Inventory
                        player.mode = 'game'
                        break
                    elif event.key == pygame.K_1:  # 1
                        SwitchToHotbar(Type, box, 1)
                    elif event.key == pygame.K_2:  # 2
                        SwitchToHotbar(Type, box, 2)
                    elif event.key == pygame.K_3:  # 3
                        SwitchToHotbar(Type, box, 3)
                    elif event.key == pygame.K_4:  # 4
                        SwitchToHotbar(Type, box, 4)
                    elif event.key == pygame.K_5:  # 5
                        SwitchToHotbar(Type, box, 5)
                    elif event.key == pygame.K_6:  # 6
                        SwitchToHotbar(Type, box, 6)
                    elif event.key == pygame.K_7:  # 7
                        SwitchToHotbar(Type, box, 7)
                    elif event.key == pygame.K_8:  # 8
                        SwitchToHotbar(Type, box, 8)
                    elif event.key == pygame.K_9:  # 9
                        SwitchToHotbar(Type, box, 9)
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse Button Down Clicking Event
                    if pygame.mouse.get_pressed(3)[0]:  # Left Click
                        ClickItem(Type, box)
                    elif pygame.mouse.get_pressed(3)[2]:  # Right Click
                        DropItem(Type, box)

            display.fill((0, 0, 0))
            world.fill((211, 211, 211))
            InventoryGrid(world) #Render Inventory Grid
            CompressorInterface(world) #Render Compressor Interface
            player.compress() #Compressing Process
            RemoveItem() #Remove Items if their value is 0
            RenderHoldingItem(world) #Render the item the user is holding
            RenderHoveringItem(world, Type, box) #Render Item Name

        display.blit(world, (0, 0))  # Render map to display
        pygame.display.flip()  # Update Display

#Render the Item the User is Holding
def RenderHoldingItem(display):
    global glint_list
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 20)
    if player.holding_item is not None:
        display.blit(player.holding_item_image, (x, y))
        display.blit(font.render(player.holding_item_number, False, (255, 255, 255)), (x + 35, y + 35))
        if player.holding_item[4] is not None:
            index = item_name_list.index(player.holding_item[0])
            display.blit(glint_list[index], (x, y))

#Convert Numbers to Roman Numerals
def DecimalToRoman(num):
    if num == 1:
        num = 'I'
    elif num == 2:
        num = 'II'
    elif num == 3:
        num = 'III'
    elif num == 4:
        num = 'IV'
    elif num == 5:
        num = 'V'
    return num

#Info Box for Items (with and without enchantments)
def TextBox(List, x, y, font, box, display):
    try:
        if List[box] is not None: #Check to prevent crashes
            if List[box][4] is None: #No Enchantments
                length = len(List[box][0]) * 10
                if x + length > 504:
                    x -= length
                pygame.draw.rect(display, (0, 0, 0), (x, y, length, 25))
                display.blit(font.render(List[box][0], False, (255, 255, 255)), (x + 10, y + 10))
            else: #With Enchantments
                length_list = [len(List[box][0] * 10)]
                for i in List[box][4]:
                    length_list.append(len(str(i[0]) + DecimalToRoman(str(i[1]))) * 10)
                length = max(length_list)
                if x + length > 504:
                    x -= length
                width = (1 + len(List[box][4])) * 25
                pygame.draw.rect(display, (0, 0, 0), (x, y, length, width))
                display.blit(font.render(List[box][0], False, (0, 255, 255)), (x + 10, y + 10))
                for i in range(len(List[box][4])):
                    display.blit(font.render(f'{List[box][4][i][0]} {DecimalToRoman(List[box][4][i][1])}', False, (255, 255, 255)), (x + 10, y + 10 + (i + 1) * 15))
    except IndexError:
        pass

#Render the Item Label for the Item that the User is Hovering Over
def RenderHoveringItem(display, Type, box):
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('images_vA1_7_4/monofur/monof55.ttf', 15)
    if box is not None:
        if Type == 'inventory grid': #Within 36 Inventory Slots
            TextBox(player.inventory_list, x, y, font, box, display)
        elif Type == 'armour grid': #Within Armour Grid
            TextBox(player.armour_list, x, y, font, box, display)
        elif Type == 'small crafting grid' or Type == 'small crafting grid item': #2x2 Crafting
            TextBox(player.craft_list, x, y, font, box, display)
        elif Type == 'crafting grid' or Type == 'crafting grid item': #3x3 Crafting
            TextBox(player.grid_list, x, y, font, box, display)
        elif Type == 'smelting' or Type == 'smelting item': #Furnace
            TextBox(player.smelting_list, x, y, font, box, display)
        elif Type == 'enchanting': #Enchantment Table
            TextBox(player.enchanting_list, x, y, font, box, display)
        elif Type == 'compressing' or Type == 'compressing item': #Compressor
            TextBox(player.compressor_list, x, y, font, box, display)

#Determine which box the user selected
def SelectedBox():
    x, y = pygame.mouse.get_pos()
    if 0 <= x <= 495 and 260 <= y <= 480:
        column = x // 55
        row = (y - 260) // 55
        box = column + 9 * row
        return "inventory grid", box
    elif 0 <= x <= 220 and 160 <= y <= 215 and player.mode == 'inventory':
        box = x // 55
        return "armour grid", box
    elif 260 <= x <= 370 and 50 <= y <= 160 and player.mode == 'inventory':
        column = (x - 260) // 55
        row = (y - 50) // 55
        box = column + 2 * row
        return "small crafting grid", box
    elif 425 <= x <= 480 and 78 <= y <= 133 and player.mode == 'inventory':
        box = 4
        return 'small crafting grid item', box
    elif 130 <= x <= 295 and 50 <= y <= 215 and player.mode == 'crafting':
        column = (x - 130) // 55
        row = (y - 50) // 55
        box = column + 3 * row
        return 'crafting grid', box
    elif 380 <= x <= 435 and 105 <= y <= 160 and player.mode == 'crafting':
        box = 9
        return 'crafting grid item', box
    elif 150 <= x <= 205 and 45 <= y <= 100 and player.mode == 'smelting':
        box = 0
        return 'smelting', box
    elif 150 <= x <= 205 and 175 <= y <= 230 and player.mode == 'smelting':
        box = 1
        return 'smelting', box
    elif 300 <= x <= 355 and 115 <= y <= 170 and player.mode == 'smelting':
        box = 2
        return 'smelting item', box
    elif 20 <= x <= 75 and 150 <= y <= 205 and player.mode == 'enchanting':
        box = 0
        return 'enchanting', box
    elif 75 <= x <= 130 and 150 <= y <= 205 and player.mode == 'enchanting':
        box = 1
        return 'enchanting', box
    elif 20 <= x <= 75 and 95 <= y <= 150 and player.mode == 'enchanting':
        box = 2
        return 'enchanting', box
    elif Upgrade.x <= x <= Upgrade.x + 55 and Upgrade.y <= y <= Upgrade.y + 55 and player.mode == 'enchanting':
        box = 0
        return 'upgrade', box
    elif Option1.x <= x <= Option1.x + 325 and Option1.y <= y <= Option1.y + 55 and player.mode == 'enchanting':
        box = 0
        return 'option1', box
    elif Option2.x <= x <= Option2.x + 325 and Option2.y <= y <= Option2.y + 55 and player.mode == 'enchanting':
        box = 1
        return 'option2', box
    elif Option3.x <= x <= (Option3.x + 325) and Option3.y <= y <= (Option3.y + 55) and player.mode == 'enchanting':
        box = 2
        return 'option3', box
    elif 150 <= x <= 205 and 95 <= y <= 150 and player.mode == 'compressing':
        box = 0
        return 'compressing', box
    elif 300 <= x <= 355 and 95 <= y <= 150 and player.mode == 'compressing':
        box = 1
        return 'compressing item', box
    else:
        return None, None

#Move items using drag and drop
def ClickItem(Type, box):
    global small_crafting_grid
    if Type is not None and box is not None:
        if Type == 'inventory grid': #Inventory Grid and Hotbar
            if player.holding_item is not None and player.inventory_list[box] is not None:
                if player.holding_item[0] == player.inventory_list[box][0] and (player.inventory_list[box][1] + player.holding_item[1] <= player.holding_item[2]): #Items can be combined
                    player.inventory_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.inventory_list[box] = player.inventory_list[box], player.holding_item
            else:
                player.holding_item, player.inventory_list[box] = player.inventory_list[box], player.holding_item
        elif Type == 'armour grid': #Armour Grid
            if box == 0: #Tier 1
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item[3] == 'Tier1':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item[3] == 'Tier1' and player.armour_list[box][3] == 'Tier1':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 1: #Tier 2
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item[3] == 'Tier2':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item[3] == 'Tier2' and player.armour_list[box][3] == 'Tier2':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 2: #Tier 3
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item[3] == 'Tier3':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item[3] == 'Tier3' and player.armour_list[box][3] == 'Tier3':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 3: #Shield
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item[3] == 'Shield':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
        elif Type == 'small crafting grid': #Small 2x2 Crafting Grid
            if player.holding_item is not None and player.craft_list[box] is not None: #Items can be combined
                if player.holding_item[0] == player.craft_list[box][0] and (player.craft_list[box][1] + player.holding_item[1] <= player.holding_item[2]):
                    player.craft_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.craft_list[box] = player.craft_list[box], player.holding_item
            else:
                player.holding_item, player.craft_list[box] = player.craft_list[box], player.holding_item
        elif Type == 'small crafting grid item': #Collecting the Item Crafted from 2x2 Crafting Grid
            if player.craft_list[4] is not None:
                inventory_add([player.craft_list[4]])
                for i in range(4):
                    if player.craft_list[i] is not None:
                        player.craft_list[i][1] -= 1
        elif Type == 'crafting grid': #Big 3x3 Crafting Grid
            if player.holding_item is not None and player.grid_list[box] is not None: #Items can be combined
                if player.holding_item[0] == player.grid_list[box][0] and (player.grid_list[box][1] + player.holding_item[1] <= player.holding_item[2]):
                    player.grid_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.grid_list[box] = player.grid_list[box], player.holding_item
            else:
                player.holding_item, player.grid_list[box] = player.grid_list[box], player.holding_item
        elif Type == 'crafting grid item': #Collecting the Item Crafted from 3x3 Crafting Grid
            if player.grid_list[9] is not None:
                inventory_add([player.grid_list[9]])
                for i in range(9):
                    if player.grid_list[i] is not None:
                        player.grid_list[i][1] -= 1
        elif Type == 'smelting':
            if player.holding_item is not None and player.smelting_list[box] is not None: #Items can be combined
                if player.holding_item[0] == player.smelting_list[box][0] and (player.smelting_list[box][1] + player.holding_item[1] <= player.holding_item[2]):
                    player.smelting_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.smelting_list[box] = player.smelting_list[box], player.holding_item
            else:
                player.holding_item, player.smelting_list[box] = player.smelting_list[box], player.holding_item
        elif Type == 'smelting item': #Collecting the Item Smelted from Furnace
            inventory_add([player.smelting_list[2]])
            player.smelting_list[2] = None
        elif Type == 'enchanting':
            if player.holding_item is not None and player.enchanting_list[box] is not None: #Items can be combined
                if player.holding_item[0] == player.enchanting_list[box][0] and (player.enchanting_list[box][1] + player.holding_item[1] <= player.holding_item[2]):
                    player.enchanting_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.enchanting_list[box] = player.enchanting_list[box], player.holding_item
            else:
                player.holding_item, player.enchanting_list[box] = player.enchanting_list[box], player.holding_item
            if box == 0:
                EnchantSet()
        elif Type == 'upgrade':
            EnchantUpgrade()
        elif Type == 'option1':
            Enchant1()
        elif Type == 'option2':
            Enchant2()
        elif Type == 'option3':
            Enchant3()
        elif Type == 'compressing':
            if player.holding_item is not None and player.compressor_list[box] is not None: #Items can be combined
                if player.holding_item[0] == player.compressor_list[box][0] and (player.compressor_list[box][1] + player.holding_item[1] <= player.holding_item[2]):
                    player.compressor_list[box][1] += player.holding_item[1]
                    player.holding_item = None
                else:
                    player.holding_item, player.compressor_list[box] = player.compressor_list[box], player.holding_item
            else:
                player.holding_item, player.compressor_list[box] = player.compressor_list[box], player.holding_item
        elif Type == 'compressing item':
            inventory_add([player.compressor_list[1]])
            player.compressor_list[1] = None

#Switch items in inventory straight to hotbar
def SwitchToHotbar(Type, box, key_pressed):
    if Type is not None and box is not None:
        if Type == 'inventory grid':
            player.inventory_list[key_pressed + 26], player.inventory_list[box] = player.inventory_list[box], player.inventory_list[key_pressed + 26]

#Right Click - Drop Item / Separate Item into two different stacks
def DropItem(Type, box):
    if Type is not None and box is not None and player.holding_item is not None:
        if Type == 'inventory grid': #Inventory Grid
            if player.inventory_list[box] is None:
                player.inventory_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.inventory_list[box] is not None and player.inventory_list[box][0] == player.holding_item[0] and (player.inventory_list[box][1] + 1 <= player.inventory_list[box][2]):
                player.inventory_list[box][1] += 1
                player.holding_item[1] -= 1
        elif Type == 'small crafting grid': #Small 2x2 Crafting Grid
            if player.craft_list[box] is None:
                player.craft_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.craft_list[box] is not None and player.craft_list[box][0] == player.holding_item[0] and (player.craft_list[box][1] + 1 <= player.craft_list[box][2]):
                player.craft_list[box][1] += 1
                player.holding_item[1] -= 1
        elif Type == 'crafting grid': #Big 3x3 Crafting Grid
            if player.grid_list[box] is None:
                player.grid_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.grid_list[box] is not None and player.grid_list[box][0] == player.holding_item[0] and (player.grid_list[box][1] + 1 <= player.grid_list[box][2]):
                player.grid_list[box][1] += 1
                player.holding_item[1] -= 1
        elif Type == 'smelting': #Furnace Interface
            if player.smelting_list[box] is None:
                player.smelting_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.smelting_list[box] is not None and player.smelting_list[box][0] == player.holding_item[0] and (player.smelting_list[box][1] + 1 <= player.smelting_list[box][2]):
                player.smelting_list[box][1] += 1
                player.holding_item[1] -= 1
        elif Type == 'enchanting': #Enchanting Table Interface
            if player.enchanting_list[box] is None:
                player.enchanting_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.enchanting_list[box] is not None and player.enchanting_list[box][0] == player.holding_item[0] and (player.enchanting_list[box][1] + 1 <= player.enchanting_list[box][2]):
                player.enchanting_list[box][1] += 1
                player.holding_item[1] -= 1
        elif Type == 'compressing': #Compressor Interface
            if player.compressor_list[box] is None:
                player.compressor_list[box] = [player.holding_item[0], 1, player.holding_item[2], player.holding_item[3], player.holding_item[4]]
                player.holding_item[1] -= 1
            elif player.compressor_list[box] is not None and player.compressor_list[box][0] == player.holding_item[0] and (player.compressor_list[box][1] + 1 <= player.compressor_list[box][2]):
                player.compressor_list[box][1] += 1
                player.holding_item[1] -= 1

#Limit number of times a player can repeat a command
def NumberLimit(number, val):
    if number > 16:
        screen.print("ERROR: Invalid Integer")
    elif number < 1:
        screen.print("ERROR: Invalid Integer")
    else:
        commands(number, val)

class Screen:
    def __init__(self):
        self.x = 0
        self.y = 380
        self.input_line = 0
        self.print_list = []
        self.isTyping = False
        self.typingText = ''
        self.position = 0
        self.foretext = ''

    def scroll_up(self):
        if self.position < len(self.print_list) - 15:
            self.position += 1

    def scroll_down(self):
        if self.position > 0:
            self.position -= 1

    def start_typing(self, text):
        self.input_line = 10
        self.isTyping = True
        self.foretext = text

    def type(self, char):
        self.typingText += char

    def stop_typing(self):
        global screen, player
        self.input_line = 0
        self.isTyping = False
        if self.foretext == 'Item ID (0 - 45): ':
            inventory_add([give(item_name_list, stack_list, item_type_list, self.typingText)])
        elif self.foretext == 'Coordinates (X,Y): ':
            player.x, player.y = teleport(player.x, player.y, self.typingText)
        else:
            screen.text_validate()
        self.typingText = ''
        self.position = 0

    def delete(self):
        self.typingText = self.typingText[0:-1]

    def text_validate(self):
        global screen
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
                        NumberLimit(number, self.typingText)
                    except ValueError:
                        screen.print("Invalid integer")
                else:
                    number = 1  # Set number to 1 when number is not specified
                    NumberLimit(number, self.typingText)
            # Regular text message
            else:
                screen.print(f"<Player> {self.typingText}")

    def print(self, text):
        self.print_list.append(text)

    def render(self, display):
        if len(self.print_list) <= 16:
            self.screen_list = self.print_list[:]
            height = len(self.print_list) * 10 + self.input_line
        else:
            if self.position == 0:
                self.screen_list = self.print_list[-16 - self.position:]
                height = 16 * 10 + self.input_line
            else:
                self.screen_list = self.print_list[-16 - self.position: 0 - self.position]
                height = 16 * 10 + self.input_line
        self.screen_list.reverse()
        width = 250
        x = self.x
        y = self.y - height
        surface = pygame.Surface((width, height))
        surface.fill((125, 125, 125))
        surface.set_alpha(200)
        display.blit(surface, (x, y))
        font = pygame.font.Font('images_vA1_7_4/monofur/monof55.ttf', 12)

        for i in range(len(self.screen_list)):
            display.blit(font.render(self.screen_list[i], False, (255, 255, 255)), (x, y + height - (i + 1) * 10 - self.input_line))
        display.blit(font.render(self.foretext + self.typingText, True, (255, 255, 255)), (x, y + height - 10))

# Create Hotbar Outline
class Hotbar:
    def __init__(self, colour, rect, width):
        self.colour = colour
        self.rect = rect
        self.width = width

#Player Class and Methods
class Player:
    def __init__(self):
        self.advancements = []
        self.image = pygame.Surface((24, 24))  # Create Player Image
        self.image.fill((255, 0, 0))  # Fill Player Red
        self.rect = pygame.Rect((240, 240), (24, 24))  # Create Player Rect
        self.x = 0  # Set Starting X Coordinate
        self.y = 0  # Set Starting Y Coordinate
        self.actualX = 0
        self.actualY = 0
        self.dimension = "Overworld"
        self.regenerate_val = False
        self.regenerate_start_time = 180
        self.F3 = False

        # Setup Health Bar Images
        global health_vals, health_nums, heart1, heart2, heart3, heart4, heart5, heart6, heart7, heart8, heart9, heart10, full_heart, health, half_heart, empty_heart
        full_heart = pygame.image.load(
            'images_vA1_7_4/FullHeart_20x20.png').convert()  # Full Heart (2)
        half_heart = pygame.image.load(
            'images_vA1_7_4/half_heart_20x20.png').convert()  # Half Heart (1)
        empty_heart = pygame.image.load(
            'images_vA1_7_4/empty_heart_20x20.png').convert()  # Empty Heart (0)
        heart1 = info_bar(full_heart, 5, 395)
        heart2 = info_bar(full_heart, 28, 395)
        heart3 = info_bar(full_heart, 51, 395)
        heart4 = info_bar(full_heart, 74, 395)
        heart5 = info_bar(full_heart, 97, 395)
        heart6 = info_bar(full_heart, 120, 395)
        heart7 = info_bar(full_heart, 143, 395)
        heart8 = info_bar(full_heart, 166, 395)
        heart9 = info_bar(full_heart, 189, 395)
        heart10 = info_bar(full_heart, 212, 395)
        self.health_vals = [heart1, heart2, heart3, heart4, heart5, heart6, heart7, heart8, heart9, heart10]
        self.health_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.health = 20  # Set Health = 20

        # Setup Hunger Bar Images
        global experience_bar, hunger_vals, backdrop, empty_hunger, distance, hunger_nums, full_hunger, hunger, half_hunger, dead, hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10
        full_hunger = pygame.image.load(
            'images_vA1_7_4/hunger_20x20.png')  # Full Hunger (2)
        half_hunger = pygame.image.load(
            'images_vA1_7_4/half_hunger_20x20.png')  # Half Hunger (1)
        empty_hunger = pygame.image.load(
            'images_vA1_7_4/empty_hunger_20x20.png')  # Empty Hunger (0)
        self.hunger = 20  # Set Hunger = 20
        self.hunger_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.distance = 0  # Set Distance Travelled
        self.dead = False
        self.hunger_subtracted = 0

        hunger1 = info_bar(full_hunger, 477, 395)
        hunger2 = info_bar(full_hunger, 454, 395)
        hunger3 = info_bar(full_hunger, 431, 395)
        hunger4 = info_bar(full_hunger, 408, 395)
        hunger5 = info_bar(full_hunger, 385, 395)
        hunger6 = info_bar(full_hunger, 362, 395)
        hunger7 = info_bar(full_hunger, 339, 395)
        hunger8 = info_bar(full_hunger, 316, 395)
        hunger9 = info_bar(full_hunger, 293, 395)
        hunger10 = info_bar(full_hunger, 270, 395)
        self.hunger_vals = [hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10]  # Hunger bar list
        experience_bar = pygame.image.load('images_vA1_7_4/item_imgs/experience.png').convert()
        backdrop = pygame.Rect((20, 395), (465, 20))  # Set Background for Hunger and Health Bar

        self.waiting_list = []
        self.selected_slot = 'slot1'
        self.inventory_list = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None,
                          None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None,
                          None, None, None, None]
        self.image_list = []
        self.number_list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                       '',
                       '', '', '', '', '', '', '', '', '', '', '']
        self.armour_list = [None, None, None, None]
        self.armour_image_list = []
        self.layer_list = []
        self.craft_list = [None, None, None, None, None]
        self.craft_image_list = []
        self.craft_number_list = []
        self.grid_list = [None, None, None, None, None, None, None, None, None, None]
        self.grid_image_list = []
        self.grid_number_list = []
        self.smelting_list = [None, None, None]
        self.smelt_image_list = []
        self.smelt_number_list = []
        self.fuel_val = 0
        global no_fire
        self.fuel_img = no_fire
        self.smelting_time = 0
        self.experience = 0
        self.enchanting_list = [None, None, None]
        self.enchanting_image_list = []
        self.enchanting_number_list = []
        self.option_list = ['', '', '']
        self.enchanting_level = 0
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.optional_enchant2 = None
        self.optional_enchant3 = None

        #Create Hotbar
        global slot
        slot = pygame.image.load("images_vA1_7_4/item_imgs/slot.png").convert()
        bar1 = info_bar(slot, 5, 445)
        bar2 = info_bar(slot, 60, 445)
        bar3 = info_bar(slot, 115, 445)
        bar4 = info_bar(slot, 170, 445)
        bar5 = info_bar(slot, 225, 445)
        bar6 = info_bar(slot, 280, 445)
        bar7 = info_bar(slot, 335, 445)
        bar8 = info_bar(slot, 390, 445)
        bar9 = info_bar(slot, 445, 445)
        self.hotbar_imgs = [bar1, bar2, bar3, bar4, bar5, bar6, bar7, bar8, bar9]

        # Set Background Rects
        background_1 = pygame.Rect((5, 445), (55, 55))
        background_2 = pygame.Rect((60, 445), (55, 55))
        background_3 = pygame.Rect((115, 445), (55, 55))
        background_4 = pygame.Rect((170, 445), (55, 55))
        background_5 = pygame.Rect((225, 445), (55, 55))
        background_6 = pygame.Rect((280, 445), (55, 55))
        background_7 = pygame.Rect((335, 445), (55, 55))
        background_8 = pygame.Rect((390, 445), (55, 55))
        background_9 = pygame.Rect((445, 445), (55, 55))

        # Set Hotbar Classes
        global Hotbar1, Hotbar2, Hotbar3, Hotbar4, Hotbar5, Hotbar6, Hotbar7, Hotbar8, Hotbar9, hotbar_backgrounds, hotbar_item, mode, hotbar_order
        Hotbar1 = Hotbar((255, 255, 255), background_1, 3)
        Hotbar2 = Hotbar((83, 83, 83), background_2, 2)
        Hotbar3 = Hotbar((83, 83, 83), background_3, 2)
        Hotbar4 = Hotbar((83, 83, 83), background_4, 2)
        Hotbar5 = Hotbar((83, 83, 83), background_5, 2)
        Hotbar6 = Hotbar((83, 83, 83), background_6, 2)
        Hotbar7 = Hotbar((83, 83, 83), background_7, 2)
        Hotbar8 = Hotbar((83, 83, 83), background_8, 2)
        Hotbar9 = Hotbar((83, 83, 83), background_9, 2)
        self.hotbar_backgrounds = [Hotbar1, Hotbar2, Hotbar3, Hotbar4, Hotbar5, Hotbar6, Hotbar7, Hotbar8, Hotbar9]
        self.selected_hotbar = 'Hotbar1'
        self.hotbar_item = None
        self.mode = 'game'
        self.holding_item = None
        self.holding_item_image = None
        self.holding_item_number = None

        self.compressor_list = [None, None]
        self.compressor_image_list = []
        self.compressor_number_list = []
        self.compressing_time = 0

    #Method to convert health and hunger integers to image lists
    def health_hunger_update(self):
        # UPDATE HUNGER LIST
        self.hunger_nums = []
        if self.hunger > 20:
            self.hunger = 20
        hunger_difference = self.hunger
        while hunger_difference > 0:
            if hunger_difference >= 2:
                hunger_difference -= 2
                self.hunger_nums.append(2)
            elif hunger_difference == 1:
                hunger_difference -= 1
                self.hunger_nums.append(1)
        while len(self.hunger_nums) < 10:
            self.hunger_nums.append(0)

        # UPDATE HUNGER BAR IMAGES
        for i in range(len(self.hunger_vals)):
            if self.hunger_nums[i] == 2:
                self.hunger_vals[i].img = full_hunger
            elif self.hunger_nums[i] == 1:
                self.hunger_vals[i].img = half_hunger
            else:
                self.hunger_vals[i].img = empty_hunger

        # UPDATE HEALTH LIST
        self.health_nums = []
        if self.health > 20:
            self.health = 20
        health_difference = self.health
        while health_difference > 0:
            if health_difference >= 2:
                health_difference -= 2
                self.health_nums.append(2)
            elif health_difference == 1:
                health_difference -= 1
                self.health_nums.append(1)
        while len(self.health_nums) < 10:
            self.health_nums.append(0)

        # UPDATE HEALTH BAR IMAGES
        for i in range(len(self.health_vals)):
            if self.health_nums[i] == 2:
                self.health_vals[i].img = full_heart
            elif self.health_nums[i] == 1:
                self.health_vals[i].img = half_heart
            else:
                self.health_vals[i].img = empty_heart

    # Hunger mechanism to decrease hunger as distance travelled increases
    def hunger_mechanism(self):
        global player
        if self.hunger > 0 and self.distance != 0 and self.distance // 512 != self.hunger_subtracted:
            self.hunger -= 1
            self.hunger_subtracted += 1
        player.health_hunger_update()

    #Update Health and Regeneration
    def health_update(self):
        global player
        if self.hunger >= 17 and self.health < 20 and frame % 16 == 0:
            self.hunger -= 1
            self.health += 1
        if self.hunger == 0 and frame % 16 == 0:
            self.health -= 1
        if self.health == 0:
            self.dead = True
        if self.regenerate_val and self.health < 20:
            if self.regenerate_start_time < 180:
                if frame % 16 == 0:
                    self.health += 1
                self.regenerate_start_time += 1
            else:
                self.regenerate_val = False
        player.health_hunger_update()

    #Player Move Keybinds
    def move(self):
        # Position calculation
        self.left = self.x * 24 - 240
        self.right = self.x * 24 + 264
        self.bottom = self.y * 24 + 264
        self.top = self.y * 24 - 240
        self.ScreenLeft = self.x * 24 - 288
        self.ScreenRight = self.x * 24 + 288
        self.ScreenBottom = self.y * 24 + 288
        self.ScreenTop = self.y * 24 - 288

        key = pygame.key.get_pressed() #Get Keyboard Input (Press Key)

        if key[pygame.K_w]: #Up
            if key[pygame.K_r]: #Sprinting
                self.y -= 3/32
                self.distance += 4
                player.hunger_mechanism()
            else: #Not Sprinting
                self.y -= 1 / 16
                self.distance += 1
                player.hunger_mechanism()
        if key[pygame.K_a]: #Left
            if key[pygame.K_r]: #Sprinting
                self.x -= 3/32
                self.distance += 4
                player.hunger_mechanism()
            else: #Not Sprinting
                self.x -= 1 / 16
                self.distance += 1
                player.hunger_mechanism()
        if key[pygame.K_s]: #Down
            if key[pygame.K_r]: #Sprinting
                self.y += 3/32
                self.distance += 4
                player.hunger_mechanism()
            else: #Not Sprinting
                self.y += 1 / 16
                self.distance += 1
                player.hunger_mechanism()
        if key[pygame.K_d]: #Right
            if key[pygame.K_r]: #Sprinting
                self.x += 3/32
                self.distance += 4
                player.hunger_mechanism()
            else: #Not Sprinting
                self.x += 1 / 16
                self.distance += 1
                player.hunger_mechanism()

    def smelt(self):
        # Load Fuel
        if self.smelting_list[1] is not None:
            if self.smelting_list[1][0] == "Coal" and self.fuel_val == 0:
                self.smelting_list[1] = [self.smelting_list[1][0], self.smelting_list[1][1] - 1, self.smelting_list[1][2], self.smelting_list[1][3], self.smelting_list[1][4]]
                self.fuel_val = 8

        # Smelting Process
        if self.smelting_list[0] is not None:
            if self.smelting_list[0][0] == "Iron Ore" and self.fuel_val > 0:
                self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time == 300:
            self.smelting_time = 0
            self.smelting_list[0] = [self.smelting_list[0][0], self.smelting_list[0][1] - 1, self.smelting_list[0][2], self.smelting_list[0][3], self.smelting_list[0][4]]
            self.fuel_val -= 1
            if self.smelting_list[2] is None:
                self.smelting_list[2] = ["Iron Ingot", 1, 64, "Item", None]
                self.experience += 1
            else:
                self.smelting_list[2] = ["Iron Ingot", self.smelting_list[2][1] + 1, 64, "Item", None]
                self.experience += 1

        # Render Fire
        if self.fuel_val > 0:
            self.fuel_img = fire
        else:
            self.fuel_img = no_fire

    def compress(self):
        #Compressing Process
        if self.compressor_list[0] is not None:
            if self.compressor_list[0][1] >= 2:
                if self.compressor_list[0][0] == 'Iron Ingot':
                    if self.compressor_list[1] is not None:
                        if self.compressor_list[1][0] == 'Iron Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
                elif self.compressor_list[0][0] == 'Diamond':
                    if self.compressor_list[1] is not None:
                        if self.compressor_list[1][0] == 'Diamond Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
        else:
            self.compressing_time = 0

        #Finish Compressing Item
        if self.compressing_time == 300:
            self.compressing_time = 0
            self.compressor_list[0] = [self.compressor_list[0][0], self.compressor_list[0][1] - 2, self.compressor_list[0][2], self.compressor_list[0][3], self.compressor_list[0][4]]
            if self.compressor_list[1] is None:
                if self.compressor_list[0][0] == 'Iron Ingot':
                    self.compressor_list[1] = ['Iron Plate', 1, 64, "Item", None]
                elif self.compressor_list[0][0] == 'Diamond':
                    self.compressor_list[1] = ['Diamond Plate', 1, 64, "Item", None]
            else:
                if self.compressor_list[0][0] == 'Iron Ingot' and self.compressor_list[1][0] == 'Iron Plate':
                    self.compressor_list[1] = ['Iron Plate', self.compressor_list[1][1] + 1, 64, 'Item', None]
                elif self.compressor_list[0][0] == 'Diamond' and self.compressor_list[1][0] == 'Diamond Plate':
                    self.compressor_list[1] = ['Diamond Plate', self.compressor_list[1][1] + 1, 64, 'Item', None]

    def render(self, display):
        global backdrop, experience_bar, previous_frame

        # DRAW BACKDROP FOR HUNGER AND HEALTH BARS
        pygame.draw.rect(display, (255, 255, 255), backdrop)

        # DRAW PLAYER
        display.blit(self.image, (self.rect.x, self.rect.y))

        # DRAW HEALTH BAR
        for j in self.health_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW HUNGER BAR
        for j in self.hunger_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW EXPERIENCE BAR
        display.blit(experience_bar, (3, 420))  # Experience Bar
        fontx = pygame.font.Font('images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 30)
        experience_number = fontx.render(str(self.experience), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (252, 410)
        display.blit(experience_number, experience_number_r)  # Experience Number

        # GENERATE HOTBAR LIST
        for i in range(27, 36):
            if self.inventory_list[i] is None:  # Set White Background for NONE Slots
                self.hotbar_imgs[i - 27].img = slot
                self.number_list[i] = ''
            else:  # No Enchantments
                item_index = item_name_list.index(self.inventory_list[i][0])
                self.hotbar_imgs[i - 27].img = pygame_imgs[item_index]
                self.number_list[i] = str(self.inventory_list[i][1])
                if self.number_list[i] == '1':
                    self.number_list[i] = ''
                if self.inventory_list[i][1] == 0:
                    self.inventory_list[i] = None

        # DRAW HOTBAR
        for i in range(len(self.hotbar_imgs)):
            display.blit(slot, (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))  # Background
            display.blit(self.hotbar_imgs[i].img, (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))  #Item
            if self.inventory_list[i+27] is not None:
                if player.inventory_list[i+27][4] is not None:
                    index = item_name_list.index(player.inventory_list[i+27][0])
                    display.blit(glint_list[index], (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))

        # DRAW HOTBAR BACKGROUNDS
        for j in self.hotbar_backgrounds:
            pygame.draw.rect(display, j.colour, j.rect, j.width)

        # SETUP HOTBAR NUMBERS
        font = pygame.font.Font(
            'images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 16)

        pygame_number_text = [
            Text(font.render(self.number_list[27], True, (255, 0, 0), (255, 255, 255)), 40, 480),
            Text(font.render(self.number_list[28], True, (255, 0, 0), (255, 255, 255)), 95, 480),
            Text(font.render(self.number_list[29], True, (255, 0, 0), (255, 255, 255)), 150, 480),
            Text(font.render(self.number_list[30], True, (255, 0, 0), (255, 255, 255)), 205, 480),
            Text(font.render(self.number_list[31], True, (255, 0, 0), (255, 255, 255)), 260, 480),
            Text(font.render(self.number_list[32], True, (255, 0, 0), (255, 255, 255)), 315, 480),
            Text(font.render(self.number_list[33], True, (255, 0, 0), (255, 255, 255)), 370, 480),
            Text(font.render(self.number_list[34], True, (255, 0, 0), (255, 255, 255)), 425, 480),
            Text(font.render(self.number_list[35], True, (255, 0, 0), (255, 255, 255)), 480, 480)
        ]

        # DRAW HOTBAR NUMBERS
        for j in pygame_number_text:
            display.blit(j.surface, (j.x, j.y))

        # RENDER F3 Screen
        if player.F3:
            font9 = pygame.font.Font(
                'images_vA1_7_4/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
            version = font9.render("Tilecraft vAlpha 1.7.4", True, (0, 0, 0), (255, 255, 255))
            display.blit(version, (0, 0))
            pygame_version = font9.render("Graphics: pygame v2.0.1", True, (0, 0, 0), (255, 255, 255))
            display.blit(pygame_version, (0, 25))
            FPS = font9.render(f"FPS: {previous_frame}", True, (0, 0, 0), (255, 255, 255))
            display.blit(FPS, (0, 75))
            Coords = font9.render(f"X: {round(player.x, 3)}, Y: {round(player.y, 3)}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Coords, (0, 100))
            SEEDs = font9.render(f"Seed: {World.seed}", True, (0, 0, 0), (255, 255, 255))
            display.blit(SEEDs, (0, 50))

def exit_death_screen():
    global death_window
    death_window.destroy()
    title_screen()


def death_screen():
    global death_window, true_play_time
    death_window = tkinter.Tk()
    death_window.title("Tilecraft Alpha 1.7.4")
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


def create_world():
    # Play Minecraft Music (Sweden)
    pygame.mixer.init()
    pygame.mixer.music.load("images_vA1_7_4/sweden.mp3")
    pygame.mixer.music.play()

    # Variables
    global netherGenerated, background, numList, call, difference, previous_frame, individual_frame, second_time, start, load, frame
    netherGenerated = False
    background = (255, 255, 255)
    numList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' ']
    call = False
    load = optionData()
    Quit()
    start = time.time()
    second_time = 0
    individual_frame = 0
    previous_frame = 0
    difference = 0
    frame = 0

    '''Initialise Display, Player, Images and Inventory Details'''

    global display, clock, world, game_engine

    pygame.init()  # Initialise Pygame Module
    display = pygame.display.set_mode((504, 504))  # Set display
    pygame.display.set_caption("Tilecraft Alpha 1.7.4")  # Set title
    clock = pygame.time.Clock()

    # Block Textures
    global grass, netherrack, stone
    grass = pygame.image.load('images_vA1_7_4/grass.png').convert()  # Grass
    netherrack = pygame.image.load('images_vA1_7_4/netherrack.png').convert()  # Netherrack
    stone = pygame.image.load('images_vA1_7_4/stone.png').convert()  # Stone

    global pygame_imgs, hotbar_imgs, pygame_enchant_imgs, hotbar_order, none_img, fire, no_fire

    # Create PYGAME inventory images for hotbar
    gravel = pygame.image.load("images_vA1_7_4/item_imgs/gravel.png").convert_alpha()  # 0
    flint = pygame.image.load("images_vA1_7_4/item_imgs/flint.png").convert_alpha()  # 1
    shield = pygame.image.load("images_vA1_7_4/item_imgs/shield.png").convert_alpha()  # 2
    water_bucket = pygame.image.load("images_vA1_7_4/item_imgs/water_bucket.png").convert_alpha()  # 3
    bucket = pygame.image.load("images_vA1_7_4/item_imgs/bucket.png").convert_alpha()  # 4
    iron_axe = pygame.image.load("images_vA1_7_4/item_imgs/iron_axe.png").convert_alpha()  # 5
    iron_pickaxe = pygame.image.load("images_vA1_7_4/item_imgs/iron_pickaxe.png").convert_alpha()  # 6
    iron_ore = pygame.image.load("images_vA1_7_4/item_imgs/iron_ore.png").convert_alpha()  # 7
    coal = pygame.image.load("images_vA1_7_4/item_imgs/coal.png").convert_alpha()  # 8
    iron_ingot = pygame.image.load("images_vA1_7_4/item_imgs/iron_ingot.png").convert_alpha()  # 9
    furnace = pygame.image.load("images_vA1_7_4/item_imgs/furnace.png").convert_alpha()  # 10
    stone_hoe = pygame.image.load("images_vA1_7_4/item_imgs/stone_hoe.png").convert_alpha()  # 11
    stone_shovel = pygame.image.load("images_vA1_7_4/item_imgs/stone_shovel.png").convert_alpha()  # 12
    stone_axe = pygame.image.load("images_vA1_7_4/item_imgs/stone_axe.png").convert_alpha()  # 13
    stone_pickaxe = pygame.image.load("images_vA1_7_4/item_imgs/stone_pickaxe.png").convert_alpha()  # 14
    wooden_pickaxe = pygame.image.load("images_vA1_7_4/item_imgs/wooden_pickaxe.png").convert_alpha()  # 15
    stick = pygame.image.load("images_vA1_7_4/item_imgs/stick.png").convert_alpha()  # 16
    planks = pygame.image.load("images_vA1_7_4/item_imgs/oak_planks.png").convert_alpha()  # 17
    wood = pygame.image.load("images_vA1_7_4/item_imgs/oak_log.png").convert_alpha()  # 18
    cobblestone = pygame.image.load("images_vA1_7_4/item_imgs/cobblestone.png").convert_alpha()  # 19
    flint_and_steel = pygame.image.load("images_vA1_7_4/item_imgs/flint_and_steel.png").convert_alpha()  # 20
    bed = pygame.image.load("images_vA1_7_4/item_imgs/bed.png").convert_alpha()  # 21
    hay = pygame.image.load("images_vA1_7_4/item_imgs/hay_bale.png").convert_alpha()  # 22
    diamond = pygame.image.load("images_vA1_7_4/item_imgs/diamond.png").convert_alpha()  # 23
    jukebox = pygame.image.load("images_vA1_7_4/item_imgs/jukebox.png").convert_alpha()  # 24
    bread = pygame.image.load("images_vA1_7_4/item_imgs/bread.png").convert_alpha()  # 25
    obsidian = pygame.image.load("images_vA1_7_4/item_imgs/obsidian.png").convert_alpha()  # 26
    diamond_pickaxe = pygame.image.load("images_vA1_7_4/item_imgs/diamond_pickaxe.png").convert_alpha()  # 27
    diamond_axe = pygame.image.load("images_vA1_7_4/item_imgs/diamond_axe.png").convert_alpha()  # 28
    pigstep_disc = pygame.image.load("images_vA1_7_4/item_imgs/pigstep_disc.png").convert_alpha()  # 29
    book = pygame.image.load("images_vA1_7_4/item_imgs/book.png").convert_alpha()  # 30
    enchanting_table = pygame.image.load("images_vA1_7_4/item_imgs/enchanting_table.png").convert_alpha()  # 31
    bookshelf = pygame.image.load("images_vA1_7_4/item_imgs/bookshelf.png").convert_alpha()  # 32
    lapis = pygame.image.load("images_vA1_7_4/item_imgs/lapis_lazuli.png").convert_alpha()  # 33
    golden_carrot = pygame.image.load("images_vA1_7_4/item_imgs/golden_carrot.png").convert_alpha()  # 34
    golden_apple = pygame.image.load("images_vA1_7_4/item_imgs/golden_apple.png")  # 35
    crafting_table = pygame.image.load("images_vA1_7_4/item_imgs/crafting_table.png").convert_alpha()  # 436
    iron_plate = pygame.image.load("images_vA1_7_4/item_imgs/iron_plate.png").convert_alpha() #37
    tier1_iron_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier1_iron_plate.png").convert_alpha() #38
    tier2_iron_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier2_iron_plate.png").convert_alpha() #39
    tier3_iron_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier3_iron_plate.png").convert_alpha() #40
    compressor = pygame.image.load("images_vA1_7_4/item_imgs/compressor.png").convert_alpha() #41
    diamond_plate = pygame.image.load("images_vA1_7_4/item_imgs/diamond_plate.png").convert_alpha() #42
    tier1_diamond_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier1_diamond_plate.png").convert_alpha() #43
    tier2_diamond_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier2_diamond_plate.png").convert_alpha() #44
    tier3_diamond_plate = pygame.image.load("images_vA1_7_4/item_imgs/tier3_diamond_plate.png").convert_alpha() #45

    none_img = pygame.image.load("images_vA1_7_4/item_imgs/slot.png").convert_alpha()  # White Space
    fire = pygame.image.load("images_vA1_7_4/item_imgs/fire.png").convert_alpha() #Fire when smelting                                                                                                  1)  # Fire when smelting
    no_fire = pygame.image.load("images_vA1_7_4/item_imgs/no_fire.png").convert_alpha()  # No fire when smelting

    pygame_imgs = [gravel, flint, shield, water_bucket, bucket, iron_axe, iron_pickaxe, iron_ore, coal,
                   iron_ingot, furnace, stone_hoe, stone_shovel, stone_axe, stone_pickaxe,
                   wooden_pickaxe, stick, planks, wood, cobblestone, flint_and_steel, bed,
                   hay, diamond, jukebox, bread, obsidian, diamond_pickaxe,
                   diamond_axe, pigstep_disc, book, enchanting_table, bookshelf, lapis,
                   golden_carrot, golden_apple, crafting_table, iron_plate, tier1_iron_plate,
                   tier2_iron_plate, tier3_iron_plate, compressor, diamond_plate, tier1_diamond_plate,
                   tier2_diamond_plate, tier3_diamond_plate]

    #Create GLINT images for enchanted items
    global glint_list
    glint_list = []
    glint_fullname_list = []
    glint_num_list = []
    new_glint_name_list = []
    int_glint_num_list = []
    for filename in os.listdir('images_vA1_7_4/glints'):
        glint_num_list.append(filename[5:-4])
        glint_fullname_list.append(filename[:-4])
    for i in glint_num_list:
        int_glint_num_list.append(int(i))
    new_glint_num_list = sorted(int_glint_num_list)
    for i in new_glint_num_list:
        index = glint_num_list.index(str(i))
        new_glint_name_list.append(glint_fullname_list[index])
    for i in new_glint_name_list:
        image = pygame.image.load('images_vA1_7_4/glints/' + i + '.png').convert_alpha()
        glint_list.append(image)

    # List for Hotbar Orders
    hotbar_order = ['Hotbar1', 'Hotbar2', 'Hotbar3', 'Hotbar4', 'Hotbar5', 'Hotbar6', 'Hotbar7', 'Hotbar8', 'Hotbar9']

    global stack_list, item_name_list, item_type_list
    item_name_list = ["Gravel", "Flint", "Shield", "Water Bucket", "Bucket", "Iron Axe", "Iron Pickaxe", "Iron Ore", "Coal", "Iron Ingot",
                      "Furnace", "Stone Hoe", "Stone Shovel", "Stone Axe", "Stone Pickaxe", "Wooden Pickaxe",
                      "Stick", "Oak Planks", "Oak Log", "Cobblestone", "Flint and Steel", "Bed", "Hay Bale",
                      "Diamond", "Jukebox", "Bread", "Obsidian", "Diamond Pickaxe", "Diamond Axe", "Pigstep Disc",
                      "Book", "Enchanting Table", "Bookshelf", "Lapis Lazuli", "Golden Carrot", "Golden Apple",
                      "Crafting Table", "Iron Plate", "Tier 1 Iron Plate", "Tier 2 Iron Plate", "Tier 3 Iron Plate", "Compressor",
                      "Diamond Plate", "Tier 1 Diamond Plate", "Tier 2 Diamond Plate", "Tier 3 Diamond Plate"]
    item_type_list = ["Item", "Item", "Shield", "Item", "Item", "Axe", "Pickaxe", "Item", "Item", "Item",
                      "Item", "Hoe", "Shovel", "Axe", "Pickaxe", "Pickaxe", "Item", "Item", "Item", "Item", "Item",
                      "Item", "Item", "Item", "Item", "Food", "Item", "Pickaxe", "Axe", "Item",
                      "Item", "Item", "Item", "Item", "Food", "Food", "Item", "Item", "Tier1", "Tier2", "Tier3", "Item",
                      "Item", "Tier1", "Tier2", "Tier3"]
    stack_list = [64, 64, 1, 1, 64, 1, 1, 64, 64, 64, 64, 1, 1, 1, 1, 1, 64, 64, 64, 64, 1, 1, 64, 64, 64,
                  64, 64, 1, 1, 1, 64, 64, 64, 64, 64, 64, 64, 64, 1, 1, 1, 64, 64, 1, 1, 1]

    world = pygame.Surface((504, 504))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black

    global player, World, Option1, Option2, Option3, Upgrade, screen, TimerRunning

    player = Player()  # Create Player
    World = TilecraftWorld(GetSeed())  # Create World
    screen = Screen() #Create Text Screen
    TimerRunning = True
    Upgrade = Button(55, 55, 75, 95, (158, 145, 115))
    Option1 = Button(325, 55, 170, 50, (158, 145, 115))
    Option2 = Button(325, 55, 170, 105, (158, 145, 115))
    Option3 = Button(325, 55, 170, 160, (158, 145, 115))
    signal = Main(display, clock)  #Start Game by Calling the Main Loop
    if signal == 'title screen':
        title_screen()
    elif signal == 'death screen':
            death_screen()

'''Function to handle all commands'''


def commands(number, val):
    global screen, player, cobblestone_index, obsidian_index, stack_list, item_name_list, item_type_list, previous_frame, experience, inventory_list, hotbar_order, hotbar_index, mode, hotbar_item, item_val_list, background, enchantable_list, flint_val, gravel_val, blacksmith_book, bool_blacksmith_iron, bool_blacksmith_diamond, bool_blacksmith_bread, blacksmith_iron, blacksmith_diamond, blacksmith_bread, endTime, bound_overworld_portal, overworld_portal, diaval, call, actualX, actualY, dimension
    for o in range(number):
        if val == "/minewood":  # Mine Wood
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Stone Axe":  # Stone Axe (+2)
                        screen.print("+2 Oak Log")
                        inventory_add([["Oak Log", 2, 64, "Item", None]])
                    elif player.hotbar_item[0] == "Iron Axe":  # Iron Axe (+3)
                        screen.print("+3 Oak Log")
                        inventory_add([["Oak Log", 3, 64, "Item", None]])
                    elif player.hotbar_item[0] == "Diamond Axe":  # Diamond Axe (+4)
                        screen.print("+4 Oak Log")
                        inventory_add([["Oak Log", 4, 64, "Item", None]])
                    else: #Other Items
                        screen.print("+1 Oak Log")
                        inventory_add([["Oak Log", 1, 64, "Item", None]])
                else:  # No item held
                    screen.print("+1 Oak Log")
                    inventory_add([["Oak Log", 1, 64, "Item", None]])
            else:
                screen.print('You are not in the overworld')
        elif val == "/minestone":  # Mine Stone
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Wooden Pickaxe":  # Wooden Pickaxe (+1)
                        screen.print("+1 Cobblestone")
                        inventory_add([["Cobblestone", 1, 64, "Item", None]])
                    elif player.hotbar_item[0] == "Stone Pickaxe":  # Stone Pickaxe (+2)
                        screen.print("+2 Cobblestone")
                        inventory_add([["Cobblestone", 2, 64, "Item", None]])
                    elif player.hotbar_item[0] == "Iron Pickaxe":  # Iron Pickaxe (+3)
                        screen.print("+3 Cobblestone")
                        inventory_add([["Cobblestone", 3, 64, "Item", None]])
                    elif player.hotbar_item[0] == "Diamond Pickaxe":  # Diamond Pickaxe (+4)
                        screen.print("+4 Cobblestone")
                        inventory_add([["Cobblestone", 4, 64, "Item", None]])
                    else:
                        screen.print("Requires Wooden Pickaxe")
                else:
                    screen.print("Requires Wooden Pickaxe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/minecoal":  # Mine Coal (Cave)
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Wooden Pickaxe" or player.hotbar_item[0] == "Stone Pickaxe" or player.hotbar_item[0] == "Iron Pickaxe" or player.hotbar_item[0] == "Diamond Pickaxe":
                        for j in range(len(World.bound_cave)):
                            if (World.bound_cave[j][0][0] < player.x < World.bound_cave[j][0][2]) and (
                                    World.bound_cave[j][1][0] < player.y < World.bound_cave[j][1][2]):
                                coal = random.randint(30, 50)
                                inventory_add([["Coal", coal, 64, "Item", None]])
                                screen.print(f"+{coal} Coal")
                                actualX = World.bound_cave[j][0][1]
                                actualY = World.bound_cave[j][1][1]
                                World.empty_cave1.append([actualX, actualY])
                                World.bound_cave.remove(World.bound_cave[j])
                                player.experience += coal // 7
                                call = True
                                empty_cave()
                                break
                    else:
                        screen.print("Require Wooden Pickaxe")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a cave")
                else:
                    screen.print("Require Wooden Pickaxe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/mineiron":  # Mine Iron (Cave)
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Stone Pickaxe" or player.hotbar_item[0] == "Iron Pickaxe" or player.hotbar_item[0] == "Diamond Pickaxe":
                        for j in range(len(World.bound_cave2)):
                            if (World.bound_cave2[j][0][0] < player.x < World.bound_cave2[j][0][2]) and (
                                    World.bound_cave2[j][1][0] < player.y < World.bound_cave2[j][1][2]):
                                iron = random.randint(16, 36)
                                inventory_add([["Iron Ore", iron, 64, "Item", None]])
                                screen.print("+" + str(iron) + " Iron Ore")
                                actualX = World.bound_cave2[j][0][1]
                                actualY = World.bound_cave2[j][1][1]
                                World.empty_cave2.append([actualX, actualY])
                                World.bound_cave2.remove(World.bound_cave2[j])
                                player.experience += iron // 5
                                call = True
                                empty_cave()
                                break
                    else:
                        screen.print("Require Stone Pickaxe")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a cave")
                else:
                    screen.print("Require Stone Pickaxe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/lootvillagehay":  # Loot Village Hay
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Stone Hoe":
                        for j in range(len(World.bound_village)):
                            if (World.bound_village[j][0][0] < player.x < World.bound_village[j][0][2]) and (
                                    World.bound_village[j][1][0] < player.y < World.bound_village[j][1][2]):
                                hay = random.randint(25, 45)
                                inventory_add([["Hay Bale", hay, 64, "Item", None]])
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
                        beds = random.randint(2, 7)
                        inventory_add([["Bed", beds, 1, "Item", None]])
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
                            blacksmith_iron = random.randint(1, 7)
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
                            blacksmith_diamond = random.randint(1, 5)
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
                            blacksmith_bread = random.randint(1, 14)
                        else:
                            blacksmith_bread = 0

                        # UPDATE AND PRINT INVENTORY VALUES
                        if blacksmith_iron > 0:
                            screen.print(f"+{blacksmith_iron} Iron Ingot")
                            inventory_add([["Iron Ingot", blacksmith_iron, 64, "Item", None]])
                        if blacksmith_diamond > 0:
                            screen.print(f"+{blacksmith_diamond} Diamond")
                            inventory_add([["Diamond", blacksmith_diamond, 64, "Item", None]])
                        if blacksmith_bread > 0:
                            screen.print(f"+{blacksmith_bread} Bread")
                            inventory_add([["Bread", blacksmith_bread, 64, "Food", None]])

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
                        library_bookshelf = random.randint(1, 3)
                        library_books = random.randint(7, 14)
                        screen.print(f"+{library_bookshelf} Bookshelf")
                        screen.print(f"+{library_books} Books")
                        inventory_add([["Bookshelf", library_bookshelf, 64, "Item", None]])
                        inventory_add([["Book", library_books, 64, "Item", None]])
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
        elif val == "/fillbucket":
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == 'Bucket':
                        for j in range(len(World.bound_water)):
                            if (World.bound_water[j][0][0] < player.x < World.bound_water[j][0][2]) and (World.bound_water[j][1][0] < player.y < World.bound_water[j][1][2]):
                                screen.print("+1 Water Bucket")
                                screen.print("-1 Bucket")
                                hotbar_index = hotbar_order.index(player.selected_hotbar)
                                player.inventory_list[hotbar_index + 27][1] -= 1  # Subtract 1 Bucket
                                inventory_add([['Water Bucket', 1, 1, 'Item', None]])  # Add 1 Water Bucket
                                call = True
                                break
                    else:
                        screen.print("Error: Not Enough Resources")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a water pool")
                else:
                    screen.print("Error: Not Enough Resources")
            else:
                screen.print("You are not in the overworld")
        elif val == "/minegravel":
            if player.dimension == 'Overworld':
                flint_val = 0
                gravel_val = 0
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == 'Stone Shovel':
                        for j in range(len(World.bound_water2)):
                            if (World.bound_water2[j][0][0] < player.x < World.bound_water2[j][0][2]) and (World.bound_water2[j][1][0] < player.y < World.bound_water2[j][1][2]):
                                gravel_number = random.randint(11, 24)
                                for k in range(gravel_number):
                                    gr = random.randint(1, 10)
                                    if gr == 6:
                                        flint_val += 1
                                    else:
                                        gravel_val += 1
                                if gravel_val > 0:
                                    screen.print("+" + str(gravel_val) + " Gravel")
                                    inventory_add([["Gravel", gravel_val, 64, "Item", None]])
                                if flint_val > 0:
                                    screen.print("+" + str(flint_val) + " Flint")
                                    inventory_add([["Flint", flint_val, 64, "Item", None]])
                                actualX = World.bound_water2[j][0][1]
                                actualY = World.bound_water2[j][1][1]
                                World.empty_water.append([actualX, actualY])
                                World.bound_water2.remove(World.bound_water2[j])
                                call = True
                                break
                    else:
                        screen.print("Require Stone Shovel")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a water pool")
                else:
                    screen.print("Require Stone Shovel")
            else:
                screen.print("You are not in the overworld")
        elif val == "/buildnetherportal":  # Build nether portal
            if player.dimension == 'Overworld':

                # Declare Variables
                water_bucket_bool = False
                flint_and_steel_bool = False
                cobblestone_bool = False

                for i in player.inventory_list:
                    if i is not None:
                        if i[0] == 'Water Bucket':  # Test for Water Bucket
                            water_bucket_bool = True
                            break
                for i in player.inventory_list:
                    if i is not None:
                        if i[0] == 'Flint and Steel':  # Test for Flint and Steel
                            flint_and_steel_bool = True
                            break
                for i in player.inventory_list:
                    if i is not None:
                        if i[0] == "Cobblestone" and i[1] > 5:  # Test for at least 6 Cobblestone
                            cobblestone_index = player.inventory_list.index(i)
                            cobblestone_bool = True
                            break

                if water_bucket_bool and flint_and_steel_bool and cobblestone_bool:
                    for j in range(len(World.bound_lava)):
                        if (World.bound_lava[j][0][0] < player.x < World.bound_lava[j][0][2]) and (
                                World.bound_lava[j][1][0] < player.y < World.bound_lava[j][1][2]):
                            screen.print("Built a Nether Portal at your location.")
                            player.inventory_list[cobblestone_index][1] -= 6
                            actualX = World.bound_lava[j][0][1]
                            actualY = World.bound_lava[j][1][1]
                            World.overworld_portal.append([actualX, actualY])
                            World.bound_overworld_portal.append([[actualX - 10 / 16, actualX, actualX + 10 / 16],
                                                           [actualY - 10 / 16, actualY, actualY + 10 / 16]])
                            call = True
                            break
                else:
                    screen.print("Error: Not Enough Resources")
                if call:
                    call = False
                else:
                    screen.print("You are not at a lava pool")
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
        elif val == "/minediamonds":  # Mine Diamonds
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Iron Pickaxe" or player.hotbar_item[0] == "Diamond Pickaxe":
                        for j in range(len(World.bound_deep_cave)):
                            if (World.bound_deep_cave[j][0][0] < player.x < World.bound_deep_cave[j][0][2]) and (
                                    World.bound_deep_cave[j][1][0] < player.y < World.bound_deep_cave[j][1][2]):
                                diaval = random.randint(0, 8)
                                inventory_add([["Diamond", diaval, 64, "Item", None]])
                                if diaval > 0:
                                    screen.print(f"+{diaval} Diamonds")
                                else:
                                    screen.print("No diamonds to mine")
                                actualX = World.bound_deep_cave[j][0][1]
                                actualY = World.bound_deep_cave[j][1][1]
                                World.empty_deep_cave1.append([actualX, actualY])
                                World.bound_deep_cave.remove(World.bound_deep_cave[j])
                                player.experience += diaval // 2
                                call = True
                                empty_deep_caves()
                                break
                    else:
                        screen.print("Require Iron Pickaxe")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a deep cave")
                else:
                    screen.print("Require Iron Pickaxe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/minelapis":  # Mine Lapis
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Stone Pickaxe" or player.hotbar_item[0] == "Iron Pickaxe" or player.hotbar_item[0] == "Diamond Pickaxe":
                        for j in range(len(World.bound_deep_cave2)):
                            if (World.bound_deep_cave2[j][0][0] < player.x < World.bound_deep_cave2[j][0][2]) and (
                                    World.bound_deep_cave2[j][1][0] < player.y < World.bound_deep_cave2[j][1][2]):
                                lapisval = random.randint(4, 8)
                                inventory_add([["Lapis Lazuli", lapisval, 64, "Item", None]])
                                screen.print(f"+{lapisval} Lapis Lazuli")
                                actualX = World.bound_deep_cave2[j][0][1]
                                actualY = World.bound_deep_cave2[j][1][1]
                                World.empty_deep_cave2.append([actualX, actualY])
                                World.bound_deep_cave2.remove(World.bound_deep_cave2[j])
                                player.experience += lapisval // 3
                                call = True
                                empty_deep_caves()
                                break
                    else:
                        screen.print("Require Stone Pickaxe")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a deep cave")
                else:
                    screen.print("Require Stone Pickaxe")
            else:
                screen.print("You are not in the overworld")
        elif val == "/lootbastion":
            if player.dimension == 'Nether':
                for j in range(len(World.bound_bastion)):
                    if (World.bound_bastion[j][0][0] < player.x < World.bound_bastion[j][0][2]) and (
                            World.bound_bastion[j][1][0] < player.y < World.bound_bastion[j][1][2]):
                        inventory_add([["Pigstep Disc", 1, 1, "Item", None]])
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

            for i in player.inventory_list:
                if i is not None:
                    if i[0] == "Pigstep Disc":  # Pigstep Disc
                        pigstep_disc_bool = True
                        break
            for i in player.inventory_list:
                if i is not None:
                    if i[0] == "Jukebox":  # Jukebox
                        jukebox_bool = True
                        break

            if pigstep_disc_bool and jukebox_bool:  # Play Pigstep
                pygame.mixer.init()
                pygame.mixer.music.load("images_vA1_7_4/pigstep.mp3")
                pygame.mixer.music.set_volume(10)
                pygame.mixer.music.play()
                MusicPlayer(player.advancements) #Update Advancement and Speedrun Details
            else:
                screen.print("Error: Not Enough Resources")
        elif val == "/mineobsidian":  # Mine Obsidian
            if player.dimension == 'Overworld':

                # Test if Water Bucket is in inventory:
                water_bucket_bool = False
                for i in player.inventory_list:
                    if i is not None:
                        if i[0] == "Water Bucket":
                            water_bucket_bool = True
                            break

                if player.hotbar_item is not None:
                    if player.hotbar_item[0] == "Diamond Pickaxe" and water_bucket_bool:
                        for j in range(len(World.bound_lava)):
                            if (World.bound_lava[j][0][0] < player.x < World.bound_lava[j][0][2]) and (
                                    World.bound_lava[j][1][0] < player.y < World.bound_lava[j][1][2]):
                                screen.print("+1 Obsidian")
                                inventory_add([["Obsidian", 1, 64, "Item", None]])
                                call = True
                                break
                    else:
                        screen.print("Error: Not Enough Resources")
                    if call:
                        call = False
                    else:
                        screen.print("You are not at a lava pool")
                else:
                    screen.print("Error: Not Enough Resources")
            else:
                screen.print("You are not in the overworld")
        elif val == '/lootruinedportal':  # Loot Ruined Portal
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_ruined_portal)):
                    if (World.bound_ruined_portal[j][0][0] < player.x < World.bound_ruined_portal[j][0][2]) and (
                            World.bound_ruined_portal[j][1][0] < player.y < World.bound_ruined_portal[j][1][2]):
                        R_iron_val = random.randint(2, 7)
                        R_flint_val = random.randint(1, 3)
                        R_golden_carrot_val = random.randint(0, 6)
                        R_golden_apple_val = random.randint(0, 2)
                        R_obsidian_val = random.randint(0, 3)
                        inventory_add([["Iron Ingot", R_iron_val, 64, "Item", None]])  # Add Iron Ingot
                        screen.print(f"+{R_iron_val} Iron Ingot")
                        inventory_add([["Flint", R_flint_val, 64, "Item", None]])  # Add Flint
                        screen.print(f"+{R_flint_val} Flint")
                        if R_golden_carrot_val > 0:  # Add Golden Carrot
                            screen.print(f"+{R_golden_carrot_val} Golden Carrot")
                            inventory_add([["Golden Carrot", R_golden_carrot_val, 64, "Food", None]])
                        if R_golden_apple_val > 0:  # Add Golden Apple
                            screen.print(f"+{R_golden_apple_val} Golden Apple")
                            inventory_add([["Golden Apple", R_golden_apple_val, 64, "Food", None]])
                        if R_obsidian_val > 0:  # Add Obsidian
                            screen.print(f"+{R_obsidian_val} Obsidian")
                            inventory_add([["Obsidian", R_obsidian_val, 64, "Item", None]])
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

                        for i in player.inventory_list:
                            if i is not None:
                                if i[0] == 'Flint and Steel':  # Test for flint and steel
                                    flint_and_steel_bool = True
                                    break
                        if obsidian_num == 0:
                            obsidian_bool = True
                        for i in player.inventory_list:
                            if i is not None:
                                if i[0] == "Obsidian" and i[1] >= obsidian_num:  # Test for enough obsidian
                                    obsidian_index = player.inventory_list.index(i)
                                    obsidian_bool = True
                                    break

                        if flint_and_steel_bool and obsidian_bool:
                            if obsidian_num > 0:
                                player.inventory_list[obsidian_index][1] -= obsidian_num
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
                print_cheats(item_name_list)
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == '/give':
            if load == 'Cheats':
                screen.start_typing("Item ID (0 - 45): ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == '/tp':
            if load == 'Cheats':
                screen.start_typing("Coordinates (X,Y): ")
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        else:
            screen.print("Invalid Function")

#Health and Hunger Info Bar Class
class info_bar:
    def __init__(self, img, x, y):
        self.img = img
        self.x = x
        self.y = y

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


# Displays empty cave
def empty_cave():
    global actualX, actualY, bool_empty_cave1, bool_empty_cave2, empty_cave_total, cave
    bool_empty_cave1 = False
    bool_empty_cave2 = False
    for i in range(len(World.empty_cave1)):
        if (actualX in World.empty_cave1[i]) and (actualY in World.empty_cave1[i]):
            bool_empty_cave1 = True
    for i in range(len(World.empty_cave2)):
        if (actualX in World.empty_cave2[i]) and (actualY in World.empty_cave2[i]):
            bool_empty_cave2 = True
    if bool_empty_cave1 and bool_empty_cave2:
        World.empty_cave_total.append([actualX, actualY])


# Displays empty deep cave
def empty_deep_caves():
    global actualX, actualY, bool_empty_deep_cave1, bool_empty_deep_cave2, empty_deep_cave_total, deep_cave
    bool_empty_deep_cave1 = False
    bool_empty_deep_cave2 = False
    for i in range(len(World.empty_deep_cave1)):
        if (actualX in World.empty_deep_cave1[i]) and (actualY in World.empty_deep_cave1[i]):
            bool_empty_deep_cave1 = True
    for i in range(len(World.empty_deep_cave2)):
        if (actualX in World.empty_deep_cave2[i]) and (actualY in World.empty_deep_cave2[i]):
            bool_empty_deep_cave2 = True
    if bool_empty_deep_cave1 and bool_empty_deep_cave2:
        World.empty_deep_cave_total.append([actualX, actualY])


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
    window1.title('Tilecraft Alpha 1.7.4')
    window1.geometry('500x500')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40)
    font = tkinter.font.Font(family='Minecraft', size=24)
    font2 = tkinter.font.Font(family='Minecraft', size=10)

    title = tkinter.Label(window1, text='Patch Notes', font=bold_font, fg='black')
    title.place(x=125, y=0)

    with open("patch_notes.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window1, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=55, y=50)

    back_to_title_screen = tkinter.Button(window1, text='Title Screen', fg='black', font=font, command=BackToTitleScreen)
    back_to_title_screen.place(x=150, y=425)

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
    window2.title('Tilecraft Alpha 1.7.4')
    window2.geometry('500x500')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40)
    font = tkinter.font.Font(family='Minecraft', size=24)
    font2 = tkinter.font.Font(family='Minecraft', size=10)

    title = tkinter.Label(window2, text='How To Play', font=bold_font, fg='black')
    title.place(x=125, y=0)

    with open("how_to_play.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window2, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=55, y=50)

    back_to_title_screen = tkinter.Button(window2, text='Title Screen', fg='black', font=font, command=BackToTitleScreen2)
    back_to_title_screen.place(x=150, y=425)

    window2.mainloop()

# Title Screen Function
def title_screen():
    global window, tkvar2, fontStyle2, fileMenu, startWorld, bg, bold_font, regular_font, fontStyle2, font4, tkvar3, first_click

    first_click = True #Set Variable to track when the user first clicked on the seed box

    # Play Minecraft Music (Minecraft)
    pygame.mixer.init()
    pygame.mixer.music.load("images_vA1_7_4/Minecraft.mp3")
    pygame.mixer.music.play()

    # Create tkinter window
    window = tkinter.Tk()
    window.title('Tilecraft Alpha 1.7.4')
    window.geometry('500x500')

    # Create background image
    bg = tkinter.PhotoImage(file="images_vA1_7_4/A1_7_background.png")

    # Create fonts
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40)
    regular_font = tkinter.font.Font(family='Minecraft Regular', size=18)
    fontStyle2 = tkinter.font.Font(size=26, family='Minecraft Regular')
    font4 = tkinter.font.Font(size=15, family='Minecraft Regular')

    # Create canvas
    canvas1 = tkinter.Canvas(window, width=500, height=500)
    canvas1.create_image(0, 0, image=bg, anchor="nw")
    canvas1.create_text(250, 25, fill="black", font=bold_font, text="Tilecraft")
    canvas1.create_text(250, 50, fill="black", font=regular_font, text="Alpha 1.7.4")
    canvas1.place(x=0, y=0)

    #Create Seed Box Entry Widget
    tkvar3 = tkinter.StringVar(window)
    tkvar3.set('World Seed: ')
    SeedBox = tkinter.Entry(window, textvariable=tkvar3)
    SeedBox.configure(width=38, fg='white', font=font4)
    SeedBox.place(x=80, y=100)

    # Create a tkinter variable
    tkvar2 = tkinter.StringVar(window)
    tkvar2.set('None')

    # Set choices for option menu
    choices = {'"Music Player" Speedrun Data Pack', '"God Gear" Speedrun Data Pack', 'Cheats Data Pack', 'None'}

    # Option menu for datapacks
    fileMenu = tkinter.OptionMenu(window, tkvar2, *choices)
    fileMenu.configure(width=34, foreground='black', font=font4)
    fileMenu.place(x=80, y=125)

    # New World button
    startWorld = tkinter.Button(window, text="New World", command=create_world, width="19", height="2", font=fontStyle2,
                                foreground='black')
    startWorld.place(x=80, y=145)

    # How to play button
    htp = tkinter.Button(window, text="How to Play", width="19", height="2", font=fontStyle2, foreground='black', command=howtoplay)
    htp.place(x=80, y=205)

    # Patch Notes
    patch_notes = tkinter.Button(window, text="Patch Notes", width="19", height="2", font=fontStyle2, foreground='black', command=patchnotes)
    patch_notes.place(x=80, y=265)

    # Quit Button
    quit_button = tkinter.Button(window, text="Quit", command=Quit, width="19", height="2", font=fontStyle2, foreground='black')
    quit_button.place(x=80, y=325)

    #Clicking on Seedbox entry widget
    SeedBox.bind('<FocusIn>', get_first_click)

    # Tkinter main loop
    window.mainloop()

def RemoveItem():
    global player
    # Remove Value if Number is 0
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i][1] <= 0:
                player.enchanting_list[i] = None
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i][1] <= 0:
                player.inventory_list[i] = None
    for i in range(len(player.craft_list)):
        if player.craft_list[i] is not None:
            if player.craft_list[i][1] <= 0:
                player.craft_list[i] = None
    if player.holding_item is not None:
        if player.holding_item[1] <= 0:
            player.holding_item = None
    for i in range(len(player.grid_list)):
        if player.grid_list[i] is not None:
            if player.grid_list[i][1] <= 0:
                player.grid_list[i] = None
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i][1] <= 0:
                player.smelting_list[i] = None
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i][1] <= 0:
                player.compressor_list[i] = None

def Crafting():
    if player.mode == "inventory":
        global craft_list
        if player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is None:
            if player.craft_list[0][0] == 'Oak Log':
                player.craft_list[4] = ['Oak Planks', 4, 64, 'Item', None]
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is not None and player.craft_list[3] is None:
            if player.craft_list[0][0] == 'Oak Planks' and player.craft_list[2][0] == 'Oak Planks':
                player.craft_list[4] = ['Stick', 4, 64, 'Item', None]
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is not None and player.craft_list[2] is not None and player.craft_list[3] is not None:
            if player.craft_list[0][0] == 'Oak Planks' and player.craft_list[1][0] == 'Oak Planks' and player.craft_list[2][0] == 'Oak Planks' and player.craft_list[3][0] == 'Oak Planks':
                player.craft_list[4] = ['Crafting Table', 1, 64, 'Item', None]
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is not None:
            if player.craft_list[0][0] == 'Iron Ingot' and player.craft_list[3][0] == 'Flint':
                player.craft_list[4] = ['Flint and Steel', 1, 1, 'Item', None]
            else:
                player.craft_list[4] = None
        else:
            player.craft_list[4] = None

def GridCraft():
    if player.mode == "crafting":
        if player.grid_list[0] is not None and player.grid_list[1] is None and player.grid_list[2] is None and player.grid_list[3] is None and \
                player.grid_list[4] is None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is None and \
                player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Oak Log':  # Craft Planks
                player.grid_list[9] = ['Oak Planks', 4, 64, 'Item', None]
            elif player.grid_list[0][0] == "Hay Bale":  # Craft Bread
                player.grid_list[9] = ['Bread', 3, 64, "Food", None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is None and player.grid_list[2] is None and player.grid_list[3] is not None and \
                player.grid_list[4] is None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is None and \
                player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Oak Planks' and player.grid_list[3][0] == 'Oak Planks':  # Craft Sticks
                player.grid_list[9] = ['Stick', 4, 64, 'Item', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is None and player.grid_list[3] is not None and player.grid_list[4] is not None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is None and player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Oak Planks' and player.grid_list[1][0] == 'Oak Planks' and player.grid_list[3][0] == 'Oak Planks' and player.grid_list[4][0] == 'Oak Planks':  # Craft Crafting Table
                player.grid_list[9] = ['Crafting Table', 1, 64, 'Item', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[3] is None and player.grid_list[4] is not None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Oak Planks' and player.grid_list[1][0] == 'Oak Planks' and player.grid_list[2][0] == 'Oak Planks' and player.grid_list[4][0] == 'Stick' and player.grid_list[7][0] == 'Stick':  # Craft Wooden Pickaxe
                player.grid_list[9] = ['Wooden Pickaxe', 1, 1, 'Pickaxe', None]
            elif player.grid_list[0][0] == 'Cobblestone' and player.grid_list[1][0] == 'Cobblestone' and player.grid_list[2][0] == 'Cobblestone' and player.grid_list[4][0] == 'Stick' and player.grid_list[7][0] == 'Stick':  # Craft Stone Pickaxe
                player.grid_list[9] = ['Stone Pickaxe', 1, 1, 'Pickaxe', None]
            elif player.grid_list[0][0] == 'Iron Ingot' and player.grid_list[1][0] == 'Iron Ingot' and player.grid_list[2][0] == 'Iron Ingot' and player.grid_list[4][0] == 'Stick' and player.grid_list[7][0] == 'Stick':  # Craft Iron Pickaxe
                player.grid_list[9] = ['Iron Pickaxe', 1, 1, 'Pickaxe', None]
            elif player.grid_list[0][0] == 'Diamond' and player.grid_list[1][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and \
                    player.grid_list[4][0] == 'Stick' and player.grid_list[7][0] == 'Stick':  # Craft Diamond Pickaxe
                player.grid_list[9] = ['Diamond Pickaxe', 1, 1, 'Pickaxe', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[3] is None and \
                player.grid_list[4] is not None and player.grid_list[5] is not None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[1][0] == 'Cobblestone' and player.grid_list[2][0] == 'Cobblestone' and player.grid_list[4][0] == 'Stick' and \
                    player.grid_list[5][0] == 'Cobblestone' and player.grid_list[7][0] == 'Stick':  # Craft Stone Axe
                player.grid_list[9] = ['Stone Axe', 1, 1, 'Axe', None]
            elif player.grid_list[1][0] == 'Iron Ingot' and player.grid_list[2][0] == 'Iron Ingot' and player.grid_list[4][0] == 'Stick' and \
                    player.grid_list[5][0] == 'Iron Ingot' and player.grid_list[7][0] == 'Stick':  # Craft Iron Axe
                player.grid_list[9] = ['Iron Axe', 1, 1, 'Axe', None]
            elif player.grid_list[1][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and player.grid_list[4][0] == 'Stick' and \
                    player.grid_list[5][0] == 'Diamond' and player.grid_list[7][0] == 'Stick':  # Craft Diamond Axe
                player.grid_list[9] = ['Diamond Axe', 1, 1, 'Axe', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is None and player.grid_list[3] is None and \
                player.grid_list[4] is not None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[1][0] == 'Cobblestone' and player.grid_list[4][0] == 'Stick' and player.grid_list[7][0] == 'Stick':  # Craft Stone Shovel
                player.grid_list[9] = ['Stone Shovel', 1, 1, 'Shovel', None]
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[3] is None and \
                player.grid_list[4] is not None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[1][0] == 'Cobblestone' and player.grid_list[2][0] == 'Cobblestone' and player.grid_list[4][0] == 'Stick' and \
                    player.grid_list[7][0] == 'Stick':  # Craft Stone Hoe
                player.grid_list[9] = ['Stone Hoe', 1, 1, 'Hoe', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is not None and \
                player.grid_list[7] is not None and player.grid_list[8] is not None:
            if player.grid_list[0][0] == 'Cobblestone' and player.grid_list[1][0] == 'Cobblestone' and player.grid_list[2][
                0] == 'Cobblestone' and player.grid_list[3][0] == 'Cobblestone' and player.grid_list[5][0] == 'Cobblestone' and \
                    player.grid_list[6][0] == 'Cobblestone' and player.grid_list[7][0] == 'Cobblestone' and player.grid_list[8][0] == 'Cobblestone':  # Craft Furnace
                player.grid_list[9] = ['Furnace', 1, 64, 'Item', None]
            elif player.grid_list[0][0] == 'Iron Plate' and player.grid_list[1][0] == 'Iron Plate' and player.grid_list[2][0] == 'Iron Plate' and \
                player.grid_list[3][0] == 'Iron Plate' and player.grid_list[5][0] == 'Iron Plate' and player.grid_list[6][0] == 'Iron Plate' and \
                player.grid_list[7][0] == 'Iron Plate' and player.grid_list[8][0] == 'Iron Plate': #Craft Tier 3 Iron Plate (Armour)
                    player.grid_list[9] = ['Tier 3 Iron Plate', 1, 1, "Tier3", None]
            elif player.grid_list[0][0] == 'Diamond Plate' and player.grid_list[1][0] == 'Diamond Plate' and player.grid_list[2][0] == 'Diamond Plate' and \
                player.grid_list[3][0] == 'Diamond Plate' and player.grid_list[5][0] == 'Diamond Plate' and player.grid_list[6][0] == 'Diamond Plate' and \
                player.grid_list[7][0] == 'Diamond Plate' and player.grid_list[8][0] == 'Diamond Plate': #Craft Tier 3 Diamond Plate (Armour)
                    player.grid_list[9] = ['Tier 3 Diamond Plate', 1, 1, "Tier3", None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is None and player.grid_list[2] is None and player.grid_list[3] is not None and \
                player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[3][0] == 'Iron Ingot' and player.grid_list[5][0] == 'Iron Ingot' and player.grid_list[7][0] == 'Iron Ingot':  # Craft Bucket
                player.grid_list[9] = ['Bucket', 1, 64, 'Item', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is not None and player.grid_list[5] is not None and player.grid_list[6] is None and \
                player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Oak Planks' and player.grid_list[1][0] == 'Iron Ingot' and player.grid_list[2][
                0] == 'Oak Planks' and player.grid_list[3][0] == 'Oak Planks' and player.grid_list[4][0] == 'Oak Planks' and \
                    player.grid_list[5][0] == 'Oak Planks' and player.grid_list[7][0] == 'Oak Planks':  # Craft Shield
                player.grid_list[9] = ['Shield', 1, 1, 'Shield', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[3] is not None and player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is None and player.grid_list[7] is None and player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Diamond' and player.grid_list[1][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and \
                    player.grid_list[3][0] == 'Diamond' and player.grid_list[5][0] == 'Diamond':  # Craft Diamond Helmet
                player.grid_list[9] = ['Diamond Helmet', 1, 1, 'Helmet', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is not None and player.grid_list[5] is not None and player.grid_list[6] is not None and \
                player.grid_list[7] is not None and player.grid_list[8] is not None:
            if player.grid_list[0][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and player.grid_list[3][0] == 'Diamond' and \
                    player.grid_list[4][0] == 'Diamond' and player.grid_list[5][0] == 'Diamond' and player.grid_list[6][0] == 'Diamond' and \
                    player.grid_list[7][0] == 'Diamond' and player.grid_list[8][0] == 'Diamond':  # Craft Diamond Chestplate
                player.grid_list[9] = ['Diamond Chestplate', 1, 1, 'Chestplate', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is not None and \
                player.grid_list[7] is None and player.grid_list[8] is not None:
            if player.grid_list[0][0] == 'Diamond' and player.grid_list[1][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and \
                    player.grid_list[3][0] == 'Diamond' and player.grid_list[5][0] == 'Diamond' and player.grid_list[6][0] == 'Diamond' and \
                    player.grid_list[8][0] == 'Diamond':  # Craft Diamond Leggings
                player.grid_list[9] = ['Diamond Leggings', 1, 1, 'Leggings', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is None and player.grid_list[7] is None and player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Diamond' and player.grid_list[2][0] == 'Diamond' and player.grid_list[3][0] == 'Diamond' and \
                    player.grid_list[5][0] == 'Diamond':  # Craft Diamond Boots
                player.grid_list[9] = ['Diamond Boots', 1, 1, 'Boots', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is None and player.grid_list[2] is None and player.grid_list[3] is None and \
                player.grid_list[4] is not None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is None and \
                player.grid_list[8] is None:
            if player.grid_list[0][0] == 'Iron Ingot' and player.grid_list[4][0] == 'Flint':  # Craft Flint and Steel
                player.grid_list[9] = ['Flint and Steel', 1, 1, 'Item', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is not None and player.grid_list[1] is not None and player.grid_list[2] is not None and player.grid_list[
            3] is not None and player.grid_list[4] is not None and player.grid_list[5] is not None and player.grid_list[6] is not None and \
                player.grid_list[7] is not None and player.grid_list[8] is not None:
            if player.grid_list[0][0] == "Oak Planks" and player.grid_list[1][0] == "Oak Planks" and player.grid_list[2][
                0] == "Oak Planks" and player.grid_list[3][0] == "Oak Planks" and player.grid_list[4][0] == "Diamond" and \
                    player.grid_list[5][0] == "Oak Planks" and player.grid_list[6][0] == "Oak Planks" and player.grid_list[7][0] == "Oak Planks" and player.grid_list[8][0] == "Oak Planks":  # Craft Jukebox
                player.grid_list[9] = ['Jukebox', 1, 64, "Item", None]
            elif player.grid_list[0][0] == "Oak Planks" and player.grid_list[1][0] == "Oak Planks" and player.grid_list[2][
                0] == "Oak Planks" and player.grid_list[3][0] == "Book" and player.grid_list[4][0] == "Book" and player.grid_list[5][
                0] == "Book" and player.grid_list[6][0] == "Oak Planks" and player.grid_list[7][0] == "Oak Planks" and player.grid_list[8][0] == "Oak Planks":  # Craft Bookshelf
                player.grid_list[9] = ['Bookshelf', 1, 64, 'Item', None]
            elif player.grid_list[0][0] == 'Cobblestone' and player.grid_list[1][0] == 'Cobblestone' and player.grid_list[2][0] == 'Cobblestone' and player.grid_list[3][0] == 'Cobblestone' \
                and player.grid_list[4][0] == 'Iron Ingot' and player.grid_list[5][0] == 'Cobblestone' and player.grid_list[6][0] == 'Cobblestone' and \
                    player.grid_list[7][0] == 'Cobblestone' and player.grid_list[8][0] == 'Cobblestone':
                player.grid_list[9] = ['Compressor', 1, 64, 'Item', None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is None and player.grid_list[3] is not None and \
                player.grid_list[4] is not None and player.grid_list[5] is not None and player.grid_list[6] is not None and player.grid_list[7] is not None and player.grid_list[8] is not None:
            if player.grid_list[1][0] == "Book" and player.grid_list[3][0] == "Diamond" and player.grid_list[4][0] == "Obsidian" and \
                    player.grid_list[5][0] == "Diamond" and player.grid_list[6][0] == "Obsidian" and player.grid_list[7][0] == "Obsidian" and \
                    player.grid_list[8][0] == "Obsidian":  # Craft Enchanting Table
                player.grid_list[9] = ['Enchanting Table', 1, 64, "Item", None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is None and player.grid_list[3] is None and \
                player.grid_list[4] is None and player.grid_list[5] is None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[1][0] == 'Iron Plate' and player.grid_list[7][0] == 'Iron Plate': #Craft Tier 1 Iron Plate (Armour)
                player.grid_list[9] = ['Tier 1 Iron Plate', 1, 1, "Tier1", None]
            elif player.grid_list[1][0] == 'Diamond Plate' and player.grid_list[7][0] == 'Diamond Plate': #Craft Tier 1 Diamond Plate (Armour)
                player.grid_list[9] = ['Tier 1 Diamond Plate', 1, 1, "Tier1", None]
            else:
                player.grid_list[9] = None
        elif player.grid_list[0] is None and player.grid_list[1] is not None and player.grid_list[2] is None and player.grid_list[3] is not None and \
                player.grid_list[4] is None and player.grid_list[5] is not None and player.grid_list[6] is None and player.grid_list[7] is not None and player.grid_list[8] is None:
            if player.grid_list[1][0] == 'Iron Plate' and player.grid_list[3][0] == 'Iron Plate' and \
            player.grid_list[5][0] == 'Iron Plate' and player.grid_list[7][0] == 'Iron Plate': #Craft Tier 2 Iron Plate (Armour)
                player.grid_list[9] = ['Tier 2 Iron Plate', 1, 1, "Tier2", None]
            elif player.grid_list[1][0] == 'Diamond Plate' and player.grid_list[3][0] == 'Diamond Plate' and \
            player.grid_list[5][0] == 'Diamond Plate' and player.grid_list[7][0] == 'Diamond Plate': #Craft Tier 2 Diamond Plate (Armour)
                player.grid_list[9] = ['Tier 2 Diamond Plate', 1, 1, "Tier2", None]
            else:
                player.grid_list[9] = None
        else:
            player.grid_list[9] = None

def EnchantUpgrade():
    global player
    if player.enchanting_list[2] is not None and player.enchanting_level < 5:
        if player.enchanting_list[2][0] == 'Bookshelf' and player.enchanting_list[2][1] > 3:
            player.enchanting_list[2][1] -= 4
            player.enchanting_level += 1
            EnchantSet()  # Set Enchants


def EnchantSet():
    global player
    if player.enchanting_list[0] is not None:
        if player.enchanting_list[0][4] is None:
            player.level1 = 0
            player.level2 = 0
            player.level3 = 0
            player.optional_enchant2 = None
            player.optional_enchant3 = None
            if player.enchanting_level == 0:  # LEVEL 0
                player.level1 = 0
                player.level2 = 0
                player.level3 = random.randint(0, 1)
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 1:  # LEVEL 1
                player.level1 = 1
                player.level2 = random.randint(1, 2)
                player.level3 = 2
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 2:  # LEVEL 2
                player.level1 = 2
                player.level2 = random.randint(2, 3)
                player.level3 = 3
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 3:  # LEVEL 3
                player.level1 = 3
                player.level2 = random.randint(3, 4)
                player.level3 = 4
                player.optional_enchant2 = None
                player.optional_enchant3 = random.randint(0, 1)
            elif player.enchanting_level == 4:  # LEVEL 4
                player.level1 = 4
                player.level2 = random.randint(4, 5)
                player.level3 = 5
                player.optional_enchant2 = random.randint(0, 1)
                player.optional_enchant3 = random.randint(1, 2)
            else:  # LEVEL 5
                player.level1 = random.randint(4, 5)
                player.level2 = 5
                player.level3 = 5
                player.optional_enchant2 = random.randint(1, 2)
                player.optional_enchant3 = random.randint(2, 3)

            if player.enchanting_list[0][3] == 'Tier1' or player.enchanting_list[0][3] == 'Tier2' or player.enchanting_list[0][3] == 'Tier3':  # Armour
                player.option_list[0] = f'Protection {player.level1}'
                player.option_list[1] = f'Protection {player.level2}'
                player.option_list[2] = f'Protection {player.level3}'
            elif player.enchanting_list[0][3] == 'Pickaxe' or player.enchanting_list[0][3] == 'Axe' or player.enchanting_list[0][3] == 'Shovel' or player.enchanting_list[0][3] == 'Hoe':  # Tools
                player.option_list[0] = f'Efficiency {player.level1}'
                player.option_list[1] = f'Efficiency {player.level2}'
                player.option_list[2] = f'Efficiency {player.level3}'
            for i in range(len(player.option_list)):
                if player.option_list[i] == 'Protection 0' or player.option_list[i] == 'Efficiency 0':
                    player.option_list[i] = 'N/A'
        else:
            player.option_list[0] = player.option_list[1] = player.option_list[2] = ''
    else:
        player.option_list[0] = player.option_list[1] = player.option_list[2] = ''


def Enchant1():  # First ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, no extras)
    global player
    if player.enchanting_list[1] is not None:
        if player.enchanting_list[1][1] > 0 and player.experience > 0:  # REQUIRE 1 Lapis + 1 Experience
            if player.option_list[0] != 'N/A' and player.enchanting_list[0] is not None:
                player.enchanting_list[0][4] = [[player.option_list[0][0:-2], int(player.option_list[0][-1])]]
                player.enchanting_list[1][1] -= 1
                player.experience -= 1
                EnchantSet()  # Remove Enchants


def Enchant2():  # Second ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2)
    global player
    if player.enchanting_list[1] is not None:
        if player.enchanting_list[1][1] > 1 and player.experience > 1:  # REQUIRE 2 Lapis + 2 Experience
            if player.option_list[1] != 'N/A' and player.enchanting_list[0] is not None:  # Test for None
                if player.optional_enchant2 is not None:  # Extra enchantment
                    if player.optional_enchant2 > 0:  # Enchantment level > 0
                        player.enchanting_list[0][4] = [[player.option_list[1][0:-2], int(player.option_list[1][-1])],
                                                 ['Unbreaking', player.optional_enchant2]]
                    else:  # No extra enchantment
                        player.enchanting_list[0][4] = [[player.option_list[1][0:-2], int(player.option_list[1][-1])]]
                else:
                    player.enchanting_list[0][4] = [[player.option_list[1][0:-2], int(player.option_list[1][-1])]]
                player.enchanting_list[1][1] -= 2
                player.experience -= 2
                EnchantSet()  # Remove Enchants


def Enchant3():  # Third ENCHANTING BOX (ENCHANTS start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3)
    global player
    if player.enchanting_list[1] is not None:
        if player.enchanting_list[1][1] > 2 and player.experience > 2:  # REQUIRE 3 Lapis + 3 Experience
            if player.option_list[2] != 'N/A' and player.enchanting_list[0] is not None:  # Test for None
                if player.optional_enchant3 is not None:  # Extra enchantment
                    if player.optional_enchant3 > 0:  # Enchantment level > 0
                        player.enchanting_list[0][4] = [[player.option_list[2][0:-2], int(player.option_list[2][-1])],
                                                 ['Unbreaking', player.optional_enchant3]]
                    else:  # No extra enchantment
                        player.enchanting_list[0][4] = [[player.option_list[2][0:-2], int(player.option_list[2][-1])]]
                else:  # No extra enchantment
                    player.enchanting_list[0][4] = [[player.option_list[2][0:-2], int(player.option_list[2][-1])]]
                player.enchanting_list[1][1] -= 3
                player.experience -= 3
                EnchantSet()  # Remove Enchants

# ADD ITEMS TO INVENTORY
def inventory_add(waiting_list):
    global base_index, additional_index, count, none_index, inventory_full
    inventory_full = True

    # TEST FOR FULL INVENTORY
    for i in player.inventory_list:
        if i is None:
            inventory_full = False
            break
    if inventory_full:
        screen.print("Your inventory is nearly full or is already full. New items added may be lost.")

    # Add items to inventory and combine into singular stacks (if stackable)
    for i in waiting_list:
        if i is not None:
            if i[2] == 64:
                Call = False
                for j in range(len(player.inventory_list)):
                    if player.inventory_list[j] is not None:
                        if i[0] == player.inventory_list[j][0] and player.inventory_list[j][1] < 64:
                            player.inventory_list[j] = [player.inventory_list[j][0], i[1] + player.inventory_list[j][1],
                                                 player.inventory_list[j][2], player.inventory_list[j][3],
                                                 player.inventory_list[j][4]]  # Add values
                            Call = True
                            break
                if not Call:
                    for j in range(len(player.inventory_list)):
                        if player.inventory_list[j] is None:
                            player.inventory_list[j] = i
                            break
            elif i[2] == 1:
                for j in range(len(player.inventory_list)):
                    if player.inventory_list[j] is None:
                        player.inventory_list[j] = i
                        break

    # Separate Items into stacks (Armour = Stack of 1), (Item = Stack of 64)
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i][2] == 1 and player.inventory_list[i][1] > 1:  # Armour
                count = 0
                while count < player.inventory_list[i][1]:  # Separate into individual items
                    if None in player.inventory_list:
                        none_index = player.inventory_list.index(None)
                        player.inventory_list[none_index] = [player.inventory_list[i][0], 1, player.inventory_list[i][2],
                                                      player.inventory_list[i][3], player.inventory_list[i][4]]
                    count += 1
                player.inventory_list[i] = None
            elif player.inventory_list[i][2] == 64 and player.inventory_list[i][1] > 64:  # Item
                while player.inventory_list[i][1] > 64:  # Separate into stacks of 64
                    player.inventory_list[i][1] -= 64
                    if None in player.inventory_list:
                        none_index = player.inventory_list.index(None)
                        player.inventory_list[none_index] = [player.inventory_list[i][0], 64, player.inventory_list[i][2],
                                                      player.inventory_list[i][3], player.inventory_list[i][4]]
                if None in player.inventory_list:  # Remainder (Less than 64)
                    none_index = player.inventory_list.index(None)
                    player.inventory_list[none_index] = [player.inventory_list[i][0], player.inventory_list[i][1], player.inventory_list[i][2],
                                                  player.inventory_list[i][3], player.inventory_list[i][4]]
                    player.inventory_list[i] = None

# Render Inventory List to Image and Number List
def image_render():
    global pygame_enchant_imgs, pygame_imgs, player, enchant_name_list, enchant_img_list, enchanting_list, enchanting_image_list, enchanting_number_list, experience, smelting_time, no_fire, fire, fuel_val, inventory_list, image_list, number_list, armour_image_list, craft_image_list, craft_number_list, item_name_list, grid_image_list, grid_number_list, grid_list, smelting_list, smelt_image_list, smelt_number_list, fuel_img
    player.image_list, player.number_list, player.armour_image_list, player.craft_image_list, \
    player.craft_number_list, player.grid_image_list, player.grid_number_list, player.smelt_image_list, \
    player.smelt_number_list, player.enchanting_image_list, player.enchanting_number_list, player.compressor_image_list, \
    player.compressor_number_list, player.layer_list = [], [], [], [], [], [], [], [], [], [], [], [], [], []

    '''Inventory Section'''

    # Remove Values with 0
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i][1] == 0:
                player.inventory_list[i] = None

    # Create images list and number list
    for i in player.inventory_list:
        if i is None:  # Set White Background for NONE Slots
            player.image_list.append(none_img)
            player.number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.image_list.append(pygame_imgs[item_index])
            player.number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i][1] == 1:
                player.number_list[i] = ''

    #Create Holding Item for Inventory
    if player.holding_item is None:
        player.holding_item_image = none_img
        player.holding_item_number = ''
    else:
        item_index = item_name_list.index(player.holding_item[0])
        player.holding_item_image = pygame_imgs[item_index]
        player.holding_item_number = str(player.holding_item[1])

    if player.holding_item is not None:
        if player.holding_item[1] == 1:
            player.holding_item_number = ''

    '''Armour Section'''

    # Create armour image list for armour slots
    for j in player.armour_list:
        if j is None:  # Set White Background for NONE Slots
            player.armour_image_list.append(none_img)
        else:
            item_index = item_name_list.index(j[0])
            player.armour_image_list.append(pygame_imgs[item_index])

    for i in player.armour_list:
        if i is not None:
            if i[0] == 'Tier 1 Iron Plate':
                player.layer_list.append([(200, 200, 200), 1])
            elif i[0] == 'Tier 2 Iron Plate':
                player.layer_list.append([(200, 200, 200), 2])
            elif i[0] == 'Tier 3 Iron Plate':
                player.layer_list.append([(200, 200, 200), 3])
            elif i[0] == 'Tier 1 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 1])
            elif i[0] == 'Tier 2 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 2])
            elif i[0] == 'Tier 3 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 3])
        else:
            player.layer_list.append(None)

    '''Crafting Section (2x2)'''

    for i in player.craft_list:
        if i is None:  # Set White Background for NONE Slots
            player.craft_image_list.append(none_img)
            player.craft_number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.craft_image_list.append(pygame_imgs[item_index])
            player.craft_number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for j in range(len(player.craft_list)):
        if player.craft_list[j] is not None:
            if player.craft_list[j][1] == 1:
                player.craft_number_list[j] = ''

    '''Crafting Section (3x3)'''

    for i in player.grid_list:
        if i is None:  # Set White Background for NONE Slots
            player.grid_image_list.append(none_img)
            player.grid_number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.grid_image_list.append(pygame_imgs[item_index])
            player.grid_number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for i in range(len(player.grid_list)):
        if player.grid_list[i] is not None:
            if player.grid_list[i][1] == 1:
                player.grid_number_list[i] = ''

    '''Smelting Section'''

    # Remove Value if Number is 0
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i][1] == 0:
                player.smelting_list[i] = None

    # Convert List to Images and Numbers
    for i in player.smelting_list:
        if i is None:  # Set White Background for NONE Slots
            player.smelt_image_list.append(none_img)
            player.smelt_number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.smelt_image_list.append(pygame_imgs[item_index])
            player.smelt_number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i][1] == 1:
                player.smelt_number_list[i] = ''

    '''Enchanting Section'''

    # Remove Value if Number is 0
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i][1] == 0:
                player.enchanting_list[i] = None

    # Convert List to Images and Numbers
    for i in player.enchanting_list:
        if i is None:  # Set White Background for NONE Slots
            player.enchanting_image_list.append(none_img)
            player.enchanting_number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.enchanting_image_list.append(pygame_imgs[item_index])
            player.enchanting_number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i][1] == 1:
                player.enchanting_number_list[i] = ''

    '''Compressing Section'''

    # Remove Value if Number is 0
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i][1] == 0:
                player.compressor_list[i] = None

    for i in player.compressor_list:
        if i is None: #Set Background for NONE Slots
            player.compressor_image_list.append(none_img)
            player.compressor_number_list.append('')
        else:
            item_index = item_name_list.index(i[0])
            player.compressor_image_list.append(pygame_imgs[item_index])
            player.compressor_number_list.append(str(i[1]))

    # Remove Value if Number is 1
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i][1] == 1:
                player.compressor_number_list[i] = ''
title_screen()