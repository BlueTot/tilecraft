from types import SimpleNamespace
from typing import Optional

import pytest

from tilecraft.constants import Item, Context
from tilecraft.inventory import FurnaceInterface
from tilecraft.player_info import Experience


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


@pytest.fixture
def context() -> Context:
    """Provide the two image references the backend uses, without opening a window."""
    return SimpleNamespace(ITEM_IMAGES={"fire": object(), "no_fire": object()})


@pytest.fixture
def furnace(context: Context) -> FurnaceInterface:
    """Creates a new furance interface"""
    return FurnaceInterface(context)


@pytest.fixture
def experience() -> Experience:
    """
        Creates a new experience object with points=0
    """
    return Experience()


def advance(furnace, context, experience, ticks: int, fps=60):
    """
        Smelts for {ticks} ticks
    """
    for _ in range(ticks):
        furnace.smelt(context, fps, experience)


##################################
#             TESTS              #
##################################


def test_furnace_starts_empty_and_unlit(furnace, context):
    """
        Asserts that furnace starts with no items and no fuel value
    """
    assert furnace.items == [None, None, None]
    assert furnace.fuel_val == 0
    assert furnace.smelting_time == 0
    assert furnace.fuel_img is context.ITEM_IMAGES["no_fire"]


@pytest.mark.parametrize("fps", [1, 30, 60])
def test_furnace_produces_correct_output_after_five_seconds(furnace, context, experience, fps):
    """
        Tests that furance produces correct output after five seconds of
        smelting with different frame rates.
    """

    furnace.items[0] = Item.new("Iron Ore", 2)
    furnace.items[1] = Item.new("Coal", 2)

    advance(furnace, context, experience, 5 * fps - 1, fps)

    assert furnace.items[2] is None
    assert furnace.items[0].number == 2
    assert experience.levels == 0

    furnace.smelt(context, fps, experience)

    assert furnace.items[2].name == "Iron Ingot"
    assert furnace.items[2].number == 1
    assert furnace.items[0].number == 1
    assert furnace.items[1].number == 1
    assert furnace.fuel_val == 7
    assert furnace.smelting_time == 0
    # Twelve points reach level three: 3 * (3 + 1) == 12.
    assert experience.levels == pytest.approx(3)


@pytest.mark.parametrize("fuel_name", [None, "Dirt"])
def test_furnace_does_not_smelt_without_valid_fuel(furnace, context, experience, fuel_name):
    """
        Tests that furnace does not smelt without valid fuel
    """
    furnace.items[0] = Item.new("Iron Ore", 2)
    furnace.items[1] = Item.new(fuel_name, 1) if fuel_name is not None else None

    advance(furnace, context, experience, 300)

    assert furnace.items[2] is None
    assert furnace.items[0].number == 2
    if fuel_name is not None:
        assert furnace.items[1].number == 1
    assert furnace.smelting_time == 0
    assert furnace.fuel_val == 0
    assert experience.levels == 0
    assert furnace.fuel_img is context.ITEM_IMAGES["no_fire"]


@pytest.mark.parametrize("input_name", [None, "Dirt"])
def test_furnace_does_not_process_missing_or_invalid_input(furnace, context, experience, input_name):
    """
        Tests that furnace doesn't try to smelt empty or invalid input
    """
    furnace.items[0] = Item.new(input_name, 1) if input_name is not None else None
    furnace.fuel_val = 8

    advance(furnace, context, experience, 300)

    assert furnace.items[2] is None
    if input_name is not None:
        assert furnace.items[0].number == 1
    assert furnace.smelting_time == 0
    assert furnace.fuel_val == 8
    assert experience.levels == 0


def test_furnace_loads_one_coal_and_keeps_using_its_fuel(furnace, context, experience):
    """
        Tests that fuel is loaded one at a time until it needs more
    """
    furnace.items[0] = Item.new("Iron Ore", 2)
    furnace.items[1] = Item.new("Coal", 3)

    advance(furnace, context, experience, 2)

    assert furnace.items[1].number == 2
    assert furnace.fuel_val == 8
    assert furnace.fuel_img is context.ITEM_IMAGES["fire"]


def test_furnace_adds_to_existing_ingot_stack(furnace, context, experience):
    """
        Tests that furnace adds to the existing output stack
    """
    furnace.items[0] = Item.new("Iron Ore", 3)
    furnace.items[2] = Item.new("Iron Ingot", 10)
    furnace.fuel_val = 8

    advance(furnace, context, experience, 600)

    assert furnace.items[2].name == "Iron Ingot"
    assert furnace.items[2].number == 12
    assert furnace.items[0].number == 1
    assert furnace.fuel_val == 6
    assert experience.levels == pytest.approx((-1 + 97 ** 0.5) / 2)


def test_furnace_resets_progress_when_input_is_removed(furnace, context, experience):
    """
        Test that furnace resets progress when smelting item is removed
    """
    furnace.items[0] = Item.new("Iron Ore", 2)
    furnace.fuel_val = 8
    advance(furnace, context, experience, 150)

    furnace.items[0] = None
    furnace.smelt(context, 60, experience)
    assert furnace.smelting_time == 0

    furnace.items[0] = Item.new("Iron Ore", 2)
    advance(furnace, context, experience, 150)
    assert furnace.items[2] is None
    assert experience.levels == 0


def test_furnace_stops_when_stored_fuel_runs_out(furnace, context, experience):
    """
        Tests that furnace stops smelting when fuel value is 0
    """
    furnace.items[0] = Item.new("Iron Ore", 3)
    furnace.fuel_val = 1

    advance(furnace, context, experience, 600)

    assert furnace.items[2].number == 1
    assert furnace.items[0].number == 2
    assert furnace.fuel_val == 0
    assert furnace.smelting_time == 0
    assert furnace.fuel_img is context.ITEM_IMAGES["no_fire"]
    assert experience.levels == pytest.approx(3)


def test_furnace_does_not_smelt_depleted_input(furnace, context, experience):
    """
        Tests that furnace does not smelt input item with count 0
    """
    furnace.items[0] = Item.new("Iron Ore", 0)
    furnace.fuel_val = 8

    advance(furnace, context, experience, 300)

    assert furnace.items[2] is None
    assert furnace.items[0].number == 0
    assert furnace.fuel_val == 8
    assert experience.levels == 0


@pytest.mark.parametrize("blocked_output", [
    Item.new("Dirt", 1),  # different item
    Item.new("Iron Ingot", 64),  # stack full
    Item("Iron Ingot", 1, [["Efficiency", 5]], None) # enchantments do not stack
])
def test_furnace_does_not_smelt_into_blocked_output(furnace, context, experience, blocked_output: Item):
    """
        Tests that furnace does not smelt if output item cannot be added to
    """
    furnace.items[0] = Item.new("Iron Ore", 2)
    furnace.items[2] = Item.clone(blocked_output)
    furnace.fuel_val = 8

    advance(furnace, context, experience, 300)

    print(furnace.items[2])
    assert item_equals(furnace.items[2], blocked_output)
    assert furnace.fuel_val == 8
    assert experience.levels == 0
