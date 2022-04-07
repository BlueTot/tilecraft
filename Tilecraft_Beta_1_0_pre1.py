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

#Print Item List
def print_cheats(name):
    global screen
    screen.print("CODE   ITEM NAME")
    screen.print('-' * 25)
    for i in range(len(name)):
        screen.print((str(i) + ' ' * (7 - len(str(i))) + str(name[i])))

#/give command
def give(item_id):
    global screen, TC_ITEMS
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
        length = len(list(TC_ITEMS.keys())) - 1
        if 0 <= code <= length:
            add_item = Item(list(TC_ITEMS.keys())[code], amount, None)
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
                    return Item(player.hotbar_item.name, player.hotbar_item.number, enchantments)
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
def advancements_update(advancements, inventory_list, armour_list, dimension, load, start):
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
    font = pygame.font.Font('images_vB1_0_pre1/monofur/monof55.ttf', 25)
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

class Tile:
    def __init__(self, tile, x, y, image):
        global TC_TILES
        self.tile = tile
        self.x = x
        self.y = y
        self.image = image
        self.breaking_time = TC_TILES[self.tile].breaking_time
        self.requireTool = TC_TILES[self.tile].tool
        self.requireToolTier = TC_TILES[self.tile].tier

class Chunk:
    def __init__(self, x, y, biome):
        self.x = x
        self.y = y
        self.biome = biome

def Random(Seed, Pos, Range):
    x, y = Pos
    a, b = Range
    random.seed((Seed % 2048) * 2 - 5)
    for i in range(x % 50):
        for j in range(y % 50 - 1):
            value = random.randint(a, b)
    value = random.randint(a, b)
    return value

def OverworldGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list


def OverworldGenerate(ChunkX, ChunkY, villages, waters, lavas, ruined_portals, obsidian_counts,
                      generated_list, bound_village, bound_village2, bound_village3, bound_village4,
                      bound_water, bound_water2, bound_lava, bound_ruined_portal,
                      bound_ruined_portal2, seed, UnderTiles, Tiles):
    num = Random(seed, (ChunkX, ChunkY), (1, 25))
    if num == 1 or num == 2:
        villages.append([ChunkX - 12, ChunkY - 12])  # Village
        bound_village.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 1
        bound_village2.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 2
        bound_village3.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 3
        bound_village4.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 4
    elif num == 7 or num == 8 or num == 9:
        waters.append([ChunkX - 14, ChunkY - 14])  # Water Pool
        bound_water.append([[ChunkX - 14 - 10 / 32, ChunkX - 14, ChunkX - 14 + 10 / 32], [ChunkY - 14 - 10 / 32, ChunkY - 14, ChunkY - 14 + 10 / 32]])  # Bounding box for water pool 1
        bound_water2.append([[ChunkX - 14 - 10 / 32, ChunkX - 14, ChunkX - 14 + 10 / 32], [ChunkY - 14 - 10 / 32, ChunkY - 14, ChunkY - 14 + 10 / 32]])  # Bounding box for water pool 2
    elif num == 10 or num == 11 or num == 12:
        lavas.append([ChunkX - 8, ChunkY - 8])  # Lava Pool
        bound_lava.append([[ChunkX - 8 - 10 / 32, ChunkX - 8, ChunkX - 8 + 10 / 32], [ChunkY - 8 - 10 / 32, ChunkY - 8, ChunkY - 8 + 10 / 32]])  # bounding box for lava pool
    elif num == 15 or num == 16 or num == 17:
        ruined_portals.append([ChunkX - 1, ChunkY - 1])  # Ruined Portal
        obsidian_counts.append(int(Random(seed, (ChunkX, ChunkY), (5, 10))))  # Obsidian remaining in ruined portal
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
            if land >= -0.075:
                if temperature < -0.1:
                    UnderTiles[(i, j)] = Tile('Snow', i, j, alpha_snow_tile)
                elif -0.1 <= temperature <= 0.1:
                    UnderTiles[(i, j)] = Tile('Grass', i, j, alpha_grass_tile)
                elif temperature > 0.1:
                    UnderTiles[(i, j)] = Tile('Sand', i, j, alpha_sand_tile)
            else:
                UnderTiles[(i, j)] = Tile('Water', i, j, alpha_water_tile)
            Tiles[(i, j)] = Tile('Air', i, j, None)
    for i in range(ChunkX, ChunkX + 16, 4):
        for j in range(ChunkY, ChunkY + 16, 4):
            x = i + Random(seed, (i, j), (1, 4))
            y = j + Random(seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and Random(seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and Random(seed, (x, y), (1, 16)) == 1:
                canGenerateBoulder = True
            if canGenerateTree:
                for X in range(-1, 2, 1):
                    for Y in range(-1, 2, 1):
                        if not (X == 0 and Y == 0):
                            Tiles[(x + X, y + Y)] = Tile("Leaf", x + X, y + Y, leaf_tile)
                        else:
                            Tiles[(x + X, y + Y)] = Tile("Tree", x, y, tree_tile)
            if canGenerateBoulder:
                for X in range(4):
                    for Y in range(4):
                        if not (X == 0 and Y == 0 or X == 3 and Y == 0 or X == 0 and Y == 3 or X == 3 and Y == 3):
                            Tiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y, stone_tile)

    return villages, waters, lavas, ruined_portals, obsidian_counts, generated_list, \
           bound_village, bound_village2, bound_village3, bound_village4, bound_water, \
           bound_water2, bound_lava, bound_ruined_portal, bound_ruined_portal2, UnderTiles, Tiles


def SpawnOverworldGenerate(seed):
    global alpha_grass_tile, alpha_sand_tile, alpha_snow_tile, alpha_water_tile, tree_tile, leaf_tile, stone_tile
    li_vil = []
    li_w = []
    li_l = []
    li_ruined_portal = []
    villages = []
    waters = []
    lavas = []
    ruined_portals = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = Random(seed, (i, j), (1, 25))
            if num == 1 or num == 2:
                li_vil.append([i, j])
            elif num == 7 or num == 8 or num == 9:
                li_w.append([i, j])
            elif num == 10 or num == 11 or num == 12:
                li_l.append([i, j])
            elif num == 15 or num == 16 or num == 17:
                li_ruined_portal.append([i, j])

    # Village (Chunk Code: 4, 4)
    for i in li_vil:
        villages.append([i[0] - 12, i[1] - 12])

    # Water Pool (Chunk Code: 2, 2)
    for i in li_w:
        waters.append([i[0] - 14, i[1] - 14])

    # Lava Pool (Chunk Code: 8, 8)
    for i in li_l:
        lavas.append([i[0] - 8, i[1] - 8])

    # Ruined Portal (Chunk Code: 15, 15)
    for i in li_ruined_portal:
        ruined_portals.append([i[0] - 1, i[1] - 1])
    obsidian_counts = []
    for i in range(len(ruined_portals)):
        obsidian_counts.append(int(Random(seed, (ruined_portals[i][0] + 1, ruined_portals[i][1] + 1), (5, 10))))

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
            if land >= -0.075:
                if temperature < -0.1:
                    UnderTiles[(i, j)] = Tile('Snow', i, j, alpha_snow_tile)
                elif -0.1 <= temperature <= 0.1:
                    UnderTiles[(i, j)] = Tile('Grass', i, j, alpha_grass_tile)
                elif temperature > 0.1:
                    UnderTiles[(i, j)] = Tile('Sand', i, j, alpha_sand_tile)
            else:
                UnderTiles[(i, j)] = Tile('Water', i, j, alpha_water_tile)
            Tiles[(i, j)] = Tile('Air', i, j, None)
    for i in range(-64, 81, 4):
        for j in range(-64, 81, 4):
            x = i + Random(seed, (i, j), (1, 4))
            y = j + Random(seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and Random(seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and Random(seed, (x, y), (1, 16)) == 1:
                canGenerateBoulder = True
            if canGenerateTree:
                for X in range(-1, 2, 1):
                    for Y in range(-1, 2, 1):
                        if not(X == 0 and Y == 0):
                            Tiles[(x + X, y + Y)] = Tile("Leaf", x + X, y + Y, leaf_tile)
                        else:
                            Tiles[(x + X, y + Y)] = Tile("Tree", x, y, tree_tile)
            if canGenerateBoulder:
                for X in range(4):
                    for Y in range(4):
                        if not (X == 0 and Y == 0 or X == 3 and Y == 0 or X == 0 and Y == 3 or X == 3 and Y == 3):
                            Tiles[(x + X, y + Y)] = Tile("Stone", x + X, y + Y, stone_tile)

    return villages, waters, lavas, ruined_portals, obsidian_counts, UnderTiles, Tiles

def SpawnOverworldBoundGenerate(villages, waters, lavas, ruined_portals):
    bound_village, bound_water, bound_lava, bound_ruined_portal = [], [], [], []
    for i in range(len(villages)):
        bound_village.append([])
        for j in range(2):
            bound_village[i].append([villages[i][j] - 10 / 32, villages[i][j], villages[i][j] + 10 / 32])
    for i in range(len(waters)):
        bound_water.append([])
        for j in range(2):
            bound_water[i].append([waters[i][j] - 10 / 32, waters[i][j], waters[i][j] + 10 / 32])
    for i in range(len(lavas)):
        bound_lava.append([])
        for j in range(2):
            bound_lava[i].append([lavas[i][j] - 10 / 32, lavas[i][j], lavas[i][j] + 10 / 32])
    for i in range(len(ruined_portals)):
        bound_ruined_portal.append([])
        for j in range(2):
            bound_ruined_portal[i].append([ruined_portals[i][j] - 10 / 32, ruined_portals[i][j], ruined_portals[i][j] + 10 / 32])
    return bound_village, bound_water, bound_lava, bound_ruined_portal

def GenerateOres(ore, img, vein_size, Tiles, x, y):
    global stone_tile
    if vein_size == 1:
        Tiles[(x, y)] = Tile(ore, x, y, img)
    elif vein_size == 2:
        Tiles[(x, y)] = Tile(ore, x, y, img)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y, img)
    elif vein_size == 3:
        Tiles[(x, y)] = Tile(ore, x, y, img)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y, img)
        Tiles[(x, y + 1)] = Tile(ore, x, y + 1, img)
    elif vein_size == 4:
        Tiles[(x, y)] = Tile(ore, x, y, img)
        Tiles[(x + 1, y)] = Tile(ore, x + 1, y, img)
        Tiles[(x, y + 1)] = Tile(ore, x, y + 1, img)
        Tiles[(x + 1, y + 1)] = Tile(ore, x + 1, y + 1, img)
    return Tiles

def UndergroundGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list

def SpawnUndergroundGenerate(seed):
    global stone_tile, alpha_stone_tile, coal_ore_tile, iron_ore_tile, lapis_ore_tile, diamond_ore_tile, alpha_lava_tile
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
                    Tiles[(i + x, j + y)] = Tile("Stone", i + x, j + y, stone_tile)
                    UnderTiles[(i + x, j + y)] = Tile("Stone", i + x, j + y, alpha_stone_tile)
            if biome < 0:
                num = Random(seed, (i, j), (1, 9))
                if num == 1 or num == 2 or num == 3:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", coal_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", iron_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", lapis_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", diamond_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
            else:
                num = Random(seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", coal_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", iron_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
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
                Tiles[(i, j)] = Tile("Air", i, j, None)
                biome = noise.pnoise2(i / 50,
                                      j / 50,
                                      octaves=8,
                                      persistence=1 / 2,
                                      lacunarity=1 / 2,
                                      repeatx=1024,
                                      repeaty=1024,
                                      base=seed % 600)
                if biome < 0:
                    UnderTiles[(i, j)] = Tile("Lava", i, j, alpha_lava_tile)
    return UnderTiles, Tiles

def UndergroundGenerate(seed, ChunkX, ChunkY, UnderTiles, Tiles, UndergroundGeneratedList):
    global stone_tile, alpha_stone_tile, alpha_lava_tile
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
                    Tiles[(i + x, j + y)] = Tile("Stone", i + x, j + y, stone_tile)
                    UnderTiles[(i + x, j + y)] = Tile("Stone", i + x, j + y, alpha_stone_tile)
            if biome < 0:
                num = Random(seed, (i, j), (1, 12))
                if num == 1 or num == 2 or num == 3:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", coal_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", iron_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", lapis_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", diamond_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
            else:
                num = Random(seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", coal_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = Random(seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", iron_ore_tile, vein_size, Tiles, i + Random(seed, (i, j), (1, 8)), j + Random(seed, (i, j), (1, 8)))
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
                Tiles[(i, j)] = Tile("Air", i, j, None)
                biome = noise.pnoise2(i / 50,
                                      j / 50,
                                      octaves=8,
                                      persistence=1 / 2,
                                      lacunarity=1 / 2,
                                      repeatx=1024,
                                      repeaty=1024,
                                      base=seed % 600)
                if biome < 0:
                    UnderTiles[(i, j)] = Tile("Lava", i, j, alpha_lava_tile)
    UndergroundGeneratedList.append([ChunkX, ChunkY])
    return UnderTiles, Tiles

def UndergroundGeneratePortal(x, y, Tiles):
    global mine_entrance_tile
    Tiles[(x, y)] = Tile("Mine Entrance", x, y, mine_entrance_tile)
    for i in range(x - 1, x + 2, 1):
        for j in range(y - 1, y + 2, 1):
            if Tiles[(i, j)].tile != "Mine Entrance":
                Tiles[(i, j)] = Tile("Air", i, j, None)
    return Tiles

def OverworldGeneratePortal(x, y, Tiles):
    global mine_entrance_tile
    Tiles[(x, y)] = Tile("Mine Entrance", x, y, mine_entrance_tile)
    for i in range(x - 1, x + 2, 1):
        for j in range(y - 1, y + 2, 1):
            if Tiles[(i, j)].tile != "Mine Entrance":
                Tiles[(i, j)] = Tile("Air", i, j, None)
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
            bound_bastion[i].append([bastions[i][j] - 10 / 32, bastions[i][j], bastions[i][j] + 10 / 32])
    for i in range(len(fortresses)):
        bound_fortress.append([])
        for j in range(2):
            bound_fortress[i].append([fortresses[i][j] - 10 / 32, fortresses[i][j], fortresses[i][j] + 10 / 32])
    return bound_bastion, bound_fortress

def NetherGenerate(ChunkX, ChunkY, bastions, fortresses, generated_list, bound_bastion, seed):
    num = Random(seed, (ChunkX, ChunkY), (1, 15))
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
        self.empty_vil1 = []
        self.empty_vil2 = []
        self.empty_vil3 = []
        self.empty_vil4 = []
        self.empty_vil_total = []
        self.empty_water = []
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

        self.village, self.water, self.lava, self.ruined_portal, self.obsidian_counts, \
        self.UnderTiles, self.Tiles = SpawnOverworldGenerate(self.seed)  # Spawn Generation for Structures and Biomes
        self.bound_village, self.bound_water, \
        self.bound_lava, self.bound_ruined_portal = SpawnOverworldBoundGenerate(
            self.village, self.water, self.lava, self.ruined_portal)  # Spawn Bounding Box Generation
        self.bound_village2 = self.bound_village.copy()
        self.bound_village3 = self.bound_village.copy()
        self.bound_village4 = self.bound_village.copy()
        self.bound_water2 = self.bound_water.copy()
        self.bound_ruined_portal2 = self.bound_ruined_portal.copy()
        self.overworld_generated_list = OverworldGeneratedList()

    #Generate Chunks Per Frame
    def generate_chunks(self):
        global hasGeneratedUnderground
        if player.dimension == 'Overworld':
            for i in self.render_list:
                if i not in self.overworld_generated_list:
                    self.village, self.water, self.lava, self.ruined_portal, self.obsidian_counts, self.overworld_generated_list, \
                    self.bound_village, self.bound_village2, self.bound_village3, self.bound_village4, self.bound_water, \
                    self.bound_water2, self.bound_lava, self.bound_ruined_portal, self.bound_ruined_portal2, self.UnderTiles, self.Tiles = \
                    OverworldGenerate(i[0], i[1], self.village, self.water, self.lava, self.ruined_portal,
                                                      self.obsidian_counts, self.overworld_generated_list, self.bound_village,
                                                      self.bound_village2, self.bound_village3, self.bound_village4,
                                                      self.bound_water, self.bound_water2, self.bound_lava,
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

    def render(self, display):
        global hotbar_imgs, slot, number_list, experience, pygame_enchant_imgs, enchant_name_list, player, hasGeneratedUnderground, bedrock_tile
        player.health_hunger_update()

        # DRAW OVERWORLD DIMENSION
        if player.dimension == "Overworld":
            for key, value in self.UnderTiles.items(): #background tiles (no collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.image is not None:
                        display.blit(value.image, (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                    else:
                        display.blit(bedrock_tile, (value.x * 32 - player.left, value.y * 32 - player.top))
                    pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            for key, value in self.Tiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.image is not None:
                        display.blit(value.image, (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                        pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            # DRAWING OVERWORLD STRUCTURES
            for k in range(len(self.village)):
                if -32 <= (self.village[k][0] * 32 - player.left) <= 1032 and -32 <= (self.village[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (255, 165, 0), (self.village[k][0] * 32 - player.left, self.village[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.lava)):
                if -32 <= (self.lava[k][0] * 32 - player.left) <= 1032 and -32 <= (self.lava[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (255, 0, 0), (self.lava[k][0] * 32 - player.left, self.lava[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.water)):
                if -32 <= (self.water[k][0] * 32 - player.left) <= 1032 and -32 <= (self.water[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (173, 216, 230), (self.water[k][0] * 32 - player.left, self.water[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.ruined_portal)):
                if -32 <= (self.ruined_portal[k][0] * 32 - player.left) <= 1032 and -32 <= (self.ruined_portal[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (56, 0, 89), (self.ruined_portal[k][0] * 32 - player.left, self.ruined_portal[k][1] * 32 - player.top), 10, 10)

            # DRAWING OVERWORLD EMPTY STRUCTURES
            for k in range(len(self.empty_vil_total)):
                if -32 <= (self.empty_vil_total[k][0] * 32 - player.left) <= 1032 and -32 <= (self.empty_vil_total[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (153, 102, 0), (self.empty_vil_total[k][0] * 32 - player.left, self.empty_vil_total[k][1] * 32 - player.top), 10, 10)
            for k in range(len(self.empty_water)):
                if -32 <= (self.empty_water[k][0] * 32 - player.left) <= 1032 and -32 <= (self.empty_water[k][1] * 32 - player.top) <= 1032:
                    pygame.draw.circle(world, (0, 0, 255), (self.empty_water[k][0] * 32 - player.left, self.empty_water[k][1] * 32 - player.top), 10, 10)
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
                    if value.image is not None:
                        display.blit(value.image, (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                    else:
                        display.blit(bedrock_tile, (value.x * 32 - player.left, value.y * 32 - player.top))
                    pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline
            for key, value in self.UndergroundTiles.items(): #surface tiles (with collisions)
                if -32 <= (key[0] * 32 - player.left) <= 1032 and -32 <= (key[1] * 32 - player.top) <= 1032:
                    if value.image is not None:
                        display.blit(value.image, (value.x * 32 - player.left, value.y * 32 - player.top)) #Draw Image
                        pygame.draw.rect(world, (100, 100, 100), (value.x * 32 - player.left, value.y * 32 - player.top, 32, 32), 1) #Draw Border Outline

        # DRAW NETHER DIMENSION
        elif player.dimension == "Nether":
            # DRAWING NETHERRACK TEXTURES
            for k in range(player.rect.x - 384, player.rect.x + 384, 24):
                for j in range(player.rect.y - 384, player.rect.y + 384, 24):
                    display.blit(netherrack, (k, j))
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
            display.blit(breaking_list[math.floor(player.breaking_time) - 1], (player.target[0] * 32 - player.left, player.target[1] * 32 - player.top))
        pygame.draw.rect(world, (50, 50, 50), (player.target[0] * 32 - player.left, player.target[1] * 32 - player.top, 32, 32), 1)  # Draw target block outline

class ITEM_TYPE: #Class to store item details for every item in game
    def __init__(self, Image, Type, Stack, Tier, Rarity):
        self.img = Image
        self.type = Type
        self.stack = Stack
        self.tier = Tier
        self.rarity = Rarity

class TILE_TYPE: #Class to store tile details for every tile type in the game
    def __init__(self, Image, AlphaImage, BreakingTime, Tool, Tier):
        self.img = Image
        self.alpha_img = AlphaImage
        self.breaking_time = BreakingTime
        self.tool = Tool
        self.tier = Tier

class Item: #Item in the inventory
    def __init__(self, name, number, enchantments):
        global TC_ITEMS, TC_TILES, ITEM_COLOURS
        self.name = name #Item Name
        self.number = number #Quantity
        self.enchantments = enchantments #Enchantments List
        self.img = TC_ITEMS[self.name].img #Image
        self.stackNum = TC_ITEMS[self.name].stack #Stackability
        self.itemType = TC_ITEMS[self.name].type #Type of item
        self.toolTier = TC_ITEMS[self.name].tier #Tier of tool
        self.rarity = TC_ITEMS[self.name].rarity #Rarity of item
        if self.enchantments is not None:
            self.rarity += 1
        self.colour = ITEM_COLOURS[self.rarity]
        if self.toolTier is not None:
            self.mining_speed = 2 * self.toolTier - 1 #Mining speed
        else:
            self.mining_speed = None
        if self.enchantments is not None:
            if self.mining_speed is not None:
                for i in self.enchantments:
                    if i[0] == "Efficiency":
                        self.mining_speed += i[1]**2 + 1
        if self.name == "Bookshelf" or self.name == "Cobblestone" or self.name == "Gravel" or self.name == "Hay Bale" or \
                self.name == "Iron Ore" or self.name == "Oak Log" or self.name == "Oak Planks" or self.name == "Obsidian" or \
                self.name == "Mine Entrance" or self.name == "Dirt" or self.name == "Sand" or self.name == "Snow":
            self.hasTile = True #Has a placable tile
            self.targetTile = self.name #Placable tile name
            self.tile_img = TC_TILES[self.targetTile].img
            self.alpha_tile_img = TC_TILES[self.targetTile].alpha_img
        else: #Item cannot be placed
            self.hasTile = False
            self.targetTile = None
            self.tile_img = None
            self.alpha_tile_img = None

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
        self.font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', size)
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
    global TC_GLINTS, item_name_list
    image_render()
    inventory_slots = [
        Grid((83, 83, 83), pygame.Rect((0*2, 260*2), (110, 110)), 2, player.image_list[0]),
        Grid((83, 83, 83), pygame.Rect((110, 260*2), (110, 110)), 2, player.image_list[1]),
        Grid((83, 83, 83), pygame.Rect((110*2, 260*2), (110, 110)), 2, player.image_list[2]),
        Grid((83, 83, 83), pygame.Rect((165*2, 260*2), (110, 110)), 2, player.image_list[3]),
        Grid((83, 83, 83), pygame.Rect((220*2, 260*2), (110, 110)), 2, player.image_list[4]),
        Grid((83, 83, 83), pygame.Rect((275*2, 260*2), (110, 110)), 2, player.image_list[5]),
        Grid((83, 83, 83), pygame.Rect((330*2, 260*2), (110, 110)), 2, player.image_list[6]),
        Grid((83, 83, 83), pygame.Rect((385*2, 260*2), (110, 110)), 2, player.image_list[7]),
        Grid((83, 83, 83), pygame.Rect((440*2, 260*2), (110, 110)), 2, player.image_list[8]),
        Grid((83, 83, 83), pygame.Rect((0*2, 315*2), (110, 110)), 2, player.image_list[9]),
        Grid((83, 83, 83), pygame.Rect((110, 315*2), (110, 110)), 2, player.image_list[10]),
        Grid((83, 83, 83), pygame.Rect((110*2, 315*2), (110, 110)), 2, player.image_list[11]),
        Grid((83, 83, 83), pygame.Rect((165*2, 315*2), (110, 110)), 2, player.image_list[12]),
        Grid((83, 83, 83), pygame.Rect((220*2, 315*2), (110, 110)), 2, player.image_list[13]),
        Grid((83, 83, 83), pygame.Rect((275*2, 315*2), (110, 110)), 2, player.image_list[14]),
        Grid((83, 83, 83), pygame.Rect((330*2, 315*2), (110, 110)), 2, player.image_list[15]),
        Grid((83, 83, 83), pygame.Rect((385*2, 315*2), (110, 110)), 2, player.image_list[16]),
        Grid((83, 83, 83), pygame.Rect((440*2, 315*2), (110, 110)), 2, player.image_list[17]),
        Grid((83, 83, 83), pygame.Rect((0*2, 370*2), (110, 110)), 2, player.image_list[18]),
        Grid((83, 83, 83), pygame.Rect((110, 370*2), (110, 110)), 2, player.image_list[19]),
        Grid((83, 83, 83), pygame.Rect((110*2, 370*2), (110, 110)), 2, player.image_list[20]),
        Grid((83, 83, 83), pygame.Rect((165*2, 370*2), (110, 110)), 2, player.image_list[21]),
        Grid((83, 83, 83), pygame.Rect((220*2, 370*2), (110, 110)), 2, player.image_list[22]),
        Grid((83, 83, 83), pygame.Rect((275*2, 370*2), (110, 110)), 2, player.image_list[23]),
        Grid((83, 83, 83), pygame.Rect((330*2, 370*2), (110, 110)), 2, player.image_list[24]),
        Grid((83, 83, 83), pygame.Rect((385*2, 370*2), (110, 110)), 2, player.image_list[25]),
        Grid((83, 83, 83), pygame.Rect((440*2, 370*2), (110, 110)), 2, player.image_list[26]),
        Grid((83, 83, 83), pygame.Rect((0*2, 425*2), (110, 110)), 2, player.image_list[27]),
        Grid((83, 83, 83), pygame.Rect((110, 425*2), (110, 110)), 2, player.image_list[28]),
        Grid((83, 83, 83), pygame.Rect((110*2, 425*2), (110, 110)), 2, player.image_list[29]),
        Grid((83, 83, 83), pygame.Rect((165*2, 425*2), (110, 110)), 2, player.image_list[30]),
        Grid((83, 83, 83), pygame.Rect((220*2, 425*2), (110, 110)), 2, player.image_list[31]),
        Grid((83, 83, 83), pygame.Rect((275*2, 425*2), (110, 110)), 2, player.image_list[32]),
        Grid((83, 83, 83), pygame.Rect((330*2, 425*2), (110, 110)), 2, player.image_list[33]),
        Grid((83, 83, 83), pygame.Rect((385*2, 425*2), (110, 110)), 2, player.image_list[34]),
        Grid((83, 83, 83), pygame.Rect((440*2, 425*2), (110, 110)), 2, player.image_list[35])
    ]

    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    numbers = [
        Text(font.render(player.number_list[0], False, (255, 255, 255)), 35*2, 295*2),
        Text(font.render(player.number_list[1], False, (255, 255, 255)), 90*2, 295*2),
        Text(font.render(player.number_list[2], False, (255, 255, 255)), 145*2, 295*2),
        Text(font.render(player.number_list[3], False, (255, 255, 255)), 200*2, 295*2),
        Text(font.render(player.number_list[4], False, (255, 255, 255)), 255*2, 295*2),
        Text(font.render(player.number_list[5], False, (255, 255, 255)), 310*2, 295*2),
        Text(font.render(player.number_list[6], False, (255, 255, 255)), 365*2, 295*2),
        Text(font.render(player.number_list[7], False, (255, 255, 255)), 420*2, 295*2),
        Text(font.render(player.number_list[8], False, (255, 255, 255)), 475*2, 295*2),
        Text(font.render(player.number_list[9], False, (255, 255, 255)), 35*2, 350*2),
        Text(font.render(player.number_list[10], False, (255, 255, 255)), 90*2, 350*2),
        Text(font.render(player.number_list[11], False, (255, 255, 255)), 145*2, 350*2),
        Text(font.render(player.number_list[12], False, (255, 255, 255)), 200*2, 350*2),
        Text(font.render(player.number_list[13], False, (255, 255, 255)), 255*2, 350*2),
        Text(font.render(player.number_list[14], False, (255, 255, 255)), 310*2, 350*2),
        Text(font.render(player.number_list[15], False, (255, 255, 255)), 365*2, 350*2),
        Text(font.render(player.number_list[16], False, (255, 255, 255)), 420*2, 350*2),
        Text(font.render(player.number_list[17], False, (255, 255, 255)), 475*2, 350*2),
        Text(font.render(player.number_list[18], False, (255, 255, 255)), 35*2, 405*2),
        Text(font.render(player.number_list[19], False, (255, 255, 255)), 90*2, 405*2),
        Text(font.render(player.number_list[20], False, (255, 255, 255)), 145*2, 405*2),
        Text(font.render(player.number_list[21], False, (255, 255, 255)), 200*2, 405*2),
        Text(font.render(player.number_list[22], False, (255, 255, 255)), 255*2, 405*2),
        Text(font.render(player.number_list[23], False, (255, 255, 255)), 310*2, 405*2),
        Text(font.render(player.number_list[24], False, (255, 255, 255)), 365*2, 405*2),
        Text(font.render(player.number_list[25], False, (255, 255, 255)), 420*2, 405*2),
        Text(font.render(player.number_list[26], False, (255, 255, 255)), 475*2, 405*2),
        Text(font.render(player.number_list[27], False, (255, 255, 255)), 35*2, 460*2),
        Text(font.render(player.number_list[28], False, (255, 255, 255)), 90*2, 460*2),
        Text(font.render(player.number_list[29], False, (255, 255, 255)), 145*2, 460*2),
        Text(font.render(player.number_list[30], False, (255, 255, 255)), 200*2, 460*2),
        Text(font.render(player.number_list[31], False, (255, 255, 255)), 255*2, 460*2),
        Text(font.render(player.number_list[32], False, (255, 255, 255)), 310*2, 460*2),
        Text(font.render(player.number_list[33], False, (255, 255, 255)), 365*2, 460*2),
        Text(font.render(player.number_list[34], False, (255, 255, 255)), 420*2, 460*2),
        Text(font.render(player.number_list[35], False, (255, 255, 255)), 475*2, 460*2)
    ]
    for i in range(len(inventory_slots)):
        display.blit(inventory_slots[i].img, (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
        pygame.draw.rect(display, inventory_slots[i].colour, inventory_slots[i].rect, inventory_slots[i].width)
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.inventory_list[i].name], (inventory_slots[i].rect.x, inventory_slots[i].rect.y))
    for i in numbers:
        display.blit(i.surface, (i.x, i.y))

#Armour Grid for Player
def ArmourGrid(display):
    image_render()
    armour_grid = [
        Grid((83, 83, 83), pygame.Rect((0*2, 160*2), (110, 110)), 2, player.armour_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((110, 160*2), (110, 110)), 2, player.armour_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((110*2, 160*2), (110, 110)), 2, player.armour_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((165*2, 160*2), (110, 110)), 2, player.armour_image_list[3]),
    ]
    for i in range(len(armour_grid)):
        display.blit(armour_grid[i].img, (armour_grid[i].rect.x, armour_grid[i].rect.y))
        pygame.draw.rect(display, armour_grid[i].colour, armour_grid[i].rect, armour_grid[i].width)
        if player.armour_list[i] is not None:
            if player.armour_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.armour_list[i].name], (armour_grid[i].rect.x, armour_grid[i].rect.y))
    pygame.draw.rect(display, (0, 0, 0), (0, 0, 220*2, 160*2)) #Draw Black Background
    pygame.draw.rect(display, (255, 0, 0), (85*2, 110, 50*2, 50*2)) #Draw Player Icon
    for i in player.layer_list: #Draw Armour Layers
        if i is not None:
            if i[1] == 1: #Tier 1
                pygame.draw.rect(display, i[0], (75*2, 45*2, 70*2, 70*2), 8*2)
            elif i[1] == 2: #Tier 2
                pygame.draw.rect(display, i[0], (66*2, 36*2, 89*2, 89*2), 8*2)
            elif i[1] == 3: #Tier 3
                pygame.draw.rect(display, i[0], (56*2, 26*2, 110*2, 110*2), 8*2)

#2x2 Small Crafting Grid within Inventory
def SmallCraftGrid(display):
    image_render()
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((260*2, 50*2), (110, 110)), 2, player.craft_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((315*2, 50*2), (110, 110)), 2, player.craft_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((260*2, 105*2), (110, 110)), 2, player.craft_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((315*2, 105*2), (110, 110)), 2, player.craft_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((425*2, 78*2), (110, 110)), 2, player.craft_image_list[4]),
    ]
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    arrow_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftBold-nMK1.otf', 24*2)
    crafting_numbers = [
        Text(font.render(player.craft_number_list[0], False, (255, 255, 255)), 295*2, 85*2),
        Text(font.render(player.craft_number_list[1], False, (255, 255, 255)), 350*2, 85*2),
        Text(font.render(player.craft_number_list[2], False, (255, 255, 255)), 295*2, 140*2),
        Text(font.render(player.craft_number_list[3], False, (255, 255, 255)), 350*2, 140*2),
        Text(font.render(player.craft_number_list[4], False, (255, 255, 255)), 460*2, 113*2),
    ]

    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.craft_list[i] is not None:
            if player.craft_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.craft_list[i].name], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (375*2, 95*2))

def CraftGrid(display):
    image_render()
    crafting_grid = [
        Grid((83, 83, 83), pygame.Rect((130*2, 50*2), (110, 110)), 2, player.grid_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((185*2, 50*2), (110, 110)), 2, player.grid_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((240*2, 50*2), (110, 110)), 2, player.grid_image_list[2]),
        Grid((83, 83, 83), pygame.Rect((130*2, 105*2), (110, 110)), 2, player.grid_image_list[3]),
        Grid((83, 83, 83), pygame.Rect((185*2, 105*2), (110, 110)), 2, player.grid_image_list[4]),
        Grid((83, 83, 83), pygame.Rect((240*2, 105*2), (110, 110)), 2, player.grid_image_list[5]),
        Grid((83, 83, 83), pygame.Rect((130*2, 160*2), (110, 110)), 2, player.grid_image_list[6]),
        Grid((83, 83, 83), pygame.Rect((185*2, 160*2), (110, 110)), 2, player.grid_image_list[7]),
        Grid((83, 83, 83), pygame.Rect((240*2, 160*2), (110, 110)), 2, player.grid_image_list[8]),
        Grid((83, 83, 83), pygame.Rect((380*2, 105*2), (110, 110)), 2, player.grid_image_list[9])
    ]
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    title_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 27*2)
    arrow_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftBold-nMK1.otf', 27*2)
    crafting_numbers = [
        Text(font.render(player.grid_number_list[0], False, (255, 255, 255)), 165*2, 85*2),
        Text(font.render(player.grid_number_list[1], False, (255, 255, 255)), 220*2, 85*2),
        Text(font.render(player.grid_number_list[2], False, (255, 255, 255)), 275*2, 85*2),
        Text(font.render(player.grid_number_list[3], False, (255, 255, 255)), 165*2, 140*2),
        Text(font.render(player.grid_number_list[4], False, (255, 255, 255)), 220*2, 140*2),
        Text(font.render(player.grid_number_list[5], False, (255, 255, 255)), 275*2, 140*2),
        Text(font.render(player.grid_number_list[6], False, (255, 255, 255)), 165*2, 195*2),
        Text(font.render(player.grid_number_list[7], False, (255, 255, 255)), 220*2, 195*2),
        Text(font.render(player.grid_number_list[8], False, (255, 255, 255)), 275*2, 195*2),
        Text(font.render(player.grid_number_list[9], False, (255, 255, 255)), 415*2, 140*2)
    ]

    display.blit(title_font.render('Crafting Table', False, (0, 0, 0)), (130*2, 0))
    for i in range(len(crafting_grid)):
        display.blit(crafting_grid[i].img, (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
        pygame.draw.rect(display, crafting_grid[i].colour, crafting_grid[i].rect, crafting_grid[i].width)
        if player.grid_list[i] is not None:
            if player.grid_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.grid_list[i].name], (crafting_grid[i].rect.x, crafting_grid[i].rect.y))
    for i in crafting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (310*2, 120*2))

def FurnaceInterface(display):
    global FPS
    image_render()
    smelting_grid = [
        Grid((83, 83, 83), pygame.Rect((150*2, 45*2), (110, 110)), 2, player.smelt_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((150*2, 175*2), (110, 110)), 2, player.smelt_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((300*2, 115*2), (110, 110)), 2, player.smelt_image_list[2]),
    ]
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    side_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 24*2)
    title_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 27*2)
    arrow_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftBold-nMK1.otf', 30*2)
    smelting_numbers = [
        Text(font.render(player.smelt_number_list[0], False, (255, 255, 255)), 185*2, 80*2),
        Text(font.render(player.smelt_number_list[1], False, (255, 255, 255)), 185*2, 210*2),
        Text(font.render(player.smelt_number_list[2], False, (255, 255, 255)), 335*2, 150*2)
    ]

    display.blit(title_font.render('Furnace', False, (0, 0, 0)), (200*2, 0))
    for i in range(len(smelting_grid)):
        display.blit(smelting_grid[i].img, (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
        pygame.draw.rect(display, smelting_grid[i].colour, smelting_grid[i].rect, smelting_grid[i].width)
        if player.smelting_list[i] is not None:
            if player.smelting_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.smelting_list[i].name], (smelting_grid[i].rect.x, smelting_grid[i].rect.y))
    for i in smelting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(player.fuel_img, (150*2, 115*2)) #Render Fire Image
    display.blit(side_font.render(str(player.fuel_val), False, (255, 0, 0)), (125*2, 125*2)) #Render Power of Fuel Remaining
    display.blit(side_font.render(str(player.smelting_time // FPS), False, (255, 0, 0)), (245*2, 105*2)) #Render Time to Smelt
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (225*2, 125*2)) #Render Arrow

def EnchantingInterface(display):
    global Option1, Option2, Option3, Upgrade
    image_render()
    enchanting_grid = [
        Grid((83, 83, 83), pygame.Rect((20*2, 150*2), (110, 110)), 2, player.enchanting_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((75*2, 150*2), (110, 110)), 2, player.enchanting_image_list[1]),
        Grid((83, 83, 83), pygame.Rect((20*2, 95*2), (110, 110)), 2, player.enchanting_image_list[2])
    ]
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    enchanting_numbers = [
        Text(font.render(str(player.enchanting_number_list[0]), False, (255, 255, 255)), 110, 185*2),
        Text(font.render(str(player.enchanting_number_list[1]), False, (255, 255, 255)), 110*2, 185*2),
        Text(font.render(str(player.enchanting_number_list[2]), False, (255, 255, 255)), 110, 130*2)
    ]
    for i in range(len(enchanting_grid)):
        display.blit(enchanting_grid[i].img, (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
        pygame.draw.rect(display, enchanting_grid[i].colour, enchanting_grid[i].rect, enchanting_grid[i].width)
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.enchanting_list[i].name], (enchanting_grid[i].rect.x, enchanting_grid[i].rect.y))
    for i in enchanting_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(font.render(f'Enchanting Table LEVEL {player.enchanting_level}', False, (0, 0, 0)), (0, 0))
    Upgrade.render(world, 'Upgrade', 14*2)
    Option1.render(world, player.option_list[0], 20*2)
    Option2.render(world, player.option_list[1], 20*2)
    Option3.render(world, player.option_list[2], 20*2)

def CompressorInterface(display):
    global player, FPS
    image_render()
    compressor_grid = [
        Grid((83, 83, 83), pygame.Rect((150*2, 95*2), (110, 110)), 2, player.compressor_image_list[0]),
        Grid((83, 83, 83), pygame.Rect((300*2, 95*2), (110, 110)), 2, player.compressor_image_list[1])
    ]
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    title_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 27*2)
    arrow_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftBold-nMK1.otf', 30*2)
    side_font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 24*2)
    compressor_numbers = [
        Text(font.render(player.compressor_number_list[0], False, (255, 255, 255)), 185*2, 130*2),
        Text(font.render(player.compressor_number_list[1], False, (255, 255, 255)), 335*2, 130*2)
    ]
    display.blit(title_font.render('Compressor', False, (0, 0, 0)), (175*2, 0))
    for i in range(len(compressor_grid)):
        display.blit(compressor_grid[i].img, (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
        pygame.draw.rect(display, compressor_grid[i].colour, compressor_grid[i].rect, compressor_grid[i].width)
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].enchantments is not None:
                display.blit(TC_GLINTS[player.compressor_list[i].name], (compressor_grid[i].rect.x, compressor_grid[i].rect.y))
    for i in compressor_numbers:
        display.blit(i.surface, (i.x, i.y))
    display.blit(arrow_font.render('-->', False, (0, 0, 0)), (225*2, 115*2))  # Render Arrow
    display.blit(side_font.render(str(player.compressing_time // FPS), False, (255, 0, 0)), (240*2, 95*2))  # Render Time to Compress


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
def Main():
    global TimerRunning, screen, furnace_interface, crafting_grid, small_crafting_grid, inventory_grid, World, player, difference, individual_frame, FPS, second_time, mode, val, comma, number, called, world, frame, play_time, endTime, minute, seconds, true_play_time, PlayTime, hotbar_backgrounds, selected_hotbar
    global hasGeneratedOverworld, display, clock, loading, hasGeneratedUnderground, previous_frame
    while True:
        clock.tick()

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
                                player.F3 = not player.F3
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
                World.render(world)  # Render all world blocks to world
                hotbar_identify() #Update hotbar item
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
        elif not hasGeneratedOverworld and hasGeneratedUnderground == "Not Loaded":
            display.fill((255, 255, 255))
            for i in range(0, 1000, 32):
                for j in range(0, 1000, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 25*2)
            display.blit(font.render("Generating Overworld", False, (255, 255, 255)), (130*2, 150*2))
            pygame.display.flip()
            IntialiseDetails()
        if hasGeneratedUnderground == "Generating":
            display.fill((255, 255, 255))
            for i in range(0, 1000, 32):
                for j in range(0, 1000, 32):
                    display.blit(loading, (i, j))
            font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 25*2)
            display.blit(font.render("Generating Underground", False, (255, 255, 255)), (120*2, 150*2))
            pygame.display.flip()
            World.undergroundGenerated = True
            World.generateUnderground()
            World.UndergroundTiles = UndergroundGeneratePortal(round(player.x), round(player.y), World.UndergroundTiles)
            hasGeneratedUnderground = "Generated"
        if not pygame.mixer.music.get_busy():
            if random.randint(1, 500) == 1:
                pygame.mixer.music.load("images_vB1_0_pre1/music/song" + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
                pygame.mixer.music.play()


#Render the Item the User is Holding
def RenderHoldingItem(display):
    global TC_GLINTS
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
    if player.holding_item is not None:
        display.blit(player.holding_item_image, (x, y))
        display.blit(font.render(player.holding_item_number, False, (255, 255, 255)), (x + 35*2, y + 35*2))
        if player.holding_item.enchantments is not None:
            display.blit(TC_GLINTS[player.holding_item.name], (x, y))

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
    elif num == 6:
        num = 'VI'
    elif num == 7:
        num = 'VII'
    elif num == 8:
        num = 'VIII'
    elif num == 9:
        num = 'IX'
    elif num == 10:
        num = 'X'
    return num

#Info Box for Items (with and without enchantments)
def TextBox(List, x, y, font, box, display):
    try:
        if List[box] is not None: #Check to prevent crashes
            length_list = [len(List[box].name * 10*2)]
            if List[box].enchantments is not None:
                width = (1 + len(List[box].enchantments)) * 25*2
                for i in List[box].enchantments:
                    length_list.append(len(str(i[0]) + DecimalToRoman(str(i[1]))) * 10*2)
            else:
                width = 25*2
            if List[box].toolTier is not None and List[box].mining_speed is not None:
                width += 30*2
                length_list.append(len(f"Breaking Power {List[box].toolTier}") * 10*2)
                length_list.append(len(f"Mining Speed: +{List[box].mining_speed}") * 10*2)
            length = max(length_list)
            if x + length > 1000:
                x -= length
            if y + width > 1000:
                y -= width
            pygame.draw.rect(display, (0, 0, 0), (x, y, length, width))
            display.blit(font.render(List[box].name, False, List[box].colour), (x + 10*2, y + 10*2))
            if List[box].toolTier is not None and List[box].mining_speed is not None:
                display.blit(font.render(f"Breaking Power {List[box].toolTier}", False, (175, 175, 175)), (x + 10*2, y + 25*2))
                display.blit(font.render(f"Mining Speed: +{List[box].mining_speed}", False, (175, 175, 175)), (x + 10*2, y + 40*2))
                if List[box].enchantments is not None:
                    for i in range(len(List[box].enchantments)):
                        display.blit(font.render(f'{List[box].enchantments[i][0]} {DecimalToRoman(List[box].enchantments[i][1])}', False, (255, 255, 255)), (x + 10*2, y + 40*2 + (i + 1) * 15*2))
            else:
                if List[box].enchantments is not None:
                    for i in range(len(List[box].enchantments)):
                        display.blit(font.render(f'{List[box].enchantments[i][0]} {DecimalToRoman(List[box].enchantments[i][1])}', False, (255, 255, 255)), (x + 10*2, y + 10*2 + (i + 1) * 15*2))
    except IndexError:
        pass

#Render the Item Label for the Item that the User is Hovering Over
def RenderHoveringItem(display, Type, box):
    x, y = pygame.mouse.get_pos()
    font = pygame.font.Font('images_vB1_0_pre1/monofur/monof55.ttf', 15*2)
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
    if 0 <= x <= 495*2 and 260*2 <= y <= 480*2:
        column = x // 110
        row = (y - 260*2) // 110
        box = column + 9 * row
        return "inventory grid", box
    elif 0 <= x <= 220*2 and 160*2 <= y <= 215*2 and player.mode == 'inventory':
        box = x // 110
        return "armour grid", box
    elif 260*2 <= x <= 370*2 and 50*2 <= y <= 160*2 and player.mode == 'inventory':
        column = (x - 260*2) // 110
        row = (y - 50*2) // 110
        box = column + 2 * row
        return "small crafting grid", box
    elif 425*2 <= x <= 480*2 and 78*2 <= y <= 133*2 and player.mode == 'inventory':
        box = 4
        return 'small crafting grid item', box
    elif 130*2 <= x <= 295*2 and 50*2 <= y <= 215*2 and player.mode == 'crafting':
        column = (x - 130*2) // 110
        row = (y - 50*2) // 110
        box = column + 3 * row
        return 'crafting grid', box
    elif 380*2 <= x <= 435*2 and 105*2 <= y <= 160*2 and player.mode == 'crafting':
        box = 9
        return 'crafting grid item', box
    elif 150*2 <= x <= 205*2 and 45*2 <= y <= 100*2 and player.mode == 'smelting':
        box = 0
        return 'smelting', box
    elif 150*2 <= x <= 205*2 and 175*2 <= y <= 230*2 and player.mode == 'smelting':
        box = 1
        return 'smelting', box
    elif 300*2 <= x <= 3110 and 115*2 <= y <= 170*2 and player.mode == 'smelting':
        box = 2
        return 'smelting item', box
    elif 20*2 <= x <= 75*2 and 150*2 <= y <= 205*2 and player.mode == 'enchanting':
        box = 0
        return 'enchanting', box
    elif 75*2 <= x <= 130*2 and 150*2 <= y <= 205*2 and player.mode == 'enchanting':
        box = 1
        return 'enchanting', box
    elif 20*2 <= x <= 75*2 and 95*2 <= y <= 150*2 and player.mode == 'enchanting':
        box = 2
        return 'enchanting', box
    elif Upgrade.x <= x <= Upgrade.x + 110 and Upgrade.y <= y <= Upgrade.y + 110 and player.mode == 'enchanting':
        box = 0
        return 'upgrade', box
    elif Option1.x <= x <= Option1.x + 325*2 and Option1.y <= y <= Option1.y + 110 and player.mode == 'enchanting':
        box = 0
        return 'option1', box
    elif Option2.x <= x <= Option2.x + 325*2 and Option2.y <= y <= Option2.y + 110 and player.mode == 'enchanting':
        box = 1
        return 'option2', box
    elif Option3.x <= x <= (Option3.x + 325*2) and Option3.y <= y <= (Option3.y + 110) and player.mode == 'enchanting':
        box = 2
        return 'option3', box
    elif 150*2 <= x <= 205*2 and 95*2 <= y <= 150*2 and player.mode == 'compressing':
        box = 0
        return 'compressing', box
    elif 300*2 <= x <= 3110 and 95*2 <= y <= 150*2 and player.mode == 'compressing':
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
                player.inventory_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.inventory_list[box] is not None and player.inventory_list[box].name == player.holding_item.name and (player.inventory_list[box].number + 1 <= player.inventory_list[box].stackNum):
                player.inventory_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'small crafting grid': #Small 2x2 Crafting Grid
            if player.craft_list[box] is None:
                player.craft_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.craft_list[box] is not None and player.craft_list[box].name == player.holding_item.name and (player.craft_list[box].number + 1 <= player.craft_list[box].stackNum):
                player.craft_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'crafting grid': #Big 3x3 Crafting Grid
            if player.grid_list[box] is None:
                player.grid_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.grid_list[box] is not None and player.grid_list[box].name == player.holding_item.name and (player.grid_list[box].number + 1 <= player.grid_list[box].stackNum):
                player.grid_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'smelting': #Furnace Interface
            if player.smelting_list[box] is None:
                player.smelting_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.smelting_list[box] is not None and player.smelting_list[box].name == player.holding_item.name and (player.smelting_list[box].number + 1 <= player.smelting_list[box].stackNum):
                player.smelting_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'enchanting': #Enchanting Table Interface
            if player.enchanting_list[box] is None:
                player.enchanting_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.enchanting_list[box] is not None and player.enchanting_list[box].name == player.holding_item.name and (player.enchanting_list[box].number + 1 <= player.enchanting_list[box].stackNum):
                player.enchanting_list[box].number += 1
                player.holding_item.number -= 1
        elif Type == 'compressing': #Compressor Interface
            if player.compressor_list[box] is None:
                player.compressor_list[box] = Item(player.holding_item.name, 1, player.holding_item.enchantments)
                player.holding_item.number -= 1
            elif player.compressor_list[box] is not None and player.compressor_list[box].name == player.holding_item.name and (player.compressor_list[box].number + 1 <= player.compressor_list[box].stackNum):
                player.compressor_list[box].number += 1
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
        self.y = 380*2
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
        self.input_line = 10*2
        self.isTyping = True
        self.foretext = text
        self.timer = 0

    def type(self, char):
        self.typingText += char

    def stop_typing(self):
        global screen, player, TC_ITEMS, hotbar_order
        self.input_line = 0
        self.isTyping = False
        length = len(list(TC_ITEMS.keys())) - 1
        if self.foretext == f'Item ID (0 - {length}): ':
            inventory_add(give(self.typingText))
            self.foretext = ''
        elif self.foretext == 'Coordinates (X,Y): ':
            player.x, player.y = teleport(player.x, player.y, self.typingText)
            self.foretext = ''
        elif self.foretext == "Enchantment (Name, Lvl): ":
            index = hotbar_order.index(player.selected_hotbar)
            item = enchant(self.typingText)
            if item is not None:
                player.inventory_list[27 + index] = item
            self.foretext = ''
        elif self.foretext == "Experience Level: ":
            experience(self.typingText)
            self.foretext = ''
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
        self.timer = 0
        self.print_list.append(text)

    def render(self, display):
        if self.timer != 600:
            if len(self.print_list) <= 16:
                self.screen_list = self.print_list[:]
                height = len(self.print_list) * 10*2 + self.input_line
            else:
                if self.position == 0:
                    self.screen_list = self.print_list[-16 - self.position:]
                    height = 16 * 10*2 + self.input_line
                else:
                    self.screen_list = self.print_list[-16 - self.position: 0 - self.position]
                    height = 16 * 10*2 + self.input_line
            self.screen_list.reverse()
            width = 250*2
            x = self.x
            y = self.y - height
            surface = pygame.Surface((width, height))
            surface.fill((125, 125, 125))
            surface.set_alpha(200)
            display.blit(surface, (x, y))
            font = pygame.font.Font('images_vB1_0_pre1/monofur/monof55.ttf', 12*2)
            for i in range(len(self.screen_list)):
                display.blit(font.render(self.screen_list[i], False, (255, 255, 255)), (x, y + height - (i + 1) * 10*2 - self.input_line))
            display.blit(font.render(self.foretext + self.typingText, True, (255, 255, 255)), (x, y + height - 10*2))
            self.timer += 1

# Create Hotbar Outline
class Hotbar:
    def __init__(self, colour, rect, width):
        self.colour = colour
        self.rect = rect
        self.width = width

#Player Class and Methods
class Player:
    def __init__(self):
        global World
        self.advancements = []
        self.image = pygame.Surface((32, 32))  # Create Player Image
        self.image.fill((255, 0, 0))  # Fill Player Red
        self.rect = pygame.Rect((484, 484), (32, 32))  # Create Player Rect
        self.x = 0  # Set Starting X Coordinate
        self.y = 0  # Set Starting Y Coordinate
        self.actualX = 0
        self.actualY = 0
        self.dimension = "Overworld"
        self.regenerate_val = False
        self.regenerate_start_time = 180
        self.F3 = False
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
            'images_vB1_0_pre1/FullHeart_20x20.png').convert()  # Full Heart (2)
        half_heart = pygame.image.load(
            'images_vB1_0_pre1/half_heart_20x20.png').convert()  # Half Heart (1)
        empty_heart = pygame.image.load(
            'images_vB1_0_pre1/empty_heart_20x20.png').convert()  # Empty Heart (0)
        heart1 = info_bar(full_heart, 5*2, 395*2)
        heart2 = info_bar(full_heart, 28*2, 395*2)
        heart3 = info_bar(full_heart, 51*2, 395*2)
        heart4 = info_bar(full_heart, 74*2, 395*2)
        heart5 = info_bar(full_heart, 97*2, 395*2)
        heart6 = info_bar(full_heart, 120*2, 395*2)
        heart7 = info_bar(full_heart, 143*2, 395*2)
        heart8 = info_bar(full_heart, 166*2, 395*2)
        heart9 = info_bar(full_heart, 189*2, 395*2)
        heart10 = info_bar(full_heart, 212*2, 395*2)
        self.health_vals = [heart1, heart2, heart3, heart4, heart5, heart6, heart7, heart8, heart9, heart10]
        self.health_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.health = 20  # Set Health = 20

        # Setup Hunger Bar Images
        global experience_bar, hunger_vals, backdrop, empty_hunger, distance, hunger_nums, full_hunger, hunger, half_hunger, dead, hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10
        full_hunger = pygame.image.load(
            'images_vB1_0_pre1/hunger_20x20.png')  # Full Hunger (2)
        half_hunger = pygame.image.load(
            'images_vB1_0_pre1/half_hunger_20x20.png')  # Half Hunger (1)
        empty_hunger = pygame.image.load(
            'images_vB1_0_pre1/empty_hunger_20x20.png')  # Empty Hunger (0)
        self.hunger = 20  # Set Hunger = 20
        self.hunger_nums = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        self.distance = 0  # Set Distance Travelled
        self.dead = False
        self.hunger_subtracted = 0

        hunger1 = info_bar(full_hunger, 477*2, 395*2)
        hunger2 = info_bar(full_hunger, 454*2, 395*2)
        hunger3 = info_bar(full_hunger, 431*2, 395*2)
        hunger4 = info_bar(full_hunger, 408*2, 395*2)
        hunger5 = info_bar(full_hunger, 385*2, 395*2)
        hunger6 = info_bar(full_hunger, 362*2, 395*2)
        hunger7 = info_bar(full_hunger, 339*2, 395*2)
        hunger8 = info_bar(full_hunger, 316*2, 395*2)
        hunger9 = info_bar(full_hunger, 293*2, 395*2)
        hunger10 = info_bar(full_hunger, 270*2, 395*2)
        self.hunger_vals = [hunger1, hunger2, hunger3, hunger4, hunger5, hunger6, hunger7, hunger8, hunger9, hunger10]  # Hunger bar list
        experience_bar = pygame.image.load('images_vB1_0_pre1/item_imgs/experience.png').convert()
        backdrop = pygame.Rect((20*2, 395*2), (465*2, 20*2))  # Set Background for Hunger and Health Bar

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
        global no_fire
        self.fuel_img = no_fire
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
        slot = pygame.image.load("images_vB1_0_pre1/item_imgs/slot.png").convert()
        bar1 = info_bar(slot, 5*2, 445*2)
        bar2 = info_bar(slot, 60*2, 445*2)
        bar3 = info_bar(slot, 115*2, 445*2)
        bar4 = info_bar(slot, 170*2, 445*2)
        bar5 = info_bar(slot, 225*2, 445*2)
        bar6 = info_bar(slot, 280*2, 445*2)
        bar7 = info_bar(slot, 335*2, 445*2)
        bar8 = info_bar(slot, 390*2, 445*2)
        bar9 = info_bar(slot, 445*2, 445*2)
        self.hotbar_imgs = [bar1, bar2, bar3, bar4, bar5, bar6, bar7, bar8, bar9]

        # Set Background Rects
        background_1 = pygame.Rect((5*2, 445*2), (110, 110))
        background_2 = pygame.Rect((60*2, 445*2), (110, 110))
        background_3 = pygame.Rect((115*2, 445*2), (110, 110))
        background_4 = pygame.Rect((170*2, 445*2), (110, 110))
        background_5 = pygame.Rect((225*2, 445*2), (110, 110))
        background_6 = pygame.Rect((280*2, 445*2), (110, 110))
        background_7 = pygame.Rect((335*2, 445*2), (110, 110))
        background_8 = pygame.Rect((390*2, 445*2), (110, 110))
        background_9 = pygame.Rect((445*2, 445*2), (110, 110))

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
            if self.regenerate_start_time < 60:
                if frame % 5 == 0:
                    self.health += 1
                self.regenerate_start_time += 1
            else:
                self.regenerate_val = False
        player.health_hunger_update()

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
        self.left = self.x * 32 - 484
        self.right = self.x * 32 + 516
        self.bottom = self.y * 32 + 516
        self.top = self.y * 32 - 484
        self.ScreenLeft = self.x * 32 - 484
        self.ScreenRight = self.x * 32 + 516
        self.ScreenBottom = self.y * 32 + 516
        self.ScreenTop = self.y * 32 - 484

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
                    World.Tiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y), None)
            elif self.dimension == "Underground" and hasGeneratedUnderground == "Generated":
                if World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Air" and World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))].tile != "Mine Entrance":
                    World.UndergroundTiles[(math.floor(self.x), math.floor(self.y))] = Tile("Air", math.floor(self.x), math.floor(self.y), None)
        except KeyError:
            World.generate_chunks()

    def smelt(self):
        global FPS
        # Load Fuel
        if self.smelting_list[1] is not None:
            if self.smelting_list[1].name == "Coal" and self.fuel_val == 0:
                self.smelting_list[1] = Item(self.smelting_list[1].name, self.smelting_list[1].number - 1, self.smelting_list[1].enchantments)
                self.fuel_val = 8

        # Smelting Process
        if self.smelting_list[0] is not None:
            if self.smelting_list[0].name == "Iron Ore" and self.fuel_val > 0:
                self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time == 5 * FPS:
            self.smelting_time = 0
            self.smelting_list[0] = Item(self.smelting_list[0].name, self.smelting_list[0].number - 1, self.smelting_list[0].enchantments)
            self.fuel_val -= 1
            if self.smelting_list[2] is None:
                self.smelting_list[2] = Item("Iron Ingot", 1, None)
                self.experience_points += 12
            else:
                self.smelting_list[2] = Item("Iron Ingot", self.smelting_list[2].number + 1, None)
                self.experience_points += 12

        # Render Fire
        if self.fuel_val > 0:
            self.fuel_img = fire
        else:
            self.fuel_img = no_fire

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
        if self.compressing_time == 5 * FPS:
            self.compressing_time = 0
            self.compressor_list[0] = Item(self.compressor_list[0].name, self.compressor_list[0].number - 2, self.compressor_list[0].enchantments)
            if self.compressor_list[1] is None:
                if self.compressor_list[0].name == 'Iron Ingot':
                    self.compressor_list[1] = Item("Iron Plate", 1, None)
                elif self.compressor_list[0].name == 'Diamond':
                    self.compressor_list[1] = Item("Diamond Plate", 1, None)
            else:
                if self.compressor_list[0].name == 'Iron Ingot' and self.compressor_list[1].name == 'Iron Plate':
                    self.compressor_list[1] = Item("Iron Plate", self.compressor_list[1].number + 1, None)
                elif self.compressor_list[0].name == 'Diamond' and self.compressor_list[1].name == 'Diamond Plate':
                    self.compressor_list[1] = Item("Diamond Plate", self.compressor_list[1].number + 1, None)

    def place_tile(self): #Place tiles
        if self.isShifting: #is shifting = can edit background tiles
            if self.dimension == "Overworld": #Overworld background tiles
                if self.hotbar_item.hasTile:
                    if World.UnderTiles[(self.target[0], self.target[1])].tile == "Air": #Open space to place tile
                        World.UnderTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1], self.hotbar_item.alpha_tile_img) #Place tile
                        self.hotbar_item.number -= 1 #Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None #Remove from inventory
            elif self.dimension == "Underground": #Underground background tiles
                if self.hotbar_item.hasTile:
                    if World.UndergroundUnderTiles[(self.target[0], self.target[1])].tile == "Air":  # Open space to place tile
                        World.UndergroundUnderTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1], self.hotbar_item.alpha_tile_img)  # Place tile
                        self.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None  # Remove from inventory
        else:
            if self.dimension == "Overworld": #Overworld Collision tiles
                if self.hotbar_item.hasTile:
                    if World.Tiles[(self.target[0], self.target[1])].tile == "Air":  # Open space to place tile
                        World.Tiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1], self.hotbar_item.alpha_tile_img)  # Place tile
                        self.hotbar_item.number -= 1  # Subtract 1 from item in hand
                        if self.hotbar_item.number == 0:
                            self.hotbar_item = None  # Remove from inventory
            elif self.dimension == "Underground": #Underground Collision Tiles
                if self.hotbar_item.hasTile:
                    if World.UndergroundTiles[(self.target[0], self.target[1])].tile == "Air":  # Open space to place tile
                        World.UndergroundTiles[(self.target[0], self.target[1])] = Tile(self.hotbar_item.targetTile, self.target[0], self.target[1], self.hotbar_item.alpha_tile_img)  # Place tile
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
                    inventory_add(Item("Oak Log", random.randint(1, 5), None))
                elif value.tile == "Stone":
                    inventory_add(Item("Cobblestone", 1, None))
                elif value.tile == "Coal Ore":
                    inventory_add(Item("Coal", 1, None))
                    self.experience_points += 12
                elif value.tile == "Lapis Ore":
                    inventory_add(Item("Lapis Lazuli", 1, None))
                    self.experience_points += 12
                elif value.tile == "Diamond Ore":
                    inventory_add(Item("Diamond", 1, None))
                    self.experience_points += 12
                elif value.tile == "Grass":
                    inventory_add(Item("Dirt", 1, None))
                else:
                    inventory_add(Item(value.tile, 1, None))
        elif self.dimension == "Underground":
            if value.tile != "Leaf":
                if value.tile == "Tree":
                    inventory_add(Item("Oak Log", random.randint(1, 5), None))
                elif value.tile == "Stone":
                    inventory_add(Item("Cobblestone", 1, None))
                elif value.tile == "Coal Ore":
                    inventory_add(Item("Coal", 1, None))
                    self.experience_points += 12
                elif value.tile == "Lapis Ore":
                    inventory_add(Item("Lapis Lazuli", 1, None))
                    self.experience_points += 12
                elif value.tile == "Diamond Ore":
                    inventory_add(Item("Diamond", 1, None))
                    self.experience_points += 12
                elif value.tile == "Grass":
                    inventory_add(Item("Dirt", 1, None))
                else:
                    inventory_add(Item(value.tile, 1, None))

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
                World.UnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1], None)
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
                World.UndergroundUnderTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1], None)
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
                World.Tiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1], None)
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
                World.UndergroundTiles[(value.x, value.y)] = Tile("Air", self.target[0], self.target[1], None)

    def render(self, display):
        global backdrop, experience_bar, FPS, breaking_list

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
            pygame.draw.line(display, (0, 0, 0), (500, 500), (500, 484), width=4)
        elif player.direction == 'East':
            pygame.draw.line(display, (0, 0, 0), (500, 500), (516, 500), width=4)
        elif player.direction == 'South':
            pygame.draw.line(display, (0, 0, 0), (500, 500), (500, 516), width=4)
        elif player.direction == 'West':
            pygame.draw.line(display, (0, 0, 0), (500, 500), (484, 500), width=4)

        # DRAW HEALTH BAR
        for j in self.health_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW HUNGER BAR
        for j in self.hunger_vals:
            display.blit(j.img, (j.x, j.y))

        # DRAW EXPERIENCE BAR
        fontx = pygame.font.Font('images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 30*2)
        pygame.draw.rect(display, "#72a34c", (5, 420 * 2, round(self.percent_xp_to_next_level * 990), 40))
        pygame.draw.rect(display, "#424d42", (round(self.percent_xp_to_next_level * 990) + 5, 420 * 2, round((1 - self.percent_xp_to_next_level) * 990), 40))
        for i in range(18):
            pygame.draw.rect(display, (0, 0, 0), (i * 55 + 5, 420*2, 55, 40), 3)
        experience_number = fontx.render(str(math.floor(self.experience_levels)), True, '#82b054', (255, 255, 255))
        experience_number_r = experience_number.get_rect()
        experience_number_r.center = (252 * 2, 410 * 2)
        display.blit(experience_number, experience_number_r)  # Experience Number

        # GENERATE HOTBAR LIST
        for i in range(27, 36):
            if self.inventory_list[i] is None:  # Set White Background for NONE Slots
                self.hotbar_imgs[i - 27].img = slot
                self.number_list[i] = ''
            else:  # No Enchantments
                self.hotbar_imgs[i - 27].img = self.inventory_list[i].img
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
                    display.blit(TC_GLINTS[player.inventory_list[i+27].name], (self.hotbar_imgs[i].x, self.hotbar_imgs[i].y))

        # DRAW HOTBAR BACKGROUNDS
        for j in self.hotbar_backgrounds:
            pygame.draw.rect(display, j.colour, j.rect, j.width)

        # SETUP HOTBAR NUMBERS
        font = pygame.font.Font(
            'images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 16*2)

        pygame_number_text = [
            Text(font.render(self.number_list[27], True, (255, 0, 0), (255, 255, 255)), 40*2, 480*2),
            Text(font.render(self.number_list[28], True, (255, 0, 0), (255, 255, 255)), 95*2, 480*2),
            Text(font.render(self.number_list[29], True, (255, 0, 0), (255, 255, 255)), 150*2, 480*2),
            Text(font.render(self.number_list[30], True, (255, 0, 0), (255, 255, 255)), 205*2, 480*2),
            Text(font.render(self.number_list[31], True, (255, 0, 0), (255, 255, 255)), 260*2, 480*2),
            Text(font.render(self.number_list[32], True, (255, 0, 0), (255, 255, 255)), 315*2, 480*2),
            Text(font.render(self.number_list[33], True, (255, 0, 0), (255, 255, 255)), 370*2, 480*2),
            Text(font.render(self.number_list[34], True, (255, 0, 0), (255, 255, 255)), 425*2, 480*2),
            Text(font.render(self.number_list[35], True, (255, 0, 0), (255, 255, 255)), 480*2, 480*2)
        ]

        # DRAW HOTBAR NUMBERS
        for j in pygame_number_text:
            display.blit(j.surface, (j.x, j.y))

        # RENDER F3 Screen
        if player.F3:
            font9 = pygame.font.Font(
                'images_vB1_0_pre1/minecraft-font/MinecraftRegular-Bmg3.otf', 20*2)
            version = font9.render("Tilecraft vBeta 1.0 Pre-Release 1", True, (0, 0, 0), (255, 255, 255))
            display.blit(version, (0, 0))
            python_version = font9.render("Python 3.10.1", True, (0, 0, 0), (255, 255, 255))
            display.blit(python_version, (0, 20*2))
            pygame_version = font9.render("Graphics: pygame v2.1.2", True, (0, 0, 0), (255, 255, 255))
            display.blit(pygame_version, (0, 40*2))
            SEEDs = font9.render(f"Seed: {World.seed}", True, (0, 0, 0), (255, 255, 255))
            display.blit(SEEDs, (0, 60*2))
            FPS = font9.render(f"FPS: {FPS}", True, (0, 0, 0), (255, 255, 255))
            display.blit(FPS, (0, 80*2))
            Direction = font9.render(f"Facing: {self.direction}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Direction, (0, 100*2))
            Target = font9.render(f"Target Tile: {self.target[0]}, {self.target[1]}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Target, (0, 120*2))
            Coords = font9.render(f"X: {round(player.x, 3)}, Y: {round(player.y, 3)}", True, (0, 0, 0), (255, 255, 255))
            display.blit(Coords, (0, 140*2))

def exit_death_screen():
    global death_window
    death_window.destroy()
    title_screen()


def death_screen():
    global death_window, true_play_time
    death_window = tkinter.Tk()
    death_window.title("Tilecraft Beta 1.0 Pre-Release 1")
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

class Recipe:
    def __init__(self, requirements, result):
        self.requirements = requirements
        self.result = (result.name, result.number, result.enchantments)

    def canCraft(self):
        global player
        for i in range(9):
            if player.grid_list[i] is not None:
                if player.grid_list[i].name != self.requirements[i]:
                    return False
            elif player.grid_list[i] != self.requirements[i]:
                return False
        return True

    def craft(self):
        if player.grid_list[9] != Item(self.result[0], self.result[1], self.result[2]):
            player.grid_list[9] = Item(self.result[0], self.result[1], self.result[2])

def IntialiseDetails():
    global hasGeneratedOverworld, display, clock
    # Play Minecraft Music (Sweden)
    pygame.mixer.init()
    pygame.mixer.music.load("images_vB1_0_pre1/music/song" + str(random.choice([3, 5, 7, 11, 12, 13, 14, 18])) + ".mp3")
    pygame.mixer.music.play()

    global netherGenerated, background, numList, call, difference, FPS, individual_frame, second_time, start, load, frame

    '''Create Items'''

    global hotbar_imgs, pygame_enchant_imgs, hotbar_order, none_img, fire, no_fire

    # Create PYGAME inventory images for hotbar
    wood = pygame.image.load("images_vB1_0_pre1/item_imgs/oak_log.png").convert_alpha() #0
    planks = pygame.image.load("images_vB1_0_pre1/item_imgs/oak_planks.png").convert_alpha() #1
    stick = pygame.image.load("images_vB1_0_pre1/item_imgs/stick.png").convert_alpha() #2
    crafting_table = pygame.image.load("images_vB1_0_pre1/item_imgs/crafting_table.png").convert_alpha() #3
    wooden_pickaxe = pygame.image.load("images_vB1_0_pre1/item_imgs/wooden_pickaxe.png").convert_alpha() #4
    wooden_axe = pygame.image.load("images_vB1_0_pre1/item_imgs/wooden_axe.png").convert_alpha() #5
    wooden_shovel = pygame.image.load("images_vB1_0_pre1/item_imgs/wooden_shovel.png").convert_alpha() #6
    wooden_hoe = pygame.image.load("images_vB1_0_pre1/item_imgs/wooden_hoe.png").convert_alpha() #7
    cobblestone = pygame.image.load("images_vB1_0_pre1/item_imgs/cobblestone.png").convert_alpha() #8
    mine_entrance = pygame.image.load("images_vB1_0_pre1/item_imgs/mine_entrance.png").convert_alpha() #9
    stone_pickaxe = pygame.image.load("images_vB1_0_pre1/item_imgs/stone_pickaxe.png").convert_alpha() #10
    stone_axe = pygame.image.load("images_vB1_0_pre1/item_imgs/stone_axe.png").convert_alpha() #11
    stone_shovel = pygame.image.load("images_vB1_0_pre1/item_imgs/stone_shovel.png").convert_alpha() #12
    stone_hoe = pygame.image.load("images_vB1_0_pre1/item_imgs/stone_hoe.png").convert_alpha() #13
    furnace = pygame.image.load("images_vB1_0_pre1/item_imgs/furnace.png").convert_alpha() #14
    compressor = pygame.image.load("images_vB1_0_pre1/item_imgs/compressor.png").convert_alpha() #15
    coal = pygame.image.load("images_vB1_0_pre1/item_imgs/coal.png").convert_alpha() #16
    iron_ore = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_ore.png").convert_alpha() #17
    iron_ingot = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_ingot.png").convert_alpha() #18
    iron_pickaxe = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_pickaxe.png").convert_alpha() #19
    iron_axe = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_axe.png").convert_alpha() #20
    iron_shovel = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_shovel.png").convert_alpha() #21
    iron_hoe = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_hoe.png").convert_alpha() #22
    bucket = pygame.image.load("images_vB1_0_pre1/item_imgs/bucket.png").convert_alpha() #23
    water_bucket = pygame.image.load("images_vB1_0_pre1/item_imgs/water_bucket.png").convert_alpha() #24
    lava_bucket = pygame.image.load("images_vB1_0_pre1/item_imgs/lava_bucket.png").convert_alpha() #25
    shield = pygame.image.load("images_vB1_0_pre1/item_imgs/shield.png").convert_alpha() #26
    flint_and_steel = pygame.image.load("images_vB1_0_pre1/item_imgs/flint_and_steel.png").convert_alpha() #27
    iron_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/iron_plate.png").convert_alpha() #28
    tier1_iron_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier1_iron_plate.png").convert_alpha() #29
    tier2_iron_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier2_iron_plate.png").convert_alpha() #30
    tier3_iron_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier3_iron_plate.png").convert_alpha() #31
    diamond = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond.png").convert_alpha() #32
    diamond_pickaxe = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond_pickaxe.png").convert_alpha() #33
    diamond_axe = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond_axe.png").convert_alpha() #34
    diamond_shovel = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond_shovel.png").convert_alpha() #35
    diamond_hoe = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond_hoe.png").convert_alpha() #36
    diamond_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/diamond_plate.png").convert_alpha() #37
    tier1_diamond_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier1_diamond_plate.png").convert_alpha() #38
    tier2_diamond_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier2_diamond_plate.png").convert_alpha() #39
    tier3_diamond_plate = pygame.image.load("images_vB1_0_pre1/item_imgs/tier3_diamond_plate.png").convert_alpha() #40
    jukebox = pygame.image.load("images_vB1_0_pre1/item_imgs/jukebox.png").convert_alpha() #41
    pigstep_disc = pygame.image.load("images_vB1_0_pre1/item_imgs/pigstep_disc.png").convert_alpha() #42
    obsidian = pygame.image.load("images_vB1_0_pre1/item_imgs/obsidian.png").convert_alpha() #43
    enchanting_table = pygame.image.load("images_vB1_0_pre1/item_imgs/enchanting_table.png").convert_alpha() #44
    book = pygame.image.load("images_vB1_0_pre1/item_imgs/book.png").convert_alpha() #45
    bookshelf = pygame.image.load("images_vB1_0_pre1/item_imgs/bookshelf.png").convert_alpha() #46
    lapis = pygame.image.load("images_vB1_0_pre1/item_imgs/lapis_lazuli.png").convert_alpha() #47
    bread = pygame.image.load("images_vB1_0_pre1/item_imgs/bread.png").convert_alpha() #48
    golden_carrot = pygame.image.load("images_vB1_0_pre1/item_imgs/golden_carrot.png").convert_alpha() #49
    golden_apple = pygame.image.load("images_vB1_0_pre1/item_imgs/golden_apple.png") #50
    dirt = pygame.image.load("images_vB1_0_pre1/item_imgs/dirt.png").convert_alpha() #51
    sand = pygame.image.load("images_vB1_0_pre1/item_imgs/sand.png").convert_alpha() #52
    snow = pygame.image.load("images_vB1_0_pre1/item_imgs/snow.png").convert_alpha() #53
    gravel = pygame.image.load("images_vB1_0_pre1/item_imgs/gravel.png").convert_alpha() #54
    flint = pygame.image.load("images_vB1_0_pre1/item_imgs/flint.png").convert_alpha() #55
    bed = pygame.image.load("images_vB1_0_pre1/item_imgs/bed.png").convert_alpha() #56
    hay = pygame.image.load("images_vB1_0_pre1/item_imgs/hay_bale.png").convert_alpha() #57

    none_img = pygame.image.load("images_vB1_0_pre1/item_imgs/slot.png").convert_alpha()  # White Space
    fire = pygame.image.load("images_vB1_0_pre1/item_imgs/fire.png").convert_alpha()  # Fire when smelting
    no_fire = pygame.image.load("images_vB1_0_pre1/item_imgs/no_fire.png").convert_alpha()  # No fire when smelting

    # List for Hotbar Orders
    hotbar_order = ['Hotbar1', 'Hotbar2', 'Hotbar3', 'Hotbar4', 'Hotbar5', 'Hotbar6', 'Hotbar7', 'Hotbar8', 'Hotbar9']

    global ITEM_COLOURS
    ITEM_COLOURS = { #Colours for all rarities
        1: (255, 255, 255),
        2: (0, 255, 0),
        3: (0, 0, 255),
        4: "#C71585",
        5: "#d4af37"
    }

    TC_RARITIES = { #Rarities and their levels
        "Common": 1,
        "Uncommon": 2,
        "Rare": 3,
        "Epic": 4,
        "Legendary": 5
    }

    #Dictionary of all items in the game
    global TC_ITEMS
    TC_ITEMS = {
        "Oak Log": ITEM_TYPE(wood, "Item", 64, None, TC_RARITIES["Common"]),
        "Oak Planks": ITEM_TYPE(planks, "Item", 64, None, TC_RARITIES["Common"]),
        "Stick": ITEM_TYPE(stick, "Item", 64, None, TC_RARITIES["Common"]),
        "Crafting Table": ITEM_TYPE(crafting_table, "Item", 64, None, TC_RARITIES["Common"]),
        "Wooden Pickaxe": ITEM_TYPE(wooden_pickaxe, "Pickaxe", 1, 1, TC_RARITIES["Common"]),
        "Wooden Axe": ITEM_TYPE(wooden_axe, "Axe", 1, 1, TC_RARITIES["Common"]),
        "Wooden Shovel": ITEM_TYPE(wooden_shovel, "Shovel", 1, 1, TC_RARITIES["Common"]),
        "Wooden Hoe": ITEM_TYPE(wooden_hoe, "Hoe", 1, 1, TC_RARITIES["Common"]),
        "Cobblestone": ITEM_TYPE(cobblestone, "Item", 64, None, TC_RARITIES["Common"]),
        "Mine Entrance": ITEM_TYPE(mine_entrance, "Item", 64, None, TC_RARITIES["Common"]),
        "Stone Pickaxe": ITEM_TYPE(stone_pickaxe, "Pickaxe", 1, 2, TC_RARITIES["Common"]),
        "Stone Axe": ITEM_TYPE(stone_axe, "Axe", 1, 2, TC_RARITIES["Common"]),
        "Stone Shovel": ITEM_TYPE(stone_shovel, "Shovel", 1, 2, TC_RARITIES["Common"]),
        "Stone Hoe": ITEM_TYPE(stone_hoe, "Hoe", 1, 2, TC_RARITIES["Common"]),
        "Furnace": ITEM_TYPE(furnace, "Item", 64, None, TC_RARITIES["Common"]),
        "Compressor": ITEM_TYPE(compressor, "Item", 64, None, TC_RARITIES["Common"]),
        "Coal": ITEM_TYPE(coal, "Item", 64, None, TC_RARITIES["Common"]),
        "Iron Ore": ITEM_TYPE(iron_ore, "Item", 64, None, TC_RARITIES["Common"]),
        "Iron Ingot": ITEM_TYPE(iron_ingot, "Item", 64, None, TC_RARITIES["Uncommon"]),
        "Iron Pickaxe": ITEM_TYPE(iron_pickaxe, "Pickaxe", 1, 3, TC_RARITIES["Uncommon"]),
        "Iron Axe": ITEM_TYPE(iron_axe, "Axe", 1, 3, TC_RARITIES["Uncommon"]),
        "Iron Shovel": ITEM_TYPE(iron_shovel, "Shovel", 1, 3, TC_RARITIES["Uncommon"]),
        "Iron Hoe": ITEM_TYPE(iron_hoe, "Hoe", 1, 3, TC_RARITIES["Uncommon"]),
        "Bucket": ITEM_TYPE(bucket, "Item", 64, None, TC_RARITIES["Common"]),
        "Water Bucket": ITEM_TYPE(water_bucket, "Item", 1, None, TC_RARITIES["Common"]),
        "Lava Bucket": ITEM_TYPE(lava_bucket, "Item", 1, None, TC_RARITIES["Common"]),
        "Shield": ITEM_TYPE(shield, "Shield", 1, None, TC_RARITIES["Uncommon"]),
        "Flint and Steel": ITEM_TYPE(flint_and_steel, "Item", 1, None, TC_RARITIES["Common"]),
        "Iron Plate": ITEM_TYPE(iron_plate, "Item", 64, None, TC_RARITIES["Uncommon"]),
        "Tier 1 Iron Plate": ITEM_TYPE(tier1_iron_plate, "Tier1", 1, None, TC_RARITIES["Uncommon"]),
        "Tier 2 Iron Plate": ITEM_TYPE(tier2_iron_plate, "Tier2", 1, None, TC_RARITIES["Uncommon"]),
        "Tier 3 Iron Plate": ITEM_TYPE(tier3_iron_plate, "Tier3", 1, None, TC_RARITIES["Uncommon"]),
        "Diamond": ITEM_TYPE(diamond, "Item", 64, None, TC_RARITIES["Rare"]),
        "Diamond Pickaxe": ITEM_TYPE(diamond_pickaxe, "Pickaxe", 1, 4, TC_RARITIES["Rare"]),
        "Diamond Axe": ITEM_TYPE(diamond_axe, "Axe", 1, 4, TC_RARITIES["Rare"]),
        "Diamond Shovel": ITEM_TYPE(diamond_shovel, "Shovel", 1, 4, TC_RARITIES["Rare"]),
        "Diamond Hoe": ITEM_TYPE(diamond_hoe, "Hoe", 1, 4, TC_RARITIES["Rare"]),
        "Diamond Plate": ITEM_TYPE(diamond_plate, "Item", 64, None, TC_RARITIES["Rare"]),
        "Tier 1 Diamond Plate": ITEM_TYPE(tier1_diamond_plate, "Tier1", 1, None, TC_RARITIES["Rare"]),
        "Tier 2 Diamond Plate": ITEM_TYPE(tier2_diamond_plate, "Tier2", 1, None, TC_RARITIES["Rare"]),
        "Tier 3 Diamond Plate": ITEM_TYPE(tier3_diamond_plate, "Tier3", 1, None, TC_RARITIES["Rare"]),
        "Jukebox": ITEM_TYPE(jukebox, "Item", 64, None, TC_RARITIES["Common"]),
        "Pigstep Disc": ITEM_TYPE(pigstep_disc, "Item", 1, None, TC_RARITIES["Rare"]),
        "Obsidian": ITEM_TYPE(obsidian, "Item", 64, None, TC_RARITIES["Common"]),
        "Enchanting Table": ITEM_TYPE(enchanting_table, "Item", 64, None, TC_RARITIES["Common"]),
        "Book": ITEM_TYPE(book, "Item", 64, None, TC_RARITIES["Common"]),
        "Bookshelf": ITEM_TYPE(bookshelf, "Item", 64, None, TC_RARITIES["Common"]),
        "Lapis Lazuli": ITEM_TYPE(lapis, "Item", 64, None, TC_RARITIES["Uncommon"]),
        "Bread": ITEM_TYPE(bread, "Food", 64, None, TC_RARITIES["Common"]),
        "Golden Carrot": ITEM_TYPE(golden_carrot, "Food", 64, None, TC_RARITIES["Common"]),
        "Golden Apple": ITEM_TYPE(golden_apple, "Food", 64, None, TC_RARITIES["Uncommon"]),
        "Dirt": ITEM_TYPE(dirt, "Item", 64, None, TC_RARITIES["Common"]),
        "Sand": ITEM_TYPE(sand, "Item", 64, None, TC_RARITIES["Common"]),
        "Snow": ITEM_TYPE(snow, "Item", 64, None, TC_RARITIES["Common"]),
        "Gravel": ITEM_TYPE(gravel, "Item", 64, None, TC_RARITIES["Common"]),
        "Flint": ITEM_TYPE(flint, "Item", 64, None, TC_RARITIES["Common"]),
        "Bed": ITEM_TYPE(bed, "Item", 1, None, TC_RARITIES["Common"]),
        "Hay Bale": ITEM_TYPE(hay, "Item", 64, None, TC_RARITIES["Common"]),
    }

    # Create GLINT images for enchanted items
    global TC_GLINTS
    glint_list = []
    glint_fullname_list = []
    glint_num_list = []
    new_glint_name_list = []
    int_glint_num_list = []
    item_names = []
    for filename in os.listdir('images_vB1_0_pre1/glints'):
        glint_num_list.append(filename[5:-4])
        glint_fullname_list.append(filename[:-4])
    for i in glint_num_list:
        int_glint_num_list.append(int(i))
    new_glint_num_list = sorted(int_glint_num_list)
    for i in new_glint_num_list:
        index = glint_num_list.index(str(i))
        new_glint_name_list.append(glint_fullname_list[index])
    for i in new_glint_name_list:
        image = pygame.image.load('images_vB1_0_pre1/glints/' + i + '.png').convert_alpha()
        glint_list.append(image)
    for key, value in TC_ITEMS.items():
        item_names.append(key)
    TC_GLINTS = dict(zip(item_names, glint_list))

    '''Create Tiles'''

    # Create Tile Images
    global oak_log_tile, water_tile, leaf_tile, tree_tile, \
        grass_tile, netherrack_tile, sand_tile, snow_tile, stone_tile,  alpha_stone_tile, \
        mine_entrance_tile, coal_ore_tile, iron_ore_tile, lapis_ore_tile, diamond_ore_tile, alpha_lava_tile
    grass_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/grass.png').convert()  # Grass
    netherrack_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/netherrack.png').convert()  # Netherrack
    sand_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/sand.png').convert()  # Sand
    snow_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/snow.png').convert()  # Snow
    bookshelf_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/bookshelf_tile.png").convert()
    coal_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/coal_ore_tile.png").convert()
    cobblestone_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/cobblestone_tile.png").convert()
    diamond_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/diamond_ore_tile.png").convert()
    dirt_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/dirt_tile.png").convert()
    gravel_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/gravel_tile.png").convert()
    hay_bale_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/hay_bale_tile.png").convert()
    iron_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/iron_ore_tile.png").convert()
    lapis_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/lapis_ore_tile.png").convert()
    lava_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/lava_tile.png").convert()
    leaf_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/leaf.png").convert_alpha()
    mine_entrance_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/mine_entrance_tile.png").convert()
    oak_log_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_log_tile.png").convert()
    oak_planks_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_planks_tile.png").convert()
    obsidian_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/obsidian_tile.png").convert()
    stone_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/stone_tile.png").convert()
    tree_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_log_tile.png")
    water_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/water_tile.png").convert()

    # Create Background Tile Images
    global alpha_grass_tile, alpha_sand_tile, alpha_snow_tile, alpha_water_tile
    alpha_grass_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/grass.png').convert()  # Grass
    alpha_grass_tile.set_alpha(200)
    alpha_netherrack_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/netherrack.png').convert()  # Netherrack
    alpha_netherrack_tile.set_alpha(200)
    alpha_sand_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/sand.png').convert()  # Sand
    alpha_sand_tile.set_alpha(200)
    alpha_snow_tile = pygame.image.load('images_vB1_0_pre1/tile_imgs/snow.png').convert()  # Snow
    alpha_snow_tile.set_alpha(200)
    alpha_bookshelf_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/bookshelf_tile.png").convert()
    alpha_bookshelf_tile.set_alpha(200)
    alpha_coal_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/coal_ore_tile.png").convert()
    alpha_coal_ore_tile.set_alpha(200)
    alpha_cobblestone_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/cobblestone_tile.png").convert()
    alpha_cobblestone_tile.set_alpha(200)
    alpha_diamond_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/diamond_ore_tile.png").convert()
    alpha_diamond_ore_tile.set_alpha(200)
    alpha_dirt_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/dirt_tile.png").convert()
    alpha_dirt_tile.set_alpha(200)
    alpha_gravel_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/gravel_tile.png").convert()
    alpha_gravel_tile.set_alpha(200)
    alpha_hay_bale_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/hay_bale_tile.png").convert()
    alpha_hay_bale_tile.set_alpha(200)
    alpha_iron_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/iron_ore_tile.png").convert()
    alpha_iron_ore_tile.set_alpha(200)
    alpha_lapis_ore_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/lapis_ore_tile.png").convert()
    alpha_lapis_ore_tile.set_alpha(200)
    alpha_lava_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/lava_tile.png").convert()
    alpha_lava_tile.set_alpha(200)
    alpha_leaf_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/leaf.png").convert_alpha()
    alpha_leaf_tile.set_alpha(200)
    alpha_mine_entrance_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/mine_entrance_tile.png").convert()
    alpha_mine_entrance_tile.set_alpha(200)
    alpha_oak_log_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_log_tile.png").convert()
    alpha_oak_log_tile.set_alpha(200)
    alpha_oak_planks_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_planks_tile.png").convert()
    alpha_oak_planks_tile.set_alpha(200)
    alpha_obsidian_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/obsidian_tile.png").convert()
    alpha_obsidian_tile.set_alpha(200)
    alpha_stone_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/stone_tile.png").convert()
    alpha_stone_tile.set_alpha(200)
    alpha_tree_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/oak_log_tile.png")
    alpha_tree_tile.set_alpha(200)
    alpha_water_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/water_tile.png").convert()
    alpha_water_tile.set_alpha(200)

    global bedrock_tile
    bedrock_tile = pygame.image.load("images_vB1_0_pre1/tile_imgs/bedrock.png").convert()
    bedrock_tile.set_alpha(200)

    global TC_TILES
    TC_TILES = {
        "Air": TILE_TYPE(None, None, None, None, None),
        "Grass": TILE_TYPE(grass_tile, alpha_grass_tile, 0.6, "Shovel", 0),
        "Netherrack": TILE_TYPE(netherrack_tile, alpha_netherrack_tile, None, None, None),
        "Sand": TILE_TYPE(sand_tile, alpha_sand_tile, 0.6, "Shovel", 0),
        "Snow": TILE_TYPE(snow_tile, alpha_snow_tile, 0.6, "Shovel", 0),
        "Bookshelf": TILE_TYPE(bookshelf_tile, alpha_bookshelf_tile, 2, "Axe", 0),
        "Coal Ore": TILE_TYPE(coal_ore_tile, alpha_coal_ore_tile, 3, "Pickaxe", 1),
        "Cobblestone": TILE_TYPE(cobblestone_tile, alpha_cobblestone_tile, 2, "Pickaxe", 1),
        "Diamond Ore": TILE_TYPE(diamond_ore_tile, alpha_diamond_ore_tile, 3, "Pickaxe", 3),
        "Dirt": TILE_TYPE(dirt_tile, alpha_dirt_tile, 0.6, "Shovel", 0),
        "Gravel": TILE_TYPE(gravel_tile, alpha_gravel_tile, 0.6, "Shovel", 0),
        "Hay Bale": TILE_TYPE(hay_bale_tile, alpha_hay_bale_tile, 0.5, "Hoe", 0),
        "Iron Ore": TILE_TYPE(iron_ore_tile, alpha_iron_ore_tile, 3, "Pickaxe", 2),
        "Lapis Ore": TILE_TYPE(lapis_ore_tile, alpha_lapis_ore_tile, 3, "Pickaxe", 2),
        "Lava": TILE_TYPE(lava_tile, alpha_lava_tile, None, None, None),
        "Leaf": TILE_TYPE(leaf_tile, alpha_leaf_tile, 0, "None", 0),
        "Mine Entrance": TILE_TYPE(mine_entrance_tile, alpha_mine_entrance_tile, 2, "Pickaxe", 1),
        "Oak Log": TILE_TYPE(oak_log_tile, alpha_oak_log_tile, 2, "Axe", 0),
        "Oak Planks": TILE_TYPE(oak_planks_tile, alpha_oak_planks_tile, 2, "Axe", 0),
        "Obsidian": TILE_TYPE(obsidian_tile, alpha_obsidian_tile, 50, "Pickaxe", 4),
        "Stone": TILE_TYPE(stone_tile, alpha_stone_tile, 1.5, "Pickaxe", 1),
        "Tree": TILE_TYPE(tree_tile, alpha_tree_tile, 2, "Axe", 0),
        "Water": TILE_TYPE(water_tile, alpha_water_tile, None, None, None)
    }

    # Create Breaking Images
    global breaking_list, world
    breaking1 = pygame.image.load('images_vB1_0_pre1/breaking/breaking1.png').convert_alpha()
    breaking2 = pygame.image.load('images_vB1_0_pre1/breaking/breaking2.png').convert_alpha()
    breaking3 = pygame.image.load('images_vB1_0_pre1/breaking/breaking3.png').convert_alpha()
    breaking4 = pygame.image.load('images_vB1_0_pre1/breaking/breaking4.png').convert_alpha()
    breaking5 = pygame.image.load('images_vB1_0_pre1/breaking/breaking5.png').convert_alpha()
    breaking6 = pygame.image.load('images_vB1_0_pre1/breaking/breaking6.png').convert_alpha()
    breaking_list = [breaking1, breaking2, breaking3, breaking4, breaking5, breaking6]

    '''Create Crafting Recipes'''

    OakPlanks_recipe = Recipe(
        ["Oak Log", None, None,
         None, None, None,
         None, None, None], Item("Oak Planks", 4, None))
    Stick_recipe = Recipe(
        ["Oak Planks", None, None,
         "Oak Planks", None, None,
         None, None, None], Item("Stick", 4, None))
    CraftingTable_recipe = Recipe(
        ["Oak Planks", "Oak Planks", None,
        "Oak Planks", "Oak Planks", None,
         None, None, None], Item("Crafting Table", 1, None))
    WoodenPickaxe_recipe = Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
         None, "Stick", None,
         None, "Stick", None], Item("Wooden Pickaxe", 1, None))
    WoodenAxe_recipe = Recipe(
        [None, "Oak Planks", "Oak Planks",
         None, "Stick", "Oak Planks",
         None, "Stick", None], Item("Wooden Axe", 1, None))
    WoodenShovel_recipe = Recipe(
        [None, "Oak Planks", None,
         None, "Stick", None,
         None, "Stick", None], Item("Wooden Shovel", 1, None))
    WoodenHoe_recipe = Recipe(
        [None, "Oak Planks", "Oak Planks",
         None, "Stick", None,
         None, "Stick", None], Item("Wooden Hoe", 1, None))
    MineEntrance_recipe = Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
         "Cobblestone", "Wooden Pickaxe", "Cobblestone",
         "Cobblestone", "Cobblestone", "Cobblestone"], Item("Mine Entrance", 1, None))
    StonePickaxe_recipe = Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
         None, "Stick", None,
         None, "Stick", None], Item("Stone Pickaxe", 1, None))
    StoneAxe_recipe = Recipe(
        [None, "Cobblestone", "Cobblestone",
         None, "Stick", "Cobblestone",
         None, "Stick", None], Item("Stone Axe", 1, None))
    StoneShovel_recipe = Recipe(
        [None, "Cobblestone", None,
         None, "Stick", None,
         None, "Stick", None], Item("Stone Shovel", 1, None))
    StoneHoe_recipe = Recipe(
        [None, "Cobblestone", "Cobblestone",
         None, "Stick", None,
         None, "Stick", None], Item("Stone Hoe", 1, None))
    Furnace_recipe = Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
         "Cobblestone", None, "Cobblestone",
         "Cobblestone", "Cobblestone", "Cobblestone"], Item("Furnace", 1, None))
    Compressor_recipe = Recipe(
        ["Cobblestone", "Cobblestone", "Cobblestone",
         "Cobblestone", "Iron Ingot", "Cobblestone",
         "Cobblestone", "Cobblestone", "Cobblestone"], Item("Compressor", 1, None))
    IronPickaxe_recipe = Recipe(
        ["Iron Ingot", "Iron Ingot", "Iron Ingot",
         None, "Stick", None,
         None, "Stick", None], Item("Iron Pickaxe", 1, None))
    IronAxe_recipe = Recipe(
        [None, "Iron Ingot", "Iron Ingot",
         None, "Stick", "Iron Ingot",
         None, "Stick", None], Item("Iron Axe", 1, None))
    IronShovel_recipe = Recipe(
        [None, "Iron Ingot", None,
         None, "Stick", None,
         None, "Stick", None], Item("Iron Shovel", 1, None))
    IronHoe_recipe = Recipe(
        [None, "Iron Ingot", "Iron Ingot",
         None, "Stick", None,
         None, "Stick", None], Item("Iron Hoe", 1, None))
    Bucket_recipe = Recipe(
        [None, None, None,
         "Iron Ingot", None, "Iron Ingot",
         None, "Iron Ingot", None], Item("Bucket", 1, None))
    Shield_recipe = Recipe(
        ["Oak Planks", "Iron Ingot", "Oak Planks",
         "Oak Planks", "Oak Planks", "Oak Planks",
         None, "Oak Planks", None], Item("Shield", 1, None))
    FlintAndSteel_recipe = Recipe(
        ["Iron Ingot", None, None,
         None, "Flint", None,
         None, None, None], Item("Flint and Steel", 1, None))
    Tier1IronPlate_recipe = Recipe(
        [None, "Iron Plate", None,
         None, None, None,
         None, "Iron Plate", None], Item("Tier 1 Iron Plate", 1, None))
    Tier2IronPlate_recipe = Recipe(
        [None, "Iron Plate", None,
         "Iron Plate", None, "Iron Plate",
         None, "Iron Plate", None], Item("Tier 2 Iron Plate", 1, None))
    Tier3IronPlate_recipe = Recipe(
        ["Iron Plate", "Iron Plate", "Iron Plate",
         "Iron Plate", None, "Iron Plate",
         "Iron Plate", "Iron Plate", "Iron Plate"], Item("Tier 3 Iron Plate", 1, None))
    DiamondPickaxe_recipe = Recipe(
        ["Diamond", "Diamond", "Diamond",
         None, "Stick", None,
         None, "Stick", None], Item("Diamond Pickaxe", 1, None))
    DiamondAxe_recipe = Recipe(
        [None, "Diamond", "Diamond",
         None, "Stick", "Diamond",
         None, "Stick", None], Item("Diamond Axe", 1, None))
    DiamondShovel_recipe = Recipe(
        [None, "Diamond", None,
         None, "Stick", None,
         None, "Stick", None], Item("Diamond Shovel", 1, None))
    DiamondHoe_recipe = Recipe(
        [None, "Diamond", "Diamond",
         None, "Stick", None,
         None, "Stick", None], Item("Diamond Hoe", 1, None))
    Tier1DiamondPlate_recipe = Recipe(
        [None, "Diamond Plate", None,
         None, None, None,
         None, "Diamond Plate", None], Item("Tier 1 Diamond Plate", 1, None))
    Tier2DiamondPlate_recipe = Recipe(
        [None, "Diamond Plate", None,
         "Diamond Plate", None, "Diamond Plate",
         None, "Diamond Plate", None], Item("Tier 2 Diamond Plate", 1, None))
    Tier3DiamondPlate_recipe = Recipe(
        ["Diamond Plate", "Diamond Plate", "Diamond Plate",
         "Diamond Plate", None, "Diamond Plate",
         "Diamond Plate", "Diamond Plate", "Diamond Plate"], Item("Tier 3 Diamond Plate", 1, None))
    Jukebox_recipe = Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
         "Oak Planks", "Diamond", "Oak Planks",
         "Oak Planks", "Oak Planks", "Oak Planks"], Item("Jukebox", 1, None))
    EnchantingTable_recipe = Recipe(
        [None, "Book", None,
         "Diamond", "Obsidian", "Diamond",
         "Obsidian", "Obsidian", "Obsidian"], Item("Enchanting Table", 1, None))
    Bookshelf_recipe = Recipe(
        ["Oak Planks", "Oak Planks", "Oak Planks",
         "Book", "Book", "Book",
         "Oak Planks", "Oak Planks", "Oak Planks"], Item("Bookshelf", 1, None))
    Bread_recipe = Recipe(
        ["Hay Bale", None, None,
         None, None, None,
         None, None, None], Item("Bread", 3, None))

    global recipe_list
    recipe_list = [OakPlanks_recipe, Stick_recipe, CraftingTable_recipe, WoodenPickaxe_recipe, WoodenAxe_recipe,
                   WoodenShovel_recipe, WoodenHoe_recipe, MineEntrance_recipe, StonePickaxe_recipe, StoneAxe_recipe,
                   StoneShovel_recipe, StoneHoe_recipe, Furnace_recipe, Compressor_recipe, IronPickaxe_recipe,
                   IronAxe_recipe, IronShovel_recipe, IronHoe_recipe, Bucket_recipe, Shield_recipe, FlintAndSteel_recipe,
                   Tier1IronPlate_recipe, Tier2IronPlate_recipe, Tier3IronPlate_recipe, DiamondPickaxe_recipe,
                   DiamondAxe_recipe, DiamondShovel_recipe, DiamondHoe_recipe, Tier1DiamondPlate_recipe,
                   Tier2DiamondPlate_recipe, Tier3DiamondPlate_recipe, Jukebox_recipe, EnchantingTable_recipe,
                   Bookshelf_recipe, Bread_recipe]

    '''Create World and Display'''

    global player, World, Option1, Option2, Option3, Upgrade, screen, TimerRunning, world
    world = pygame.Surface((1000, 1000))  # Create Map Surface
    world.fill((0, 0, 0))  # Fill Map Surface Black
    World = TilecraftWorld(GetSeed())  # Create World
    player = Player()  # Create Player
    screen = Screen()  # Create Text Screen
    TimerRunning = True
    Upgrade = Button(55*2, 55*2, 75*2, 95*2, (158, 145, 115))
    Option1 = Button(325*2, 55*2, 170*2, 50*2, (158, 145, 115))
    Option2 = Button(325*2, 55*2, 170*2, 105*2, (158, 145, 115))
    Option3 = Button(325*2, 55*2, 170*2, 160*2, (158, 145, 115))
    hasGeneratedOverworld = True

def create_world():
    global hasGeneratedOverworld, hasGeneratedUnderground
    hasGeneratedOverworld = False
    hasGeneratedUnderground = 'Not Loaded'
    global display, clock, world, netherGenerated, background, numList, call, difference, FPS, individual_frame, second_time, start, load, frame, loading, previous_frame
    pygame.init()  # Initialise Pygame Module
    display = pygame.display.set_mode((1000, 1000))  # Set display
    pygame.display.set_caption("Tilecraft Beta 1.0 Pre-Release 1")  # Set title
    clock = pygame.time.Clock()
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
    loading = pygame.image.load("images_vB1_0_pre1/loading.png").convert()
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
                                hay = random.randint(25, 45)
                                inventory_add(Item("Hay Bale", hay, None))
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
                        inventory_add(Item("Bed", beds, None))
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
                            inventory_add(Item("Iron Ingot", blacksmith_iron, None))
                        if blacksmith_diamond > 0:
                            screen.print(f"+{blacksmith_diamond} Diamond")
                            inventory_add(Item("Diamond", blacksmith_diamond, None))
                        if blacksmith_bread > 0:
                            screen.print(f"+{blacksmith_bread} Bread")
                            inventory_add(Item("Bread", blacksmith_bread, None))

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
                        inventory_add(Item("Bookshelf", library_bookshelf, None))
                        inventory_add(Item("Book", library_books, None))
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
                    if player.hotbar_item.name == 'Bucket':
                        for j in range(len(World.bound_water)):
                            if (World.bound_water[j][0][0] < player.x < World.bound_water[j][0][2]) and (World.bound_water[j][1][0] < player.y < World.bound_water[j][1][2]):
                                screen.print("+1 Water Bucket")
                                screen.print("-1 Bucket")
                                hotbar_index = hotbar_order.index(player.selected_hotbar)
                                player.inventory_list[hotbar_index + 27][1] -= 1  # Subtract 1 Bucket
                                inventory_add(Item("Water Bucket", 1, None))  # Add 1 Water Bucket
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
                                    if random.randint(1, 10) == 1:
                                        flint_val += 1
                                    else:
                                        gravel_val += 1
                                if gravel_val > 0:
                                    screen.print("+" + str(gravel_val) + " Gravel")
                                    inventory_add(Item("Gravel", gravel_val, None))
                                if flint_val > 0:
                                    screen.print("+" + str(flint_val) + " Flint")
                                    inventory_add(Item("Flint", flint_val, None))
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
                        if i.name == 'Water Bucket':  # Test for Water Bucket
                            water_bucket_bool = True
                            break
                for i in player.inventory_list:
                    if i is not None:
                        if i.name == 'Flint and Steel':  # Test for Flint and Steel
                            flint_and_steel_bool = True
                            break
                for i in player.inventory_list:
                    if i is not None:
                        if i.name == "Cobblestone" and i.number > 5:  # Test for at least 6 Cobblestone
                            cobblestone_index = player.inventory_list.index(i)
                            cobblestone_bool = True
                            break

                if water_bucket_bool and flint_and_steel_bool and cobblestone_bool:
                    for j in range(len(World.bound_lava)):
                        if (World.bound_lava[j][0][0] < player.x < World.bound_lava[j][0][2]) and (
                                World.bound_lava[j][1][0] < player.y < World.bound_lava[j][1][2]):
                            screen.print("Built a Nether Portal at your location.")
                            player.inventory_list[cobblestone_index].number -= 6
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
        elif val == "/lootbastion":
            if player.dimension == 'Nether':
                for j in range(len(World.bound_bastion)):
                    if (World.bound_bastion[j][0][0] < player.x < World.bound_bastion[j][0][2]) and (
                            World.bound_bastion[j][1][0] < player.y < World.bound_bastion[j][1][2]):
                        inventory_add(Item("Pigstep Disc", 1, None))
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
                pygame.mixer.music.load("images_vB1_0_pre1/pigstep.mp3")
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
                        if i.name == "Water Bucket":
                            water_bucket_bool = True
                            break

                if player.hotbar_item is not None:
                    if player.hotbar_item.name == "Diamond Pickaxe" and water_bucket_bool:
                        for j in range(len(World.bound_lava)):
                            if (World.bound_lava[j][0][0] < player.x < World.bound_lava[j][0][2]) and (
                                    World.bound_lava[j][1][0] < player.y < World.bound_lava[j][1][2]):
                                screen.print("+1 Obsidian")
                                inventory_add(Item("Obsidian", 1, None))
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
                        inventory_add(Item("Iron Ingot", R_iron_val, None))  # Add Iron Ingot
                        screen.print(f"+{R_iron_val} Iron Ingot")
                        inventory_add(Item("Flint", R_flint_val, None))  # Add Flint
                        screen.print(f"+{R_flint_val} Flint")
                        if R_golden_carrot_val > 0:  # Add Golden Carrot
                            screen.print(f"+{R_golden_carrot_val} Golden Carrot")
                            inventory_add(Item("Golden Carrot", R_golden_carrot_val, None))
                        if R_golden_apple_val > 0:  # Add Golden Apple
                            screen.print(f"+{R_golden_apple_val} Golden Apple")
                            inventory_add(Item("Golden Apple", R_golden_apple_val, None))
                        if R_obsidian_val > 0:  # Add Obsidian
                            screen.print(f"+{R_obsidian_val} Obsidian")
                            inventory_add(Item("Obsidian", R_obsidian_val, None))
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
                print_cheats(list(TC_ITEMS.keys()))
            else:
                screen.print("REQUIRE CHEATS DATAPACK")
        elif val == '/give':
            if load == 'Cheats':
                length = len(list(TC_ITEMS.keys())) - 1
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
    window1.title('Tilecraft Beta 1.0 Pre-Release 1')
    window1.geometry('1000x1000')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40*2)
    font = tkinter.font.Font(family='Minecraft', size=24*2)
    font2 = tkinter.font.Font(family='Minecraft', size=10*2)

    title = tkinter.Label(window1, text='Patch Notes', font=bold_font, fg='black')
    title.place(x=125*2, y=0)

    with open("patch_notes.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window1, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=110, y=50*2)

    back_to_title_screen = tkinter.Button(window1, text='Title Screen', fg='black', font=font, command=BackToTitleScreen)
    back_to_title_screen.place(x=150*2, y=425*2)

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
    window2.title('Tilecraft Beta 1.0 Pre-Release 1')
    window2.geometry('1000x1000')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40*2)
    font = tkinter.font.Font(family='Minecraft', size=24*2)
    font2 = tkinter.font.Font(family='Minecraft', size=10*2)

    title = tkinter.Label(window2, text='How To Play', font=bold_font, fg='black')
    title.place(x=125*2, y=0)

    with open("how_to_play.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window2, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=110, y=50*2)

    back_to_title_screen = tkinter.Button(window2, text='Title Screen', fg='black', font=font, command=BackToTitleScreen2)
    back_to_title_screen.place(x=150*2, y=425*2)

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
    window3.title('Tilecraft Beta 1.0 Pre-Release 1')
    window3.geometry('1000x1000')
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40*2)
    font = tkinter.font.Font(family='Minecraft', size=24*2)
    font2 = tkinter.font.Font(family='Minecraft', size=10*2)

    title = tkinter.Label(window3, text='Credits', font=bold_font, fg='black')
    title.place(x=175*2, y=0)

    with open("credits.txt", "r") as f:
        data = f.read()
    txt = tkinter.Text(window3, width=65, height=27, font=font2)
    txt.insert(tkinter.END, data)
    txt.configure(state='disabled')
    txt.place(x=110, y=50*2)

    back_to_title_screen = tkinter.Button(window3, text='Title Screen', fg='black', font=font, command=BackToTitleScreen3)
    back_to_title_screen.place(x=150*2, y=425*2)

    window3.mainloop()

# Title Screen Function
def title_screen():
    global window, tkvar2, fontStyle2, fileMenu, startWorld, bg, bold_font, regular_font, fontStyle2, font4, tkvar3, first_click

    first_click = True #Set Variable to track when the user first clicked on the seed box

    # Play Minecraft Music
    pygame.mixer.init()
    pygame.mixer.music.load(random.choice(["images_vB1_0_pre1/music/song6.mp3", "images_vB1_0_pre1/music/song8.mp3"]))
    pygame.mixer.music.play()

    # Create tkinter window
    window = tkinter.Tk()
    window.title('Tilecraft Beta 1.0 Pre-Release 1')
    window.geometry('1000x1000')

    # Create background image
    bg = tkinter.PhotoImage(file="images_vB1_0_pre1/background_vB1_0_pre1.png")

    # Create fonts
    bold_font = tkinter.font.Font(family='Minecraft Ten', size=40*2)
    regular_font = tkinter.font.Font(family='Minecraft Regular', size=18*2)
    warning_font = tkinter.font.Font(family='Minecraft Regular', size=10*2)
    fontStyle2 = tkinter.font.Font(size=20*2, family='Minecraft Regular')
    font4 = tkinter.font.Font(size=15*2, family='Minecraft Regular')

    # Create canvas
    canvas1 = tkinter.Canvas(window, width=500*2, height=500*2)
    canvas1.create_image(0, 0, image=bg, anchor="nw")
    canvas1.create_text(250*2, 25*2, fill="black", font=bold_font, text="Tilecraft")
    canvas1.create_text(250*2, 50*2, fill="black", font=regular_font, text="Beta 1.0 Pre-Release 1")
    canvas1.create_text(250*2, 75*2, fill="red", font=warning_font, text="Warning! This is a pre-release version and contains many bugs.")
    canvas1.place(x=0, y=0)

    #Create Seed Box Entry Widget
    tkvar3 = tkinter.StringVar(window)
    tkvar3.set('World Seed: ')
    SeedBox = tkinter.Entry(window, textvariable=tkvar3)
    SeedBox.configure(width=35, fg='white', font=font4)
    SeedBox.place(x=80*2, y=100*2)

    # Create a tkinter variable
    tkvar2 = tkinter.StringVar(window)
    tkvar2.set('None')

    # Set choices for option menu
    choices = {'"Music Player" Speedrun Data Pack', '"God Gear" Speedrun Data Pack', 'Cheats Data Pack', 'None'}

    # Option menu for datapacks
    fileMenu = tkinter.OptionMenu(window, tkvar2, *choices)
    fileMenu.configure(width=33, foreground='black', font=font4)
    fileMenu.place(x=80*2, y=125*2)

    # New World button
    startWorld = tkinter.Button(window, text="New World", command=create_world, width="25", height="2", font=fontStyle2,
                                foreground='black')
    startWorld.place(x=80*2, y=145*2)

    # How to play button
    htp = tkinter.Button(window, text="How to Play", width="25", height="2", font=fontStyle2, foreground='black', command=howtoplay)
    htp.place(x=80*2, y=195*2)

    # Patch Notes
    patch_notes = tkinter.Button(window, text="Patch Notes", width="25", height="2", font=fontStyle2, foreground='black', command=patchnotes)
    patch_notes.place(x=80*2, y=245*2)

    #Credits
    Credits = tkinter.Button(window, text="Credits", width="25", height="2", font=fontStyle2, foreground='black', command=game_credits)
    Credits.place(x=80 * 2, y=295 * 2)

    # Quit Button
    quit_button = tkinter.Button(window, text="Quit", command=Quit, width="25", height="2", font=fontStyle2, foreground='black')
    quit_button.place(x=80*2, y=345*2)

    #Clicking on Seedbox entry widget
    SeedBox.bind('<FocusIn>', get_first_click)

    # Tkinter main loop
    window.mainloop()

def RemoveItem():
    global player
    # Remove Value if Number is 0
    for i in range(len(player.enchanting_list)):
        if player.enchanting_list[i] is not None:
            if player.enchanting_list[i].number <= 0:
                player.enchanting_list[i] = None
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].number <= 0:
                player.inventory_list[i] = None
    for i in range(len(player.craft_list)):
        if player.craft_list[i] is not None:
            if player.craft_list[i].number <= 0:
                player.craft_list[i] = None
    if player.holding_item is not None:
        if player.holding_item.number <= 0:
            player.holding_item = None
    for i in range(len(player.grid_list)):
        if player.grid_list[i] is not None:
            if player.grid_list[i].number <= 0:
                player.grid_list[i] = None
    for i in range(len(player.smelting_list)):
        if player.smelting_list[i] is not None:
            if player.smelting_list[i].number <= 0:
                player.smelting_list[i] = None
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].number <= 0:
                player.compressor_list[i] = None

def Crafting():
    if player.mode == "inventory":
        global craft_list
        if player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is None:
            if player.craft_list[0].name == 'Oak Log':
                player.craft_list[4] = Item("Oak Planks", 4, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is not None and player.craft_list[3] is None:
            if player.craft_list[0].name == 'Oak Planks' and player.craft_list[2].name == 'Oak Planks':
                player.craft_list[4] = Item("Stick", 4, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is not None and player.craft_list[2] is not None and player.craft_list[3] is not None:
            if player.craft_list[0].name == 'Oak Planks' and player.craft_list[1].name == 'Oak Planks' and player.craft_list[2].name == 'Oak Planks' and player.craft_list[3].name == 'Oak Planks':
                player.craft_list[4] = Item("Crafting Table", 1, None)
            else:
                player.craft_list[4] = None
        elif player.craft_list[0] is not None and player.craft_list[1] is None and player.craft_list[2] is None and player.craft_list[3] is not None:
            if player.craft_list[0].name == 'Iron Ingot' and player.craft_list[3].name == 'Flint':
                player.craft_list[4] = Item("Flint and Steel", 1, None)
            else:
                player.craft_list[4] = None
        else:
            player.craft_list[4] = None

def GridCraft():
    global recipe_list
    if player.mode == "crafting":
        for recipe in recipe_list:
            if recipe.canCraft():
                #print(recipe.requirements, recipe.result.name)
                recipe.craft()
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
                player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[0][0:-2], int(player.option_list[0][-1])]])
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
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2], int(player.option_list[1][-1])], ['Unbreaking', player.optional_enchant2]])
                    else:  # No extra enchantment
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2], int(player.option_list[1][-1])]])
                else:
                    player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[1][0:-2], int(player.option_list[1][-1])]])
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
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])], ['Unbreaking', player.optional_enchant3]])
                    else:  # No extra enchantment
                        player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])]])
                else:  # No extra enchantment
                    player.enchanting_list[0] = Item(player.enchanting_list[0].name, player.enchanting_list[0].number, [[player.option_list[2][0:-2], int(player.option_list[2][-1])]])
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
                        player.inventory_list[j] = Item(player.inventory_list[j].name, item.number + player.inventory_list[j].number, player.inventory_list[j].enchantments) #Add values
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
                        player.inventory_list[none_index] = Item(player.inventory_list[i].name, 1, player.inventory_list[i].enchantments)
                    count += 1
                player.inventory_list[i] = None
            elif player.inventory_list[i].stackNum == 64 and player.inventory_list[i].number > 64:  # Item
                while player.inventory_list[i].number > 64:  # Separate into stacks of 64
                    player.inventory_list[i].number -= 64
                    if None in player.inventory_list:
                        none_index = player.inventory_list.index(None)
                        player.inventory_list[none_index] = Item(player.inventory_list[i].name, 64, player.inventory_list[i].enchantments)
                if None in player.inventory_list:  # Remainder (Less than 64)
                    none_index = player.inventory_list.index(None)
                    player.inventory_list[none_index] = Item(player.inventory_list[i].name, player.inventory_list[i].number, player.inventory_list[i].enchantments)
                    player.inventory_list[i] = None
#UP TO HERE
# Render Inventory List to Image and Number List
def image_render():
    global pygame_enchant_imgs, player, enchant_name_list, enchant_img_list, enchanting_list, enchanting_image_list, enchanting_number_list, experience, smelting_time, no_fire, fire, fuel_val, inventory_list, image_list, number_list, armour_image_list, craft_image_list, craft_number_list, grid_image_list, grid_number_list, grid_list, smelting_list, smelt_image_list, smelt_number_list, fuel_img
    player.image_list, player.number_list, player.armour_image_list, player.craft_image_list, \
    player.craft_number_list, player.grid_image_list, player.grid_number_list, player.smelt_image_list, \
    player.smelt_number_list, player.enchanting_image_list, player.enchanting_number_list, player.compressor_image_list, \
    player.compressor_number_list, player.layer_list = [], [], [], [], [], [], [], [], [], [], [], [], [], []

    '''Inventory Section'''

    # Remove Values with 0
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].number == 0:
                player.inventory_list[i] = None

    # Create images list and number list
    for i in player.inventory_list:
        if i is None:  # Set White Background for NONE Slots
            player.image_list.append(none_img)
            player.number_list.append('')
        else:
            player.image_list.append(i.img)
            player.number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.inventory_list)):
        if player.inventory_list[i] is not None:
            if player.inventory_list[i].number == 1:
                player.number_list[i] = ''

    #Create Holding Item for Inventory
    if player.holding_item is None:
        player.holding_item_image = none_img
        player.holding_item_number = ''
    else:
        player.holding_item_image = player.holding_item.img
        player.holding_item_number = str(player.holding_item.number)

    if player.holding_item is not None:
        if player.holding_item.number == 1:
            player.holding_item_number = ''

    '''Armour Section'''

    # Create armour image list for armour slots
    for j in player.armour_list:
        if j is None:  # Set White Background for NONE Slots
            player.armour_image_list.append(none_img)
        else:
            player.armour_image_list.append(j.img)

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
            player.craft_image_list.append(none_img)
            player.craft_number_list.append('')
        else:
            player.craft_image_list.append(i.img)
            player.craft_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for j in range(len(player.craft_list)):
        if player.craft_list[j] is not None:
            if player.craft_list[j].number == 1:
                player.craft_number_list[j] = ''

    '''Crafting Section (3x3)'''

    for i in player.grid_list:
        if i is None:  # Set White Background for NONE Slots
            player.grid_image_list.append(none_img)
            player.grid_number_list.append('')
        else:
            player.grid_image_list.append(i.img)
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
            player.smelt_image_list.append(none_img)
            player.smelt_number_list.append('')
        else:
            player.smelt_image_list.append(i.img)
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
            player.enchanting_image_list.append(none_img)
            player.enchanting_number_list.append('')
        else:
            player.enchanting_image_list.append(i.img)
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
            player.compressor_image_list.append(none_img)
            player.compressor_number_list.append('')
        else:
            player.compressor_image_list.append(i.img)
            player.compressor_number_list.append(str(i.number))

    # Remove Value if Number is 1
    for i in range(len(player.compressor_list)):
        if player.compressor_list[i] is not None:
            if player.compressor_list[i].number == 1:
                player.compressor_number_list[i] = ''
title_screen()