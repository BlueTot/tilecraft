from __future__ import annotations

from dataclasses import dataclass
from errno import EFAULT
from typing import Optional

from .constants import Enchantment, Item, RandomNumberGenerator
from .player_info import Experience


class HoldingItem:
    """
        Item that the user is holding in the inventory menus
        Can be an item or nothing.
    """
    def __init__(self):
        self.item: Optional[Item] = None


class Inventory:
    """
        Player's inventory consists of 36 slots, the last 9 slots belong to the hotbar
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*36
        self.__selected_hotbar: int = 0
    
    @property
    def selected_hotbar(self):
        """
            Gets the index of the selected hotbar from 0-8
        """ 
        return self.__selected_hotbar

    @selected_hotbar.setter
    def selected_hotbar(self, index: int):
        """
            Sets the index of the selected hotbar, from 0-8
        """
        self.__selected_hotbar = index

    @property
    def hotbar_item(self) -> Optional[Item]:
        """
            Gets the item the player selected in the hotbar
        """
        return self.items[self.__selected_hotbar + 27]

    @hotbar_item.setter
    def hotbar_item(self, item: Optional[Item]) -> None:
        self.items[self.__selected_hotbar + 27] = item


    def add(self, item_to_add: Optional[Item]) -> int:
        """
            Add an item to the inventory if possible. Does not modify
            the item passed in. Returns the remaining amount that did not fit
            in the inventory.
        """

        if item_to_add is None:
            return 0

        remaining = item_to_add.number

        # attempt to add into existing stacks
        for item_at in self.items:

            if (
                item_at is not None and 
                item_at.name == item_to_add.name and # same name
                item_at.number < item_at.stackNum # not full stack
            ):
                amount_remaining = min(item_at.stackNum - item_at.number, remaining) # do not over subtract
                item_at.number += amount_remaining
                remaining -= amount_remaining

        # attempt to add to empty slots
        if remaining > 0:

            for index, item_at in enumerate(self.items):
                if item_at is None:
                    amount_to_add = min(remaining, item_to_add.stackNum)
                    self.items[index] = Item(
                        name=item_to_add.name, 
                        number=amount_to_add,
                        enchantments=item_to_add.enchantments,
                        durability=item_to_add.durability
                    )
                    remaining -= amount_to_add

                if remaining == 0:
                    break

        # by this point, there's no space for the remaining amount
        if remaining > 0:
            print("Your inventory is nearly full or is already full. New items added may be lost.") 

        return remaining


class Armour:
    """
        Player's armour items consist of four slots:
        1) tier 1 plate, 2) tier 2 plate, 3) tier 3 plate, 4) shield
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*4


class FurnaceInterface:
    """
        Smelting interrface in the inventory screen
        Consists of a fuel slot, item slot, and result slot
    """
    def __init__(self):

        self.items: list[Optional[Item]] = [None]*3
        self.fuel_val = 0
        self.smelting_time = 0


    def smelt(self, fps: float, experience: Experience):
        """
            Progress smelting an item by one tick
        """

        # Load Fuel
        if (
            self.items[1] is not None and
            self.items[1].name == "Coal" and 
            self.fuel_val == 0
        ):
            self.items[1] = Item(self.items[1].name, self.items[1].number - 1, self.items[1].enchantments, self.items[1].durability)
            self.fuel_val = 8

        # Smelting Process
        if (
            self.items[0] is not None and 
            self.items[0].name == "Iron Ore" and
            self.items[0].number > 0 and
            self.fuel_val > 0 and (
                self.items[2] is None or
                Item.new("Iron Ingot", self.items[0].number).is_stackable_with(self.items[2])
            )
        ):
            self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time >= 5 * fps:
            self.smelting_time = 0
            self.items[0] = Item(self.items[0].name, self.items[0].number - 1, self.items[0].enchantments, self.items[0].durability)
            self.fuel_val -= 1
            if self.items[2] is None:
                self.items[2] = Item.new("Iron Ingot", 1)
            else:
                self.items[2].number += 1
            experience.add_points(12)


@dataclass
class EnchantmentPair:
    """
        An enchantment pair consists of a main and optional enchantment,
        both can be None.
    """
    main_enchantment: Optional[Enchantment]
    optional_enchantment: Optional[Enchantment]

    def enchantment_list(self) -> Optional[list[Enchantment]]:
        """
            Returns a list of enchantments excluding None if possible, otherwise None
        """
        if self.main_enchantment is None:
            return None
        if self.optional_enchantment is None:
            return [Enchantment.clone(self.main_enchantment)]
        return [Enchantment.clone(self.main_enchantment), Enchantment.clone(self.optional_enchantment)]


class EnchantingTable:
    """
        Enchanting Table interface allows the player to enchant an item
        Levels of the enchanting table go up to 5 and there are three options to enchant
        Requires experience levels
    """

    PROTECTION = "Protection"
    EFFICIENCY = "Efficiency"
    UNBREAKING = "Unbreaking"

    DEFAULT_ENCHANTMENTS = {
        "Tier1": PROTECTION,
        "Tier2": PROTECTION,
        "Tier3": PROTECTION,
        "Pickaxe": EFFICIENCY,
        "Axe" : EFFICIENCY,
        "Shovel": EFFICIENCY,
        "Hoe": EFFICIENCY,
    }

    MIN_LAPIS = {
        1: 1,
        2: 2,
        3: 3,
    }

    MIN_EXPERIENCE = {
        1: 1,
        2: 2,
        3: 3,
    }

    def __init__(self, rng: RandomNumberGenerator, experience: Experience):
        self.rng = rng
        self.experience = experience

        self.enchanting_level = 0
        self.items: list[Optional[Item]] = [None]*3
        self.__options: list[EnchantmentPair] = [EnchantmentPair(None, None) for _ in range(3)]


    def option(self, option_number: int) -> str:
        """
            Public-facing method used by the UI to get the enchanting table's option string
        """
        if option_number not in (0, 1, 2):
            raise ValueError("Enchanting option must be 0, 1, or 2")
        return self.__option_string(self.__options[option_number].main_enchantment)


    def optional_enchantment_at(self, option_number: int) -> str:
        """
            Public-facing method, gets the optional enchantment at index `option_number`
        """
        if option_number not in (0, 1, 2):
            raise ValueError("Enchanting option must be 0, 1, or 2")
        return self.__option_string(self.__options[option_number].optional_enchantment)


    @staticmethod
    def __option_string(enchantment: Optional[Enchantment]):
        if enchantment is None or enchantment.level == 0:
            return ""
        return f"{enchantment.name} {enchantment.level}"


    def update(self) -> None:
        """
            Set the options in the enchanting table
            Box 1 - Enchants start at LEVEL 1, MAX 5, no extras
            Box 2 - Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2
            Box 3 - Enchants start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3
        """

        if self.items[0] is None or self.items[0].enchantments is not None:
            self.__options[0] = EnchantmentPair(None, None)
            self.__options[1] = EnchantmentPair(None, None)
            self.__options[2] = EnchantmentPair(None, None)
            return

        level1 = 0
        level2 = 0
        level3 = 0
        optional_enchant2 = 0
        optional_enchant3 = 0

        match self.enchanting_level:
            case 0:
                level1 = 0
                level2 = 0
                level3 = self.rng.next_random(0, 1)
                optional_enchant2 = 0
                optional_enchant3 = 0
            case 1:
                level1 = 1
                level2 = self.rng.next_random(1, 2)
                level3 = 2
                optional_enchant2 = 0
                optional_enchant3 = 0
            case 2:
                level1 = 2
                level2 = self.rng.next_random(2, 3)
                level3 = 3
                optional_enchant2 = 0
                optional_enchant3 = 0
            case 3:
                level1 = 3
                level2 = self.rng.next_random(3, 4)
                level3 = 4
                optional_enchant2 = 0
                optional_enchant3 = self.rng.next_random(0, 1)
            case 4:
                level1 = 4
                level2 = self.rng.next_random(4, 5)
                level3 = 5
                optional_enchant2 = self.rng.next_random(0, 1)
                optional_enchant3 = self.rng.next_random(1, 2)
            case 5:
                level1 = self.rng.next_random(4, 5)
                level2 = 5
                level3 = 5
                optional_enchant2 = self.rng.next_random(1, 2)
                optional_enchant3 = self.rng.next_random(2, 3)
            case _:
                raise ValueError("Enchanting table level must be 0-5")

        if self.items[0].itemType in self.DEFAULT_ENCHANTMENTS:
            default_enchantment = self.DEFAULT_ENCHANTMENTS[self.items[0].itemType]
            self.__options = [
                EnchantmentPair(
                    Enchantment.new_optional(default_enchantment, level1),
                    None,
                ),
                EnchantmentPair(
                    Enchantment.new_optional(default_enchantment, level2),
                    Enchantment.new_optional(self.UNBREAKING, optional_enchant2)
                ),
                EnchantmentPair(
                    Enchantment.new_optional(default_enchantment, level3),
                    Enchantment.new_optional(self.UNBREAKING, optional_enchant3)
                ),
            ]
        else:
            raise ValueError("Expected an enchantable item")


    def upgrade(self) -> None:
        """
            Upgrade the level of the enchanting table
        """
        if self.items[2] is None or self.items[2].name != "Bookshelf" or self.items[2].number < 4:
            return

        if self.enchanting_level >= 5:
            return

        self.items[2].number -= 4
        self.enchanting_level += 1
        self.update()


    def enchant(self, box: int) -> None:
        """
            Enchant an item, given the specified `box` number in (1, 2, 3)
        """
        if box not in (1, 2, 3):
            raise ValueError("Box must be between 1 and 3")

        if self.items[1] is None or self.items[1].number < self.MIN_LAPIS[box]:
            return

        if self.experience.levels < self.MIN_EXPERIENCE[box]:
            return

        if self.__options[box-1].main_enchantment is None or self.items[0] is None:
            return

        self.items[0] = Item.clone_with_enchantments(self.items[0], self.__options[box-1].enchantment_list())
        self.items[1].number -= self.MIN_LAPIS[box]
        self.experience.subtract(self.MIN_EXPERIENCE[box])
        self.update()


@dataclass
class CompressorRecipe:
    ingredient: Item
    product: Item


class Compressor:
    """
        Compressor allows the player to compress things into plates
        Has two slots, one input slot and one output slot
        Runs on a timer
    """

    RECIPES: list[CompressorRecipe] = [
        CompressorRecipe(Item.new("Iron Ingot", 2), Item.new("Iron Plate", 1)),
        CompressorRecipe(Item.new("Diamond", 2), Item.new("Diamond Plate", 1))
    ]

    def __init__(self):
        self.items: list[Optional[Item]] = [None, None]
        self.compressing_time = 0


    def compress(self, fps: float):
        """
            Advances the compressing state by one frame
        """

        expected_output: Optional[Item] = None

        # compressing process
        for recipe in self.RECIPES:
            if (
                self.items[0] is not None and
                self.items[0].name == recipe.ingredient.name and
                self.items[0].number >= recipe.ingredient.number and (
                    self.items[1] is None or
                    recipe.product.is_stackable_with(self.items[1])
                )
            ):
                self.compressing_time += 1
                expected_output = Item.clone(recipe.product)
                break
        else:
            self.compressing_time = 0

        # finish compressing item
        if self.compressing_time >= 5 * fps:
            self.compressing_time = 0
            self.items[0].number -= 2
            if self.items[1] is None and expected_output is not None:
                self.items[1] = expected_output
            else:
                self.items[1].number += 1


class Grindstone:
    """
        Grindstone interface for player to repair and disenchant 
        Consists of two input slots and one output slot
    """

    def __init__(self, experience: Experience):
        self.experience = experience
        self.items: list[Optional[Item]] = [None, None, None]


    def update(self):
        """
            Update the result slot's information
        """

        # if main slot is empty, output is empty
        if self.items[0] is None:
            self.items[2] = None
            return

        # disenchant main slot
        if self.items[1] is None and self.items[0].enchantments is not None:
            self.items[2] = Item.clone(self.items[0])
            self.items[2].enchantments = None
            return

        # repair and combine
        if (
            self.items[1] is not None and
            self.items[0].name == self.items[1].name and
            self.items[0].durability is not None and
            self.items[1].durability is not None
        ):
            total_durability = min(self.items[0].max_durability, self.items[0].durability + self.items[1].durability)
            self.items[2] = Item.clone(self.items[0])
            self.items[2].enchantments = None
            self.items[2].durability = total_durability
            return

        # otherwise, leave output empty
        self.items[2] = None


    def repair_and_disenchant(self):
        """
            Add experience to player
        """
        for enchantment in self.items[0].enchantments:
            self.experience.add_points(int(enchantment.level) * 8)
