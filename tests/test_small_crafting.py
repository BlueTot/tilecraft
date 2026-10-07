from typing import Optional

import pytest

from tilecraft.constants import Item
from tilecraft.inventory import SmallCraftingInterface 


##################################
#         TEST HELPERS           #
##################################


def new_single_item(item_name: str) -> Item:
    """
        Returns a new item with quantity 1
    """
    return Item(item_name, 1, None, None)


def new_item(item_name: str, quantity: int) -> Item:
    """
        Returns a new item with given name and quantity
    """
    return Item(item_name, quantity, None, None)


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
            new_item("Oak Planks", 4)
        ),
        (
            ["Oak Planks", "Oak Planks", "Oak Planks", "Oak Planks"],
            new_single_item("Crafting Table")
        ),
        (
            ["Oak Planks", None, "Oak Planks", None],
            new_item("Stick", 4)
        ),
        (
            ["Iron Ingot", None, None, "Flint"],
            new_single_item("Flint and Steel")
        )
    ]
)
def test_small_crafting_produces_correct_product(inputs: list[Optional[str]], output: Optional[Item]):
    """
        Tests that small crafting grid produces correct product given correct ingredients
    """

    if len(inputs) != 4:
        raise ValueError("List of inputs must have length 4")

    small_crafting_table = SmallCraftingInterface()
    for i, name in enumerate(inputs):
        small_crafting_table.items[i] = new_single_item(name) if name is not None else None 

    small_crafting_table.update()
    print(small_crafting_table.items[4].name, small_crafting_table.items[4].number)
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
def test_invalid_ingredients_produce_no_result(names):
    """
        Tests that invalid ingredients produce None in the output slot
    """
    crafting = SmallCraftingInterface()
    crafting.items[:4] = [
        new_single_item(name) if name is not None else None
        for name in names
    ]

    crafting.update()

    assert crafting.items[4] is None
