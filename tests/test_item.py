import dataclasses

import pytest

from tilecraft.constants import Enchantment, Item


##################################
#             TESTS              #
##################################


def test_item_object_cannot_be_modified():
    """ Asserts that Item objects' properties cannot be modified directly """
    with pytest.raises(dataclasses.FrozenInstanceError):
        base = Item.new("Dirt", 1)
        base.number = 0


@pytest.mark.parametrize("quantity", [0, -1])
def test_cannot_create_item_with_non_positive_quantity(quantity: int):
    """ Asserts that creating an item with non-positive quantity throws an exception """
    with pytest.raises(ValueError):
        _ = Item.new("Dirt", quantity)


@pytest.mark.parametrize("durability", [0, -1])
def test_cannot_create_item_with_non_positive_durability(durability: int):
    """ Asserts that creating an item with non-positive durability throws an exception """
    with pytest.raises(ValueError):
        _ = Item("Dirt", 1, [], durability)


def test_with_number_returns_none_for_zero_quantity_parameter():
    """ Asserts that modifying an existing item returns None if new quantity is 0 """
    base = Item.new("Dirt", 1)
    assert base.with_number(0) is None
    assert base.adjust_number(-1) is None


def test_with_durability_returns_none_for_zero_durability_parameter():
    """ Asserts that modifying an existing item returns None if new durability is 0 """
    base = Item.new("Wooden Pickaxe", 1)
    assert base.with_durability(0) is None
    assert base.adjust_durability(-base.max_durability) is None


def test_disenchant_clears_all_enchantments():
    """ Asserts that disenchant() clears all enchantments on an item """
    item = Item.new("Wooden Pickaxe", 1).with_enchantments([Enchantment("Efficiency", 5)])
    assert not item.disenchant().is_enchanted


@pytest.mark.parametrize(("enchantments", "expected"), [
    ([Enchantment("Efficiency", 5)], True),
    ([Enchantment("Efficiency", 4), Enchantment("Unbreaking", 2)], True),
    ([], False),
])
def test_item_is_enchanted_when_enchantments_has_zero_length(enchantments: list[Enchantment], expected: bool):
    """ Asserts that is_enchanted is true only when enchantments list has zero length """
    item = Item.new("Wooden Pickaxe", 1).with_enchantments(enchantments)
    assert item.is_enchanted == expected
