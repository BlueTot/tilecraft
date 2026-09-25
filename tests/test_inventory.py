from typing import Optional

from tilecraft.constants import Item
from tilecraft.inventory import Inventory


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


def test_add_item_more_than_64_splits_to_different_stack():
    """
        Test that adding an item > 64 amount splits into multiple stacks
    """
    inventory = Inventory()

    count = 100
    item = Item(name="Dirt", number=count, enchantments=None, durability=None)
    inventory.add(item)

    stacks = sorted(
        item.number
        for item in inventory.items
        if item is not None and item.name == "Dirt"
    )

    assert stacks == [36, 64]


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


def test_add_non_stackable_items_uses_separate_slots():
    """
        Test that adding non stackable items uses one slot per item
    """
    inventory = Inventory()
    inventory.add(Item("Wooden Pickaxe", 10, None, None))

    assert count_items(inventory, "Wooden Pickaxe") == 10
    assert count_number_of_slots(inventory, "Wooden Pickaxe") == 10


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
