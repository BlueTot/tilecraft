from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Optional


@dataclass(frozen=True)
class Enchantment:
    """ An enchantment has a name and a level >= 1 """
    name: str
    level: int


    def __post_init__(self) -> None:
        if self.level <= 0:
            raise ValueError("Enchantment level must not be 0")


    @classmethod
    def new_optional(cls, name: str, level: int) -> Optional[Enchantment]:
        """
            Returns None if `level` is 0, otherwise a new Enchantment
        """
        if level < 0:
            raise ValueError("Enchantment level cannot be negative")
        if level == 0:
            return None
        return cls(name, level)


    @classmethod
    def clone(cls, enchantment: Enchantment) -> Enchantment:
        """ Clones the enchantment object """
        return cls(enchantment.name, enchantment.level)


@dataclass(frozen=True)
class Item:
    """ Item in the inventory """

    name: str
    number: int
    enchantments: tuple[Enchantment, ...]
    durability: Optional[int]

    VALID_TILES = {
        "Bookshelf", "Cobblestone", "Gravel", "Hay Bale", "Iron Ore", "Oak Log",
        "Oak Planks", "Obsidian", "Mine Entrance", "Dirt", "Sand", "Snow"
    }

    def __post_init__(self) -> None:

        # normalise enchantments as tuple, as type hints do not prevent passing a list at runtime
        object.__setattr__(self, "enchantments", tuple(self.enchantments))

        if self.number <= 0:
            raise ValueError("number must be positive")
        if self.durability is not None and self.durability <= 0:
            raise ValueError("durability must be positive")
        if self.durability is not None and self.max_durability is not None and self.durability > self.max_durability:
            raise ValueError(f"durability cannot exceed the maximum value of {self.max_durability}")

    #########################################################
    #                      GETTERS                          #
    #########################################################

    @property
    def max_quantity(self) -> int:
        """ Maximum number of the item in a given stack """
        return ITEM_TYPES[self.name].stack


    @property
    def item_type(self) -> str:
        """ Type of the item """
        return ITEM_TYPES[self.name].type


    @property
    def tool_tier(self) -> Optional[int]:
        """ Tier of the tool, starting from 1 if applicable """
        return ITEM_TYPES[self.name].tier #Tier of tool


    @property
    def max_durability(self) -> Optional[int]:
        """ Maximum durability of the tool, if applicable """
        return ITEM_TYPES[self.name].max_durability


    @property
    def mining_speed(self) -> Optional[int]:
        """ Mining speed of the tool, if applicable """
        if self.tool_tier is None:
            return None
        result = 2 * self.tool_tier - 1
        for enchantment in (self.enchantments or []):
            if enchantment.name == "Efficiency":
                result += enchantment.level ** 2 + 1
        return result


    @property
    def rarity(self) -> int:
        """ Rarity of the item, as an integer """
        if not self.is_enchanted:
            return ITEM_TYPES[self.name].rarity
        return ITEM_TYPES[self.name].rarity + 1


    @property
    def colour(self) -> tuple[int, int, int] | str:
        """ Colour of the item, determined by its rarity """
        return ITEM_COLOURS[self.rarity]


    @property
    def has_tile(self) -> bool:
        """ Whether the item is a placeable tile or not """
        return self.name in self.VALID_TILES


    @property
    def target_tile(self) -> Optional[str]:
        """ The name of the item if it is placeable, otherwise None """
        return self.name if self.has_tile else None


    @property
    def is_enchanted(self) -> bool:
        """ True if the item has at least one enchantment """
        return len(self.enchantments) > 0


    #########################################################
    #                    CONSTRUCTORS                       #
    #########################################################


    @classmethod
    def new(cls, name: str, number: int) -> Item:
        """ Return a new unenchanted item set to the maximum durability """
        return cls(name, number, (), ITEM_TYPES[name].max_durability)


    @classmethod
    def clone(cls, item: Item) -> Item:
        """ Returns a copy of the item """
        return cls(item.name, item.number, item.enchantments, item.durability)


    def with_number(self, number: int) -> Optional[Item]:
        """
            Returns a new instance of the item with the number field set to `number`
            returns None if the resulting item has number = 0.
        """
        if number < 0:
            raise ValueError("number cannot be negative")
        if number == 0:
            return None
        return replace(self, number=number)


    def adjust_number(self, delta: int) -> Optional[Item]:
        """
            Returns a new instance of the item, adding `delta` to the number field.
            Returns None if the resulting item has number = 0.
        """
        return self.with_number(self.number + delta)


    def with_enchantments(self, enchantments: Iterable[Enchantment]) -> Item:
        """ Returns a new instance of the item with the enchantments field set to `enchantments` """
        return replace(self, enchantments=tuple(enchantments))


    def add_enchantment(self, enchantment: Enchantment) -> Item:
        """ Returns a new instance of the item with an added enchantment """
        return self.with_enchantments(self.enchantments + (enchantment,))


    def with_durability(self, durability: int) -> Optional[Item]:
        """
            Returns a new instance of the item with the durability field set to `durability`
            Returns None if the resulting item has durability = 0.
        """
        if self.max_durability is None:
            raise ValueError(f"Cannot set durability of item {self.name}")
        if durability < 0:
            raise ValueError("durability cannot be negative")
        if durability > self.max_durability:
            raise ValueError("durability cannot exceed the item's max durability")
        if durability == 0:
            return None
        return replace(self, durability=durability)


    def adjust_durability(self, delta: int) -> Optional[Item]:
        """
            Returns a new instance of the item, adding `delta` to the durability field
            Returns None if the resulting item has durability = 0.
        """
        if self.durability is None or self.max_durability is None:
            raise ValueError(f"Cannot set durability of item {self.name}")
        return self.with_durability(self.durability + delta)


    def disenchant(self) -> Item:
        """ Returns a new instance of the item, with all enchantments removed """
        return self.with_enchantments(())


    @staticmethod
    def equals_optional(item1: Optional[Item], item2: Optional[Item]) -> bool:
        """ Checks if two optional items are equal """
        if item1 is not None and item2 is not None:
            return all([
                item1.name == item2.name,
                item1.number == item2.number,
                item1.enchantments == item2.enchantments,
                item1.durability == item2.durability
            ])

        if (item1 is None and item2 is None):
            return True

        # one is None and the other is not
        return False


    def is_stackable_with(self, other: Item) -> bool:
        """ Items are stackable if they have the same name, enchantments, and durability """
        return (
            self.name == other.name and
            self.enchantments == other.enchantments and
            self.durability == other.durability and
            self.number + other.number <= self.max_quantity
        )


    def __repr__(self) -> str:
        """ Print method """
        return f"Item({self.name}, {self.number}, {self.enchantments}, {self.durability})"


@dataclass
class ItemType:
    """
        Class to store item details for every item in game
    """
    type: str
    stack: int
    tier: Optional[int]
    max_durability: Optional[int]
    rarity: int


# Colours for all rarities
ITEM_COLOURS: dict[int, tuple[int, int, int] | str] = {
    1: (255, 255, 255),
    2: (0, 255, 0),
    3: (0, 0, 255),
    4: "#C71585",
    5: "#d4af37"
}

# Rarities and their levels
TC_RARITIES = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 3,
    "Epic": 4,
    "Legendary": 5
}

#Dictionary of all items in the game
ITEM_TYPES = {
    "Oak Log": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Oak Planks": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Stick": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Crafting Table": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Wooden Pickaxe": ItemType("Pickaxe", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Axe": ItemType("Axe", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Shovel": ItemType("Shovel", 1, 1, 59, TC_RARITIES["Common"]),
    "Wooden Hoe": ItemType("Hoe", 1, 1, 59, TC_RARITIES["Common"]),
    "Cobblestone": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Mine Entrance": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Stone Pickaxe": ItemType("Pickaxe", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Axe": ItemType("Axe", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Shovel": ItemType("Shovel", 1, 2, 131, TC_RARITIES["Common"]),
    "Stone Hoe": ItemType("Hoe", 1, 2, 131, TC_RARITIES["Common"]),
    "Furnace": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Compressor": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Grindstone": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Coal": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Iron Ore": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Iron Ingot": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Iron Pickaxe": ItemType("Pickaxe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Axe": ItemType("Axe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Shovel": ItemType("Shovel", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Iron Hoe": ItemType("Hoe", 1, 3, 250, TC_RARITIES["Uncommon"]),
    "Bucket": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Water Bucket": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Lava Bucket": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Shield": ItemType("Shield", 1, None, 336, TC_RARITIES["Uncommon"]),
    "Flint and Steel": ItemType("Item", 1, None, 64, TC_RARITIES["Common"]),
    "Iron Plate": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Tier 1 Iron Plate": ItemType("Tier1", 1, None, 120, TC_RARITIES["Uncommon"]),
    "Tier 2 Iron Plate": ItemType("Tier2", 1, None, 240, TC_RARITIES["Uncommon"]),
    "Tier 3 Iron Plate": ItemType("Tier3", 1, None, 480, TC_RARITIES["Uncommon"]),
    "Diamond": ItemType("Item", 64, None, None, TC_RARITIES["Rare"]),
    "Diamond Pickaxe": ItemType("Pickaxe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Axe": ItemType("Axe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Shovel": ItemType("Shovel", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Hoe": ItemType("Hoe", 1, 4, 1561, TC_RARITIES["Rare"]),
    "Diamond Plate": ItemType("Item", 64, None, None, TC_RARITIES["Rare"]),
    "Tier 1 Diamond Plate": ItemType("Tier1", 1, None, 280, TC_RARITIES["Rare"]),
    "Tier 2 Diamond Plate": ItemType("Tier2", 1, None, 560, TC_RARITIES["Rare"]),
    "Tier 3 Diamond Plate": ItemType("Tier3", 1, None, 1120, TC_RARITIES["Rare"]),
    "Jukebox": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Pigstep Disc": ItemType("Item", 1, None, None, TC_RARITIES["Rare"]),
    "Obsidian": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Enchanting Table": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Book": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Bookshelf": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Lapis Lazuli": ItemType("Item", 64, None, None, TC_RARITIES["Uncommon"]),
    "Bread": ItemType("Food", 64, None, None, TC_RARITIES["Common"]),
    "Golden Carrot": ItemType("Food", 64, None, None, TC_RARITIES["Common"]),
    "Golden Apple": ItemType("Food", 64, None, None, TC_RARITIES["Uncommon"]),
    "Dirt": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Sand": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Snow": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Gravel": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Flint": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
    "Bed": ItemType("Item", 1, None, None, TC_RARITIES["Common"]),
    "Hay Bale": ItemType("Item", 64, None, None, TC_RARITIES["Common"]),
}
