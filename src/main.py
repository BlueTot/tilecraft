import tkinter  # Tkinter module
import tkinter.font  # Fonts module
import random  # Random module
import pygame  # Pygame module
import time  # Time module
import math #Math module
import noise #Perlin Noise module
import os #OS module
import sys #SYS module

from constants import *

title_screen_mode = 'normal'


'''Cheats Datapack Section'''

#Print Item List
def print_cheats(name):
    global screen
    screen.print("CODE   ITEM NAME")
    screen.print('-' * 25)
    for i in range(len(name)):
        screen.print((str(i) + ' ' * (7 - len(str(i))) + str(name[i])))

#/give command
def give(item_id):
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
        length = len(list(ITEM_TYPES.keys())) - 1
        if 0 <= code <= length:
            add_item = Item(list(ITEM_TYPES.keys())[code], amount, None, list(ITEM_TYPES.values())[code].max_durability)
            return add_item
        else:
            screen.print(f"Please enter a number between 0 and {length}.")
            return None
    except ValueError:
        screen.print("Invalid Input")

#/teleport command
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

#/enchant command
def enchant(enchantment):
    global screen, player
    if player.hotbar_item is not None:
        enchantment = enchantment.replace(' ', '') #remove whitespaces
        if ',' in enchantment and enchantment[-1] != ',':
            comma = enchantment.index(',')
            name = enchantment[0:comma]
            lvl = enchantment[comma + 1:len(enchantment)]
            try:
                lvl = int(lvl)
                if name == "protection" or name == "efficiency" or name == "unbreaking":
                    enchantments = player.hotbar_item.enchantments
                    if enchantments is not None:
                        enchantments.append([name.capitalize(), lvl])
                    else:
                        enchantments = [[name.capitalize(), lvl]]
                    return Item(player.hotbar_item.name, player.hotbar_item.number, enchantments, player.hotbar_item.durability)
            except ValueError:
                screen.print("Invalid Input")
    else:
        screen.print("No item in selected hotbar slot")
    return None

#/experience command
def experience(level):
    global player, screen
    try:
        level = int(level)
        if level > 0:
            player.experience_points += level
    except ValueError:
        screen.print("Invalid Input")

'''Advancements Section'''

#Check for completed advancements
def advancements_update(advancements, inventory_list, armour_list, dimension):
    global screen, TimerRunning
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
        TimerRunning = False

    return advancements

def MusicPlayer(advancements):
    global screen, speedrun_timer, TimerRunning
    if "Music Player" not in advancements:  # Music Player: Play Pigstep
        advancements.append("Music Player")
        screen.print("Advancement unlocked: Music Player")
        TimerRunning = False

        return advancements

def SpeedrunTimer(display, PlayTime): #Speedrun Timer Function
    global speedrun_time, TimerRunning
    font = pygame.font.Font('assets/monofur/monof55.ttf', 25)
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

class Tile:
    def __init__(self, tile, x, y):
        self.tile = tile
        self.x = x
        self.y = y
        self.breaking_time = TILE_TYPES[self.tile].breaking_time
        self.requireTool = TILE_TYPES[self.tile].tool
        self.requireToolTier = TILE_TYPES[self.tile].tier

class Chunk:
    def __init__(self, x, y, biome):
        self.x = x
        self.y = y
        self.biome = biome

def RandomPos(Seed, Pos, Range):
    x, y = Pos
    a, b = Range
    random.seed((Seed % 2048) * 2 - 5)
    for i in range(x % 50):
        for j in range(y % 50 - 1):
            value = RandomNum(a, b)
    value = RandomNum(a, b)
    return value

def RandomNum(start, stop):
    global n
    n = (n * 63) % 3301667478 #multiplication and modulo
    n = n ^ 24465343 #XOR
    n = (n * 255) % 4294967296 #multiplication and modulo
    n = n ^ 573522635 #XOR
    n = n | 78187493520 #OR
    n = ((n + 14351514) * 32) % 7777333 #addition, multplication, modulo
    return n % (stop - 1) + start

def OverworldGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list


def OverworldGenerate(ChunkX, ChunkY, villages, ruined_portals, obsidian_counts,
                      generated_list, bound_village, bound_village2, bound_village3, bound_village4,
                      bound_ruined_portal, bound_ruined_portal2, seed, UnderTiles, Tiles):

    num = RandomPos(seed, (ChunkX, ChunkY), (1, 25))
    if num == 1 or num == 2:
        villages.append([ChunkX - 12, ChunkY - 12])  # Village
        bound_village.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 1
        bound_village2.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 2
        bound_village3.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 3
        bound_village4.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 4
    elif num == 15 or num == 16 or num == 17:
        ruined_portals.append([ChunkX - 1, ChunkY - 1])  # Ruined Portal
        obsidian_counts.append(int(RandomPos(seed, (ChunkX, ChunkY), (5, 10))))  # Obsidian remaining in ruined portal
        bound_ruined_portal.append([[ChunkX - 1 - 10 / 32, ChunkX - 1, ChunkX - 1 + 10 / 32], [ChunkY - 1 - 10 / 32, ChunkY - 1, ChunkY - 1 + 10 / 32]])  # Bounding box for ruined portal 1
        bound_ruined_portal2.append([[ChunkX - 1 - 10 / 32, ChunkX - 1, ChunkX - 1 + 10 / 32], [ChunkY - 1 - 10 / 32, ChunkY - 1, ChunkY - 1 + 10 / 32]])  # Bounding box for ruined portal 2
    generated_list.append([ChunkX, ChunkY])  # Chunk is now generated and cannot generate again
    for i in range(ChunkX, ChunkX + 16, 1):
        for j in range(ChunkY, ChunkY + 16, 1):
            land = noise.pnoise2(i / 400,
                                 j / 400,
                                 octaves=8,
                                 persistence=1 / 2,
                                 lacunarity=1 / 2,
                                 repeatx=1024,
                                 repeaty=1024,
                                 base=seed % 256)  # Perlin Noise Generation
            temperature = noise.pnoise2(i / 400,
                                        j / 400,
                                        octaves=8,
                                        persistence=1 / 2,
                                        lacunarity=1 / 2,
                                        repeatx=1024,
                                        repeaty=1024,
                                        base=(seed ** 2) % 256)  # Perlin Noise Generation
            try:
                temp = UnderTiles[(i, j)].tile
            except KeyError:
                if land >= -0.075:
                    if temperature < -0.1:
                        UnderTiles[(i, j)] = Tile('Snow', i, j)
                    elif -0.1 <= temperature <= 0.1:
                        UnderTiles[(i, j)] = Tile('Grass', i, j)
                    elif temperature > 0.1:
                        UnderTiles[(i, j)] = Tile('Sand', i, j)
                else:
                    UnderTiles[(i, j)] = Tile('Water', i, j)
            try:
                temp = Tiles[(i, j)].tile
            except KeyError:
                Tiles[(i, j)] = Tile('Air', i, j)
    for i in range(ChunkX, ChunkX + 16, 4):
        for j in range(ChunkY, ChunkY + 16, 4):
            x = i + RandomPos(seed, (i, j), (1, 4))
            y = j + RandomPos(seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and RandomPos(seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 16)) == 5:
                canGenerateBoulder = True
            if canGenerateTree:
                for X in range(-1, 2, 1):
                    for Y in range(-1, 2, 1):
                        if not (X == 0 and Y == 0):
                            Tiles[(x + X, y + Y)] = Tile("Leaf", x + X, y + Y)
                        else:
                            Tiles[(x + X, y + Y)] = Tile("Tree", x, y)
            elif canGenerateBoulder:
                for X in range(4):
                    for Y in range(4):
                        if not (X == 0 and Y == 0 or X == 3 and Y == 0 or X == 0 and Y == 3 or X == 3 and Y == 3):
                            Tiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)
    for i in range(ChunkX, ChunkX + 16, 8):
        for j in range(ChunkY, ChunkY + 16, 8):
            x = i + RandomPos(seed, (i, j), (1, 8))
            y = j + RandomPos(seed, (i, j), (1, 8))
            canGenerateWaterPool = False
            canGenerateLavaPool = False
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 32)) == 10:
                canGenerateWaterPool = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 32)) == 30:
                canGenerateLavaPool = True
            if canGenerateWaterPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Water", x + X, y + Y)
                        else:
                            if RandomPos(seed, (x + X, y + Y), (1, 3)) == 1:
                                UnderTiles[(x + X, y + Y)] = Tile("Sand", x + X, y + Y)
                            else:
                                UnderTiles[(x + X, y + Y)] = Tile("Gravel", x + X, y + Y)
                for X in range(-2, 10):
                    for Y in range(-2, 10):
                        if (X < 0 or X > 7) or (Y < 0 or Y > 7):
                            if not (
                                    X == -2 and Y == -2 or X == -2 and Y == -1 or X == -1 and Y == -2 or X == 9 and Y == -2 or \
                                    X == 8 and Y == -2 or X == 9 and Y == -1 or X == -2 and Y == 8 or X == -2 and Y == 9 or \
                                    X == -1 and Y == 9 or X == 9 and Y == 9 or X == 8 and Y == 9 or X == 9 and Y == 8):
                                if RandomPos(seed, (x + X, y + Y), (1, 3)) == 1:
                                    UnderTiles[(x + X, y + Y)] = Tile("Sand", x + X, y + Y)
                                else:
                                    UnderTiles[(x + X, y + Y)] = Tile("Gravel", x + X, y + Y)
            if canGenerateLavaPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Lava", x + X, y + Y)
                        else:
                            UnderTiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)
                for X in range(-2, 10):
                    for Y in range(-2, 10):
                        if (X < 0 or X > 7) or (Y < 0 or Y > 7):
                            if not (
                                    X == -2 and Y == -2 or X == -2 and Y == -1 or X == -1 and Y == -2 or X == 9 and Y == -2 or \
                                    X == 8 and Y == -2 or X == 9 and Y == -1 or X == -2 and Y == 8 or X == -2 and Y == 9 or \
                                    X == -1 and Y == 9 or X == 9 and Y == 9 or X == 8 and Y == 9 or X == 9 and Y == 8):
                                UnderTiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)

    return villages, ruined_portals, obsidian_counts, generated_list, \
           bound_village, bound_village2, bound_village3, bound_village4, \
           bound_ruined_portal, bound_ruined_portal2, UnderTiles, Tiles


def SpawnOverworldGenerate(seed):
    li_vil = []
    li_ruined_portal = []
    villages = []
    ruined_portals = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = RandomPos(seed, (i, j), (1, 25))
            if num == 1 or num == 2:
                li_vil.append([i, j])
            elif num == 15 or num == 16 or num == 17:
                li_ruined_portal.append([i, j])

    # Village (Chunk Code: 4, 4)
    for i in li_vil:
        villages.append([i[0] - 12, i[1] - 12])

    # Ruined Portal (Chunk Code: 15, 15)
    for i in li_ruined_portal:
        ruined_portals.append([i[0] - 1, i[1] - 1])
    obsidian_counts = []
    for i in range(len(ruined_portals)):
        obsidian_counts.append(int(RandomPos(seed, (ruined_portals[i][0] + 1, ruined_portals[i][1] + 1), (5, 10))))

    #Generate Biomes for Spawn Chunks
    UnderTiles = {}
    Tiles = {}
    for i in range(-64, 81, 1):  # Spawn Chunks (-64 --> 64 x and y)
        for j in range(-64, 81, 1):
            land = noise.pnoise2(i / 400,
                                 j / 400,
                                 octaves=8,
                                 persistence=1 / 2,
                                 lacunarity=1 / 2,
                                 repeatx=1024,
                                 repeaty=1024,
                                 base=seed % 256)  # Perlin Noise Generation
            temperature = noise.pnoise2(i / 400,
                                        j / 400,
                                        octaves=8,
                                        persistence=1 / 2,
                                        lacunarity=1 / 2,
                                        repeatx=1024,
                                        repeaty=1024,
                                        base=(seed ** 2) % 256)  # Perlin Noise Generation
            try:
                temp = UnderTiles[(i, j)].tile
            except KeyError:
                if land >= -0.075:
                    if temperature < -0.1:
                        UnderTiles[(i, j)] = Tile('Snow', i, j)
                    elif -0.1 <= temperature <= 0.1:
                        UnderTiles[(i, j)] = Tile('Grass', i, j)
                    elif temperature > 0.1:
                        UnderTiles[(i, j)] = Tile('Sand', i, j)
                else:
                    UnderTiles[(i, j)] = Tile('Water', i, j)
            try:
                temp = Tiles[(i, j)].tile
            except KeyError:
                Tiles[(i, j)] = Tile('Air', i, j)
    for i in range(-64, 81, 4):
        for j in range(-64, 81, 4):
            x = i + RandomPos(seed, (i, j), (1, 4))
            y = j + RandomPos(seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and RandomPos(seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 16)) == 5:
                canGenerateBoulder = True
            if canGenerateTree:
                for X in range(-1, 2, 1):
                    for Y in range(-1, 2, 1):
                        if not(X == 0 and Y == 0):
                            Tiles[(x + X, y + Y)] = Tile("Leaf", x + X, y + Y)
                        else:
                            Tiles[(x + X, y + Y)] = Tile("Tree", x, y)
            elif canGenerateBoulder:
                for X in range(4):
                    for Y in range(4):
                        if not (X == 0 and Y == 0 or X == 3 and Y == 0 or X == 0 and Y == 3 or X == 3 and Y == 3):
                            Tiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)
    for i in range(-64, 81, 8):
        for j in range(-64, 81, 8):
            x = i + RandomPos(seed, (i, j), (1, 8))
            y = j + RandomPos(seed, (i, j), (1, 8))
            canGenerateWaterPool = False
            canGenerateLavaPool = False
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 32)) == 10:
                canGenerateWaterPool = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(seed, (x, y), (1, 32)) == 30:
                canGenerateLavaPool = True
            if canGenerateWaterPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Water", x + X, y + Y)
                        else:
                            if RandomPos(seed, (x + X, y + Y), (1, 3)) == 1:
                                UnderTiles[(x + X, y + Y)] = Tile("Sand", x + X, y + Y)
                            else:
                                UnderTiles[(x + X, y + Y)] = Tile("Gravel", x + X, y + Y)
                for X in range(-2, 10):
                    for Y in range(-2, 10):
                        if (X < 0 or X > 7) or (Y < 0 or Y > 7):
                            if not (
                                    X == -2 and Y == -2 or X == -2 and Y == -1 or X == -1 and Y == -2 or X == 9 and Y == -2 or \
                                    X == 8 and Y == -2 or X == 9 and Y == -1 or X == -2 and Y == 8 or X == -2 and Y == 9 or \
                                    X == -1 and Y == 9 or X == 9 and Y == 9 or X == 8 and Y == 9 or X == 9 and Y == 8):
                                if RandomPos(seed, (x + X, y + Y), (1, 3)) == 1:
                                    UnderTiles[(x + X, y + Y)] = Tile("Sand", x + X, y + Y)
                                else:
                                    UnderTiles[(x + X, y + Y)] = Tile("Gravel", x + X, y + Y)
            if canGenerateLavaPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Lava", x + X, y + Y)
                        else:
                            UnderTiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)
                for X in range(-2, 10):
                    for Y in range(-2, 10):
                        if (X < 0 or X > 7) or (Y < 0 or Y > 7):
                            if not (
                                    X == -2 and Y == -2 or X == -2 and Y == -1 or X == -1 and Y == -2 or X == 9 and Y == -2 or \
                                    X == 8 and Y == -2 or X == 9 and Y == -1 or X == -2 and Y == 8 or X == -2 and Y == 9 or \
                                    X == -1 and Y == 9 or X == 9 and Y == 9 or X == 8 and Y == 9 or X == 9 and Y == 8):
                                UnderTiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y)

    return villages, ruined_portals, obsidian_counts, UnderTiles, Tiles

def SpawnOverworldBoundGenerate(villages, ruined_portals):
    bound_village, bound_ruined_portal = [], []
    for i in range(len(villages)):
        bound_village.append([])
        for j in range(2):
            bound_village[i].append([villages[i][j] - 10 / 32, villages[i][j], villages[i][j] + 10 / 32])
    for i in range(len(ruined_portals)):
        bound_ruined_portal.append([])
        for j in range(2):
            bound_ruined_portal[i].append([ruined_portals[i][j] - 10 / 32, ruined_portals[i][j], ruined_portals[i][j] + 10 / 32])
    return bound_village, bound_ruined_portal

def GenerateOres(ore, vein_size, Tiles, x, y):
    if vein_size == 1:
        Tiles[(x, y)] = Tile(ore, x, y)
    elif vein_size == 2:
        Tiles[(x, y)] = Tile(ore, x, y)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y)
    elif vein_size == 3:
        Tiles[(x, y)] = Tile(ore, x, y)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y)
        Tiles[(x, y + 1)] = Tile(ore, x, y + 1)
    elif vein_size == 4:
        Tiles[(x, y)] = Tile(ore, x, y)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y)
        Tiles[(x, y + 1)] = Tile(ore, x, y + 1)
        Tiles[(x + 1, y + 1)] = Tile(ore, x + 1, y + 1)
    return Tiles

def UndergroundGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list

def SpawnUndergroundGenerate(seed):
    UnderTiles = {}
    Tiles = {}
    for i in range(-64, 81, 8):
        for j in range(-64, 81, 8):
            biome = noise.pnoise2(i / 50,
                          j / 50,
                          octaves=8,
                          persistence=1 / 2,
                          lacunarity=1 / 2,
                          repeatx=1024,
                          repeaty=1024,
                          base=seed % 600)
            for x in range(8):
                for y in range(8):
                    Tiles[(i + x, j + y)] = Tile("Stone", i + x, j + y)
                    UnderTiles[(i + x, j + y)] = Tile("Stone", i + x, j + y)
            if biome < 0:
                num = RandomPos(seed, (i, j), (1, 9))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
            else:
                num = RandomPos(seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
    for i in range(-64, 81, 1):
        for j in range(-64, 81, 1):
            cave = noise.pnoise2(i / 10,
                                  j / 10,
                                  octaves=8,
                                  persistence=1 / 2,
                                  lacunarity=1 / 2,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed % 400 * 2)
            if cave > 0.075:
                Tiles[(i, j)] = Tile("Air", i, j)
                biome = noise.pnoise2(i / 50,
                                      j / 50,
                                      octaves=8,
                                      persistence=1 / 2,
                                      lacunarity=1 / 2,
                                      repeatx=1024,
                                      repeaty=1024,
                                      base=seed % 600)
                if biome < 0:
                    UnderTiles[(i, j)] = Tile("Lava", i, j)
    return UnderTiles, Tiles

def UndergroundGenerate(seed, ChunkX, ChunkY, UnderTiles, Tiles, UndergroundGeneratedList):
    for i in range(ChunkX, ChunkX + 16, 8):
        for j in range(ChunkY, ChunkY + 16, 8):
            biome = noise.pnoise2(i / 50,
                                  j / 50,
                                  octaves=8,
                                  persistence=1 / 2,
                                  lacunarity=1 / 2,
                                  repeatx=1024,
                                  repeaty=1024,
                                  base=seed % 600)
            for x in range(8):
                for y in range(8):
                    Tiles[(i + x, j + y)] = Tile("Stone", i + x, j + y)
                    UnderTiles[(i + x, j + y)] = Tile("Stone", i + x, j + y)
            if biome < 0:
                num = RandomPos(seed, (i, j), (1, 12))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
            else:
                num = RandomPos(seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(seed, (i, j), (1, 8)), j + RandomPos(seed, (i, j), (1, 8)))
    for i in range(ChunkX, ChunkX + 16, 1):
        for j in range(ChunkY, ChunkY + 16, 1):
            cave = noise.pnoise2(i / 10,
                                 j / 10,
                                 octaves=8,
                                 persistence=1 / 2,
                                 lacunarity=1 / 2,
                                 repeatx=1024,
                                 repeaty=1024,
                                 base=seed % 400 * 2)
            if cave > 0.075:
                Tiles[(i, j)] = Tile("Air", i, j)
                biome = noise.pnoise2(i / 50,
                                      j / 50,
                                      octaves=8,
                                      persistence=1 / 2,
                                      lacunarity=1 / 2,
                                      repeatx=1024,
                                      repeaty=1024,
                                      base=seed % 600)
                if biome < 0:
                    UnderTiles[(i, j)] = Tile("Lava", i, j)
    UndergroundGeneratedList.append([ChunkX, ChunkY])
    return UnderTiles, Tiles

def UndergroundGeneratePortal(x, y, Tiles):
    Tiles[(x, y)] = Tile("Mine Entrance", x, y)
    for i in range(x - 1, x + 2, 1):
        for j in range(y - 1, y + 2, 1):
            if Tiles[(i, j)].tile != "Mine Entrance":
                Tiles[(i, j)] = Tile("Air", i, j)
    return Tiles

def OverworldGeneratePortal(x, y, Tiles):
    Tiles[(x, y)] = Tile("Mine Entrance", x, y)
    for i in range(x - 1, x + 2, 1):
        for j in range(y - 1, y + 2, 1):
            if Tiles[(i, j)].tile != "Mine Entrance":
                Tiles[(i, j)] = Tile("Air", i, j)
    return Tiles

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
            num = RandomPos(seed, (i, j), (1, 15))
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
            bound_bastion[i].append([bastions[i][j] - 10 / 32, bastions[i][j], bastions[i][j] + 10 / 32])
    for i in range(len(fortresses)):
        bound_fortress.append([])
        for j in range(2):
            bound_fortress[i].append([fortresses[i][j] - 10 / 32, fortresses[i][j], fortresses[i][j] + 10 / 32])
    return bound_bastion, bound_fortress

def NetherGenerate(ChunkX, ChunkY, bastions, fortresses, generated_list, bound_bastion, seed):
    num = RandomPos(seed, (ChunkX, ChunkY), (1, 15))
    if num == 1 or num == 2 or num == 3:
        bastions.append([ChunkX - 6, ChunkY - 6])  # Bastion
        bound_bastion.append([[ChunkX - 6 - 10 / 32, ChunkX - 6, ChunkX - 6 + 10 / 32], [ChunkY - 6 - 10 / 32, ChunkY - 6, ChunkY - 6 + 10 / 32]])  # Bounding box
    elif num == 4 or num == 5 or num == 6:
        fortresses.append([ChunkX - 10, ChunkY - 10])  # Fortress
    generated_list.append([ChunkX, ChunkY])  # Chunk is now generated and cannot generate again

    return bastions, fortresses, generated_list, bound_bastion

'''Main Part of Game Code'''

class TilecraftWorld:
    def __init__(self, seed):
        global n
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
        n = seed #Random number seed
        self.undergroundGenerated = False

        self.village, self.ruined_portal, self.obsidian_counts, \
        self.UnderTiles, self.Tiles = SpawnOverworldGenerate(self.seed)  # Spawn Generation for Structures and Biomes
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
                    OverworldGenerate(i[0], i[1], self.village, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4,
                                                      self.bound_ruined_portal, self.bound_ruined_portal2, self.seed, self.UnderTiles, self.Tiles)
        elif player.dimension == "Underground":
            if not self.undergroundGenerated:
                hasGeneratedUnderground = 'Generating'
            if hasGeneratedUnderground == "Generated":
                for i in self.render_list:
                    if i not in self.UndergroundGeneratedList:
                        self.UndergroundUnderTiles, self.UndergroundTiles = UndergroundGenerate(self.seed, i[0], i[1], self.UndergroundUnderTiles, self.UndergroundTiles, self.UndergroundGeneratedList)
        elif player.dimension == 'Nether':
            for i in self.render_list:
                if i not in self.nether_generated_list:
                    self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion = NetherGenerate(i[0], i[1], self.bastion, self.fortress, self.nether_generated_list, self.bound_bastion, self.seed)

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
        self.UndergroundUnderTiles, self.UndergroundTiles = SpawnUndergroundGenerate(self.seed)
        self.UndergroundGeneratedList = UndergroundGeneratedList()

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

    def render(self, display, context: Context):
        global netherrack_tile, hotbar_imgs, slot, number_list, experience, pygame_enchant_imgs, enchant_name_list, player, hasGeneratedUnderground, bedrock_tile
        player.health_hunger_update()

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
        self.font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', size)
        self.text = self.font.render(text, False, (0, 0, 0))
        pygame.draw.rect(display, self.colour, self.rect)
        pygame.draw.rect(display, (255, 255, 255), self.rect, 3)
        self.text_x = (self.length - len(text) * size) // 2
        if self.text_x < 0:
            self.text_x = 0
        self.text_y = (self.width - size) // 2
        display.blit(self.text, (self.x + self.text_x, self.y + self.text_y))

def DurabilityBar(durability, max_durability):
    durabilityPercent = math.floor((durability / max_durability) * 100)
    if durabilityPercent == 100:
        return None
    elif 75 < durabilityPercent <= 99:
        return "#00ff00"
    elif 50 < durabilityPercent <= 75:
        return "#ffff00"
    elif 25 < durabilityPercent <= 50:
        return "#ff8000"
    elif 5 < durabilityPercent <= 25:
        return "#ff0000"
    elif 0 < durabilityPercent <= 5:
        return "#000000"

def RenderDurabilityBar(display, x, y, durability, max_durability):
    colour = DurabilityBar(durability, max_durability)
    if colour is not None:
        pygame.draw.rect(display, (0, 0, 0), (x + 5, y + 72, 72, 5))
        pygame.draw.rect(display, colour, (x + 5, y + 72, math.floor(72 * durability / max_durability), 5))

#Inventory Grid (36 Slots)
def InventoryGrid(context: Context, display):
    image_render(context)
    inventory_slots = [
        Grid((83, 83, 83), pygame.Rect((0, 390), (82, 82)), 2, player.image_list[0]),
        Grid((83, 83, 83), pygame.Rect((82, 390), (82, 82)), 2, player.image_list[1]),
        Grid((83, 83, 83), pygame.Rect((164, 390), (82, 82)), 2, player.image_list[2]),
        Grid((83, 83, 83), pygame.Rect((246, 390), (82, 82)), 2, player.image_list[3]),
        Grid((83, 83, 83), pygame.Rect((328, 390), (82, 82)), 2, player.image_list[4]),
        Grid((83, 83, 83), pygame.Rect((410, 390), (82, 82)), 2, player.image_list[5]),
        Grid((83, 83, 83), pygame.Rect((492, 390), (82, 82)), 2, player.image_list[6]),
        Grid((83, 83, 83), pygame.Rect((574, 390), (82, 82)), 2, player.image_list[7]),
        Grid((83, 83, 83), pygame.Rect((656, 390), (82, 82)), 2, player.image_list[8]),
        Grid((83, 83, 83), pygame.Rect((0, 472), (82, 82)), 2, player.image_list[9]),
        Grid((83, 83, 83), pygame.Rect((82, 472), (82, 82)), 2, player.image_list[10]),
        Grid((83, 83, 83), pygame.Rect((164, 472), (82, 82)), 2, player.image_list[11]),
        Grid((83, 83, 83), pygame.Rect((246, 472), (82, 82)), 2, player.image_list[12]),
        Grid((83, 83, 83), pygame.Rect((328, 472), (82, 82)), 2, player.image_list[13]),
        Grid((83, 83, 83), pygame.Rect((410, 472), (82, 82)), 2, player.image_list[14]),
        Grid((83, 83, 83), pygame.Rect((492, 472), (82, 82)), 2, player.image_list[15]),
        Grid((83, 83, 83), pygame.Rect((574, 472), (82, 82)), 2, player.image_list[16]),
        Grid((83, 83, 83), pygame.Rect((656, 472), (82, 82)), 2, player.image_list[17]),
        Grid((83, 83, 83), pygame.Rect((0, 554), (82, 82)), 2, player.image_list[18]),
        Grid((83, 83, 83), pygame.Rect((82, 554), (82, 82)), 2, player.image_list[19]),
        Grid((83, 83, 83), pygame.Rect((164, 554), (82, 82)), 2, player.image_list[20]),
        Grid((83, 83, 83), pygame.Rect((246, 554), (82, 82)), 2, player.image_list[21]),
        Grid((83, 83, 83), pygame.Rect((328, 554), (82, 82)), 2, player.image_list[22]),
        Grid((83, 83, 83), pygame.Rect((410, 554), (82, 82)), 2, player.image_list[23]),
        Grid((83, 83, 83), pygame.Rect((492, 554), (82, 82)), 2, player.image_list[24]),
        Grid((83, 83, 83), pygame.Rect((574, 554), (82, 82)), 2, player.image_list[25]),
        Grid((83, 83, 83), pygame.Rect((656, 554), (82, 82)), 2, player.image_list[26]),
        Grid((83, 83, 83), pygame.Rect((0, 636), (82, 82)), 2, player.image_list[27]),
        Grid((83, 83, 83), pygame.Rect((82, 636), (82, 82)), 2, player.image_list[28]),
        Grid((83, 83, 83), pygame.Rect((164, 636), (82, 82)), 2, player.image_list[29]),
        Grid((83, 83, 83), pygame.Rect((246, 636), (82, 82)), 2, player.image_list[30]),
        Grid((83, 83, 83), pygame.Rect((328, 636), (82, 82)), 2, player.image_list[31]),
        Grid((83, 83, 83), pygame.Rect((410, 636), (82, 82)), 2, player.image_list[32]),
        Grid((83, 83, 83), pygame.Rect((492, 636), (82, 82)), 2, player.image_list[33]),
        Grid((83, 83, 83), pygame.Rect((574, 636), (82, 82)), 2, player.image_list[34]),
        Grid((83, 83, 83), pygame.Rect((656, 636), (82, 82)), 2, player.image_list[35])
    ]

    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    numbers = [
        Text(font.render(player.number_list[0], False, (255, 255, 255)), 52, 442),
        Text(font.render(player.number_list[1], False, (255, 255, 255)), 134, 442),
        Text(font.render(player.number_list[2], False, (255, 255, 255)), 216, 442),
        Text(font.render(player.number_list[3], False, (255, 255, 255)), 298, 442),
        Text(font.render(player.number_list[4], False, (255, 255, 255)), 380, 442),
        Text(font.render(player.number_list[5], False, (255, 255, 255)), 462, 442),
        Text(font.render(player.number_list[6], False, (255, 255, 255)), 544, 442),
        Text(font.render(player.number_list[7], False, (255, 255, 255)), 626, 442),
        Text(font.render(player.number_list[8], False, (255, 255, 255)), 708, 442),
        Text(font.render(player.number_list[9], False, (255, 255, 255)), 52, 524),
        Text(font.render(player.number_list[10], False, (255, 255, 255)), 134, 524),
        Text(font.render(player.number_list[11], False, (255, 255, 255)), 216, 524),
        Text(font.render(player.number_list[12], False, (255, 255, 255)), 298, 524),
        Text(font.render(player.number_list[13], False, (255, 255, 255)), 380, 524),
        Text(font.render(player.number_list[14], False, (255, 255, 255)), 462, 524),
        Text(font.render(player.number_list[15], False, (255, 255, 255)), 544, 524),
        Text(font.render(player.number_list[16], False, (255, 255, 255)), 626, 524),
        Text(font.render(player.number_list[17], False, (255, 255, 255)), 708, 524),
        Text(font.render(player.number_list[18], False, (255, 255, 255)), 52, 606),
        Text(font.render(player.number_list[19], False, (255, 255, 255)), 134, 606),
        Text(font.render(player.number_list[20], False, (255, 255, 255)), 216, 606),
        Text(font.render(player.number_list[21], False, (255, 255, 255)), 298, 606),
        Text(font.render(player.number_list[22], False, (255, 255, 255)), 380, 606),
        Text(font.render(player.number_list[23], False, (255, 255, 255)), 462, 606),
        Text(font.render(player.number_list[24], False, (255, 255, 255)), 544, 606),
        Text(font.render(player.number_list[25], False, (255, 255, 255)), 626, 606),
        Text(font.render(player.number_list[26], False, (255, 255, 255)), 708, 606),
        Text(font.render(player.number_list[27], False, (255, 255, 255)), 52, 688),
        Text(font.render(player.number_list[28], False, (255, 255, 255)), 134, 688),
        Text(font.render(player.number_list[29], False, (255, 255, 255)), 216, 688),
        Text(font.render(player.number_list[30], False, (255, 255, 255)), 298, 688),
        Text(font.render(player.number_list[31], False, (255, 255, 255)), 380, 688),
        Text(font.render(player.number_list[32], False, (255, 255, 255)), 462, 688),
        Text(font.render(player.number_list[33], False, (255, 255, 255)), 544, 688),
        Text(font.render(player.number_list[34], False, (255, 255, 255)), 626, 688),
        Text(font.render(player.number_list[35], False, (255, 255, 255)), 708, 688)
    ]
    for i in range(len(inventory_slots)):
        display.blit(inventory_slots[i].img, (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
        pygame.draw.rect(display, inventory_slots[i].colour, inventory_slots[i].rect, inventory_slots[i].width)
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.inventory_list[i].name], (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
            if player.inventory_list[i].durability is not None:
                RenderDurabilityBar(display, inventory_slots[i].rect.x, inventory_slots[i].rect.y, player.inventory_list[i].durability, player.inventory_list[i].max_durability)
    for i in numbers:
        display.blit(i.surface, (i.x, i.y))

#Armour Grid for Player
def ArmourGrid(context: Context, display):
    image_render(context)
    armour_grid = [
        Grid((83, 83, 83), pygame.Rect((0, 240), (82, 82)), 2, player.armour_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((82, 240), (82, 82)), 2, player.armour_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((164, 240), (82, 82)), 2, player.armour_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((246, 240), (82, 82)), 2, player.armour_image_list[3]),
    ]
    for i in range(len(armour_grid)):
        display.blit(armour_grid[i].img, (armour_grid[i].rect.x, armour_grid[i].rect.y))
        pygame.draw.rect(display, armour_grid[i].colour, armour_grid[i].rect, armour_grid[i].width)
        if player.armour_list[i] is not None:
            if player.armour_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.armour_list[i].name], (armour_grid[i].rect.x, armour_grid[i].rect.y))
            if player.armour_list[i].durability is not None:
                RenderDurabilityBar(display, armour_grid[i].rect.x, armour_grid[i].rect.y, player.armour_list[i].durability, player.armour_list[i].max_durability)
    pygame.draw.rect(display, (0, 0, 0), (0, 0, 330, 240)) #Draw Black Background
    pygame.draw.rect(display, (255, 0, 0), (127, 82, 75, 75)) #Draw Player Icon
    for i in player.layer_list: #Draw Armour Layers
        if i is not None:
            if i[1] == 1: #Tier 1
                pygame.draw.rect(display, i[0], (112, 67, 105, 105), 12)
            elif i[1] == 2: #Tier 2
                pygame.draw.rect(display, i[0], (99, 54, 133, 133), 12)
            elif i[1] == 3: #Tier 3
                pygame.draw.rect(display, i[0], (84, 39, 165, 165), 12)

#2x2 Small Crafting Grid within Inventory
def SmallCraftGrid(context: Context, display):
    image_render(context)
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((390, 75), (82, 82)), 2, player.craft_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((472, 75), (82, 82)), 2, player.craft_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((390, 157), (82, 82)), 2, player.craft_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((472, 157), (82, 82)), 2, player.craft_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((637, 117), (82, 82)), 2, player.craft_image_list[4]),
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    arrow_font = pygame.font.Font('assets/minecraft-font/MinecraftBold-nMK1.otf', 36)
    crafting_numbers = [
        Text(font.render(player.craft_number_list[0], False, (255, 255, 255)), 442, 127),
        Text(font.render(player.craft_number_list[1], False, (255, 255, 255)), 525, 127),
        Text(font.render(player.craft_number_list[2], False, (255, 255, 255)), 442, 210),
        Text(font.render(player.craft_number_list[3], False, (255, 255, 255)), 525, 210),
        Text(font.render(player.craft_number_list[4], False, (255, 255, 255)), 690, 169),
    ]

    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.craft_list[i] is not None:
            if player.craft_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.craft_list[i].name], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
            if player.craft_list[i].durability is not None:
                RenderDurabilityBar(display, crafting_grid[i].rect.x, crafting_grid[i].rect.y, player.craft_list[i].durability, player.craft_list[i].max_durability)
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (562, 142))

def CraftGrid(context: Context, display):
    image_render(context)
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((195, 75), (82, 82)), 2, player.grid_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((277, 75), (82, 82)), 2, player.grid_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((359, 75), (82, 82)), 2, player.grid_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((195, 157), (82, 82)), 2, player.grid_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((277, 157), (82, 82)), 2, player.grid_image_list[4]),
        Grid((83, 83, 83), pygame.Rect((359, 157), (82, 82)), 2, player.grid_image_list[5]),
        Grid((83, 83, 83), pygame.Rect((195, 239), (82, 82)), 2, player.grid_image_list[6]),
        Grid((83, 83, 83), pygame.Rect((277, 239), (82, 82)), 2, player.grid_image_list[7]),
        Grid((83, 83, 83), pygame.Rect((359, 239), (82, 82)), 2, player.grid_image_list[8]),
        Grid((83, 83, 83), pygame.Rect((570, 157), (82, 82)), 2, player.grid_image_list[9])
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    title_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 40)
    arrow_font = pygame.font.Font('assets/minecraft-font/MinecraftBold-nMK1.otf', 40)
    crafting_numbers = [
        Text(font.render(player.grid_number_list[0], False, (255, 255, 255)), 247, 127),
        Text(font.render(player.grid_number_list[1], False, (255, 255, 255)), 329, 127),
        Text(font.render(player.grid_number_list[2], False, (255, 255, 255)), 411, 127),
        Text(font.render(player.grid_number_list[3], False, (255, 255, 255)), 247, 209),
        Text(font.render(player.grid_number_list[4], False, (255, 255, 255)), 329, 209),
        Text(font.render(player.grid_number_list[5], False, (255, 255, 255)), 411, 209),
        Text(font.render(player.grid_number_list[6], False, (255, 255, 255)), 247, 291),
        Text(font.render(player.grid_number_list[7], False, (255, 255, 255)), 329, 291),
        Text(font.render(player.grid_number_list[8], False, (255, 255, 255)), 411, 291),
        Text(font.render(player.grid_number_list[9], False, (255, 255, 255)), 622, 209)
    ]

    display.blit(title_font.render('Crafting Table', False, (0, 0, 0)), (195, 0))
    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.grid_list[i] is not None:
            if player.grid_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.grid_list[i].name], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
            if player.grid_list[i].durability is not None:
                RenderDurabilityBar(display, crafting_grid[i].rect.x, crafting_grid[i].rect.y, player.grid_list[i].durability, player.grid_list[i].max_durability)
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (465, 180))

def FurnaceInterface(context: Context, display):
    global FPS
    image_render(context)
    smelting_grid = [
        Grid((83, 83, 83), pygame.Rect((225, 67), (82, 82)), 2, player.smelt_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((225, 262), (82, 82)), 2, player.smelt_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((450, 172), (82, 82)), 2, player.smelt_image_list[2]),
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    side_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 36)
    title_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 40)
    arrow_font = pygame.font.Font('assets/minecraft-font/MinecraftBold-nMK1.otf', 45)
    smelting_numbers = [
        Text(font.render(player.smelt_number_list[0], False, (255, 255, 255)), 277, 120),
        Text(font.render(player.smelt_number_list[1], False, (255, 255, 255)), 277, 315),
        Text(font.render(player.smelt_number_list[2], False, (255, 255, 255)), 502, 225)
    ]

    display.blit(title_font.render('Furnace', False, (0, 0, 0)), (300, 0))
    for i in range(len(smelting_grid)):
        display.blit(smelting_grid[i].img, (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
        pygame.draw.rect(display, smelting_grid[i].colour, smelting_grid[i].rect, smelting_grid[i].width)
        if player.smelting_list[i] is not None:
            if player.smelting_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.smelting_list[i].name], (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
            if player.smelting_list[i].durability is not None:
                RenderDurabilityBar(display, smelting_grid[i].rect.x, smelting_grid[i].rect.y, player.smelting_list[i].durability, player.smelting_list[i].max_durability)
    for i in smelting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(player.fuel_img, (225, 172)) #Render Fire Image
    display.blit(side_font.render(str(player.fuel_val), False, (255, 0, 0)), (187, 187)) #Render Power of Fuel Remaining
    display.blit(side_font.render(str(player.smelting_time // FPS), False, (255, 0, 0)), (367, 157)) #Render Time to Smelt
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (337, 187)) #Render Arrow

def EnchantingInterface(context: Context, display):
    global Option1, Option2, Option3, Upgrade
    image_render(context)
    enchanting_grid = [
        Grid((83, 83, 83), pygame.Rect((30, 225), (82, 82)), 2, player.enchanting_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((112, 225), (82, 82)), 2, player.enchanting_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((30, 142), (82, 82)), 2, player.enchanting_image_list[2])
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    enchanting_numbers = [
        Text(font.render(str(player.enchanting_number_list[0]), False, (255, 255, 255)), 82, 277),
        Text(font.render(str(player.enchanting_number_list[1]), False, (255, 255, 255)), 165, 277),
        Text(font.render(str(player.enchanting_number_list[2]), False, (255, 255, 255)), 82, 195)
    ]
    for i in range(len(enchanting_grid)):
        display.blit(enchanting_grid[i].img, (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
        pygame.draw.rect(display, enchanting_grid[i].colour, enchanting_grid[i].rect, enchanting_grid[i].width)
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.enchanting_list[i].name], (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
            if player.enchanting_list[i].durability is not None:
                RenderDurabilityBar(display, enchanting_grid[i].rect.x, enchanting_grid[i].rect.y, player.enchanting_list[i].durability, player.enchanting_list[i].max_durability)
    for i in enchanting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(font.render(f'Enchanting Table LEVEL {player.enchanting_level}', False, (0, 0, 0)), (0, 0))
    Upgrade.render(world, 'Upgrade', 21)
    Option1.render(world, player.option_list[0], 30)
    Option2.render(world, player.option_list[1], 30)
    Option3.render(world, player.option_list[2], 30)

def CompressorInterface(context: Context, display):
    global player, FPS
    image_render(context)
    compressor_grid = [
        Grid((83, 83, 83), pygame.Rect((225, 142), (82, 82)), 2, player.compressor_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((450, 142), (82, 82)), 2, player.compressor_image_list[1])
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    title_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 40)
    arrow_font = pygame.font.Font('assets/minecraft-font/MinecraftBold-nMK1.otf', 45)
    side_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 36)
    compressor_numbers = [
        Text(font.render(player.compressor_number_list[0], False, (255, 255, 255)), 277, 195),
        Text(font.render(player.compressor_number_list[1], False, (255, 255, 255)), 502, 195)
    ]
    display.blit(title_font.render('Compressor', False, (0, 0, 0)), (262, 0))
    for i in range(len(compressor_grid)):
        display.blit(compressor_grid[i].img, (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
        pygame.draw.rect(display, compressor_grid[i].colour, compressor_grid[i].rect, compressor_grid[i].width)
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.compressor_list[i].name], (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
            if player.compressor_list[i].durability is not None:
                RenderDurabilityBar(display, compressor_grid[i].rect.x, compressor_grid[i].rect.y, player.compressor_list[i].durability, player.compressor_list[i].max_durability)
    for i in compressor_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (337, 172))  # Render Arrow
    display.blit(side_font.render(str(player.compressing_time // FPS), False, (255, 0, 0)), (360, 142))  # Render Time to Compress

def GrindstoneInterface(context: Context, display):
    global player
    image_render(context)
    grindstone_grid = [
        Grid((83, 83, 83), pygame.Rect((225, 87), (82, 82)), 2, player.grindstone_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((225, 177), (82, 82)), 2, player.grindstone_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((475, 133), (82, 82)), 2, player.grindstone_image_list[2])
    ]
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    title_font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 35)
    arrow_font = pygame.font.Font('assets/minecraft-font/MinecraftBold-nMK1.otf', 45)
    grindstone_numbers = [
        Text(font.render(player.grindstone_number_list[0], False, (255, 255, 255)), 277, 139),
        Text(font.render(player.grindstone_number_list[1], False, (255, 255, 255)), 277, 229),
        Text(font.render(player.grindstone_number_list[2], False, (255, 255, 255)), 527, 185)
    ]
    display.blit(title_font.render("Repair & Disenchant", False, (0, 0, 0)), (90, 0))
    for i in range(len(grindstone_grid)):
        display.blit(grindstone_grid[i].img, (grindstone_grid[i].rect.x, grindstone_grid[i].rect.y))
        pygame.draw.rect(display, grindstone_grid[i].colour, grindstone_grid[i].rect, grindstone_grid[i].width)
        if player.grindstone_list[i] is not None:
            if player.grindstone_list[i].enchantments is not None:
                display.blit(context.TC_GLINTS[player.grindstone_list[i].name], (grindstone_grid[i].rect.x, grindstone_grid[i].rect.y))
            if player.grindstone_list[i].durability is not None:
                RenderDurabilityBar(display, grindstone_grid[i].rect.x, grindstone_grid[i].rect.y, player.grindstone_list[i].durability, player.grindstone_list[i].max_durability)
    for i in grindstone_numbers:
        display.blit(i.surface, (i.x, i.y))
    pygame.draw.rect(display, (0, 0, 0), (215, 77, 102, 194), 2)
    pygame.draw.rect(display, (0, 0, 0), (185, 97, 30, 194), 2)
    pygame.draw.rect(display, (0, 0, 0), (317, 97, 30, 194), 2)
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (367, 152))  # Render Arrow

def hotbar_identify():
    global selected_hotbar, hotbar_item, hotbar_index
    hotbar_index = HOTBAR_ORDER.index(player.selected_hotbar)
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
def Main():
    global TimerRunning, screen, furnace_interface, crafting_grid, small_crafting_grid, inventory_grid, World, player, difference, individual_frame, FPS, mode, val, comma, number, called, world, frame, play_time, endTime, minute, seconds, true_play_time, PlayTime, hotbar_backgrounds, selected_hotbar
    global hasGeneratedOverworld, display, clock, loading, hasGeneratedUnderground, previous_frame

    context: Context = None

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
                                    if player.hotbar_item.itemType == "Food":
                                        if player.hunger < 20:
                                            if player.hotbar_item.name == 'Bread':
                                                index = player.inventory_list.index(player.hotbar_item)
                                                player.inventory_list[index].number -= 1
                                                player.hunger += 5
                                            # GOLDEN CARROT
                                            elif player.hotbar_item.name == 'Golden Carrot':
                                                index = player.inventory_list.index(player.hotbar_item)
                                                player.inventory_list[index].number -= 1
                                                player.hunger += 6
                                            # GOLDEN APPLE
                                            elif player.hotbar_item.name == 'Golden Apple':
                                                index = player.inventory_list.index(player.hotbar_item)
                                                player.inventory_list[index].number -= 1
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
                                if player.hotbar_item is not None:
                                    if player.hotbar_item.name == 'Crafting Table': #Crafting Key
                                        player.mode = 'crafting'
                                    elif player.hotbar_item.name == 'Furnace': #Smelting Key
                                        player.mode = 'smelting'
                                    elif player.hotbar_item.name == 'Enchanting Table': #Enchanting Key
                                        player.mode = 'enchanting'
                                    elif player.hotbar_item.name == 'Compressor': #Compressing Key
                                        player.mode = 'compressing'
                                    elif player.hotbar_item.name == "Grindstone": #Repairing and Disenchanting Key
                                        player.mode = 'repairing and disenchanting'
                                    elif player.hotbar_item.name == "Bucket": #Picking up liquids
                                        player.pick_up_liquid()
                                    elif player.hotbar_item.name == "Water Bucket" or \
                                            player.hotbar_item.name == "Lava Bucket":  #Placing liquids
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
                World.render(world, context)  # Render all world blocks to world
                RemoveItem() #Remove Items if their number is 0
                hotbar_identify() #Update hotbar item
                player.render(context, world)  # Render player and player accessories to world
                SpeedrunTimer(world, PlayTime)
                advancements_update(player.advancements, player.inventory_list, player.armour_list, player.dimension)  # Update Advancements
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
                InventoryGrid(context, world) #Render Inventory Grid
                ArmourGrid(context, world) #Render Armour Grid for Player
                SmallCraftGrid(context, world) #Render Small Crafting Grid
                Crafting() #Update Small 2x2 Crafting Grid
                RemoveItem() #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world) #Render the item the user is holding
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
                InventoryGrid(context, world) #Render Inventory Grid
                CraftGrid(context, world) #Render 3x3 Crafting Grid
                GridCraft()  #Update 3x3 Crafting Grid
                RemoveItem()  #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world)  # Render the item the user is holding
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
                InventoryGrid(context, world) #Render Inventory Grid
                FurnaceInterface(context, world) #Render Furnace Interface
                player.smelt(context) #Furnace Smelting
                RemoveItem()  #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world)  # Render the item the user is holding
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
                InventoryGrid(context, world)  # Render Inventory Grid
                EnchantingInterface(context, world) #Render Enchanting Table Interface
                RemoveItem()  #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world)  # Render the item the user is holding
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
                InventoryGrid(context, world) #Render Inventory Grid
                CompressorInterface(context, world) #Render Compressor Interface
                player.compress() #Compressing Process
                RemoveItem() #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world) #Render the item the user is holding
                RenderHoveringItem(world, Type, box) #Render Item Name

            elif player.mode == 'repairing and disenchanting':

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
                InventoryGrid(context, world) #Render Inventory Grid
                GrindstoneInterface(context, world) #Render Grindstone Interface
                player.repair_and_disenchant() #Update repaired/disenchanted item
                RemoveItem() #Remove all items with number of 0 or durability of 0
                RenderHoldingItem(context, world) #Render the item the user is holding
                RenderHoveringItem(world, Type, box) #Render Item Name

            display.blit(world, (0, 0))  # Render map to display
            pygame.display.flip()  # Update Display
        elif not hasGeneratedOverworld and hasGeneratedUnderground == "Not Loaded":
            display.fill((255, 255, 255))
            for i in range(0, 750, 32):
                for j in range(0, 750, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 37)
            display.blit(font.render("Generating Overworld", False, (255, 255, 255)), (180, 225))
            pygame.display.flip()
            context = PygameInitialise()
            print("PYGAME INITIALISED")
        if hasGeneratedUnderground == "Generating":
            display.fill((255, 255, 255))
            for i in range(0, 750, 32):
                for j in range(0, 750, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 37)
            display.blit(font.render("Generating Underground", False, (255, 255, 255)), (180, 225))
            pygame.display.flip()
            World.undergroundGenerated = True
            World.generateUnderground()
            World.UndergroundTiles = UndergroundGeneratePortal(round(player.x), round(player.y), World.UndergroundTiles)
            hasGeneratedUnderground = "Generated"
        if not pygame.mixer.music.get_busy():
            if RandomNum(1, 500) == 1:
                pygame.mixer.music.load("assets/music/song" + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()


#Render the Item the User is Holding
def RenderHoldingItem(context, display):
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
    if player.holding_item is not None:
        display.blit(player.holding_item_image, (x, y))
        display.blit(font.render(player.holding_item_number, False, (255, 255, 255)), (x + 52, y + 52))
        if player.holding_item.enchantments is not None:
            display.blit(context.TC_GLINTS[player.holding_item.name], (x, y))
        if player.holding_item.durability is not None:
            RenderDurabilityBar(display, x, y, player.holding_item.durability, player.holding_item.max_durability)

#Convert Numbers to Roman Numerals
def DecimalToRoman(num):
    num = int(num)
    nums = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    symbols = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12
    roman_value = ""
    while num:
        div = num // nums[i]
        num %= nums[i]
        while div:
            roman_value += symbols[i]
            div -= 1
        i -= 1
    return roman_value

#Info Box for Items (with and without enchantments)
def TextBox(List, x, y, font, box, display):
    try:
        if List[box] is not None: #Check to prevent crashes
            length_list = [len(List[box].name * 15)]
            if List[box].enchantments is not None:
                width = (1 + len(List[box].enchantments)) * 37
                for i in List[box].enchantments:
                    length_list.append(len(str(i[0]) + DecimalToRoman(str(i[1]))) * 15)
            else:
                width = 37
            if List[box].durability is not None:
                width += 22
                length_list.append(len(f"Durability: {List[box].durability}/{List[box].max_durability}") * 15)
            length = max(length_list)
            if x + length > 750:
                x -= length
            if y + width > 750:
                y -= width
            pygame.draw.rect(display, (0, 0, 0), (x, y, length, width))
            display.blit(font.render(List[box].name, False, List[box].colour), (x + 15, y + 15))
            if List[box].durability is not None: #WITH DURABILITY
                if List[box].enchantments is not None:
                    for i in range(len(List[box].enchantments)):
                        display.blit(font.render(f'{List[box].enchantments[i][0]} {DecimalToRoman(List[box].enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
                display.blit(font.render(f"Durability: {List[box].durability}/{List[box].max_durability}", False, (175, 175, 175)), (x + 15, y + width - 20))
            else: #EVERYTHING ELSE
                if List[box].enchantments is not None:
                    for i in range(len(List[box].enchantments)):
                        display.blit(font.render(f'{List[box].enchantments[i][0]} {DecimalToRoman(List[box].enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
    except IndexError:
        pass

#Render the Item Label for the Item that the User is Hovering Over
def RenderHoveringItem(display, Type, box):
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('assets/monofur/monof55.ttf', 22)
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
        elif Type == 'repairing and disenchanting' or Type == 'repairing and disenchanting item': #Grindstone
            TextBox(player.grindstone_list, x, y, font, box, display)

#Determine which box the user selected
def SelectedBox():
    x, y = pygame.mouse.get_pos()
    if 0 <= x <= 742 and 390 <= y <= 720:
        column = x // 82
        row = (y - 390) // 82
        box = column + 9 * row
        return "inventory grid", box
    elif 0 <= x <= 330 and 240 <= y <= 322 and player.mode == 'inventory':
        box = x // 82
        return "armour grid", box
    elif 390 <= x <= 555 and 75 <= y <= 240 and player.mode == 'inventory':
        column = (x - 390) // 82
        row = (y - 75) // 82
        box = column + 2 * row
        return "small crafting grid", box
    elif 637 <= x <= 720 and 117 <= y <= 199 and player.mode == 'inventory':
        box = 4
        return 'small crafting grid item', box
    elif 195 <= x <= 442 and 75 <= y <= 322 and player.mode == 'crafting':
        column = (x - 195) // 82
        row = (y - 75) // 82
        box = column + 3 * row
        return 'crafting grid', box
    elif 570 <= x <= 652 and 157 <= y <= 240 and player.mode == 'crafting':
        box = 9
        return 'crafting grid item', box
    elif 225 <= x <= 307 and 67 <= y <= 150 and player.mode == 'smelting':
        box = 0
        return 'smelting', box
    elif 225 <= x <= 307 and 262 <= y <= 345 and player.mode == 'smelting':
        box = 1
        return 'smelting', box
    elif 450 <= x <= 532 and 172 <= y <= 255 and player.mode == 'smelting':
        box = 2
        return 'smelting item', box
    elif 30 <= x <= 112 and 225 <= y <= 307 and player.mode == 'enchanting':
        box = 0
        return 'enchanting', box
    elif 112 <= x <= 195 and 225 <= y <= 307 and player.mode == 'enchanting':
        box = 1
        return 'enchanting', box
    elif 30 <= x <= 112 and 142 <= y <= 225 and player.mode == 'enchanting':
        box = 2
        return 'enchanting', box
    elif Upgrade.x <= x <= Upgrade.x + 82 and Upgrade.y <= y <= Upgrade.y + 82 and player.mode == 'enchanting':
        box = 0
        return 'upgrade', box
    elif Option1.x <= x <= Option1.x + 487 and Option1.y <= y <= Option1.y + 82 and player.mode == 'enchanting':
        box = 0
        return 'option1', box
    elif Option2.x <= x <= Option2.x + 487 and Option2.y <= y <= Option2.y + 82 and player.mode == 'enchanting':
        box = 1
        return 'option2', box
    elif Option3.x <= x <= (Option3.x + 487) and Option3.y <= y <= (Option3.y + 82) and player.mode == 'enchanting':
        box = 2
        return 'option3', box
    elif 75 <= x <= 307 and 142 <= y <= 225 and player.mode == 'compressing':
        box = 0
        return 'compressing', box
    elif 450 <= x <= 532 and 142 <= y <= 225 and player.mode == 'compressing':
        box = 1
        return 'compressing item', box
    elif 225 <= x <= 307 and 87 <= y <= 169 and player.mode == 'repairing and disenchanting':
        box = 0
        return 'repairing and disenchanting', box
    elif 225 <= x <= 307 and 177 <= y <= 259 and player.mode == 'repairing and disenchanting':
        box = 1
        return 'repairing and disenchanting', box
    elif 475 <= x <= 557 and 133 <= y <= 215 and player.mode == 'repairing and disenchanting':
        box = 2
        return 'repairing and disenchanting item', box
    else:
        return None, None

#Move items using drag and drop
def ClickItem(Type, box):
    global small_crafting_grid
    if Type is not None and box is not None:
        if Type == 'inventory grid': #Inventory Grid and Hotbar
            if player.holding_item is not None and player.inventory_list[box] is not None:
                if player.holding_item.name == player.inventory_list[box].name and (player.inventory_list[box].number + player.holding_item.number <= player.holding_item.stackNum): #Items can be combined
                    player.inventory_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.inventory_list[box] = player.inventory_list[box], player.holding_item
            else:
                player.holding_item, player.inventory_list[box] = player.inventory_list[box], player.holding_item
        elif Type == 'armour grid': #Armour Grid
            if box == 0: #Tier 1
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item.itemType == 'Tier1':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item.itemType == 'Tier1' and player.armour_list[box].itemType == 'Tier1':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 1: #Tier 2
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item.itemType == 'Tier2':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item.itemType == 'Tier2' and player.armour_list[box].itemType == 'Tier2':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 2: #Tier 3
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item.itemType == 'Tier3':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is not None and player.armour_list[box] is not None:
                    if player.holding_item.itemType == 'Tier3' and player.armour_list[box].itemType == 'Tier3':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
            elif box == 3: #Shield
                if player.holding_item is not None and player.armour_list[box] is None:
                    if player.holding_item.itemType == 'Shield':
                        player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
                elif player.holding_item is None and player.armour_list[box] is not None:
                    player.holding_item, player.armour_list[box] = player.armour_list[box], player.holding_item
        elif Type == 'small crafting grid': #Small 2x2 Crafting Grid
            if player.holding_item is not None and player.craft_list[box] is not None: #Items can be combined
                if player.holding_item.name == player.craft_list[box].name and (player.craft_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.craft_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.craft_list[box] = player.craft_list[box], player.holding_item
            else:
                player.holding_item, player.craft_list[box] = player.craft_list[box], player.holding_item
        elif Type == 'small crafting grid item': #Collecting the Item Crafted from 2x2 Crafting Grid
            if player.craft_list[4] is not None:
                inventory_add(player.craft_list[4])
                for i in range(4):
                    if player.craft_list[i] is not None:
                        player.craft_list[i].number -= 1
        elif Type == 'crafting grid': #Big 3x3 Crafting Grid
            if player.holding_item is not None and player.grid_list[box] is not None: #Items can be combined
                if player.holding_item.name == player.grid_list[box].name and (player.grid_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.grid_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.grid_list[box] = player.grid_list[box], player.holding_item
            else:
                player.holding_item, player.grid_list[box] = player.grid_list[box], player.holding_item
        elif Type == 'crafting grid item': #Collecting the Item Crafted from 3x3 Crafting Grid
            if player.grid_list[9] is not None:
                inventory_add(player.grid_list[9])
                for i in range(9):
                    if player.grid_list[i] is not None:
                        player.grid_list[i].number -= 1
        elif Type == 'smelting':
            if player.holding_item is not None and player.smelting_list[box] is not None: #Items can be combined
                if player.holding_item.name == player.smelting_list[box].name and (player.smelting_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.smelting_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.smelting_list[box] = player.smelting_list[box], player.holding_item
            else:
                player.holding_item, player.smelting_list[box] = player.smelting_list[box], player.holding_item
        elif Type == 'smelting item': #Collecting the Item Smelted from Furnace
            inventory_add(player.smelting_list[2])
            player.smelting_list[2] = None
        elif Type == 'enchanting':
            if player.holding_item is not None and player.enchanting_list[box] is not None: #Items can be combined
                if player.holding_item.name == player.enchanting_list[box].name and (player.enchanting_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.enchanting_list[box].number += player.holding_item.number
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
                if player.holding_item.name == player.compressor_list[box].name and (player.compressor_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.compressor_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.compressor_list[box] = player.compressor_list[box], player.holding_item
            else:
                player.holding_item, player.compressor_list[box] = player.compressor_list[box], player.holding_item
        elif Type == 'compressing item':
            inventory_add(player.compressor_list[1])
            player.compressor_list[1] = None
        elif Type == 'repairing and disenchanting':
            if player.holding_item is not None and player.grindstone_list[box] is not None:  # Items can be combined
                if player.holding_item.name == player.grindstone_list[box].name and (player.grindstone_list[box].number + player.holding_item.number <= player.holding_item.stackNum):
                    player.grindstone_list[box].number += player.holding_item.number
                    player.holding_item = None
                else:
                    player.holding_item, player.grindstone_list[box] = player.grindstone_list[box], player.holding_item
            else:
                player.holding_item, player.grindstone_list[box] = player.grindstone_list[box], player.holding_item
        elif Type == 'repairing and disenchanting item':
            inventory_add(player.grindstone_list[2])
            if player.grindstone_list[0] is not None and player.grindstone_list[1] is None:
                if player.grindstone_list[0].enchantments is not None:
                    player.disenchant()
            player.grindstone_list[0], player.grindstone_list[1], player.grindstone_list[2] = None, None, None

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
                player.inventory_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.inventory_list[box] is not None and player.inventory_list[box].name == player.holding_item.name and (player.inventory_list[box].number + 1 <= player.inventory_list[box].stackNum):
                player.inventory_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'small crafting grid': #Small 2x2 Crafting Grid
            if player.craft_list[box] is None:
                player.craft_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.craft_list[box] is not None and player.craft_list[box].name == player.holding_item.name and (player.craft_list[box].number + 1 <= player.craft_list[box].stackNum):
                player.craft_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'crafting grid': #Big 3x3 Crafting Grid
            if player.grid_list[box] is None:
                player.grid_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.grid_list[box] is not None and player.grid_list[box].name == player.holding_item.name and (player.grid_list[box].number + 1 <= player.grid_list[box].stackNum):
                player.grid_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'smelting': #Furnace Interface
            if player.smelting_list[box] is None:
                player.smelting_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.smelting_list[box] is not None and player.smelting_list[box].name == player.holding_item.name and (player.smelting_list[box].number + 1 <= player.smelting_list[box].stackNum):
                player.smelting_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'enchanting': #Enchanting Table Interface
            if player.enchanting_list[box] is None:
                player.enchanting_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.enchanting_list[box] is not None and player.enchanting_list[box].name == player.holding_item.name and (player.enchanting_list[box].number + 1 <= player.enchanting_list[box].stackNum):
                player.enchanting_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'compressing': #Compressor Interface
            if player.compressor_list[box] is None:
                player.compressor_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.holding_item.number -= 1
            elif player.compressor_list[box] is not None and player.compressor_list[box].name == player.holding_item.name and (player.compressor_list[box].number + 1 <= player.compressor_list[box].stackNum):
                player.compressor_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'repairing and disenchanting': #Grindstone Interface
            if player.grindstone_list[box] is None:
                player.grindstone_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments, player.holding_item.durability)
                player.grindstone.number -= 1
            elif player.grindstone_list[box] is not None and player.grindstone_list[box].name == player.holding_item.name and (player.grindstone_list[box].number + 1 <= player.grindstone_list[box].stackNum):
                player.grindstone_list[box].number += 1
                player.holding_item.number -= 1

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
        self.y = 570
        self.input_line = 0
        self.print_list = []
        self.isTyping = False
        self.typingText = ''
        self.position = 0
        self.foretext = ''
        self.timer = 0

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
        global player 
        self.input_line = 0
        self.isTyping = False
        length = len(list(ITEM_TYPES.keys())) - 1
        if self.foretext == f'Item ID (0 - {length}): ':
            inventory_add(give(self.typingText))
            self.foretext = ''
        elif self.foretext == 'Coordinates (X,Y): ':
            player.x, player.y = teleport(player.x, player.y, self.typingText)
            self.foretext = ''
        elif self.foretext == "Enchantment (Name, Lvl): ":
            index = HOTBAR_ORDER.index(player.selected_hotbar)
            item = enchant(self.typingText)
            if item is not None:
                player.inventory_list[27 + index] = item
            self.foretext = ''
        elif self.foretext == "Experience Level: ":
            experience(self.typingText)
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
                        NumberLimit(number, self.typingText)
                    except ValueError:
                        self.print("Invalid integer")
                else:
                    number = 1  # Set number to 1 when number is not specified
                    NumberLimit(number, self.typingText)
            # Regular text message
            else:
                self.print(f"<Player> {self.typingText}")

    def print(self, text):
        self.timer = 0
        self.print_list.append(text)

    def render(self, display):
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
            font = pygame.font.Font('assets/monofur/monof55.ttf', 18)
            for i in range(len(self.screen_list)):
                display.blit(font.render(self.screen_list[i], False, (255, 255, 255)), (x, y + height - (i + 1) * 15 - self.input_line))
            display.blit(font.render(self.foretext + self.typingText, True, (255, 255, 255)), (x, y + height - 15))
            self.timer += 1

# Create Hotbar Outline
class Hotbar:
    def __init__(self, colour, rect, width):
        self.colour = colour
        self.rect = rect
        self.width = width

#Player Class and Methods
class Player:
    def __init__(self, context: Context):
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

        #TO PREVENT PLAYERS FROM SPAWNING INSIDE A TREE OR BOULDER
        while True: #Infinite loop
            if World.Tiles[(self.x, self.y)].tile != "Air": #If tile that player spawns in is not air
                self.x += 1 #increase x by 1
            else:
                break #tile is air so the loop ends

        # Setup Health Bar Images
        global health_vals, health_nums, heart1, heart2, heart3, heart4, heart5, heart6, heart7, heart8, heart9, heart10, full_heart, health, half_heart, empty_heart
        full_heart = pygame.image.load(
            'assets/FullHeart_20x20.png').convert()  # Full Heart (2)
        half_heart = pygame.image.load(
            'assets/half_heart_20x20.png').convert()  # Half Heart (1)
        empty_heart = pygame.image.load(
            'assets/empty_heart_20x20.png').convert()  # Empty Heart (0)
        heart1 = info_bar(full_heart, 7, 592)
        heart2 = info_bar(full_heart, 42, 592)
        heart3 = info_bar(full_heart, 76, 592)
        heart4 = info_bar(full_heart, 111, 592)
        heart5 = info_bar(full_heart, 145, 592)
        heart6 = info_bar(full_heart, 180, 592)
        heart7 = info_bar(full_heart, 214, 592)
        heart8 = info_bar(full_heart, 249, 592)
        heart9 = info_bar(full_heart, 283, 592)
        heart10 = info_bar(full_heart, 318, 592)
        self.health_vals = [heart1, heart2, heart3, heart4, heart5, heart6, heart7, heart8, heart9, heart10]
        self.health_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.health = 20  # Set Health = 20

        # Setup Hunger Bar Images
        global experience_bar, hunger_vals, backdrop, empty_hunger, distance, hunger_nums, full_hunger, hunger, half_hunger, dead, hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10
        full_hunger = pygame.image.load(
            'assets/hunger_20x20.png')  # Full Hunger (2)
        half_hunger = pygame.image.load(
            'assets/half_hunger_20x20.png')  # Half Hunger (1)
        empty_hunger = pygame.image.load(
            'assets/empty_hunger_20x20.png')  # Empty Hunger (0)
        self.hunger = 20  # Set Hunger = 20
        self.hunger_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.distance = 0  # Set Distance Travelled
        self.dead = False
        self.hunger_subtracted = 0

        hunger1 = info_bar(full_hunger, 715, 592)
        hunger2 = info_bar(full_hunger, 681, 592)
        hunger3 = info_bar(full_hunger, 646, 592)
        hunger4 = info_bar(full_hunger, 612, 592)
        hunger5 = info_bar(full_hunger, 577, 592)
        hunger6 = info_bar(full_hunger, 543, 592)
        hunger7 = info_bar(full_hunger, 508, 592)
        hunger8 = info_bar(full_hunger, 474, 592)
        hunger9 = info_bar(full_hunger, 439, 592)
        hunger10 = info_bar(full_hunger, 405, 592)
        self.hunger_vals = [hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10]  # Hunger bar list
        experience_bar = pygame.image.load('assets/item_imgs/experience.png').convert()
        backdrop = pygame.Rect((30, 592), (697, 30))  # Set Background for Hunger and Health Bar

        self.waiting_list = []
        self.selected_slot = 'slot1'
        self.inventory_list = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None,
                          None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                          None,
                          None, None, None, None]
        self.image_list = []
        self.number_list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
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
        self.fuel_img = context.ITEM_IMAGES["no_fire"]
        self.smelting_time = 0
        self.experience_points = 0
        self.experience_levels = 0
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
        slot = pygame.image.load("assets/item_imgs/slot.png").convert()
        bar1 = info_bar(slot, 7, 667)
        bar2 = info_bar(slot, 89, 667)
        bar3 = info_bar(slot, 171, 667)
        bar4 = info_bar(slot, 253, 667)
        bar5 = info_bar(slot, 335, 667)
        bar6 = info_bar(slot, 417, 667)
        bar7 = info_bar(slot, 499, 667)
        bar8 = info_bar(slot, 581, 667)
        bar9 = info_bar(slot, 663, 667)
        self.hotbar_imgs = [bar1, bar2, bar3, bar4, bar5, bar6, bar7, bar8, bar9]

        # Set Background Rects
        background_1 = pygame.Rect((7, 667), (82, 82))
        background_2 = pygame.Rect((89, 667), (82, 82))
        background_3 = pygame.Rect((171, 667), (82, 82))
        background_4 = pygame.Rect((253, 667), (82, 82))
        background_5 = pygame.Rect((335, 667), (82, 82))
        background_6 = pygame.Rect((417, 667), (82, 82))
        background_7 = pygame.Rect((499, 667), (82, 82))
        background_8 = pygame.Rect((581, 667), (82, 82))
        background_9 = pygame.Rect((663, 667), (82, 82))

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
        self.grindstone_list = [None, None, None]
        self.grindstone_image_list = []
        self.grindstone_number_list = []

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
        if self.hunger > 0 and self.distance != 0 and self.distance // 512 != self.hunger_subtracted:
            self.hunger -= 1
            self.hunger_subtracted += 1
        self.health_hunger_update()

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
        self.health_hunger_update()

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

    def smelt(self, context: Context):
        global FPS
        # Load Fuel
        if self.smelting_list[1] is not None:
            if self.smelting_list[1].name == "Coal" and self.fuel_val == 0:
                self.smelting_list[1] = Item(self.smelting_list[1].name, self.smelting_list[1].number - 1, self.smelting_list[1].enchantments, self.smelting_list[1].durability)
                self.fuel_val = 8

        # Smelting Process
        if self.smelting_list[0] is not None:
            if self.smelting_list[0].name == "Iron Ore" and self.fuel_val > 0:
                self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time >= 5 * FPS:
            self.smelting_time = 0
            self.smelting_list[0] = Item(self.smelting_list[0].name, self.smelting_list[0].number - 1, self.smelting_list[0].enchantments, self.smelting_list[0].durability)
            self.fuel_val -= 1
            if self.smelting_list[2] is None:
                self.smelting_list[2] = Item("Iron Ingot", 1, None, None)
                self.experience_points += 12
            else:
                self.smelting_list[2] = Item("Iron Ingot", self.smelting_list[2].number + 1, None, None)
                self.experience_points += 12

        # Render Fire
        if self.fuel_val > 0:
            self.fuel_img = context.ITEM_IMAGES["fire"]
        else:
            self.fuel_img = context.ITEM_IMAGES["no_fire"]

    def compress(self):
        global FPS
        #Compressing Process
        if self.compressor_list[0] is not None:
            if self.compressor_list[0].number >= 2:
                if self.compressor_list[0].name == 'Iron Ingot':
                    if self.compressor_list[1] is not None:
                        if self.compressor_list[1].name == 'Iron Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
                elif self.compressor_list[0].name == 'Diamond':
                    if self.compressor_list[1] is not None:
                        if self.compressor_list[1].name == 'Diamond Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
        else:
            self.compressing_time = 0

        #Finish Compressing Item
        if self.compressing_time >= 5 * FPS:
            self.compressing_time = 0
            self.compressor_list[0] = Item(self.compressor_list[0].name, self.compressor_list[0].number - 2, self.compressor_list[0].enchantments, self.compressor_list[0].durability)
            if self.compressor_list[1] is None:
                if self.compressor_list[0].name == 'Iron Ingot':
                    self.compressor_list[1] = Item("Iron Plate", 1, None, None)
                elif self.compressor_list[0].name == 'Diamond':
                    self.compressor_list[1] = Item("Diamond Plate", 1, None, None)
            else:
                if self.compressor_list[0].name == 'Iron Ingot' and self.compressor_list[1].name == 'Iron Plate':
                    self.compressor_list[1] = Item("Iron Plate", self.compressor_list[1].number + 1, None, None)
                elif self.compressor_list[0].name == 'Diamond' and self.compressor_list[1].name == 'Diamond Plate':
                    self.compressor_list[1] = Item("Diamond Plate", self.compressor_list[1].number + 1, None, None)

    def repair_and_disenchant(self):
        call = False
        if self.grindstone_list[0] is not None and self.grindstone_list[1] is None:
            if self.grindstone_list[0].enchantments is not None:
                self.grindstone_list[2] = Item(self.grindstone_list[0].name, self.grindstone_list[0].number, None, self.grindstone_list[0].durability)
                call = True
        elif self.grindstone_list[0] is not None and self.grindstone_list[1] is not None:
            if self.grindstone_list[0].durability is not None and self.grindstone_list[1].durability is not None:
                if self.grindstone_list[0].name == self.grindstone_list[1].name:
                    total_durability = self.grindstone_list[0].durability + self.grindstone_list[1].durability
                    if total_durability > self.grindstone_list[0].max_durability:
                        total_durability = self.grindstone_list[0].max_durability
                    self.grindstone_list[2] = Item(self.grindstone_list[0].name, self.grindstone_list[0].number, None, total_durability)
                    call = True
        if not call:
            self.grindstone_list[2] = None

    def disenchant(self):
        enchantments = self.grindstone_list[0].enchantments
        for i in enchantments:
            self.experience_points += int(i[1]) * 8

    def place_tile(self): #Place tiles
        if self.isShifting: #is shifting = can edit background tiles
            if self.dimension == "Overworld": #Overworld background tiles
                if self.hotbar_item.hasTile:
                    if World.UnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Open space to place tile
                        World.UnderTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1]) #Place tile
                        self.hotbar_item.number -= 1 #Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None #Remove from inventory
            elif self.dimension == "Underground": #Underground background tiles
                if self.hotbar_item.hasTile:
                    if World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None  # Remove from inventory
        else:
            if self.dimension == "Overworld": #Overworld Collision tiles
                if self.hotbar_item.hasTile:
                    if World.Tiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.Tiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.Tiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.Tiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None  # Remove from inventory
            elif self.dimension == "Underground": #Underground Collision Tiles
                if self.hotbar_item.hasTile:
                    if World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Air" or \
                            World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water" or \
                            World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava":  # Open space to place tile
                        World.UndergroundTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1])  # Place tile
                        self.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None  # Remove from inventory

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
                                if self.hotbar_item is not None:  # not holding any item
                                    if self.hotbar_item.toolTier is not None:  # is holding item
                                        if self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.hotbar_item.mining_speed) / (tile.breaking_time * 30) >= 1:
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.hotbar_item.mining_speed)
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
                                if self.hotbar_item is not None:  # not holding any item
                                    if self.hotbar_item.toolTier is not None:  # is holding item
                                        if self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.hotbar_item.mining_speed)
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
                                if self.hotbar_item is not None:  # not holding any item
                                    if self.hotbar_item.toolTier is not None:  # is holding item
                                        if self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.hotbar_item.mining_speed)
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
                                if self.hotbar_item is not None:  # not holding any item
                                    if self.hotbar_item.toolTier is not None:  # is holding item
                                        if self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier >= tile.requireToolTier:  # correct tool and tier
                                            if (1 + self.hotbar_item.mining_speed) / (tile.breaking_time * FPS * 1.5) >= 1 / (FPS/20):
                                                self.breaking_time += 7
                                                self.isInstantMining = True
                                            else:
                                                self.breaking_time += ((7 / FPS) / (tile.breaking_time * 1.5)) * (1 + self.hotbar_item.mining_speed)
                                                self.isInstantMining = False
                                            CALLED = True
                                        elif self.hotbar_item.itemType == tile.requireTool and self.hotbar_item.toolTier < tile.requireToolTier:  # correct tool but incorrect tier
                                            self.breaking_time += ((7 / FPS) / (tile.breaking_time * 5)) * (1 + self.hotbar_item.mining_speed)
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
                    inventory_add(Item("Oak Log", RandomNum(1, 5), None, None))
                elif value.tile == "Stone":
                    inventory_add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    inventory_add(Item("Coal", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Lapis Ore":
                    inventory_add(Item("Lapis Lazuli", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Diamond Ore":
                    inventory_add(Item("Diamond", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Grass":
                    inventory_add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if RandomNum(1, 10) == 1:
                        inventory_add(Item("Flint", 1, None, None))
                    else:
                        inventory_add(Item("Gravel", 1, None, None))
                else:
                    inventory_add(Item(value.tile, 1, None, None))
        elif self.dimension == "Underground":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    inventory_add(Item("Oak Log", RandomNum(1, 5), None, None))
                elif value.tile == "Stone":
                    inventory_add(Item("Cobblestone", 1, None, None))
                elif value.tile == "Coal Ore":
                    inventory_add(Item("Coal", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Lapis Ore":
                    inventory_add(Item("Lapis Lazuli", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Diamond Ore":
                    inventory_add(Item("Diamond", 1, None, None))
                    self.experience_points += 12
                elif value.tile == "Grass":
                    inventory_add(Item("Dirt", 1, None, None))
                elif value.tile == "Gravel":
                    if RandomNum(1, 10) == 1:
                        inventory_add(Item("Flint", 1, None, None))
                    else:
                        inventory_add(Item("Gravel", 1, None, None))
                else:
                    inventory_add(Item(value.tile, 1, None, None))
        if self.hotbar_item is not None:
            if self.hotbar_item.durability is not None:
                if self.hotbar_item.enchantments is not None:
                    for i in self.hotbar_item.enchantments:
                        if i[0] == "Unbreaking":
                            if RandomNum(1, i[1] + 1) == 1:
                                self.hotbar_item.durability -= 1
                            break
                    else:
                        self.hotbar_item.durability -= 1
                else:
                    self.hotbar_item.durability -= 1

    def break_tile(self, value):
        if self.isShifting:
            if self.dimension == "Overworld":
                if self.hotbar_item is not None:
                    if self.hotbar_item.itemType == value.requireTool:
                        if self.hotbar_item.toolTier >= value.requireToolTier:
                            if self.hotbar_item.name == value.tile:
                                self.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.hotbar_item.name == value.tile:
                            self.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.hotbar_item is not None:
                    if self.hotbar_item.itemType == value.requireTool:
                        if self.hotbar_item.toolTier >= value.requireToolTier:
                            if self.hotbar_item.name == value.tile:
                                self.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.hotbar_item.name == value.tile:
                            self.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UndergroundUnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
        else:
            if self.dimension == "Overworld":
                if self.hotbar_item is not None:
                    if self.hotbar_item.itemType == value.requireTool:
                        if self.hotbar_item.toolTier >= value.requireToolTier:
                            if self.hotbar_item.name == value.tile:
                                self.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.hotbar_item.name == value.tile:
                            self.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.Tiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])
            elif self.dimension == "Underground":
                if self.hotbar_item is not None:
                    if self.hotbar_item.itemType == value.requireTool:
                        if self.hotbar_item.toolTier >= value.requireToolTier:
                            if self.hotbar_item.name == value.tile:
                                self.hotbar_item.number += 1
                            else:
                                self.break_add_item(value)
                    elif value.requireToolTier == 0:
                        if self.hotbar_item.name == value.tile:
                            self.hotbar_item.number += 1
                        else:
                            self.break_add_item(value)
                elif value.requireToolTier == 0:
                    self.break_add_item(value)
                World.UndergroundTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1])

    def pick_up_liquid(self): #Picking up liquids with a bucket
        if self.dimension == "Overworld": #Overworld
            if self.isShifting: #Background tiles
                if World.UnderTiles[(self.target[0], self.target[1])].tile == "Water": #Wate
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Water Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Lava Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision tiles
                if World.Tiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Water Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1],)
                elif World.Tiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Lava Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
        elif self.dimension == "Underground": #Underground
            if self.isShifting: #Background Tiles
                if World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Water Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Lava Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
            else: #Collision Tiles
                if World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Water": #Water
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Water Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])
                elif World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Lava": #Lava
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Lava Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Air", self.target[0], self.target[1])

    def place_liquid(self):
        global alpha_water_tile, alpha_lava_tile
        if self.dimension == "Overworld":
            if self.isShifting:
                if self.hotbar_item.name == "Water Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.hotbar_item.name == "Lava Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.hotbar_item.name == "Water Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.hotbar_item.name == "Lava Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.Tiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
        elif self.dimension == "Underground":
            if self.isShifting:
                if self.hotbar_item.name == "Water Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.hotbar_item.name == "Lava Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])
            else:
                if self.hotbar_item.name == "Water Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Water", self.target[0], self.target[1])
                elif self.hotbar_item.name == "Lava Bucket":
                    self.hotbar_item.number -= 1
                    inventory_add(Item("Bucket", 1, None, None))
                    World.UndergroundTiles[(self.target[0], self.target[1])] = Tile("Lava", self.target[0], self.target[1])

    def render(self, context: Context, display):
        global backdrop, experience_bar, FPS, BREAKING_LIST

        def item_image(item_name: str) -> pygame.Surface:
            return context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item_name]]

        if self.breaking_delay > 0:
            self.breaking_delay -= 1
        else:
            self.breaking_delay = 0

        self.experience_levels += (-1 + (1 + 4 * (self.experience_points + self.experience_levels ** 2 + self.experience_levels)) ** 0.5) / 2 - self.experience_levels
        self.experience_points = 0
        try:
            self.percent_xp_to_next_level = (self.experience_levels - math.floor(self.experience_levels))
        except ZeroDivisionError:
            self.percent_xp_to_next_level = 0

        # DRAW BACKDROP FOR HUNGER AND HEALTH BARS
        pygame.draw.rect(display, (255, 255, 255), backdrop)

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

        # DRAW HEALTH BAR
        for j in self.health_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW HUNGER BAR
        for j in self.hunger_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW EXPERIENCE BAR
        fontx = pygame.font.Font('assets/minecraft-font/MinecraftRegular-Bmg3.otf', 45)
        pygame.draw.rect(display, "#72a34c", (5, 630, round(self.percent_xp_to_next_level * 738), 30))
        pygame.draw.rect(display, "#424d42", (round(self.percent_xp_to_next_level * 738) + 5, 630, round((1 - self.percent_xp_to_next_level) * 738), 30))
        for i in range(18):
            pygame.draw.rect(display, (0, 0, 0), (i * 41 + 5, 630, 41, 30), 2)
        experience_number = fontx.render(str(math.floor(self.experience_levels)), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (378, 615)
        display.blit(experience_number, experience_number_r)  # Experience Number

        # GENERATE HOTBAR LIST
        for i in range(27, 36):
            if self.inventory_list[i] is None:  # Set White Background for NONE Slots
                self.hotbar_imgs[i - 27].img = slot
                self.number_list[i] = ''
            else:  # No Enchantments
                self.hotbar_imgs[i - 27].img = item_image(self.inventory_list[i].name)
                self.number_list[i] = str(self.inventory_list[i].number)
                if self.number_list[i] == '1':
                    self.number_list[i] = ''
                if self.inventory_list[i].number == 0:
                    self.inventory_list[i] = None

        # DRAW HOTBAR
        for i in range(len(self.hotbar_imgs)):
            display.blit(slot, (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))  # Background
            display.blit(self.hotbar_imgs[i].img, (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))  #Item
            if self.inventory_list[i+27] is not None:
                if player.inventory_list[i+27].enchantments is not None:
                    display.blit(context.TC_GLINTS[player.inventory_list[i+27].name], (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))
                if player.inventory_list[i+27].durability is not None:
                    RenderDurabilityBar(display, self.hotbar_imgs[i].x, self.hotbar_imgs[i].y, player.inventory_list[i+27].durability, player.inventory_list[i+27].max_durability)

        # DRAW HOTBAR BACKGROUNDS
        for j in self.hotbar_backgrounds:
            pygame.draw.rect(display, j.colour, j.rect, j.width)

        # SETUP HOTBAR NUMBERS
        font = pygame.font.Font(
            'assets/minecraft-font/MinecraftRegular-Bmg3.otf', 24)

        pygame_number_text = [
            Text(font.render(self.number_list[27], True, (255, 0, 0), (255, 255, 255)), 60, 720),
            Text(font.render(self.number_list[28], True, (255, 0, 0), (255, 255, 255)), 142, 720),
            Text(font.render(self.number_list[29], True, (255, 0, 0), (255, 255, 255)), 225, 720),
            Text(font.render(self.number_list[30], True, (255, 0, 0), (255, 255, 255)), 307, 720),
            Text(font.render(self.number_list[31], True, (255, 0, 0), (255, 255, 255)), 390, 720),
            Text(font.render(self.number_list[32], True, (255, 0, 0), (255, 255, 255)), 472, 720),
            Text(font.render(self.number_list[33], True, (255, 0, 0), (255, 255, 255)), 555, 720),
            Text(font.render(self.number_list[34], True, (255, 0, 0), (255, 255, 255)), 637, 720),
            Text(font.render(self.number_list[35], True, (255, 0, 0), (255, 255, 255)), 720, 720)
        ]

        # DRAW HOTBAR NUMBERS
        for j in pygame_number_text:
            display.blit(j.surface, (j.x, j.y))

        # RENDER DEBUG MENU
        global screen_width, screen_height
        if player.debug_menu:
            font9 = pygame.font.Font(
                'assets/minecraft-font/MinecraftRegular-Bmg3.otf', 25)
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




def PygameInitialise() -> Context:
    global hasGeneratedOverworld, display, clock
    global netherGenerated, background, numList, call, difference, FPS, individual_frame, second_time, start, load, frame
    global hotbar_imgs, pygame_enchant_imgs, hotbar_order

    # Play Minecraft Music (Sweden)
    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/song" + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
    pygame.mixer.music.play()

    # [EXPORT] Create PYGAME inventory images for hotbar
    ITEM_IMAGES = {
        "wood": pygame.image.load("assets/item_imgs/oak_log.png").convert_alpha(), #0
        "planks": pygame.image.load("assets/item_imgs/oak_planks.png").convert_alpha(), #1
        "stick": pygame.image.load("assets/item_imgs/stick.png").convert_alpha(), #2
        "crafting_table": pygame.image.load("assets/item_imgs/crafting_table.png").convert_alpha(), #3
        "wooden_pickaxe": pygame.image.load("assets/item_imgs/wooden_pickaxe.png").convert_alpha(), #4
        "wooden_axe": pygame.image.load("assets/item_imgs/wooden_axe.png").convert_alpha(), #5
        "wooden_shovel": pygame.image.load("assets/item_imgs/wooden_shovel.png").convert_alpha(), #6
        "wooden_hoe": pygame.image.load("assets/item_imgs/wooden_hoe.png").convert_alpha(), #7
        "cobblestone": pygame.image.load("assets/item_imgs/cobblestone.png").convert_alpha(), #8
        "mine_entrance": pygame.image.load("assets/item_imgs/mine_entrance.png").convert_alpha(), #9
        "stone_pickaxe": pygame.image.load("assets/item_imgs/stone_pickaxe.png").convert_alpha(), #10
        "stone_axe": pygame.image.load("assets/item_imgs/stone_axe.png").convert_alpha(), #11
        "stone_shovel": pygame.image.load("assets/item_imgs/stone_shovel.png").convert_alpha(), #12
        "stone_hoe": pygame.image.load("assets/item_imgs/stone_hoe.png").convert_alpha(), #13
        "furnace": pygame.image.load("assets/item_imgs/furnace.png").convert_alpha(), #14
        "compressor": pygame.image.load("assets/item_imgs/compressor.png").convert_alpha(), #15
        "grindstone": pygame.image.load("assets/item_imgs/grindstone.png").convert_alpha(), #16
        "coal": pygame.image.load("assets/item_imgs/coal.png").convert_alpha(), #17
        "iron_ore": pygame.image.load("assets/item_imgs/iron_ore.png").convert_alpha(), #18
        "iron_ingot": pygame.image.load("assets/item_imgs/iron_ingot.png").convert_alpha(), #19
        "iron_pickaxe": pygame.image.load("assets/item_imgs/iron_pickaxe.png").convert_alpha(), #20
        "iron_axe": pygame.image.load("assets/item_imgs/iron_axe.png").convert_alpha(), #21
        "iron_shovel": pygame.image.load("assets/item_imgs/iron_shovel.png").convert_alpha(), #22
        "iron_hoe": pygame.image.load("assets/item_imgs/iron_hoe.png").convert_alpha(), #23
        "bucket": pygame.image.load("assets/item_imgs/bucket.png").convert_alpha(), #24
        "water_bucket": pygame.image.load("assets/item_imgs/water_bucket.png").convert_alpha(), #25
        "lava_bucket": pygame.image.load("assets/item_imgs/lava_bucket.png").convert_alpha(), #26
        "shield": pygame.image.load("assets/item_imgs/shield.png").convert_alpha(), #27
        "flint_and_steel": pygame.image.load("assets/item_imgs/flint_and_steel.png").convert_alpha(), #28
        "iron_plate": pygame.image.load("assets/item_imgs/iron_plate.png").convert_alpha(), #29
        "tier1_iron_plate": pygame.image.load("assets/item_imgs/tier1_iron_plate.png").convert_alpha(), #30
        "tier2_iron_plate": pygame.image.load("assets/item_imgs/tier2_iron_plate.png").convert_alpha(), #31
        "tier3_iron_plate": pygame.image.load("assets/item_imgs/tier3_iron_plate.png").convert_alpha(), #32
        "diamond": pygame.image.load("assets/item_imgs/diamond.png").convert_alpha(), #33
        "diamond_pickaxe": pygame.image.load("assets/item_imgs/diamond_pickaxe.png").convert_alpha(), #34
        "diamond_axe": pygame.image.load("assets/item_imgs/diamond_axe.png").convert_alpha(), #35
        "diamond_shovel": pygame.image.load("assets/item_imgs/diamond_shovel.png").convert_alpha(), #36
        "diamond_hoe": pygame.image.load("assets/item_imgs/diamond_hoe.png").convert_alpha(), #37
        "diamond_plate": pygame.image.load("assets/item_imgs/diamond_plate.png").convert_alpha(), #38
        "tier1_diamond_plate": pygame.image.load("assets/item_imgs/tier1_diamond_plate.png").convert_alpha(), #39
        "tier2_diamond_plate": pygame.image.load("assets/item_imgs/tier2_diamond_plate.png").convert_alpha(), #40
        "tier3_diamond_plate": pygame.image.load("assets/item_imgs/tier3_diamond_plate.png").convert_alpha(), #41
        "jukebox": pygame.image.load("assets/item_imgs/jukebox.png").convert_alpha(), #42
        "pigstep_disc": pygame.image.load("assets/item_imgs/pigstep_disc.png").convert_alpha(), #43
        "obsidian": pygame.image.load("assets/item_imgs/obsidian.png").convert_alpha(), #44
        "enchanting_table": pygame.image.load("assets/item_imgs/enchanting_table.png").convert_alpha(), #45
        "book": pygame.image.load("assets/item_imgs/book.png").convert_alpha(), #46
        "bookshelf": pygame.image.load("assets/item_imgs/bookshelf.png").convert_alpha(), #47
        "lapis": pygame.image.load("assets/item_imgs/lapis_lazuli.png").convert_alpha(), #48
        "bread": pygame.image.load("assets/item_imgs/bread.png").convert_alpha(), #49
        "golden_carrot": pygame.image.load("assets/item_imgs/golden_carrot.png").convert_alpha(), #50
        "golden_apple": pygame.image.load("assets/item_imgs/golden_apple.png"), #51
        "dirt": pygame.image.load("assets/item_imgs/dirt.png").convert_alpha(), #52
        "sand": pygame.image.load("assets/item_imgs/sand.png").convert_alpha(), #53
        "snow": pygame.image.load("assets/item_imgs/snow.png").convert_alpha(), #54
        "gravel": pygame.image.load("assets/item_imgs/gravel.png").convert_alpha(), #55
        "flint": pygame.image.load("assets/item_imgs/flint.png").convert_alpha(), #56
        "bed": pygame.image.load("assets/item_imgs/bed.png").convert_alpha(), #57
        "hay": pygame.image.load("assets/item_imgs/hay_bale.png").convert_alpha(), #58
        "none_img": pygame.image.load("assets/item_imgs/slot.png").convert_alpha(),  # White Space
        "fire": pygame.image.load("assets/item_imgs/fire.png").convert_alpha(),  # Fire when smelting
        "no_fire": pygame.image.load("assets/item_imgs/no_fire.png").convert_alpha(),  # No fire when smelting
    }

    # Create GLINT images for enchanted items
    glint_list = []
    glint_fullname_list = []
    glint_num_list = []
    new_glint_name_list = []
    int_glint_num_list = []
    item_names = []
    for filename in os.listdir('assets/glints'):
        glint_num_list.append(filename[5:-4])
        glint_fullname_list.append(filename[:-4])
    for i in glint_num_list:
        int_glint_num_list.append(int(i))
    new_glint_num_list = sorted(int_glint_num_list)
    for i in new_glint_num_list:
        index = glint_num_list.index(str(i))
        new_glint_name_list.append(glint_fullname_list[index])
    for i in new_glint_name_list:
        image = pygame.image.load('assets/glints/' + i + '.png').convert_alpha()
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
        "grass_tile": pygame.image.load('assets/tile_imgs/grass.png').convert(),  # Grass
        "netherrack_tile": pygame.image.load('assets/tile_imgs/netherrack.png').convert(),  # Netherrack
        "sand_tile": pygame.image.load('assets/tile_imgs/sand.png').convert(),  # Sand
        "snow_tile": pygame.image.load('assets/tile_imgs/snow.png').convert(),  # Snow
        "bookshelf_tile": pygame.image.load("assets/tile_imgs/bookshelf_tile.png").convert(),
        "coal_ore_tile": pygame.image.load("assets/tile_imgs/coal_ore_tile.png").convert(),
        "cobblestone_tile": pygame.image.load("assets/tile_imgs/cobblestone_tile.png").convert(),
        "diamond_ore_tile": pygame.image.load("assets/tile_imgs/diamond_ore_tile.png").convert(),
        "dirt_tile": pygame.image.load("assets/tile_imgs/dirt_tile.png").convert(),
        "gravel_tile": pygame.image.load("assets/tile_imgs/gravel_tile.png").convert(),
        "hay_bale_tile": pygame.image.load("assets/tile_imgs/hay_bale_tile.png").convert(),
        "iron_ore_tile": pygame.image.load("assets/tile_imgs/iron_ore_tile.png").convert(),
        "lapis_ore_tile": pygame.image.load("assets/tile_imgs/lapis_ore_tile.png").convert(),
        "lava_tile": pygame.image.load("assets/tile_imgs/lava_tile.png").convert(),
        "leaf_tile": pygame.image.load("assets/tile_imgs/leaf.png").convert_alpha(),
        "mine_entrance_tile": pygame.image.load("assets/tile_imgs/mine_entrance_tile.png").convert(),
        "oak_log_tile": pygame.image.load("assets/tile_imgs/oak_log_tile.png").convert(),
        "oak_planks_tile": pygame.image.load("assets/tile_imgs/oak_planks_tile.png").convert(),
        "obsidian_tile": pygame.image.load("assets/tile_imgs/obsidian_tile.png").convert(),
        "stone_tile": pygame.image.load("assets/tile_imgs/stone_tile.png").convert(),
        "tree_tile": pygame.image.load("assets/tile_imgs/oak_log_tile.png"),
        "water_tile": pygame.image.load("assets/tile_imgs/water_tile.png").convert(),
        "alpha_grass_tile": set_alpha("assets/tile_imgs/grass.png"),  # Grass
        "alpha_netherrack_tile": set_alpha("assets/tile_imgs/netherrack.png"),  # Netherrack
        "alpha_sand_tile": set_alpha("assets/tile_imgs/sand.png"),  # Sand
        "alpha_snow_tile": set_alpha("assets/tile_imgs/snow.png"),  # Snow
        "alpha_bookshelf_tile": set_alpha("assets/tile_imgs/bookshelf_tile.png"),
        "alpha_coal_ore_tile": set_alpha("assets/tile_imgs/coal_ore_tile.png"),
        "alpha_cobblestone_tile": set_alpha("assets/tile_imgs/cobblestone_tile.png"),
        "alpha_diamond_ore_tile": set_alpha("assets/tile_imgs/diamond_ore_tile.png"),
        "alpha_dirt_tile": set_alpha("assets/tile_imgs/dirt_tile.png"),
        "alpha_gravel_tile": set_alpha("assets/tile_imgs/gravel_tile.png"),
        "alpha_hay_bale_tile": set_alpha("assets/tile_imgs/hay_bale_tile.png"),
        "alpha_iron_ore_tile": set_alpha("assets/tile_imgs/iron_ore_tile.png"),
        "alpha_lapis_ore_tile": set_alpha("assets/tile_imgs/lapis_ore_tile.png"),
        "alpha_lava_tile": set_alpha("assets/tile_imgs/lava_tile.png"),
        "alpha_leaf_tile": set_alpha("assets/tile_imgs/leaf.png"),
        "alpha_mine_entrance_tile": set_alpha("assets/tile_imgs/mine_entrance_tile.png"),
        "alpha_oak_log_tile": set_alpha("assets/tile_imgs/oak_log_tile.png"),
        "alpha_oak_planks_tile": set_alpha("assets/tile_imgs/oak_planks_tile.png"),
        "alpha_obsidian_tile": set_alpha("assets/tile_imgs/obsidian_tile.png"),
        "alpha_stone_tile": set_alpha("assets/tile_imgs/stone_tile.png"),
        "alpha_tree_tile": set_alpha("assets/tile_imgs/oak_log_tile.png"),
        "alpha_water_tile": set_alpha("assets/tile_imgs/water_tile.png"),
        "bedrock_tile": set_alpha("assets/tile_imgs/bedrock.png"),
    }


    # [EXPORT] Create Breaking Images
    BREAKING_LIST = [
        pygame.image.load('assets/breaking/breaking1.png').convert_alpha(),
        pygame.image.load('assets/breaking/breaking2.png').convert_alpha(),
        pygame.image.load('assets/breaking/breaking3.png').convert_alpha(),
        pygame.image.load('assets/breaking/breaking4.png').convert_alpha(),
        pygame.image.load('assets/breaking/breaking5.png').convert_alpha(),
        pygame.image.load('assets/breaking/breaking6.png').convert_alpha()
    ]

    context = Context(
        ITEM_IMAGES = ITEM_IMAGES,
        TC_GLINTS = TC_GLINTS,
        TILE_IMAGES = TILE_IMAGES,
        BREAKING_LIST = BREAKING_LIST,
    )

    global player, World, Option1, Option2, Option3, Upgrade, screen, TimerRunning, world
    world = pygame.Surface((750, 750))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    World = TilecraftWorld(GetSeed())  # Create World
    player = Player(context)  # Create Player
    screen = Screen()  # Create Text Screen
    TimerRunning = True
    Upgrade = Button(82, 82, 112, 142, (158, 145, 115))
    Option1 = Button(487, 82, 255, 75, (158, 145, 115))
    Option2 = Button(487, 82, 255, 157, (158, 145, 115))
    Option3 = Button(487, 82, 255, 240, (158, 145, 115))
    hasGeneratedOverworld = True

    # return context to be passed around
    return context

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
    loading = pygame.image.load("assets/loading.png").convert()
    signal = Main()  #Start Game by Calling the Main Loop
    if signal == 'title screen':
        title_screen()
    elif signal == 'death screen':
        death_screen()

'''Function to handle all commands'''

#UP TO HERE
def commands(number, val):
    global screen, player, cobblestone_index, obsidian_index, item_name_list, FPS, experience, inventory_list, hotbar_order, hotbar_index, mode, hotbar_item, item_val_list, background, enchantable_list, flint_val, gravel_val, blacksmith_book, bool_blacksmith_iron, bool_blacksmith_diamond, bool_blacksmith_bread, blacksmith_iron, blacksmith_diamond, blacksmith_bread, endTime, bound_overworld_portal, overworld_portal, diaval, call, actualX, actualY, dimension
    for o in range(number):
        if val == "/lootvillagehay":  # Loot Village Hay
            if player.dimension == 'Overworld':
                if player.hotbar_item is not None:
                    if player.hotbar_item.name == "Stone Hoe":
                        for j in range(len(World.bound_village)):
                            if (World.bound_village[j][0][0] < player.x < World.bound_village[j][0][2]) and (
                                    World.bound_village[j][1][0] < player.y < World.bound_village[j][1][2]):
                                hay = RandomNum(25, 45)
                                inventory_add(Item("Hay Bale", hay, None, None))
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
                        beds = RandomNum(2, 7)
                        inventory_add(Item("Bed", beds, None, None))
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
                            blacksmith_iron = RandomNum(1, 7)
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
                            blacksmith_diamond = RandomNum(1, 5)
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
                            blacksmith_bread = RandomNum(1, 14)
                        else:
                            blacksmith_bread = 0

                        # UPDATE AND PRINT INVENTORY VALUES
                        if blacksmith_iron > 0:
                            screen.print(f"+{blacksmith_iron} Iron Ingot")
                            inventory_add(Item("Iron Ingot", blacksmith_iron, None, None))
                        if blacksmith_diamond > 0:
                            screen.print(f"+{blacksmith_diamond} Diamond")
                            inventory_add(Item("Diamond", blacksmith_diamond, None, None))
                        if blacksmith_bread > 0:
                            screen.print(f"+{blacksmith_bread} Bread")
                            inventory_add(Item("Bread", blacksmith_bread, None, None))

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
                        library_bookshelf = RandomNum(1, 3)
                        library_books = RandomNum(7, 14)
                        screen.print(f"+{library_bookshelf} Bookshelf")
                        screen.print(f"+{library_books} Books")
                        inventory_add(Item("Bookshelf", library_bookshelf, None, None))
                        inventory_add(Item("Book", library_books, None, None))
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
                        inventory_add(Item("Pigstep Disc", 1, None, None))
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
                    if i.name == "Pigstep Disc":  # Pigstep Disc
                        pigstep_disc_bool = True
                        break
            for i in player.inventory_list:
                if i is not None:
                    if i.name == "Jukebox":  # Jukebox
                        jukebox_bool = True
                        break

            if pigstep_disc_bool and jukebox_bool:  # Play Pigstep
                pygame.mixer.init()
                pygame.mixer.music.load("assets/pigstep.mp3")
                pygame.mixer.music.set_volume(10)
                pygame.mixer.music.play()
                MusicPlayer(player.advancements) #Update Advancement and Speedrun Details
            else:
                screen.print("Error: Not Enough Resources")
        elif val == '/lootruinedportal':  # Loot Ruined Portal
            if player.dimension == 'Overworld':
                for j in range(len(World.bound_ruined_portal)):
                    if (World.bound_ruined_portal[j][0][0] < player.x < World.bound_ruined_portal[j][0][2]) and (
                            World.bound_ruined_portal[j][1][0] < player.y < World.bound_ruined_portal[j][1][2]):
                        R_iron_val = RandomNum(2, 7)
                        R_flint_val = RandomNum(1, 3)
                        R_golden_carrot_val = RandomNum(0, 6)
                        R_golden_apple_val = RandomNum(0, 2)
                        R_obsidian_val = RandomNum(0, 3)
                        inventory_add(Item("Iron Ingot", R_iron_val, None, None))  # Add Iron Ingot
                        screen.print(f"+{R_iron_val} Iron Ingot")
                        inventory_add(Item("Flint", R_flint_val, None, None))  # Add Flint
                        screen.print(f"+{R_flint_val} Flint")
                        if R_golden_carrot_val > 0:  # Add Golden Carrot
                            screen.print(f"+{R_golden_carrot_val} Golden Carrot")
                            inventory_add(Item("Golden Carrot", R_golden_carrot_val, None, None))
                        if R_golden_apple_val > 0:  # Add Golden Apple
                            screen.print(f"+{R_golden_apple_val} Golden Apple")
                            inventory_add(Item("Golden Apple", R_golden_apple_val, None, None))
                        if R_obsidian_val > 0:  # Add Obsidian
                            screen.print(f"+{R_obsidian_val} Obsidian")
                            inventory_add(Item("Obsidian", R_obsidian_val, None, None))
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
                                if i.name == 'Flint and Steel':  # Test for flint and steel
                                    flint_and_steel_bool = True
                                    break
                        if obsidian_num == 0:
                            obsidian_bool = True
                        for i in player.inventory_list:
                            if i is not None:
                                if i.name == "Obsidian" and i.number >= obsidian_num:  # Test for enough obsidian
                                    obsidian_index = player.inventory_list.index(i)
                                    obsidian_bool = True
                                    break

                        if flint_and_steel_bool and obsidian_bool:
                            if obsidian_num > 0:
                                player.inventory_list[obsidian_index].number -= obsidian_num
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
                print_cheats(list(ITEM_TYPES.keys()))
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
    pygame.mixer.music.load(random.choice(["assets/music/song6.mp3", "assets/music/song8.mp3"]))
    pygame.mixer.music.play()

    # Create tkinter window
    window = tkinter.Tk()
    window.title('Tilecraft Beta 1.0 Pre-Release 3')
    window.geometry('750x750')

    global screen_width, screen_height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Create background image
    bg = tkinter.PhotoImage(file="assets/background_vB1_0_pre3.png")

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
    all_lists = [player.enchanting_list, player.inventory_list, player.craft_list,
                 player.grid_list, player.smelting_list, player.compressor_list, player.grindstone_list]
    for i in all_lists:
        for j in range(len(i)):
            if i[j] is not None:
                if i[j].number <= 0:
                    i[j] = None
                elif i[j].durability is not None:
                    if i[j].durability <= 0:
                        i[j] = None
    player.enchanting_list, player.inventory_list, player.craft_list, \
    player.grid_list, player.smelting_list, player.compressor_list, player.grindstone_list = all_lists
    if player.holding_item is not None:
        if player.holding_item.number <= 0:
            player.holding_item = None
        elif player.holding_item.durability is not None:
            if player.holding_item.durability <= 0:
                player.holding_item = None

def Crafting():
    if player.mode == "inventory":
        global craft_list
        if player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is None:
            if player.craft_list[0].name == 'Oak Log':
                player.craft_list[4] = Item("Oak Planks", 4, None, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is not None and player.craft_list[3] is None:
            if player.craft_list[0].name == 'Oak Planks' and player.craft_list[2].name == 'Oak Planks':
                player.craft_list[4] = Item("Stick", 4, None, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is not None and player.craft_list[2] is not None and player.craft_list[3] is not None:
            if player.craft_list[0].name == 'Oak Planks' and player.craft_list[1].name == 'Oak Planks' and player.craft_list[2].name == 'Oak Planks' and player.craft_list[3].name == 'Oak Planks':
                player.craft_list[4] = Item("Crafting Table", 1, None, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is not None:
            if player.craft_list[0].name == 'Iron Ingot' and player.craft_list[3].name == 'Flint':
                player.craft_list[4] = Item("Flint and Steel", 1, None, None)
            else:
                player.craft_list[4] = None
        else:
            player.craft_list[4] = None

def GridCraft():
    if player.mode == "crafting":
        for recipe in CRAFTING_RECIPES.values():
            if recipe.canCraft(player):
                #print(recipe.requirements, recipe.result.name)
                recipe.craft(player)
                return
            else:
                player.grid_list[9] = None

def EnchantUpgrade():
    global player
    if player.enchanting_list[2] is not None and player.enchanting_level < 5:
        if player.enchanting_list[2].name == 'Bookshelf' and player.enchanting_list[2].number > 3:
            player.enchanting_list[2].number -= 4
            player.enchanting_level += 1
            EnchantSet()  # Set Enchants


def EnchantSet():
    global player
    if player.enchanting_list[0] is not None:
        if player.enchanting_list[0].enchantments is None:
            player.level1 = 0
            player.level2 = 0
            player.level3 = 0
            player.optional_enchant2 = None
            player.optional_enchant3 = None
            if player.enchanting_level == 0:  # LEVEL 0
                player.level1 = 0
                player.level2 = 0
                player.level3 = RandomNum(0, 1)
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 1:  # LEVEL 1
                player.level1 = 1
                player.level2 = RandomNum(1, 2)
                player.level3 = 2
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 2:  # LEVEL 2
                player.level1 = 2
                player.level2 = RandomNum(2, 3)
                player.level3 = 3
                player.optional_enchant2 = None
                player.optional_enchant3 = None
            elif player.enchanting_level == 3:  # LEVEL 3
                player.level1 = 3
                player.level2 = RandomNum(3, 4)
                player.level3 = 4
                player.optional_enchant2 = None
                player.optional_enchant3 = RandomNum(0, 1)
            elif player.enchanting_level == 4:  # LEVEL 4
                player.level1 = 4
                player.level2 = RandomNum(4, 5)
                player.level3 = 5
                player.optional_enchant2 = RandomNum(0, 1)
                player.optional_enchant3 = RandomNum(1, 2)
            else:  # LEVEL 5
                player.level1 = RandomNum(4, 5)
                player.level2 = 5
                player.level3 = 5
                player.optional_enchant2 = RandomNum(1, 2)
                player.optional_enchant3 = RandomNum(2, 3)

            if player.enchanting_list[0].itemType == 'Tier1' or player.enchanting_list[0].itemType == 'Tier2' or player.enchanting_list[0].itemType == 'Tier3':  # Armour
                player.option_list[0] = f'Protection {player.level1}'
                player.option_list[1] = f'Protection {player.level2}'
                player.option_list[2] = f'Protection {player.level3}'
            elif player.enchanting_list[0].itemType == 'Pickaxe' or player.enchanting_list[0].itemType == 'Axe' or player.enchanting_list[0].itemType == 'Shovel' or player.enchanting_list[0].itemType == 'Hoe':  # Tools
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
        if player.enchanting_list[1].number > 0 and player.experience_levels > 0:  # REQUIRE 1 Lapis + 1 Experience
            if player.option_list[0] != 'N/A' and player.enchanting_list[0] is not None:
                player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[0][0:-2], int(player.option_list[0][-1])]], player.enchanting_list[0].number)
                player.enchanting_list[1].number -= 1
                player.experience_levels -= 1
                EnchantSet()  # Remove Enchants


def Enchant2():  # Second ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2)
    global player
    if player.enchanting_list[1] is not None:
        if player.enchanting_list[1].number > 1 and player.experience_levels > 1:  # REQUIRE 2 Lapis + 2 Experience
            if player.option_list[1] != 'N/A' and player.enchanting_list[0] is not None:  # Test for None
                if player.optional_enchant2 is not None:  # Extra enchantment
                    if player.optional_enchant2 > 0:  # Enchantment level > 0
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2],
                                                                                                                             int(player.option_list[1][-1])], ['Unbreaking', player.optional_enchant2]], player.enchanting_list[0].durability)
                    else:  # No extra enchantment
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2], int(player.option_list[1][-1])]], player.enchanting_list[0].durability)
                else:
                    player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2], int(player.option_list[1][-1])]], player.enchanting_list[0].durability)
                player.enchanting_list[1].number -= 2
                player.experience_levels -= 2
                EnchantSet()  # Remove Enchants


def Enchant3():  # Third ENCHANTING BOX (ENCHANTS start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3)
    global player
    if player.enchanting_list[1] is not None:
        if player.enchanting_list[1].number > 2 and player.experience_levels > 2:  # REQUIRE 3 Lapis + 3 Experience
            if player.option_list[2] != 'N/A' and player.enchanting_list[0] is not None:  # Test for None
                if player.optional_enchant3 is not None:  # Extra enchantment
                    if player.optional_enchant3 > 0:  # Enchantment level > 0
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])], ['Unbreaking', player.optional_enchant3]],
                                                         player.enchanting_list[0].durability)
                    else:  # No extra enchantment
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])]], player.enchanting_list[0].durability)
                else:  # No extra enchantment
                    player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])]], player.enchanting_list[0].durability)
                player.enchanting_list[1].number -= 3
                player.experience_levels -= 3
                EnchantSet()  # Remove Enchants

#add items to inventory
def inventory_add(item):
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
    if item is not None:
        if item.stackNum == 64:
            Call = False
            for j in range(len(player.inventory_list)):
                if player.inventory_list[j] is not None:
                    if item.name == player.inventory_list[j].name and player.inventory_list[j].number < 64:
                        player.inventory_list[j] = Item(player.inventory_list[j].name, item.number + player.inventory_list[j].number, player.inventory_list[j].enchantments, player.inventory_list[j].durability) #Add values
                        Call = True
                        break
            if not Call:
                for j in range(len(player.inventory_list)):
                    if player.inventory_list[j] is None:
                        player.inventory_list[j] = item
                        break
        elif item.stackNum == 1:
            for j in range(len(player.inventory_list)):
                if player.inventory_list[j] is None:
                    player.inventory_list[j] = item
                    break

    # Separate Items into stacks (Armour = Stack of 1), (Item = Stack of 64)
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].stackNum == 1 and player.inventory_list[i].number > 1:  # Armour
                count = 0
                while count < player.inventory_list[i].number:  # Separate into individual items
                    if None in player.inventory_list:
                        none_index = player.inventory_list.index(None)
                        player.inventory_list[none_index] = Item(player.inventory_list[i].name, 1, player.inventory_list[i].enchantments, player.inventory_list[i].durability)
                    count += 1
                player.inventory_list[i] = None
            elif player.inventory_list[i].stackNum == 64 and player.inventory_list[i].number > 64:  # Item
                while player.inventory_list[i].number > 64:  # Separate into stacks of 64
                    player.inventory_list[i].number -= 64
                    if None in player.inventory_list:
                        none_index = player.inventory_list.index(None)
                        player.inventory_list[none_index] = Item(player.inventory_list[i].name, 64, player.inventory_list[i].enchantments, player.inventory_list[i].durability)
                if None in player.inventory_list:  # Remainder (Less than 64)
                    none_index = player.inventory_list.index(None)
                    player.inventory_list[none_index] = Item(player.inventory_list[i].name, player.inventory_list[i].number, player.inventory_list[i].enchantments, player.inventory_list[i].durability)
                    player.inventory_list[i] = None
#UP TO HERE
# Render Inventory List to Image and Number List
def image_render(context: Context):
    global pygame_enchant_imgs, player, enchant_name_list, enchant_img_list, enchanting_list, enchanting_image_list, enchanting_number_list, experience, smelting_time, no_fire, fire, fuel_val, inventory_list, image_list, number_list, armour_image_list, craft_image_list, craft_number_list, grid_image_list, grid_number_list, grid_list, smelting_list, smelt_image_list, smelt_number_list, fuel_img
    player.image_list, player.number_list, player.armour_image_list, player.craft_image_list, \
    player.craft_number_list, player.grid_image_list, player.grid_number_list, player.smelt_image_list, \
    player.smelt_number_list, player.enchanting_image_list, player.enchanting_number_list, player.compressor_image_list, \
    player.compressor_number_list, player.layer_list, player.grindstone_image_list, player.grindstone_number_list = \
        [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

    def item_image(item_name: str) -> pygame.Surface:
        return context.ITEM_IMAGES[ITEM_IMAGE_MAPPING[item_name]]

    '''Inventory Section'''

    # Remove Values with 0
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].number == 0:
                player.inventory_list[i] = None

    # Create images list and number list
    for i in player.inventory_list:
        if i is None:  # Set White Background for NONE Slots
            player.image_list.append(context.ITEM_IMAGES["none_img"])
            player.number_list.append('')
        else:
            player.image_list.append(item_image(i.name))
            player.number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].number == 1:
                player.number_list[i] = ''

    #Create Holding Item for Inventory
    if player.holding_item is None:
        player.holding_item_image = context.ITEM_IMAGES["none_img"]
        player.holding_item_number = ''
    else:
        player.holding_item_image = item_image(player.holding_item.name)
        player.holding_item_number = str(player.holding_item.number)

    if player.holding_item is not None:
        if player.holding_item.number == 1:
            player.holding_item_number = ''

    '''Armour Section'''

    # Create armour image list for armour slots
    for j in player.armour_list:
        if j is None:  # Set White Background for NONE Slots
            player.armour_image_list.append(context.ITEM_IMAGES["none_img"])
        else:
            player.armour_image_list.append(item_image(j.name))

    for i in player.armour_list:
        if i is not None:
            if i.name == 'Tier 1 Iron Plate':
                player.layer_list.append([(200, 200, 200), 1])
            elif i.name == 'Tier 2 Iron Plate':
                player.layer_list.append([(200, 200, 200), 2])
            elif i.name == 'Tier 3 Iron Plate':
                player.layer_list.append([(200, 200, 200), 3])
            elif i.name == 'Tier 1 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 1])
            elif i.name == 'Tier 2 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 2])
            elif i.name == 'Tier 3 Diamond Plate':
                player.layer_list.append([(75, 237, 219), 3])
        else:
            player.layer_list.append(None)

    '''Crafting Section (2x2)'''

    for i in player.craft_list:
        if i is None:  # Set White Background for NONE Slots
            player.craft_image_list.append(context.ITEM_IMAGES["none_img"])
            player.craft_number_list.append('')
        else:
            player.craft_image_list.append(item_image(i.name))
            player.craft_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for j in range(len(player.craft_list)):
        if player.craft_list[j] is not None:
            if player.craft_list[j].number == 1:
                player.craft_number_list[j] = ''

    '''Crafting Section (3x3)'''

    for i in player.grid_list:
        if i is None:  # Set White Background for NONE Slots
            player.grid_image_list.append(context.ITEM_IMAGES["none_img"])
            player.grid_number_list.append('')
        else:
            player.grid_image_list.append(item_image(i.name))
            player.grid_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.grid_list)):
        if player.grid_list[i] is not None:
            if player.grid_list[i].number == 1:
                player.grid_number_list[i] = ''

    '''Smelting Section'''

    # Remove Value if Number is 0
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i].number == 0:
                player.smelting_list[i] = None

    # Convert List to Images and Numbers
    for i in player.smelting_list:
        if i is None:  # Set White Background for NONE Slots
            player.smelt_image_list.append(context.ITEM_IMAGES["none_img"])
            player.smelt_number_list.append('')
        else:
            player.smelt_image_list.append(item_image(i.name))
            player.smelt_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i].number == 1:
                player.smelt_number_list[i] = ''

    '''Enchanting Section'''

    # Remove Value if Number is 0
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i].number == 0:
                player.enchanting_list[i] = None

    # Convert List to Images and Numbers
    for i in player.enchanting_list:
        if i is None:  # Set White Background for NONE Slots
            player.enchanting_image_list.append(context.ITEM_IMAGES["none_img"])
            player.enchanting_number_list.append('')
        else:
            player.enchanting_image_list.append(item_image(i.name))
            player.enchanting_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i].number == 1:
                player.enchanting_number_list[i] = ''

    '''Compressing Section'''

    # Remove Value if Number is 0
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].number == 0:
                player.compressor_list[i] = None

    for i in player.compressor_list:
        if i is None: #Set Background for NONE Slots
            player.compressor_image_list.append(context.ITEM_IMAGES["none_img"])
            player.compressor_number_list.append('')
        else:
            player.compressor_image_list.append(item_image(i.name))
            player.compressor_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].number == 1:
                player.compressor_number_list[i] = ''

    '''Grindstone Section'''

    # Remove Value if Number is 0
    for i in range(len(player.grindstone_list)):
        if player.grindstone_list[i] is not None:
            if player.grindstone_list[i].number == 0:
                player.grindstone_list[i] = None

    for i in player.grindstone_list:
        if i is None:  # Set Background for NONE Slots
            player.grindstone_image_list.append(context.ITEM_IMAGES["none_img"])
            player.grindstone_number_list.append('')
        else:
            player.grindstone_image_list.append(item_image(i.name))
            player.grindstone_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.grindstone_list)):
        if player.grindstone_list[i] is not None:
            if player.grindstone_list[i].number == 1:
                player.grindstone_number_list[i] = ''

title_screen()