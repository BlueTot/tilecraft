from tilecraft.inventory import Inventory, Armour
from tilecraft.items import Enchantment


class AdvancementsManager:
    """
        Manages all advancement statuses and updates them
    """

    def __init__(self) -> None:
        self.__advancements: list[str] = []


    @property
    def completed_advancements(self) -> list[str]:
        """ Return the list of completed advancements """
        return self.__advancements


    def update(self, inventory: Inventory, armour: Armour, dimension: str) -> list[str]:
        """ Update the advancements list, returning the list of newly unlocked advancements """

        name_list = [item.name if item is not None else None for item in inventory.items]
        enchantments_list = [item.enchantments if item is not None else None for item in inventory.items]
        armour_enchantment_list = [item.enchantments if item is not None else None for item in armour.items]
        newly_unlocked = []

        if "Stone Age" not in self.__advancements and "Cobblestone" in name_list: #Get Cobblestone
            self.__advancements.append("Stone Age")
            newly_unlocked.append("Stone Age")

        if "Getting an Upgrade" not in self.__advancements and "Stone Pickaxe" in name_list: #Get a Stone Pickaxe
            self.__advancements.append("Getting an Upgrade")
            newly_unlocked.append("Getting an Upgrade")

        if "Into the Depths" not in self.__advancements and dimension == "Underground": #Enter the underground
            newly_unlocked.append("Into the Depths")
            self.__advancements.append("Into the Depths")

        if "Acquire Hardware" not in self.__advancements and "Iron Ingot" in name_list: #Get an Iron Ingot
            self.__advancements.append("Acquire Hardware")
            newly_unlocked.append("Acquire Hardware")

        if "Isn't it Iron Pick" not in self.__advancements and "Iron Pickaxe" in name_list: #Get an Iron Pickaxe
            self.__advancements.append("Isn't it Iron Pick")
            newly_unlocked.append("Isn't it Iron Pick")

        if ("Suit Up" not in self.__advancements) and ("Tier 1 Iron Plate" in name_list or "Tier 2 Iron Plate" in name_list or "Tier 3 Iron Plate" in name_list): #Get Iron Armour
            self.__advancements.append("Suit Up")
            newly_unlocked.append("Suit Up")

        if "Diamonds!" not in self.__advancements and "Diamond" in name_list: #Get Diamonds
            self.__advancements.append("Diamonds!")
            newly_unlocked.append("Diamonds!")

        if ("Cover Me with Diamonds" not in self.__advancements) and ("Tier 1 Diamond Plate" in name_list or "Tier 2 Diamond Plate" in name_list or "Tier 3 Diamond Plate" in name_list): #Get Diamond Armour
            self.__advancements.append("Cover Me with Diamonds")
            newly_unlocked.append("Cover Me with Diamonds")

        if "Ice Bucket Challenge" not in self.__advancements and "Obsidian" in name_list: #Get Obsidian
            self.__advancements.append("Ice Bucket Challenge")
            newly_unlocked.append("Ice Bucket Challenge")

        if "We Need to Go Deeper" not in self.__advancements and dimension == 'Nether': #Go to the Nether
            newly_unlocked.append("We Need to Go Deeper")
            self.__advancements.append("We Need to Go Deeper")

        for enchantments in (enchantments_list + armour_enchantment_list):
            if enchantments is not None and len(enchantments) > 0 and "Enchanter" not in self.__advancements: #Get an enchanted tool or armour piece
                self.__advancements.append("Enchanter")
                newly_unlocked.append("Enchanter")
                break

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

        if max_t1 and max_t2 and max_t3 and "God Gear" not in self.__advancements: #Get a full set of Protection V Unbreaking III Diamond Armour
            self.__advancements.append("God Gear")
            newly_unlocked.append("God Gear")

        return newly_unlocked


    def check_music_player(self) -> bool:
        """
            Update the music player advancement's status, returning True if freshly unlocked
        """
        if "Music Player" not in self.__advancements:  # Music Player: Play Pigstep
            self.__advancements.append("Music Player")
            return True
        return False
