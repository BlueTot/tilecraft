from __future__ import annotations

from dataclasses import dataclass
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


class EnchantingTable:
    """
        Enchanting Table interface allows the player to enchant an item
        Levels of the enchanting table go up to 5 and there are three options to enchant
        Requires experience levels
    """

    def __init__(self, rng: RandomNumberGenerator, experience: Experience):
        self.rng = rng
        self.experience = experience

        self.items: list[Optional[Item]] = [None]*3
        self.__option_list: list[Optional[Enchantment]] = [None]*3
        self.enchanting_level = 0
        self.__level1 = 0
        self.__level2 = 0
        self.__level3 = 0
        self.__optional_enchant2 = None
        self.__optional_enchant3 = None


    def option(self, option_number: int) -> str:
        """
            Public-facing method used by the UI to get the enchanting table's option string
        """
        if option_number not in (0, 1, 2):
            raise ValueError("Enchanting option must be 0, 1, or 2")
        return self.__option_string(self.__option_list[option_number])


    @property
    def level1(self) -> int:
        """ Read-only access to level1 attribute """
        return self.__level1


    @property
    def level2(self) -> int:
        """ Read-only access to level2 attribute """
        return self.__level2


    @property
    def level3(self) -> int:
        """ Read-only access to level3 attribute """
        return self.__level3


    @property
    def optional_enchant2(self) -> int:
        """ Read-only access to optional_enchant2 attribute """
        return self.__optional_enchant2


    @property
    def optional_enchant3(self) -> int:
        """ Read-only access to optional_enchant3 attribute """
        return self.__optional_enchant3


    @property
    def option_list(self) -> tuple[str, str, str]:
        """ Read-only access to option_list attribute """
        return (self.option(0), self.option(1), self.option(2))


    @staticmethod
    def __option_string(enchantment: Optional[Enchantment]):
        if enchantment is None:
            return ""
        if enchantment.level == 0:
            return "N/A"
        return f"{enchantment.name} {enchantment.level}"
    

    def enchant_set(self):
        """
            Set the options in the enchanting table
        """

        if self.items[0] is None or self.items[0].enchantments is not None:
            self.__option_list[0] = None
            self.__option_list[1] = None
            self.__option_list[2] = None
            return

        match self.enchanting_level:
            case 0:
                self.__level1 = 0
                self.__level2 = 0
                self.__level3 = self.rng.next_random(0, 1)
                self.__optional_enchant2 = None
                self.__optional_enchant3 = None
            case 1:
                self.__level1 = 1
                self.__level2 = self.rng.next_random(1, 2)
                self.__level3 = 2
                self.__optional_enchant2 = None
                self.__optional_enchant3 = None
            case 2:
                self.__level1 = 2
                self.__level2 = self.rng.next_random(2, 3)
                self.__level3 = 3
                self.__optional_enchant2 = None
                self.__optional_enchant3 = None
            case 3:
                self.__level1 = 3
                self.__level2 = self.rng.next_random(3, 4)
                self.__level3 = 4
                self.__optional_enchant2 = None
                self.__optional_enchant3 = self.rng.next_random(0, 1)
            case 4:
                self.__level1 = 4
                self.__level2 = self.rng.next_random(4, 5)
                self.__level3 = 5
                self.__optional_enchant2 = self.rng.next_random(0, 1)
                self.__optional_enchant3 = self.rng.next_random(1, 2)
            case 5:
                self.__level1 = self.rng.next_random(4, 5)
                self.__level2 = 5
                self.__level3 = 5
                self.__optional_enchant2 = self.rng.next_random(1, 2)
                self.__optional_enchant3 = self.rng.next_random(2, 3)
            case _:
                raise ValueError("Enchanting table level must be 0-5")

        if self.items[0].itemType in ("Tier1", "Tier2", "Tier3"):
            self.__option_list = [
                Enchantment("Protection", self.__level1),
                Enchantment("Protection", self.__level2),
                Enchantment("Protection", self.__level3),
            ]

        elif self.items[0].itemType in ("Pickaxe", "Axe", "Shovel", "Hoe"):
            self.__option_list = [
                Enchantment("Efficiency", self.__level1),
                Enchantment("Efficiency", self.__level2),
                Enchantment("Efficiency", self.__level3),
            ]

        else:
            raise ValueError("Expected an enchantable item")


    def enchant_upgrade(self):
        """
            Upgrade the level of the enchanting table
        """
        if self.items[2] is None or self.items[2].name != "Bookshelf" or self.items[2].number < 4:
            return

        if self.enchanting_level >= 5:
            return

        self.items[2].number -= 4
        self.enchanting_level += 1
        self.enchant_set()  # Set Enchants


    def __enchant1(self):  # First ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, no extras)
        """
            Enchant using the first option box
        """

        if self.items[1] is None or self.items[1].number < 1 or self.experience.levels < 1:
            return

        if self.__option_list[0] is None or self.items[0] is None:
            return

        self.items[0] = Item(
            self.items[0].name, 
            self.items[0].number, 
            [Enchantment.clone(self.__option_list[0])],
            self.items[0].durability
        )
        self.items[1].number -= 1
        self.experience.subtract(1)
        self.enchant_set()  # Remove Enchants


    def __enchant2(self):  # Second ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2)
        """
            Enchant using the second option box
        """

        if self.items[1] is None or self.items[1].number < 2 or self.experience.levels < 2:
            return

        if self.__option_list[1] == "N/A" or self.items[0] is None:
            return

        if self.__optional_enchant2 is not None and self.__optional_enchant2 > 0:  # Extra enchantment
            self.items[0] = Item(
                self.items[0].name, 
                self.items[0].number, 
                [
                    Enchantment.clone(self.__option_list[1]),
                    Enchantment('Unbreaking', self.__optional_enchant2)
                ],
                self.items[0].durability
            )
        else:
            self.items[0] = Item(
                self.items[0].name, 
                self.items[0].number, 
                [Enchantment.clone(self.__option_list[1])],
                self.items[0].durability
            )

        self.items[1].number -= 2
        self.experience.subtract(2)
        self.enchant_set()  # Remove Enchants


    def __enchant3(self):  # Third ENCHANTING BOX (ENCHANTS start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3)
        """
            Enchant using the third option box
        """

        if self.items[1] is None or self.items[1].number < 3 or self.experience.levels < 3:
            return

        if self.__option_list[2] == "N/A" or self.items[0] is None:
            return

        if self.__optional_enchant3 is not None and self.__optional_enchant3 > 0:  # Extra enchantment
            self.items[0] = Item(
                self.items[0].name, 
                self.items[0].number, 
                [
                    Enchantment.clone(self.__option_list[2]),
                    Enchantment('Unbreaking', self.__optional_enchant3),
                ],
                self.items[0].durability
            )
        else:  # No extra enchantment
            self.items[0] = Item(
                self.items[0].name, 
                self.items[0].number, 
                [Enchantment.clone(self.__option_list[2])],
                self.items[0].durability
            )

        self.items[1].number -= 3
        self.experience.subtract(3)
        self.enchant_set()  # Remove Enchants


    def enchant(self, box: int):
        """
            Entry point for enchanting an item
        """
        match box:
            case 1:
                self.__enchant1()
                return
            case 2:
                self.__enchant2()
                return
            case 3:
                self.__enchant3()
                return
            case _:
                raise ValueError("Box must be between 1 and 3")


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
