from typing import Optional

import pytest
from unittest.mock import create_autospec

from tilecraft.constants import Item
from tilecraft.inventory import Grindstone
from tilecraft.player_info import Experience


##################################
#         TEST HELPERS           #
##################################


def mock_experience():
    """ Creates a new mock experience object to observe method calls """
    return create_autospec(Experience, instance=True, spec_set=True)


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize(("item", "experience_points"), [
    (Item("Wooden Pickaxe", 1, [["Efficiency", 5]], 0), 40),
    (Item("Stone Pickaxe", 1, [["Efficiency", 5]], 0), 40),
    (Item("Iron Pickaxe", 1, [["Efficiency", 5]], 0), 40),
    (Item("Diamond Pickaxe", 1, [["Efficiency", 5]], 0), 40),
])
def test_grindstone_produces_right_output_and_levels(item: Item, experience_points: int):
    """
        Test that the grindstone produces right output and returns the right number of
        experience points to the plyer
    """
    experience = mock_experience()
    grindstone = Grindstone(experience)
    grindstone.items[0] = item

    grindstone.repair_and_disenchant()
    assert grindstone.items[2] is not None
    assert grindstone.items[2].enchantments is None

    grindstone.disenchant()
    experience.add_points.assert_called_once_with(experience_points)


@pytest.mark.parametrize(("enchantments", "experience_points"), [
    ([["Efficiency", 5]], 40),
    ([["Efficiency", 5], ["Unbreaking", 2]], 56),
    ([["Efficiency", 1]], 8),
])
def test_grindstone_awards_experience_for_all_enchantments(enchantments, experience_points):
    """
        Test that grindstone gives experience for all enchantment types
    """
    experience = mock_experience()
    grindstone = Grindstone(experience)
    grindstone.items[0] = Item("Iron Pickaxe", 1, enchantments, 10)

    grindstone.disenchant()
    total_points = sum(
        args[0]
        for args, kwargs in experience.add_points.call_args_list
    )
    assert total_points == experience_points


def test_grindstone_previews_disenchanted_output_without_changing_input_or_experience():
    """
        Test that repair_and_disenchant shows the disenchanted item in the output slot
        without giving the user experience back
    """
    experience = mock_experience()
    grindstone = Grindstone(experience)
    item = Item("Iron Pickaxe", 1, [["Efficiency", 5]], 10)
    grindstone.items[0] = item

    grindstone.repair_and_disenchant()

    output = grindstone.items[2]
    assert output is not None
    assert output is not item
    assert output.name == "Iron Pickaxe"
    assert output.number == 1
    assert output.durability == 10
    assert output.enchantments is None
    assert item.enchantments == [["Efficiency", 5]]
    experience.add_points.assert_not_called()


@pytest.mark.parametrize("exceeds_maximum", [False, True])
@pytest.mark.parametrize("is_enchanted", [False, True])
def test_grindstone_repairs_matching_tools_with_durability_cap(exceeds_maximum, is_enchanted: bool):
    """
        Tests that grindstone repairing functionality is correct
    """
    grindstone = Grindstone(Experience())
    enchantments = [["Efficiency", 1]] if is_enchanted else []
    first = Item("Iron Pickaxe", 1, enchantments, 10)
    second_durability = first.max_durability if exceeds_maximum else 20
    grindstone.items[:2] = [first, Item("Iron Pickaxe", 1, None, second_durability)]

    grindstone.repair_and_disenchant()

    output = grindstone.items[2]
    assert output is not None
    assert output.name == "Iron Pickaxe"
    assert output.number == 1
    assert output.durability == (first.max_durability if exceeds_maximum else 30)
    assert output.enchantments is None
    assert first.durability == 10
    assert grindstone.items[1].durability == second_durability


def test_grindstone_clears_previous_output_for_mismatched_tools():
    """
        Test that grindstone cannot repair one item with a different item
    """
    grindstone = Grindstone(Experience())
    grindstone.items[0] = Item("Iron Pickaxe", 1, [["Efficiency", 1]], 10)
    grindstone.repair_and_disenchant()
    assert grindstone.items[2] is not None

    grindstone.items[1] = Item("Stone Pickaxe", 1, None, 20)
    grindstone.repair_and_disenchant()

    assert grindstone.items[2] is None


@pytest.mark.parametrize("input_slot", [None, Item.new("Iron Pickaxe", 1).set_max_durability()])
def test_grindstone_does_not_disenchant_invalid_input(input_slot: Optional[Item]):
    """
        Test that grindstone does not preview any output when input is invalid
    """
    grindstone = Grindstone(Experience())
    grindstone.items[0] = input_slot

    grindstone.repair_and_disenchant()
    assert grindstone.items[2] is None
