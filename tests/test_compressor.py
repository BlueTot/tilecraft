from typing import Optional

import pytest

from tilecraft.constants import Item
from tilecraft.inventory import Compressor


##################################
#         TEST HELPERS           #
##################################


@pytest.fixture
def compressor() -> Compressor:
    """Creates a new furance interface"""
    return Compressor()


def advance(compressor: Compressor, ticks: int, fps: int = 60) -> None:
    for _ in range(ticks):
        compressor.compress(fps)


##################################
#             TESTS              #
##################################


def test_compressor_starts_empty(compressor: Compressor):
    """
        Test that the compressor starts empty
    """
    assert compressor.items == [None, None]


@pytest.mark.parametrize("fps", [1, 30, 60])
def test_compressor_produces_correct_output_after_five_seconds(compressor: Compressor, fps: int):
    """
        Test that the compressor produces correct output after one cycle
    """
    compressor.items[0] = Item.new("Iron Ingot", 4)

    advance(compressor, 5 * fps - 1)
    assert compressor.items[1] is None
    assert compressor.items[0].number == 4

    compressor.compress(fps)

    assert Item.equals_optional(compressor.items[1], Item.new("Iron Plate", 1))
    assert compressor.items[0].number == 2


@pytest.mark.parametrize("item", [None, Item.new("Dirt", 1), Item.new("Iron Ingot", 1)])
def test_compressor_does_not_process_invalid_input(compressor: Compressor, item: Optional[Item]):
    """
        Test that the compressor does not process invalid input after one cycle
    """
    compressor.items[0] = item

    advance(compressor, 300)

    assert Item.equals_optional(compressor.items[0], item)
    assert compressor.items[1] is None


def test_compressor_adds_to_existing_output_stack(compressor: Compressor):
    """
        Test that compressor adds to existing output stack if it isn't empty
    """
    compressor.items[0] = Item.new("Iron Ingot", 2)
    compressor.items[1] = Item.new("Iron Plate", 1)

    advance(compressor, 300)

    assert Item.equals_optional(compressor.items[1], Item.new("Iron Plate", 2))


@pytest.mark.parametrize("output", [
    Item.new("Dirt", 1),
    Item.new("Iron Plate", 64),
    Item("Iron Plate", 1, [["Efficiency", 5]], None)
])
def test_compressor_does_not_process_when_output_blocked(compressor: Compressor, output: Item):
    """
        Test that the compressor does not process if output cannot be stacked into, including
        enchantments
    """
    compressor.items[0] = Item.new("Iron Ingot", 2)
    compressor.items[1] = Item.clone(output)

    advance(compressor, 300)

    assert Item.equals_optional(compressor.items[0], Item.new("Iron Ingot", 2))
    assert Item.equals_optional(compressor.items[1], output)
