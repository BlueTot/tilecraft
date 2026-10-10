from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from .constants import Item


@dataclass
class SmallCraftingRecipe:
    """
        A small crafting recipe consists of four inputs and one output
    """
    inputs: list[Optional[Item]]
    output: Optional[Item]


class SmallCraftingGrid:
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


@dataclass
class CraftingRecipe:
    """
        A crafting recipe consists of nine inputs and one output
    """
    inputs: list[Optional[Item]]
    output: Optional[Item]


class CraftingTableInterface:
    """
        3x3 crafting grid in the crafting table interface
        Consists of 9 crafting slots and 1 result slot
    """

    # Create crafting recipes
    RECIPES: list[CraftingRecipe] = [
        CraftingRecipe(
            [Item.new("Oak Log", 1), None, None,
             None, None, None,
             None, None, None], 
            Item.new("Oak Planks", 4).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), None, None,
             Item.new("Oak Planks", 1), None, None,
             None, None, None], 
            Item.new("Stick", 4).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), None,
             Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), None,
             None, None, None], 
            Item.new("Crafting Table", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Wooden Pickaxe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             None, Item.new("Stick", 1), Item.new("Oak Planks", 1),
             None, Item.new("Stick", 1), None], 
            Item.new("Wooden Axe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Oak Planks", 1), None,
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Wooden Shovel", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Wooden Hoe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), Item.new("Wooden Pickaxe", 1), Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1)], 
            Item.new("Mine Entrance", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Stone Pickaxe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             None, Item.new("Stick", 1), Item.new("Cobblestone", 1),
             None, Item.new("Stick", 1), None], 
            Item.new("Stone Axe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Cobblestone", 1), None,
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Stone Shovel", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Stone Hoe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), None, Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1)], 
            Item.new("Furnace", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), Item.new("Iron Ingot", 1), Item.new("Cobblestone", 1),
             Item.new("Cobblestone", 1), Item.new("Cobblestone", 1), Item.new("Cobblestone", 1)], 
            Item.new("Compressor", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Stick", 1), Item.new("Cobblestone", 1), Item.new("Stick", 1),
             Item.new("Oak Planks", 1), None, Item.new("Oak Planks", 1),
             None, None, None], 
            Item.new("Grindstone", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Iron Ingot", 1), Item.new("Iron Ingot", 1), Item.new("Iron Ingot", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Iron Pickaxe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Iron Ingot", 1), Item.new("Iron Ingot", 1),
             None, Item.new("Stick", 1), Item.new("Iron Ingot", 1),
             None, Item.new("Stick", 1), None], 
            Item.new("Iron Axe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Iron Ingot", 1), None,
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Iron Shovel", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Iron Ingot", 1), Item.new("Iron Ingot", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Iron Hoe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, None, None,
             Item.new("Iron Ingot", 1), None, Item.new("Iron Ingot", 1),
             None, Item.new("Iron Ingot", 1), None], 
            Item.new("Bucket", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Iron Ingot", 1), Item.new("Oak Planks", 1),
             Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             None, Item.new("Oak Planks", 1), None], 
            Item.new("Shield", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Iron Ingot", 1), None, None,
             None, Item.new("Flint", 1), None,
             None, None, None], 
            Item.new("Flint and Steel", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Iron Plate", 1), None,
             None, None, None,
             None, Item.new("Iron Plate", 1), None], 
            Item.new("Tier 1 Iron Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Iron Plate", 1), None,
             Item.new("Iron Plate", 1), None, Item.new("Iron Plate", 1),
             None, Item.new("Iron Plate", 1), None], 
            Item.new("Tier 2 Iron Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Iron Plate", 1), Item.new("Iron Plate", 1), Item.new("Iron Plate", 1),
             Item.new("Iron Plate", 1), None, Item.new("Iron Plate", 1),
             Item.new("Iron Plate", 1), Item.new("Iron Plate", 1), Item.new("Iron Plate", 1)], 
            Item.new("Tier 3 Iron Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Diamond", 1), Item.new("Diamond", 1), Item.new("Diamond", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Diamond Pickaxe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Diamond", 1), Item.new("Diamond", 1),
             None, Item.new("Stick", 1), Item.new("Diamond", 1),
             None, Item.new("Stick", 1), None], 
            Item.new("Diamond Axe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Diamond", 1), None,
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Diamond Shovel", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Diamond", 1), Item.new("Diamond", 1),
             None, Item.new("Stick", 1), None,
             None, Item.new("Stick", 1), None], 
            Item.new("Diamond Hoe", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Diamond Plate", 1), None,
             None, None, None,
             None, Item.new("Diamond Plate", 1), None], 
            Item.new("Tier 1 Diamond Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Diamond Plate", 1), None,
             Item.new("Diamond Plate", 1), None, Item.new("Diamond Plate", 1),
             None, Item.new("Diamond Plate", 1), None], 
            Item.new("Tier 2 Diamond Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Diamond Plate", 1), Item.new("Diamond Plate", 1), Item.new("Diamond Plate", 1),
             Item.new("Diamond Plate", 1), None, Item.new("Diamond Plate", 1),
             Item.new("Diamond Plate", 1), Item.new("Diamond Plate", 1), Item.new("Diamond Plate", 1)], 
            Item.new("Tier 3 Diamond Plate", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             Item.new("Oak Planks", 1), Item.new("Diamond", 1), Item.new("Oak Planks", 1),
             Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1)], 
            Item.new("Jukebox", 1).set_max_durability()
        ),
        CraftingRecipe(
            [None, Item.new("Book", 1), None,
             Item.new("Diamond", 1), Item.new("Obsidian", 1), Item.new("Diamond", 1),
             Item.new("Obsidian", 1), Item.new("Obsidian", 1), Item.new("Obsidian", 1)], 
            Item.new("Enchanting Table", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1),
             Item.new("Book", 1), Item.new("Book", 1), Item.new("Book", 1),
             Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1)], 
            Item.new("Bookshelf", 1).set_max_durability()
        ),
        CraftingRecipe(
            [Item.new("Hay Bale", 1), None, None,
             None, None, None,
             None, None, None], 
            Item.new("Bread", 3).set_max_durability()
        ),
    ]
 
    def __init__(self):
        self.items: list[Optional[Item]] = [None]*10


    def update(self):
        """
            Update attempts to craft an item from the ingredients
        """

        for recipe in self.RECIPES:

            is_recipe_complete = True
            for have, expected in zip(self.items[:9], recipe.inputs):
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
                self.items[9] = Item.clone(recipe.output)
                return

        self.items[9] = None
