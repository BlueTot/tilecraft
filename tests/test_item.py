import dataclasses

import pytest

from tilecraft.items import Enchantment, Item


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


def test_with_number_sets_number_correctly():
    """ Asserts that with_number sets the number value """
    base = Item.new("Dirt", 1)
    assert base.with_number(10).number == 10


def test_adjust_number_sets_number_correctly():
    """ Asserts that adjust_number adds to the existing number value """
    base = Item.new("Dirt", 5)
    assert base.adjust_number(10).number == 15


def test_with_number_returns_none_for_zero_quantity_parameter():
    """ Asserts that modifying an existing item returns None if new quantity is 0 """
    base = Item.new("Dirt", 1)
    assert base.with_number(0) is None
    assert base.adjust_number(-1) is None


def test_with_number_raises_error_for_negative_quantity_paramter():
    """ Asserts that modifying an existing item raises an exception if new quantity is negative """
    base = Item.new("Dirt", 1)
    with pytest.raises(ValueError):
        base.with_number(-1)
    with pytest.raises(ValueError):
        base.adjust_number(-2)


def test_with_durability_sets_durability_correctly():
    """ Asserts that with_durability sets the durability value correctly """
    base = Item.new("Wooden Pickaxe", 1)
    assert base.with_durability(1).durability == 1


def test_adjust_durability_sets_durability_correctly():
    """ Asserts that adjust_durability adds to the existing durability value correctly """
    base = Item.new("Wooden Pickaxe", 1)
    assert base.adjust_durability(-5).durability == base.durability - 5


def test_with_durability_returns_none_for_zero_durability_parameter():
    """ Asserts that modifying an existing item returns None if new durability is 0 """
    base = Item.new("Wooden Pickaxe", 1)
    assert base.with_durability(0) is None
    assert base.adjust_durability(-base.max_durability) is None


def test_with_durability_raises_error_for_negative_quantity_paramter():
    """ Asserts that modifying an existing item raises an exception if new durability is negative """
    base = Item.new("Wooden Pickaxe", 1)
    with pytest.raises(ValueError):
        base.with_durability(-1)
    with pytest.raises(ValueError):
        base.adjust_durability(-base.max_durability-1)


def test_modifying_durability_raises_error_when_max_durability_is_none():
    """ Asserts that modifying durability raises an exception when the item's max durability is None """
    base = Item.new("Dirt", 1)
    with pytest.raises(ValueError):
        base.with_durability(1)
    with pytest.raises(ValueError):
        base.adjust_durability(-1)


def test_modifying_durability_raises_error_when_exceeding_max_durability():
    """ Asserts that modifying durability raises an error when the consequent durability value
        exceeds the max_durability value """
    base = Item.new("Wooden Pickaxe", 1)
    with pytest.raises(ValueError):
        base.with_durability(base.max_durability + 1)
    with pytest.raises(ValueError):
        base.adjust_durability(1)


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


@pytest.mark.parametrize("original", [
    [Enchantment("Efficiency", 5)],
    [Enchantment("Protection", 4), Enchantment("Unbreaking", 3)],
    [Enchantment("Efficiency", 5), Enchantment("Efficiency", 5)]
])
def test_adding_enchantments_adds_to_existing_list(original: list[Enchantment]):
    """ Asserts that add_enchantment adds to the existing list of enchantments """
    enchantment_to_add = Enchantment("Unbreaking", 1)
    base = Item.new("Wooden Pickaxe", 1).with_enchantments(original)
    
    assert list(base.add_enchantment(enchantment_to_add).enchantments) == original + [enchantment_to_add]
