from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

from .constants import Item


@dataclass
class CraftingRecipe:
    """
        A small crafting recipe consists of a list of inputs and one output
    """
    inputs: list[Optional[Item]]
    output: Optional[Item]


class CraftingGrid(ABC):
    """
        Abstract crafting grid class, has {x} input slots and 1 output slot
        where {x} is configurable
    """

    def __init__(self, num_input_slots: int):
        self.num_input_slots = num_input_slots
        self.items: list[Optional[Item]] = [None] * (self.num_input_slots + 1)


    def _update(self, recipes: list[CraftingRecipe]) -> None:

        for recipe in recipes:

            is_recipe_complete = True
            for have, expected in zip(self.items[:self.num_input_slots], recipe.inputs):
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
                self.items[self.num_input_slots] = Item.clone(recipe.output)
                return

        self.items[self.num_input_slots] = None


    @abstractmethod
    def update(self) -> None:
        """
            Update attempts to craft an item from the ingredients
        """
        raise NotImplementedError


class SmallCraftingGrid(CraftingGrid):
    """
        2x2 small crafting grid in the player's inventory
        consists of four cells and one result cell
    """

    NUM_INPUT_SLOTS = 4

    RECIPES: list[CraftingRecipe] = [
        CraftingRecipe(
            [Item.new("Oak Log", 1), None, None, None], 
            Item.new("Oak Planks", 4)
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1), Item.new("Oak Planks", 1)], 
            Item.new("Crafting Table", 1)
        ),
        CraftingRecipe(
            [Item.new("Oak Planks", 1), None, Item.new("Oak Planks", 1), None], 
            Item.new("Stick", 4)
        ),
        CraftingRecipe(
            [Item.new("Iron Ingot", 1), None, None, Item.new("Flint", 1)], 
            Item.new("Flint and Steel", 1)
        )
    ]

    def __init__(self):
        super().__init__(self.NUM_INPUT_SLOTS)

    def update(self):
        return super()._update(self.RECIPES)



class LargeCraftingGrid(CraftingGrid):
    """
        3x3 crafting grid in the crafting table interface
        Consists of 9 crafting slots and 1 result slot
    """

    NUM_INPUT_SLOTS = 9

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
        super().__init__(self.NUM_INPUT_SLOTS)


    def update(self):
        return super()._update(self.RECIPES)
