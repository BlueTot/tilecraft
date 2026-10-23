import pytest

from tilecraft.constants import Item
from tilecraft.inventory import Grindstone
from tilecraft.player_info import Experience


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize(("item", "levels"), [
    (Item("Wooden Pickaxe", 1, [["Efficiency", 5]], 0), (161 ** 0.5 - 1) / 2),
    (Item("Stone Pickaxe", 1, [["Efficiency", 5]], 0), (161 ** 0.5 - 1) / 2),
    (Item("Iron Pickaxe", 1, [["Efficiency", 5]], 0), (161 ** 0.5 - 1) / 2),
    (Item("Diamond Pickaxe", 1, [["Efficiency", 5]], 0), (161 ** 0.5 - 1) / 2),
])
def test_grindstone_produces_right_output_and_levels(item: Item, levels: float):
    """
        Test that the grindstone produces right output and returns the right number of
        experience points to the plyer
    """
    grindstone = Grindstone(experience := Experience())
    grindstone.items[0] = item

    grindstone.repair_and_disenchant()
    assert grindstone.items[2] is not None
    assert grindstone.items[2].enchantments is None

    grindstone.disenchant()
    assert experience.levels == pytest.approx(levels)


@pytest.mark.parametrize(("enchantments", "initial_points", "expected_levels"), [
    ([["Efficiency", 5]], 0, (161 ** 0.5 - 1) / 2),
    ([["Efficiency", 5], ["Unbreaking", 2]], 0, 7),
    ([["Efficiency", 1]], 12, 4),
])
def test_grindstone_awards_experience_for_all_enchantments(
    enchantments, initial_points, expected_levels
):
    experience = Experience()
    experience.add_points(initial_points)
    grindstone = Grindstone(experience)
    grindstone.items[0] = Item("Iron Pickaxe", 1, enchantments, 10)

    grindstone.disenchant()

    # Each enchantment level awards 8 points; total points = levels * (levels + 1).
    assert experience.levels == pytest.approx(expected_levels)


def test_grindstone_previews_disenchanted_output_without_changing_input_or_experience():
    experience = Experience()
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
    assert experience.levels == 0


@pytest.mark.parametrize("exceeds_maximum", [False, True])
def test_grindstone_repairs_matching_tools_with_durability_cap(exceeds_maximum):
    grindstone = Grindstone(Experience())
    first = Item("Iron Pickaxe", 1, [["Efficiency", 1]], 10)
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
    grindstone = Grindstone(Experience())
    grindstone.items[0] = Item("Iron Pickaxe", 1, [["Efficiency", 1]], 10)
    grindstone.repair_and_disenchant()
    assert grindstone.items[2] is not None

    grindstone.items[1] = Item("Stone Pickaxe", 1, None, 20)
    grindstone.repair_and_disenchant()

    assert grindstone.items[2] is None
