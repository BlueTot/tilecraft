import random
import noise

from .constants import TILE_TYPES, RandomNumberGenerator

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


def RandomPos(rng: RandomNumberGenerator, Seed, Pos, Range):
    x, y = Pos
    a, b = Range
    random.seed((Seed % 2048) * 2 - 5)
    for i in range(x % 50):
        for j in range(y % 50 - 1):
            value = rng.next_random(a, b)
    value = rng.next_random(a, b)
    return value

def OverworldGeneratedList():
    generated_list = []
    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            generated_list.append([i, j])
    return generated_list


def OverworldGenerate(rng: RandomNumberGenerator, ChunkX, ChunkY, villages, ruined_portals, obsidian_counts,
                      generated_list, bound_village, bound_village2, bound_village3, bound_village4,
                      bound_ruined_portal, bound_ruined_portal2, seed, UnderTiles, Tiles):

    num = RandomPos(rng, seed, (ChunkX, ChunkY), (1, 25))
    if num == 1 or num == 2:
        villages.append([ChunkX - 12, ChunkY - 12])  # Village
        bound_village.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 1
        bound_village2.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 2
        bound_village3.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 3
        bound_village4.append([[ChunkX - 12 - 10 / 32, ChunkX - 12, ChunkX - 12 + 10 / 32], [ChunkY - 12 - 10 / 32, ChunkY - 12, ChunkY - 12 + 10 / 32]])  # Bounding box for village 4
    elif num == 15 or num == 16 or num == 17:
        ruined_portals.append([ChunkX - 1, ChunkY - 1])  # Ruined Portal
        obsidian_counts.append(int(RandomPos(rng, seed, (ChunkX, ChunkY), (5, 10))))  # Obsidian remaining in ruined portal
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
            x = i + RandomPos(rng, seed, (i, j), (1, 4))
            y = j + RandomPos(rng, seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and RandomPos(rng, seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 16)) == 5:
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
            x = i + RandomPos(rng, seed, (i, j), (1, 8))
            y = j + RandomPos(rng, seed, (i, j), (1, 8))
            canGenerateWaterPool = False
            canGenerateLavaPool = False
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 32)) == 10:
                canGenerateWaterPool = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 32)) == 30:
                canGenerateLavaPool = True
            if canGenerateWaterPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Water", x + X, y + Y)
                        else:
                            if RandomPos(rng, seed, (x + X, y + Y), (1, 3)) == 1:
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
                                if RandomPos(rng, seed, (x + X, y + Y), (1, 3)) == 1:
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


def SpawnOverworldGenerate(rng: RandomNumberGenerator, seed):
    li_vil = []
    li_ruined_portal = []
    villages = []
    ruined_portals = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = RandomPos(rng, seed, (i, j), (1, 25))
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
        obsidian_counts.append(int(RandomPos(rng, seed, (ruined_portals[i][0] + 1, ruined_portals[i][1] + 1), (5, 10))))

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
            x = i + RandomPos(rng, seed, (i, j), (1, 4))
            y = j + RandomPos(rng, seed, (i, j), (1, 4))
            canGenerateTree = False
            canGenerateBoulder = False
            if UnderTiles[(i, j)].tile == "Grass" and RandomPos(rng, seed, (x, y), (1, 8)) == 1:
                canGenerateTree = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 16)) == 5:
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
            x = i + RandomPos(rng, seed, (i, j), (1, 8))
            y = j + RandomPos(rng, seed, (i, j), (1, 8))
            canGenerateWaterPool = False
            canGenerateLavaPool = False
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 32)) == 10:
                canGenerateWaterPool = True
            if UnderTiles[(i, j)].tile != "Water" and RandomPos(rng, seed, (x, y), (1, 32)) == 30:
                canGenerateLavaPool = True
            if canGenerateWaterPool:
                for X in range(8):
                    for Y in range(8):
                        if not (X == 0 and Y == 0 or X == 0 and Y == 1 or X == 1 and Y == 0 or X == 7 and Y == 0 or \
                                X == 6 and Y == 0 or X == 7 and Y == 1 or X == 0 and Y == 6 or X == 0 and Y == 7 or \
                                X == 1 and Y == 7 or X == 7 and Y == 7 or X == 6 and Y == 7 or X == 7 and Y == 6):
                            UnderTiles[(x + X, y + Y)] = Tile("Water", x + X, y + Y)
                        else:
                            if RandomPos(rng, seed, (x + X, y + Y), (1, 3)) == 1:
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
                                if RandomPos(rng, seed, (x + X, y + Y), (1, 3)) == 1:
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

def SpawnUndergroundGenerate(rng: RandomNumberGenerator, seed):
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
                num = RandomPos(rng, seed, (i, j), (1, 9))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
            else:
                num = RandomPos(rng, seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
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

def UndergroundGenerate(rng: RandomNumberGenerator, seed, ChunkX, ChunkY, UnderTiles, Tiles, UndergroundGeneratedList):
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
                num = RandomPos(rng, seed, (i, j), (1, 12))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 6:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Lapis Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 7:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Diamond Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
            else:
                num = RandomPos(rng, seed, (i, j), (1, 6))
                if num == 1 or num == 2 or num == 3:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Coal Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
                elif num == 4 or num == 5:
                    vein_size = RandomPos(rng, seed, (i, j), (1, 4))
                    Tiles = GenerateOres("Iron Ore", vein_size, Tiles, i + RandomPos(rng, seed, (i, j), (1, 8)), j + RandomPos(rng, seed, (i, j), (1, 8)))
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

def SpawnNetherGenerate(rng: RandomNumberGenerator, seed):
    li_bastion = []
    li_fortress = []
    bastions = []
    fortresses = []

    # Generate Chunks from -64 to +64 x and y
    # 8 Chunks per Axis = 64 Total Spawn Chunks

    for i in range(-64, 65, 16):
        for j in range(-64, 65, 16):
            num = RandomPos(rng, seed, (i, j), (1, 15))
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

def NetherGenerate(rng: RandomNumberGenerator, ChunkX, ChunkY, bastions, fortresses, generated_list, bound_bastion, seed):
    num = RandomPos(rng, seed, (ChunkX, ChunkY), (1, 15))
    if num == 1 or num == 2 or num == 3:
        bastions.append([ChunkX - 6, ChunkY - 6])  # Bastion
        bound_bastion.append([[ChunkX - 6 - 10 / 32, ChunkX - 6, ChunkX - 6 + 10 / 32], [ChunkY - 6 - 10 / 32, ChunkY - 6, ChunkY - 6 + 10 / 32]])  # Bounding box
    elif num == 4 or num == 5 or num == 6:
        fortresses.append([ChunkX - 10, ChunkY - 10])  # Fortress
    generated_list.append([ChunkX, ChunkY])  # Chunk is now generated and cannot generate again

    return bastions, fortresses, generated_list, bound_bastion