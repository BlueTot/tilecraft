from tilecraft.constants import Item
from tilecraft.inventory import Inventory


def test_add_item_to_empty_inventory():
    inventory = Inventory()
    item = Item(name="Dirt", number=10, enchantments=None, durability=None)

    inventory.add(item)

    assert inventory.items[0] is not None
    assert inventory.items[0].name == "Dirt"
    assert inventory.items[0].number == 10