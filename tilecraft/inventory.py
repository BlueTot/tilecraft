from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from .constants import Item, Context, CRAFTING_RECIPES, RandomNumberGenerator 
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


@dataclass
class SmallCraftingRecipe:
    """
        A small crafting recipe consists of four inputs and one output
    """
    inputs: list[Optional[Item]]
    output: Optional[Item]


class SmallCraftingInterface:
    """
        2x2 small crafting grid in the player's inventory
        consists of four cells and one result cell
    """

    RECIPES: list[SmallCraftingRecipe] = [
        SmallCraftingRecipe(
            [Item.new("Oak Log", 1), None, None, None], 
            Item.new("Oak Planks", 4)
        ),
        SmallCraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1)], 
            Item.new("Crafting Table", 1)
        ),
        SmallCraftingRecipe(
            [Item.new("Oak Planks", 1), None, Item.new("Oak Planks", 1), None], 
            Item.new("Stick", 4)
        ),
        SmallCraftingRecipe(
            [Item.new("Iron Ingot", 1), None, None, Item.new("Flint", 1)], 
            Item.new("Flint and Steel", 1)
        )
    ]

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*5


    def update(self):
        """
            Update attempts to craft an item from the ingredients
        """

        for recipe in self.RECIPES:

            is_recipe_complete = True
            for have, expected in zip(self.items[:4], recipe.inputs):
                if have is None and expected is None:
                    continue
                if (
                    have is not None and expected is not None and
                    have.name == expected.name and have.number >= expected.number
                ):
                    continue
                is_recipe_complete = False
                break
                
            if is_recipe_complete:
                self.items[4] = Item.clone(recipe.output)
                return

        self.items[4] = None


class CraftingTableInterface:
    """
        3x3 crafting grid in the crafting table interface
        Consists of 9 crafting slots and 1 result slot
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None]*10


    def update(self):
        for recipe in CRAFTING_RECIPES.values():
            if recipe.canCraft(self.items):
                recipe.craft(self.items)
                return
            else:
                self.items[9] = None


class FurnaceInterface:
    """
        Smelting interrface in the inventory screen
        Consists of a fuel slot, item slot, and result slot
    """
    def __init__(self, context: Context):

        self.items: list[Optional[Item]] = [None]*3
        self.fuel_val = 0
        self.fuel_img = context.ITEM_IMAGES["no_fire"]
        self.smelting_time = 0


    def smelt(self, context: Context, fps: float, experience: Experience):
        """
            Progress smelting an item by one tick
        """

        # Load Fuel
        if self.items[1] is not None:
            if self.items[1].name == "Coal" and self.fuel_val == 0:
                self.items[1] = Item(self.items[1].name, self.items[1].number - 1, self.items[1].enchantments, self.items[1].durability)
                self.fuel_val = 8

        # Smelting Process
        if self.items[0] is not None:
            if self.items[0].name == "Iron Ore" and self.fuel_val > 0:
                self.smelting_time += 1
        else:
            self.smelting_time = 0

        # Finish Smelting Item
        if self.smelting_time >= 5 * fps:
            self.smelting_time = 0
            self.items[0] = Item(self.items[0].name, self.items[0].number - 1, self.items[0].enchantments, self.items[0].durability)
            self.fuel_val -= 1
            if self.items[2] is None:
                self.items[2] = Item("Iron Ingot", 1, None, None)
                experience.add_points(12)
            else:
                self.items[2] = Item("Iron Ingot", self.items[2].number + 1, None, None)
                experience.add_points(12)

        # Render Fire
        if self.fuel_val > 0:
            self.fuel_img = context.ITEM_IMAGES["fire"]
        else:
            self.fuel_img = context.ITEM_IMAGES["no_fire"]


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
        self.option_list = ['', '', '']
        self.enchanting_level = 0
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.optional_enchant2 = None
        self.optional_enchant3 = None


    def enchant_set(self):
        """
            Set the options in the enchanting table
        """
        if self.items[0] is not None:
            if self.items[0].enchantments is None:
                self.level1 = 0
                self.level2 = 0
                self.level3 = 0
                self.optional_enchant2 = None
                self.optional_enchant3 = None
                if self.enchanting_level == 0:  # LEVEL 0
                    self.level1 = 0
                    self.level2 = 0
                    self.level3 = self.rng.next_random(0, 1)
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 1:  # LEVEL 1
                    self.level1 = 1
                    self.level2 = self.rng.next_random(1, 2)
                    self.level3 = 2
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 2:  # LEVEL 2
                    self.level1 = 2
                    self.level2 = self.rng.next_random(2, 3)
                    self.level3 = 3
                    self.optional_enchant2 = None
                    self.optional_enchant3 = None
                elif self.enchanting_level == 3:  # LEVEL 3
                    self.level1 = 3
                    self.level2 = self.rng.next_random(3, 4)
                    self.level3 = 4
                    self.optional_enchant2 = None
                    self.optional_enchant3 = self.rng.next_random(0, 1)
                elif self.enchanting_level == 4:  # LEVEL 4
                    self.level1 = 4
                    self.level2 = self.rng.next_random(4, 5)
                    self.level3 = 5
                    self.optional_enchant2 = self.rng.next_random(0, 1)
                    self.optional_enchant3 = self.rng.next_random(1, 2)
                else:  # LEVEL 5
                    self.level1 = self.rng.next_random(4, 5)
                    self.level2 = 5
                    self.level3 = 5
                    self.optional_enchant2 = self.rng.next_random(1, 2)
                    self.optional_enchant3 = self.rng.next_random(2, 3)

                if self.items[0].itemType == 'Tier1' or self.items[0].itemType == 'Tier2' or self.items[0].itemType == 'Tier3':  # Armour
                    self.option_list[0] = f'Protection {self.level1}'
                    self.option_list[1] = f'Protection {self.level2}'
                    self.option_list[2] = f'Protection {self.level3}'
                elif self.items[0].itemType == 'Pickaxe' or self.items[0].itemType == 'Axe' or self.items[0].itemType == 'Shovel' or self.items[0].itemType == 'Hoe':  # Tools
                    self.option_list[0] = f'Efficiency {self.level1}'
                    self.option_list[1] = f'Efficiency {self.level2}'
                    self.option_list[2] = f'Efficiency {self.level3}'
                for i in range(len(self.option_list)):
                    if self.option_list[i] == 'Protection 0' or self.option_list[i] == 'Efficiency 0':
                        self.option_list[i] = 'N/A'
            else:
                self.option_list[0] = self.option_list[1] = self.option_list[2] = ''
        else:
            self.option_list[0] = self.option_list[1] = self.option_list[2] = ''


    def enchant_upgrade(self):
        """
            Upgrade the level of the enchanting table
        """
        if self.items[2] is not None and self.enchanting_level < 5:
            if self.items[2].name == 'Bookshelf' and self.items[2].number > 3:
                self.items[2].number -= 4
                self.enchanting_level += 1
                self.enchant_set()  # Set Enchants


    def enchant1(self):  # First ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, no extras)
        """
            Enchant using the first option box
        """
        if self.items[1] is not None:
            if self.items[1].number > 0 and self.experience.levels > 0:  # REQUIRE 1 Lapis + 1 Experience
                if self.option_list[0] != 'N/A' and self.items[0] is not None:
                    self.items[0] = Item(
                        self.items[0].name, 
                        self.items[0].number, 
                        [
                            [self.option_list[0][0:-2], int(self.option_list[0][-1])]
                        ], 
                        self.items[0].number
                    )
                    self.items[1].number -= 1
                    self.experience.subtract(1)
                    self.enchant_set()  # Remove Enchants


    def enchant2(self):  # Second ENCHANTING BOX (Enchants start at LEVEL 1, MAX 5, extras start LEVEL 4, MAX 2)
        """
            Enchant using the second option box
        """
        if self.items[1] is not None:
            if self.items[1].number > 1 and self.experience.levels > 1:  # REQUIRE 2 Lapis + 2 Experience
                if self.option_list[1] != 'N/A' and self.items[0] is not None:  # Test for None
                    if self.optional_enchant2 is not None:  # Extra enchantment
                        if self.optional_enchant2 > 0:  # Enchantment level > 0
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[1][0:-2], int(self.option_list[1][-1])], 
                                    ['Unbreaking', self.optional_enchant2]
                                ],
                                self.items[0].durability
                            )
                        else:  # No extra enchantment
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[1][0:-2], int(self.option_list[1][-1])]
                                ], 
                                self.items[0].durability
                            )
                    else:
                        self.items[0] = Item(
                            self.items[0].name, 
                            self.items[0].number, 
                            [
                                [self.option_list[1][0:-2], int(self.option_list[1][-1])]
                            ], 
                            self.items[0].durability
                        )
                    self.items[1].number -= 2
                    self.experience.subtract(2)
                    self.enchant_set()  # Remove Enchants


    def enchant3(self):  # Third ENCHANTING BOX (ENCHANTS start at LEVEL 0, MAX 5, extras start LEVEL 3, MAX 3)
        """
            Enchant using the third option box
        """
        if self.items[1] is not None:
            if self.items[1].number > 2 and self.experience.levels > 2:  # REQUIRE 3 Lapis + 3 Experience
                if self.option_list[2] != 'N/A' and self.items[0] is not None:  # Test for None
                    if self.optional_enchant3 is not None:  # Extra enchantment
                        if self.optional_enchant3 > 0:  # Enchantment level > 0
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[2][0:-2], int(self.option_list[2][-1])], 
                                    ['Unbreaking', self.optional_enchant3]
                                ],
                                self.items[0].durability
                            )
                        else:  # No extra enchantment
                            self.items[0] = Item(
                                self.items[0].name, 
                                self.items[0].number, 
                                [
                                    [self.option_list[2][0:-2], int(self.option_list[2][-1])]
                                ], 
                                self.items[0].durability
                            )
                    else:  # No extra enchantment
                        self.items[0] = Item(
                            self.items[0].name, 
                            self.items[0].number, 
                            [
                                [self.option_list[2][0:-2], int(self.option_list[2][-1])]
                            ], 
                            self.items[0].durability
                        )
                    self.items[1].number -= 3
                    self.experience.subtract(3)
                    self.enchant_set()  # Remove Enchants


class Compressor:
    """
        Compressor allows the player to compress things into plates
        Has two slots, one input slot and one output slot
        Runs on a timer
    """

    def __init__(self):
        self.items: list[Optional[Item]] = [None, None]
        self.compressing_time = 0


    def compress(self, fps: float):
        """
            Advances the compressing state by one frame
        """

        #Compressing Process
        if self.items[0] is not None:
            if self.items[0].number >= 2:
                if self.items[0].name == 'Iron Ingot':
                    if self.items[1] is not None:
                        if self.items[1].name == 'Iron Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
                elif self.items[0].name == 'Diamond':
                    if self.items[1] is not None:
                        if self.items[1].name == 'Diamond Plate':
                            self.compressing_time += 1
                    else:
                        self.compressing_time += 1
        else:
            self.compressing_time = 0

        #Finish Compressing Item
        if self.compressing_time >= 5 * fps:
            self.compressing_time = 0
            self.items[0] = Item(self.items[0].name, self.items[0].number - 2, self.items[0].enchantments, self.items[0].durability)
            if self.items[1] is None:
                if self.items[0].name == 'Iron Ingot':
                    self.items[1] = Item("Iron Plate", 1, None, None)
                elif self.items[0].name == 'Diamond':
                    self.items[1] = Item("Diamond Plate", 1, None, None)
            else:
                if self.items[0].name == 'Iron Ingot' and self.items[1].name == 'Iron Plate':
                    self.items[1] = Item("Iron Plate", self.items[1].number + 1, None, None)
                elif self.items[0].name == 'Diamond' and self.items[1].name == 'Diamond Plate':
                    self.items[1] = Item("Diamond Plate", self.items[1].number + 1, None, None)


class Grindstone:
    """
        Grindstone interface for player to repair and disenchant 
        Consists of two input slots and one output slot
    """

    def __init__(self, experience: Experience):
        self.experience = experience
        self.items: list[Optional[Item]] = [None, None, None]


    def repair_and_disenchant(self):
        """
            Update the result slot's information
        """
        if self.items[0] is not None and self.items[1] is None:
            if self.items[0].enchantments is not None:
                self.items[2] = Item(self.items[0].name, self.items[0].number, None, self.items[0].durability)
                return
        elif self.items[0] is not None and self.items[1] is not None:
            if self.items[0].durability is not None and self.items[1].durability is not None:
                if self.items[0].name == self.items[1].name:
                    total_durability = self.items[0].durability + self.items[1].durability
                    if total_durability > self.items[0].max_durability:
                        total_durability = self.items[0].max_durability
                    self.items[2] = Item(self.items[0].name, self.items[0].number, None, total_durability)
                    return
        self.items[2] = None


    def disenchant(self):
        """
            Add experience to player
        """
        enchantments = self.items[0].enchantments
        for i in enchantments:
            self.experience.add_points(int(i[1]) * 8)
