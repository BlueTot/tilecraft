import pytest

from tilecraft.constants import Item
from tilecraft.inventory import Inventory


##################################
#         TEST HELPERS           #
##################################


def inventory_contains_item(inventory: Inventory, name: str, number: int) -> bool:
    """
        Returns true only if inventory contains that item
    """
    for item in inventory.items:
        if item is not None and item.name == name and item.number == number:
            return True
    return False 


def count_items(inventory: Inventory, name: str) -> int:
    """
        Returns the total count of items in inventory with given name
    """
    return sum(
        item.number
        for item in inventory.items
        if item is not None and item.name == name
    )


def count_number_of_slots(inventory: Inventory, name: str) -> int:
    """
        Returns number of slots that an item with given name occupies
    """
    return sum(
        1
        for item in inventory.items
        if item is not None and item.name == name
    )


##################################
#             TESTS              #
##################################


def test_inventory_starts_with_36_slots():
    """
        Test that an inventory starts with 36 empty slots
    """
    inventory = Inventory()
    
    assert len(inventory.items) == 36
    assert all(item is None for item in inventory.items)


def test_add_item_to_empty_inventory():
    """
        Test that adding an item to an empty inventory works as intended
    """

    inventory = Inventory()
    item = Item(name="Dirt", number=10, enchantments=None, durability=None)

    inventory.add(item)

    assert inventory_contains_item(inventory, "Dirt", 10)


def test_adding_item_to_inventory_does_not_modify_it():
    """
        Test that adding an item to the inventory does not modify the item's quantity
    """

    inventory = Inventory()
    item = Item(name="Dirt", number=25, enchantments=None, durability=None)

    inventory.add(item)
    assert item.number == 25


def test_adding_none_to_inventory_returns_0():
    """
        Test that adding None to the inventory returns 0 and does not add anything
    """

    inventory = Inventory()
    remaining = inventory.add(None)

    assert all(item is None for item in inventory.items)
    assert remaining == 0 


def test_add_item_to_partial_stack_adds_to_it():
    """
        Test that adding an item to a partial stack adds to the same item
    """

    inventory = Inventory()

    base_number = 30
    base_item = Item(name="Dirt", number=base_number, enchantments=None, durability=None)
    inventory.add(base_item)

    new_number = 30
    new_item = Item(name="Dirt", number=new_number, enchantments=None, durability=None)
    inventory.add(new_item)

    assert inventory_contains_item(inventory, "Dirt", base_number + new_number)


def test_add_items_with_total_count_64_uses_one_slot():
    """
        Test that adding items that total to 64 in multiple runs
        uses one slot in the inventory
    """
    inventory = Inventory()
    inventory.add(Item("Dirt", 40, None, None))
    inventory.add(Item("Dirt", 24, None, None))

    assert count_number_of_slots(inventory, "Dirt") == 1
    assert count_items(inventory, "Dirt") == 64


def test_adding_items_preserves_total_quantity():
    """
        Test that adding items of the same type preserves total quantity when inventory isn't full
    """

    inventory = Inventory()
    inventory.add(Item("Dirt", 60, None, None))

    before = count_items(inventory, "Dirt")
    inventory.add(Item("Dirt", 10, None, None))
    after = count_items(inventory, "Dirt")

    assert after == before + 10


@pytest.mark.parametrize(
    ("quantity", "expected_stacks"),
    [
        (1, [1]),
        (63, [63]),
        (64, [64]),
        (65, [1, 64]),
        (128, [64, 64]),
        (129, [1, 64, 64]),
    ]
)
def test_stackable_items_are_split_correctly(quantity: int, expected_stacks: list[int]):
    """
        Test that adding an item with any amount splits into
        multiple stacks correctly
    """

    inventory = Inventory() 
    inventory.add(Item("Dirt", quantity, None, None))

    actual_stacks = sorted(
        item.number
        for item in inventory.items
        if item is not None and item.name == "Dirt"
    )

    assert actual_stacks == expected_stacks


def test_add_fills_existing_partial_stacks_before_empty_slots():
    """
        Test that, if there are two partial stacks, adding the same item
        type fills up existing partial stacks first
    """

    inventory = Inventory()
    inventory.items[0] = Item("Dirt", 60, None, None)
    inventory.items[1] = Item("Dirt", 50, None, None)

    inventory.add(Item("Dirt", 10, None, None))

    stacks = sorted(
        item.number
        for item in inventory.items
        if item is not None and item.name == "Dirt"
    )

    assert stacks == [56, 64]


def test_add_non_stackable_items_uses_separate_slots():
    """
        Test that adding non stackable items uses one slot per item
    """

    inventory = Inventory()
    inventory.add(Item("Wooden Pickaxe", 10, None, None))

    assert count_items(inventory, "Wooden Pickaxe") == 10
    assert count_number_of_slots(inventory, "Wooden Pickaxe") == 10


def test_different_item_types_do_not_combine():
    """
        Test that different item names don't combine into the same slot
    """

    inventory = Inventory()

    inventory.add(Item("Dirt", 10, None, None))
    inventory.add(Item("Sand", 12, None, None))

    assert count_items(inventory, "Dirt") == 10
    assert count_items(inventory, "Sand") == 12
    assert count_number_of_slots(inventory, "Dirt") == 1
    assert count_number_of_slots(inventory, "Sand") == 1


def test_full_inventory_returns_correct_amount_remaining():
    """
        Test that if the inventory cannot fit the new item, the correct amount is returned
    """

    inventory = Inventory()
    remaining = inventory.add(Item("Dirt", 36*64 - 32, None, None))
    assert count_items(inventory, "Dirt") == 36*64 - 32
    assert remaining == 0

    remaining = inventory.add(Item("Dirt", 48, None, None))
    assert remaining == 16 


def test_select_hotbar_returns_correct_item():
    """
        Test that selecting hotbar index returns the item at index+27
    """

    inventory = Inventory()
    for index in range(9):
        inventory.items[index+27] = Item("Dirt", index+1, None, None)

    for index in range(9):
        inventory.selected_hotbar = index

        assert inventory.hotbar_item is not None
        assert inventory.hotbar_item.number == index + 1


def test_setting_hotbar_item_updates_selected_slot():
    """
        Test that setting hotbar item through setter updates correct inventory slot
    """

    inventory = Inventory()
    inventory.selected_hotbar = 3
    item = Item("Dirt", 10, None, None)

    inventory.hotbar_item = item

    assert inventory.items[27+3] is item
    assert inventory.hotbar_item is item
