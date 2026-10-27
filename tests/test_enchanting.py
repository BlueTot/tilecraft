import pytest
from unittest.mock import call, create_autospec

from tilecraft.constants import Item, RandomNumberGenerator
from tilecraft.inventory import EnchantingTable
from tilecraft.player_info import Experience


##################################
#         TEST HELPERS           #
##################################


def mock_experience():
    """ Creates a new mock experience object to observe method calls """
    return create_autospec(Experience, instance=True, spec_set=True)


def prepare_enchanting(table, *, lapis, experience):
    """Prepare selectable options and resources; return the original input item."""
    original = Item("Iron Pickaxe", 1, None, 10)
    table.items[0] = original
    table.items[1] = Item.new("Lapis Lazuli", lapis)
    table.experience.levels = float(experience)
    table.option_list = ["Efficiency 1", "Efficiency 2", "Efficiency 3"]
    return original


def option_snapshot(table):
    """Capture option values without retaining the mutable option list."""
    return tuple(table.option_list), table.optional_enchant2, table.optional_enchant3


@pytest.fixture
def table():
    """
        Creates a enchanting table with a mock player's experience
        and mock random number generator
        """
    experience = mock_experience()
    experience.levels = 3.0
    rng = create_autospec(RandomNumberGenerator, instance=True, spec_set=True)
    rng.next_random.side_effect = lambda start, stop: start
    return EnchantingTable(rng, experience)


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize(("name", "enchantment"), [
    ("Iron Pickaxe", "Efficiency"),
    ("Tier 1 Iron Plate", "Protection"),
])
@pytest.mark.parametrize("boundary", [0, 1], ids=["minimum", "maximum"])
@pytest.mark.parametrize(("level", "expected_levels", "expected_extras", "random_ranges"), [
    (0, ((0, 0, 0), (0, 0, 1)), ((None, None), (None, None)), [(0, 1)]),
    (1, ((1, 1, 2), (1, 2, 2)), ((None, None), (None, None)), [(1, 2)]),
    (2, ((2, 2, 3), (2, 3, 3)), ((None, None), (None, None)), [(2, 3)]),
    (3, ((3, 3, 4), (3, 4, 4)), ((None, 0), (None, 1)), [(3, 4), (0, 1)]),
    (4, ((4, 4, 5), (4, 5, 5)), ((0, 1), (1, 2)), [(4, 5), (0, 1), (1, 2)]),
    (5, ((4, 5, 5), (5, 5, 5)), ((1, 2), (2, 3)), [(4, 5), (1, 2), (2, 3)]),
])
def test_enchanting_generates_options_for_tools_and_armour(
    table, name, enchantment, boundary, level, expected_levels, expected_extras, random_ranges
):
    """
        Check all three options at every table level for both random boundaries.
    """
    table.items[0] = Item.new(name, 1)
    table.enchanting_level = level
    table.rng.next_random.side_effect = lambda start, stop: (start, stop)[boundary]

    table.enchant_set()

    assert table.option_list == [
        f"{enchantment} {strength}" if strength else "N/A"
        for strength in expected_levels[boundary]
    ]
    assert (table.optional_enchant2, table.optional_enchant3) == expected_extras[boundary]
    assert table.rng.next_random.call_args_list == [call(*bounds) for bounds in random_ranges]
    assert table.items[0].enchantments is None
    table.experience.subtract.assert_not_called()


@pytest.mark.parametrize("enchanted", [False, True])
def test_enchanting_clears_options_for_missing_or_enchanted_item(table, enchanted):
    """
        Tests that enchanting table does not emit options for invald inputs
    """
    table.option_list = ["Efficiency 1", "Efficiency 2", "Efficiency 3"]
    if enchanted:
        table.items[0] = Item("Iron Pickaxe", 1, [["Efficiency", 1]], 10)

    table.enchant_set()

    assert table.option_list == ["", "", ""]
    table.rng.next_random.assert_not_called()


@pytest.mark.parametrize("choice", [1, 2, 3])
def test_enchanting_applies_selected_option_and_charges_exact_cost(table, choice):
    """
        Test that enchanting table applies selected enchantment and subtracts
        the right amount of experience
    """
    surplus = 2
    prepare_enchanting(table, lapis=choice + surplus, experience=choice)

    getattr(table, f"enchant{choice}")()

    assert table.items[0].name == "Iron Pickaxe"
    assert table.items[0].number == 1
    assert table.items[0].enchantments == [["Efficiency", choice]]
    assert table.items[1].number == surplus
    table.experience.subtract.assert_called_once_with(choice)
    assert table.option_list == ["", "", ""]


@pytest.mark.parametrize("choice", [1, 2, 3])
@pytest.mark.parametrize("missing_resource", ["lapis", "experience"])
def test_enchanting_does_not_consume_resources_when_cost_cannot_be_paid(table, choice, missing_resource):
    """
        Tests that enchanting does not consume resources if there is either not
        enough lapis or player experience
    """
    lapis_count = choice - 1 if missing_resource == "lapis" else choice
    experience = choice - 1 if missing_resource == "experience" else choice
    original = prepare_enchanting(table, lapis=lapis_count, experience=experience)

    getattr(table, f"enchant{choice}")()

    assert table.items[0] is original
    assert original.enchantments is None
    assert original.durability == 10
    assert table.items[1].number == lapis_count
    table.experience.subtract.assert_not_called()


@pytest.mark.parametrize("bookshelves", [0, 1, 2, 3, 4, 5, 8, 64])
@pytest.mark.parametrize(("level", "upgraded_strengths", "upgraded_extras"), [
    (0, (1, 1, 2), (None, None)),
    (1, (2, 2, 3), (None, None)),
    (2, (3, 3, 4), (None, 0)),
    (3, (4, 4, 5), (0, 1)),
    (4, (4, 5, 5), (1, 2)),
    (5, None, None),
])
def test_enchanting_upgrade_cost_and_maximum_level(
    table, level, bookshelves, upgraded_strengths, upgraded_extras
):
    """
        Upgrade once for four bookshelves, refresh options, and stop at level five.
    """
    table.enchanting_level = level
    original = Item("Iron Pickaxe", 1, None, 10)
    table.items[0] = original
    table.items[1] = Item.new("Lapis Lazuli", 7)
    table.items[2] = Item.new("Bookshelf", bookshelves)
    table.experience.levels = 0.0
    table.enchant_set()
    previous_options = option_snapshot(table)
    table.rng.next_random.reset_mock()

    table.enchant_upgrade()

    should_upgrade = level < 5 and bookshelves >= 4
    assert table.enchanting_level == level + int(should_upgrade)
    assert table.items[2].name == "Bookshelf"
    assert table.items[2].number == bookshelves - (4 if should_upgrade else 0)
    assert table.items[0] is original
    assert original.enchantments is None
    assert original.durability == 10
    assert table.items[1].number == 7
    table.experience.subtract.assert_not_called()
    if should_upgrade:
        assert table.option_list == [f"Efficiency {strength}" for strength in upgraded_strengths]
        assert (table.optional_enchant2, table.optional_enchant3) == upgraded_extras
    else:
        assert option_snapshot(table) == previous_options
        table.rng.next_random.assert_not_called()


@pytest.mark.parametrize("level", range(6))
@pytest.mark.parametrize("material_name", [None, "Lapis Lazuli"], ids=["empty-slot", "wrong-item"])
def test_enchanting_upgrade_rejects_missing_or_wrong_material(table, level, material_name):
    """
        Tests that enchanting table upgrades do not work if invalid material
        is passed in
    """
    table.enchanting_level = level
    table.items[0] = Item.new("Iron Pickaxe", 1)
    material = Item.new(material_name, 4) if material_name else None
    table.items[2] = material
    table.enchant_set()
    previous_options = option_snapshot(table)
    table.rng.next_random.reset_mock()

    table.enchant_upgrade()

    assert table.enchanting_level == level
    assert table.items[2] is material
    if material is not None:
        assert material.number == 4
    assert option_snapshot(table) == previous_options
    table.rng.next_random.assert_not_called()
    table.experience.subtract.assert_not_called()


@pytest.mark.parametrize("level", range(5))
@pytest.mark.parametrize("enchanted", [False, True], ids=["empty-input", "enchanted-input"])
def test_enchanting_upgrade_without_enchantable_input(table, level, enchanted):
    """
        Upgrading needs only bookshelves, even when no enchantment can be offered.
    """
    table.enchanting_level = level
    original = Item("Iron Pickaxe", 1, [["Efficiency", 1]], 10) if enchanted else None
    table.items[0] = original
    table.items[2] = Item.new("Bookshelf", 4)
    table.option_list = ["Efficiency 1", "Efficiency 2", "Efficiency 3"]

    table.enchant_upgrade()

    assert table.enchanting_level == level + 1
    assert table.items[2].number == 0
    assert table.items[0] is original
    if enchanted:
        assert original.enchantments == [["Efficiency", 1]]
        assert original.durability == 10
    assert table.option_list == ["", "", ""]
    table.rng.next_random.assert_not_called()
    table.experience.subtract.assert_not_called()


@pytest.mark.parametrize("choice", [1, 2, 3])
def test_enchanting_preserves_durability(table, choice):
    """
        Tests that enchanting an item preserves its durability
    """
    prepare_enchanting(table, lapis=3, experience=3)

    getattr(table, f"enchant{choice}")()

    assert table.items[0].durability == 10
