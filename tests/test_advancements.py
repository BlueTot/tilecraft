from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable
from unittest.mock import Mock, create_autospec

import pytest

from tilecraft.game_state import Screen, SpeedrunTimer, advancements_update
from tilecraft.inventory import Armour, Inventory
from tilecraft.items import Item


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
    def name(self):
        return "Stone Age"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Cobblestone", 1))
        return [ callback ]



class GettingAnUpgradeAdvancement(Advancement):
    """ Getting an Upgrade """

    @property
    def name(self):
        return "Getting an Upgrade"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Stone Pickaxe", 1))
        return [ callback ]


class IntoTheDepthsAdvancement(Advancement):
    """ Into the Depths """
    
    @property
    def name(self):
        return "Into the Depths"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.dimension = "Underground"
        return [ callback ]


class AcquireHardwareAdvancement(Advancement):
    """ Acquire Hardware """

    @property
    def name(self):
        return "Acquire Hardware"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Iron Ingot", 1))
        return [ callback ]


class IsntItIronPickAdvancement(Advancement):
    """ Isn't it Iron Pick """

    @property
    def name(self):
        return "Isn't it Iron Pick"

    def completion_methods(self) -> list[Callable[[], None]]:
        def callback() -> None:
            self.context.inventory.add(Item.new("Iron Pickaxe", 1))
        return [ callback ]


##################################
#             TESTS              #
##################################


@pytest.mark.parametrize("constructor", [
    StoneAgeAdvancement,
    GettingAnUpgradeAdvancement,
    IntoTheDepthsAdvancement,
    AcquireHardwareAdvancement,
    IsntItIronPickAdvancement
])
def test_advancements_trigger_correctly(constructor: Callable[[GameContext], Advancement]):
    """ Asserts that all advancements trigger when their precondition is met """

    screen = create_autospec(Screen, instance=True)
    timer = Mock(spec=SpeedrunTimer)

    index = 0
    length = 1
    
    while index < length:
        context = GameContext(Inventory(), Armour(), "Overworld")
        advancement = constructor(context)
        methods = advancement.completion_methods()
        length = len(methods)
        completion_method = methods[index]
        advancements = []

        completion_method()

        advancements = advancements_update(screen, timer, advancements, context.inventory.items, context.armour.items, context.dimension)
        assert advancement.name in advancements
        index += 1
