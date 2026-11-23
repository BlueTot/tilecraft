from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

import pytest

from tilecraft.advancements import AdvancementsManager
from tilecraft.inventory import Armour, Inventory
from tilecraft.items import Enchantment, Item


##################################
#         TEST HELPERS           #
##################################

@dataclass
class GameContext:
    """ The required gamestate to trigger an advancement completion """
    inventory: Inventory
    armour: Armour
    dimension: str


class Advancement(ABC):
    """ An advancement base class helper """

    def __init__(self, context: GameContext):
        self.context = context


    @property
    @abstractmethod
    def name(self) -> str:
        """ Returns the name of the advancement """
        return ""


    @abstractmethod
    def completion_methods(self) -> list[Callable[[], None]]:
        """ Returns a list of possible ways to complete the advancement """
        

class StoneAgeAdvancement(Advancement):
    """ Stone Age """

    @property
    def name(self) -> str:
        return "Stone Age"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Cobblestone", 1))
        return [ callback ]



class GettingAnUpgradeAdvancement(Advancement):
    """ Getting an Upgrade """

    @property
    def name(self) -> str:
        return "Getting an Upgrade"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Stone Pickaxe", 1))
        return [ callback ]


class IntoTheDepthsAdvancement(Advancement):
    """ Into the Depths """
    
    @property
    def name(self) -> str:
        return "Into the Depths"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.dimension = "Underground"
        return [ callback ]


class AcquireHardwareAdvancement(Advancement):
    """ Acquire Hardware """

    @property
    def name(self) -> str:
        return "Acquire Hardware"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Iron Ingot", 1))
        return [ callback ]


class IsntItIronPickAdvancement(Advancement):
    """ Isn't it Iron Pick """

    @property
    def name(self) -> str:
        return "Isn't it Iron Pick"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Iron Pickaxe", 1))
        return [ callback ]


class SuitUpAdvancement(Advancement):
    """ Suit Up"""

    @property
    def name(self) -> str:
        return "Suit Up"

    def completion_methods(self) -> list[Callable[[], None]]:
        def make_callback(item_name: str) -> Callable[[], None]:
            def callback():
                self.context.inventory.add(Item.new(item_name, 1))
            return callback
        return [make_callback(name) for name in ("Tier 1 Iron Plate", "Tier 2 Iron Plate", "Tier 3 Iron Plate")]

class DiamondsAdvancement(Advancement):
    """ Diamonds! """

    @property
    def name(self) -> str:
        return "Diamonds!"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Diamond", 1))
        return [ callback ]


class CoverMeWithDiamondsAdvancement(Advancement):
    """ Cover Me with Diamonds """

    @property
    def name(self) -> str:
        return "Cover Me with Diamonds"

    def completion_methods(self) -> list[Callable[[], None]]:
        def make_callback(item_name: str) -> Callable[[], None]:
            def callback():
                self.context.inventory.add(Item.new(item_name, 1))
            return callback
        return [make_callback(name) for name in ("Tier 1 Diamond Plate", "Tier 2 Diamond Plate", "Tier 3 Diamond Plate")]


class IceBucketChallengeAdvancement(Advancement):
    """ Ice Bucket Challenge """

    @property
    def name(self) -> str:
        return "Ice Bucket Challenge"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Obsidian", 1))
        return [ callback ]


class WeNeedToGoDeeperAdvancement(Advancement):
    """ We Need to Go Deeper """

    @property
    def name(self) -> str:
        return "We Need to Go Deeper"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.dimension = "Nether"
        return [ callback ]


class EnchanterAdvancement(Advancement):
    """ Enchanter """

    @property
    def name(self) -> str:
        return "Enchanter"

    def completion_methods(self) -> list[Callable[[], None]]:
        def make_inventory_callback(item_name: str, enchantments: list[Enchantment]) -> Callable[[], None]:
            def callback() -> None:
                self.context.inventory.add(Item.new(item_name, 1).with_enchantments(enchantments))
            return callback

        def make_armour_callback(index: int, item_name: str, enchantments: list[Enchantment]) -> Callable[[], None]:
            def callback() -> None:
                self.context.armour.items[index] = Item.new(item_name, 1).with_enchantments(enchantments)
            return callback

        callbacks = []
        callbacks.extend([
            make_inventory_callback(name, enchantments)
            for name in ("Wooden Pickaxe", "Tier 1 Iron Plate")
            for enchantments in ([Enchantment("Efficiency", 5)], [Enchantment("Protection", 4), Enchantment("Unbreaking", 3)])
        ])
        callbacks.extend([
            make_armour_callback(0, "Tier 1 Iron Plate", [Enchantment("Protection", 4)]),
            make_armour_callback(1, "Tier 2 Diamond Plate", [Enchantment("Efficiency", 3), Enchantment("Unbreaking", 1)]),
            make_armour_callback(2, "Tier 3 Iron Plate", [Enchantment("Unbreaking", 2), Enchantment("Unbreaking", 2)])
        ])
        return callbacks


class GodGearAdvancement(Advancement):
    """ God Gear """

    @property
    def name(self) -> str:
        return "God Gear"

    def completion_methods(self) -> list[Callable[[], None]]:
        enchantments = [Enchantment("Protection", 5), Enchantment("Unbreaking", 3)]
        def callback() -> None:
            self.context.armour.items[0] = Item.new("Tier 1 Diamond Plate", 1).with_enchantments(enchantments)
            self.context.armour.items[1] = Item.new("Tier 2 Diamond Plate", 1).with_enchantments(enchantments)
            self.context.armour.items[2] = Item.new("Tier 3 Diamond Plate", 1).with_enchantments(enchantments)
        return [ callback ]


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize("constructor", [
    StoneAgeAdvancement,
    GettingAnUpgradeAdvancement,
    IntoTheDepthsAdvancement,
    AcquireHardwareAdvancement,
    IsntItIronPickAdvancement,
    SuitUpAdvancement,
    DiamondsAdvancement,
    CoverMeWithDiamondsAdvancement,
    IceBucketChallengeAdvancement,
    WeNeedToGoDeeperAdvancement,
    EnchanterAdvancement,
    GodGearAdvancement
])
def test_advancements_trigger_correctly(constructor: Callable[[GameContext], Advancement]):
    """ Asserts that all advancements trigger when their precondition is met """

    index = 0
    length = 1
    
    while index < length:
        context = GameContext(Inventory(), Armour(), "Overworld")
        advancement = constructor(context)
        methods = advancement.completion_methods()
        length = len(methods)
        completion_method = methods[index]
        advancements_manager = AdvancementsManager()

        completion_method()

        newly_unlocked = advancements_manager.update(context.inventory, context.armour, context.dimension)
        assert advancement.name in advancements_manager.completed_advancements
        assert advancement.name in newly_unlocked
        index += 1
