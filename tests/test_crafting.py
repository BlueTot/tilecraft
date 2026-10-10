from typing import Optional

import pytest

from tilecraft.constants import Item
from tilecraft.crafting import SmallCraftingGrid, LargeCraftingGrid


##################################
#         TEST HELPERS           #
##################################


def item_equals(item1: Optional[Item], item2: Optional[Item]) -> bool:
    """
        Checks if two items are equal
    """

    if (item1 is None and item2 is None):
        return True

    if (item1 is not None and item2 is None) or (item1 is None and item2 is not None):
        return False

    return all([
        item1.name == item2.name,
        item1.number == item2.number,
        item1.enchantments == item2.enchantments,
        item1.durability == item2.durability
    ])


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize(
    ("inputs", "output"),
    [
        (
            ["Oak Log", None, None, None], 
            Item.new("Oak Planks", 4)
        ),
        (
            ["Oak Planks", "Oak Planks", "Oak Planks", "Oak Planks"],
            Item.new("Crafting Table", 1)
        ),
        (
            ["Oak Planks", None, "Oak Planks", None],
            Item.new("Stick", 4)
        ),
        (
            ["Iron Ingot", None, None, "Flint"],
            Item.new("Flint and Steel", 1)
        )
    ]
)
def test_small_crafting_produces_correct_product(inputs: list[Optional[str]], output: Optional[Item]):
    """
        Tests that small crafting grid produces correct product given correct ingredients
    """

    if len(inputs) != 4:
        raise ValueError("List of inputs must have length 4")

    small_crafting_table = SmallCraftingGrid()
    for i, name in enumerate(inputs):
        small_crafting_table.items[i] = Item.new(name, 1) if name is not None else None 

    small_crafting_table.update()
    assert item_equals(small_crafting_table.items[4], output)


@pytest.mark.parametrize(
    "names",
    [
        pytest.param(
            [None, None, None, None],
            id="empty-grid",
        ),
        pytest.param(
            ["Iron Ingot", None, None, None],
            id="missing-flint",
        ),
        pytest.param(
            ["Iron Ingot", None, None, "Dirt"],
            id="incorrect-flint-ingredient",
        ),
        pytest.param(
            ["Oak Log", "Dirt", None, None],
            id="extra-ingredient",
        ),
        pytest.param(
            ["Oak Planks", "Oak Planks", "Oak Planks", None],
            id="missing-plank-for-crafting-table",
        ),
    ],
)
def test_small_crafting_invalid_ingredients_produce_no_result(names):
    """
        Tests that for small crafting grid, invalid ingredients produce 
        None in the output slot
    """
    crafting = SmallCraftingGrid()
    crafting.items[:4] = [
        Item.new(name, 1)
        if name is not None else None
        for name in names
    ]

    crafting.update()

    assert crafting.items[4] is None


def test_small_crafting_invalid_ingredients_clear_previous_result():
    """
        Test that for small crafting grid, invalid ingredients clear a 
        previously valid result
    """
    crafting = SmallCraftingGrid()
    crafting.items[0] = Item.new("Oak Log", 1)
    crafting.update()
    assert crafting.items[4] is not None

    crafting.items[0] = Item.new("Dirt", 1)
    crafting.update()

    assert crafting.items[4] is None


@pytest.mark.parametrize(
    ("inputs", "output"),
    [
        (
            ["Oak Log", None, None, 
             None, None, None, 
             None, None, None], 
            Item.new("Oak Planks", 4).set_max_durability()
        ),
        (
            ["Oak Planks", None, None,
             "Oak Planks", None, None,
             None, None, None],
            Item.new("Stick", 4).set_max_durability()
        ),
        (
            ["Oak Planks", "Oak Planks", None,
             "Oak Planks", "Oak Planks", None,
             None, None, None],
            Item.new("Crafting Table", 1).set_max_durability()
        ),
        (
            ["Oak Planks", "Oak Planks", "Oak Planks",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Wooden Pickaxe", 1).set_max_durability()
        ),
        (
            [None, "Oak Planks", "Oak Planks",
             None, "Stick", "Oak Planks",
             None, "Stick", None],
            Item.new("Wooden Axe", 1).set_max_durability()
        ),
        (
            [None, "Oak Planks", None,
             None, "Stick", None,
             None, "Stick", None],
             Item.new("Wooden Shovel", 1).set_max_durability()
        ),
        (
            [None, "Oak Planks", "Oak Planks",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Wooden Hoe", 1).set_max_durability()
        ),
        (
            ["Cobblestone", "Cobblestone", "Cobblestone",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Stone Pickaxe", 1).set_max_durability()
        ),
        (
            [None, "Cobblestone", "Cobblestone",
             None, "Stick", "Cobblestone",
             None, "Stick", None],
            Item.new("Stone Axe", 1).set_max_durability()
        ),
        (
            [None, "Cobblestone", None,
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Stone Shovel", 1).set_max_durability()
        ),
        (
            [None, "Cobblestone", "Cobblestone",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Stone Hoe", 1).set_max_durability()
        ),
        (
            ["Cobblestone", "Cobblestone", "Cobblestone",
             "Cobblestone", None, "Cobblestone",
             "Cobblestone", "Cobblestone", "Cobblestone"],
            Item.new("Furnace", 1).set_max_durability()
        ),
        (
            ["Cobblestone", "Cobblestone", "Cobblestone",
             "Cobblestone", "Wooden Pickaxe", "Cobblestone",
             "Cobblestone", "Cobblestone", "Cobblestone"],
            Item.new("Mine Entrance", 1).set_max_durability()
        ),
        (
            ["Cobblestone", "Cobblestone", "Cobblestone",
             "Cobblestone", "Iron Ingot", "Cobblestone",
             "Cobblestone", "Cobblestone", "Cobblestone"],
            Item.new("Compressor", 1).set_max_durability()
        ),
        (
            ["Stick", "Cobblestone", "Stick",
             "Oak Planks", None, "Oak Planks",
             None, None, None],
            Item.new("Grindstone", 1).set_max_durability()
        ),
        (
            ["Iron Ingot", "Iron Ingot", "Iron Ingot",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Iron Pickaxe", 1).set_max_durability()
        ),
        (
            [None, "Iron Ingot", "Iron Ingot",
             None, "Stick", "Iron Ingot",
             None, "Stick", None],
            Item.new("Iron Axe", 1).set_max_durability()
        ),
        (
            [None, "Iron Ingot", None,
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Iron Shovel", 1).set_max_durability()
        ),
        (
            [None, "Iron Ingot", "Iron Ingot",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Iron Hoe", 1).set_max_durability()
        ),
        (
            [None, None, None,
             "Iron Ingot", None, "Iron Ingot",
             None, "Iron Ingot", None],
            Item.new("Bucket", 1).set_max_durability()
        ),
        (
            ["Oak Planks", "Iron Ingot", "Oak Planks",
             "Oak Planks", "Oak Planks", "Oak Planks",
             None, "Oak Planks", None],
            Item.new("Shield", 1).set_max_durability()
        ),
        (
            ["Iron Ingot", None, None, 
             None, "Flint", None,
             None, None, None],
            Item.new("Flint and Steel", 1).set_max_durability()
        ),
        (
            [None, "Iron Plate", None,
             None, None, None,
             None, "Iron Plate", None],
            Item.new("Tier 1 Iron Plate", 1).set_max_durability()
        ),
        (
            [None, "Iron Plate", None,
             "Iron Plate", None, "Iron Plate",
             None, "Iron Plate", None],
            Item.new("Tier 2 Iron Plate", 1).set_max_durability()
        ),
        (
            ["Iron Plate", "Iron Plate", "Iron Plate",
             "Iron Plate", None, "Iron Plate",
             "Iron Plate", "Iron Plate", "Iron Plate"],
            Item.new("Tier 3 Iron Plate", 1).set_max_durability()
        ),
        (
            ["Diamond", "Diamond", "Diamond",
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Diamond Pickaxe", 1) .set_max_durability()
        ),
        (
            [None, "Diamond", "Diamond",
             None, "Stick", "Diamond",
             None, "Stick", None],
            Item.new("Diamond Axe", 1).set_max_durability()
        ),
        (
            [None, "Diamond", None,
             None, "Stick", None,
             None, "Stick", None],
            Item.new("Diamond Shovel", 1).set_max_durability()
        ),
        (
            [None, "Diamond Plate", None,
             None, None, None,
             None, "Diamond Plate", None],
            Item.new("Tier 1 Diamond Plate", 1).set_max_durability()
        ),
        (
            [None, "Diamond Plate", None,
             "Diamond Plate", None, "Diamond Plate",
             None, "Diamond Plate", None],
            Item.new("Tier 2 Diamond Plate", 1).set_max_durability()
        ),
        (
            ["Diamond Plate", "Diamond Plate", "Diamond Plate",
             "Diamond Plate", None, "Diamond Plate",
             "Diamond Plate", "Diamond Plate", "Diamond Plate"],
            Item.new("Tier 3 Diamond Plate", 1).set_max_durability()
        ),
        (
            ["Oak Planks", "Oak Planks", "Oak Planks",
             "Oak Planks", "Diamond", "Oak Planks",
             "Oak Planks", "Oak Planks", "Oak Planks"],
            Item.new("Jukebox", 1).set_max_durability()
        ),
        (
            [None, "Book", None,
             "Diamond", "Obsidian", "Diamond",
             "Obsidian", "Obsidian", "Obsidian"],
            Item.new("Enchanting Table", 1).set_max_durability()
        ),
        (
            ["Oak Planks", "Oak Planks", "Oak Planks",
             "Book", "Book", "Book",
             "Oak Planks", "Oak Planks", "Oak Planks"],
            Item.new("Bookshelf", 1).set_max_durability()
        ),
        (
            ["Hay Bale", None, None,
             None, None, None,
             None, None, None],
            Item.new("Bread", 3).set_max_durability()
        )
    ]
)
def test_crafting_produces_correct_product(inputs: list[Optional[str]], output: Optional[Item]):
    """
        Tests that large crafting grid produces correct product given correct ingredients
    """

    if len(inputs) != 9:
        raise ValueError("List of inputs must have length 9")

    crafting_table = LargeCraftingGrid()
    for i, name in enumerate(inputs):
        crafting_table.items[i] = Item.new(name, 1) if name is not None else None 

    crafting_table.update()
    assert item_equals(crafting_table.items[9], output)


@pytest.mark.parametrize(
    "names",
    [
        pytest.param(
            [None, None, None,
             None, None, None,
             None, None, None],
            id="empty-grid",
        ),
        pytest.param(
            ["Oak Planks", "Oak Planks", "Oak Planks",
             None, "Stick", None,
             None, None, None],
            id="missing-stick-for-pickaxe",
        ),
        pytest.param(
            ["Oak Planks", "Oak Planks", "Dirt",
             None, "Stick", None,
             None, "Stick", None],
            id="incorrect-pickaxe-ingredient",
        ),
        pytest.param(
            ["Oak Log", None, None,
             None, None, None,
             None, None, "Dirt"],
            id="extra-ingredient",
        ),
        pytest.param(
            ["Oak Planks", "Oak Planks", "Oak Planks",
             "Stick", None, None,
             None, "Stick", None],
            id="misplaced-stick-for-pickaxe",
        ),
    ],
)
def test_crafting_invalid_ingredients_produce_no_result(names):
    """
        Tests that for large crafting grid, invalid ingredients produce
        None in the output slot
    """
    crafting = LargeCraftingGrid()
    crafting.items[:9] = [
        Item.new(name, 1)
        if name is not None else None
        for name in names
    ]

    crafting.update()

    assert crafting.items[9] is None
