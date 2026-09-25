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
    return sum(
        item.number
        for item in inventory.items
        if item is not None and item.name == name
    )


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

    assert inventory_contains_item(inventory, "Dirt", 64)
    assert inventory_contains_item(inventory, "Dirt", 100 - 64)


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
