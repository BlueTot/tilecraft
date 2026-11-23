from abc import ABC, abstractmethod
from typing import Callable

from tilecraft.inventory import Inventory, Armour
from tilecraft.items import Enchantment


class Advancement(ABC):
    """ Base class for all advancements """

    @property
    @abstractmethod
    def name(self) -> str:
        """ Name of the advancement """
        return ""

    @abstractmethod
    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        """ Returns whether the advancement can be unlocked """
        return False


class StoneAgeAdvancement(Advancement):
    """ Stone Age advancement """

    @property
    def name(self) -> str:
        return "Stone Age"
    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Cobblestone" for item in inventory.items if item is not None)


class GettingAnUpgradeAdvancement(Advancement):
    """ Getting an Upgrade advancement """

    @property
    def name(self) -> str:
        return "Getting an Upgrade"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Stone Pickaxe" for item in inventory.items if item is not None)


class IntoTheDepthsAdvancement(Advancement):
    """ Into the Depths advancement """

    @property
    def name(self) -> str:
        return "Into the Depths"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return dimension == "Underground"


class AcquireHardwareAdvancement(Advancement):
    """ Acquire Hardware advancement """

    @property
    def name(self) -> str:
        return "Acquire Hardware"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Iron Ingot" for item in inventory.items if item is not None)


class IsntItIronPickAdvancement(Advancement):
    """ Isn't it Iron Pick advancement """

    @property
    def name(self) -> str:
        return "Isn't it Iron Pick"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Iron Pickaxe" for item in inventory.items if item is not None)


class SuitUpAdvancement(Advancement):
    """ Suit Up advancement """

    @property
    def name(self) -> str:
        return "Suit Up"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(
            item.name in ("Tier 1 Iron Plate", "Tier 2 Iron Plate", "Tier 3 Iron Plate")
            for item in inventory.items
            if item is not None
        )


class DiamondsAdvancement(Advancement):
    """ Diamonds! advancement """

    @property
    def name(self) -> str:
        return "Diamonds!"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Diamond" for item in inventory.items if item is not None)


class CoverMeWithDiamondsAdvancement(Advancement):
    """ Cover Me with Diamonds advancement """

    @property
    def name(self) -> str:
        return "Cover Me with Diamonds"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(
            item.name in ("Tier 1 Diamond Plate", "Tier 2 Diamond Plate", "Tier 3 Diamond Plate")
            for item in inventory.items
            if item is not None
        )


class IceBucketChallengeAdvancement(Advancement):
    """ Ice Bucket Challenge advancement """

    @property
    def name(self) -> str:
        return "Ice Bucket Challenge"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(item.name == "Obsidian" for item in inventory.items if item is not None)


class WeNeedToGoDeeperAdvancement(Advancement):
    """ We Need to Go Deeper advancement """

    @property
    def name(self) -> str:
        return "We Need to Go Deeper"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return dimension == "Nether"


class EnchanterAdvancement(Advancement):
    """ Enchanter advancement """

    @property
    def name(self) -> str:
        return "Enchanter"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        return any(
            item.is_enchanted
            for item in (inventory.items + armour.items)
            if item is not None
        )


class GodGearAdvancement(Advancement):
    """ God Gear Advancement """

    @property
    def name(self) -> str:
        return "God Gear"

    def can_unlock(self, inventory: Inventory, armour: Armour, dimension: str) -> bool:
        slot1, slot2, slot3 = armour.items[:3]
        max_t1 = (
            slot1 is not None and
            slot1.name == "Tier 1 Diamond Plate" and
            Enchantment("Protection", 5) in slot1.enchantments and
            Enchantment("Unbreaking", 3) in slot1.enchantments
        )
        max_t2 = (
            slot2 is not None and
            slot2.name == "Tier 2 Diamond Plate" and
            Enchantment("Protection", 5) in slot2.enchantments and
            Enchantment("Unbreaking", 3) in slot2.enchantments
        )
        max_t3 = (
            slot3 is not None and
            slot3.name == "Tier 3 Diamond Plate" and
            Enchantment("Protection", 5) in slot3.enchantments and
            Enchantment("Unbreaking", 3) in slot3.enchantments
        )
        return max_t1 and max_t2 and max_t3


class AdvancementsManager:
    """
        Manages all advancement statuses and updates them
    """

    ADVANCEMENTS: list[Callable[[], Advancement]] = [
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
    ]

    def __init__(self) -> None:
        self.__advancements: list[str] = []


    @property
    def completed_advancements(self) -> list[str]:
        """ Return the list of completed advancements """
        return self.__advancements


    def update(self, inventory: Inventory, armour: Armour, dimension: str) -> list[str]:
        """ Update the advancements list, returning the list of newly unlocked advancements """

        newly_unlocked = []

        for constructor in self.ADVANCEMENTS:
            adv = constructor()
            if adv.name not in self.__advancements and adv.can_unlock(inventory, armour, dimension):
                self.__advancements.append(adv.name)
                newly_unlocked.append(adv.name)

        return newly_unlocked


    def check_music_player(self) -> bool:
        """
            Update the music player advancement's status, returning True if freshly unlocked
        """
        if "Music Player" not in self.__advancements:  # Music Player: Play Pigstep
            self.__advancements.append("Music Player")
            return True
        return False
