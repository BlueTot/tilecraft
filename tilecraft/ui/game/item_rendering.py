import math
from typing import Optional
import pygame

from tilecraft.constants import Item

def durability_colour(durability: int, max_durability: int) -> Optional[str]:
    """
        Get the durability colour given a tool's durability and max durability
    """
    percentage = math.floor((durability / max_durability) * 100)
    if percentage == 100:
        return None
    elif 75 < percentage <= 99:
        return "#00ff00"
    elif 50 < percentage <= 75:
        return "#ffff00"
    elif 25 < percentage <= 50:
        return "#ff8000"
    elif 5 < percentage <= 25:
        return "#ff0000"
    elif 0 < percentage <= 5:
        return "#000000"
    elif percentage <= 0:
        return None
    
    raise ValueError("Something bad went wrong")


def render_durability_bar(display: pygame.Surface, x: int, y: int, durability: int, max_durability: int) -> None:
    """
        Render a durability bar to the `display` at coordiantes x, y
    """
    colour = durability_colour(durability, max_durability)
    if colour is not None:
        pygame.draw.rect(display, (0, 0, 0), (x + 5, y + 72, 72, 5))
        pygame.draw.rect(display, colour, (x + 5, y + 72, math.floor(72 * durability / max_durability), 5))


def decimal_to_roman(num: str | int) -> str:
    """
        Convert Numbers to Roman Numerals
    """
    num = int(num)
    nums = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
    symbols = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12
    roman_value = ""
    while num:
        div = num // nums[i]
        num %= nums[i]
        while div:
            roman_value += symbols[i]
            div -= 1
        i -= 1
    return roman_value


def render_info_box(display: pygame.Surface, item: Optional[Item], x: int, y: int, font: pygame.font.Font) -> None:
    """
        Info Box for Items (with and without enchantments)
    """
    try:
        if item is not None: #Check to prevent crashes
            length_list = [len(item.name * 15)]
            if item.is_enchanted:
                width = (1 + len(item.enchantments)) * 37
                for enchantment in item.enchantments:
                    length_list.append(len(str(enchantment.name) + decimal_to_roman(str(enchantment.level))) * 15)
            else:
                width = 37
            if item.durability is not None:
                width += 22
                length_list.append(len(f"Durability: {item.durability}/{item.max_durability}") * 15)
            length = max(length_list)
            if x + length > 750:
                x -= length
            if y + width > 750:
                y -= width
            pygame.draw.rect(display, (0, 0, 0), (x, y, length, width))
            display.blit(font.render(item.name, False, item.colour), (x + 15, y + 15))
            if item.durability is not None: #WITH DURABILITY
                for i, enchantment in enumerate(item.enchantments):
                    display.blit(
                        font.render(f'{enchantment.name} {decimal_to_roman(enchantment.level)}', False, (175, 175, 175)), 
                        (x + 15, y + 15 + (i + 1) * 22)
                    )
                display.blit(font.render(f"Durability: {item.durability}/{item.max_durability}", False, (175, 175, 175)), (x + 15, y + width - 20))
            else: #EVERYTHING ELSE
                for i, enchantment in enumerate(item.enchantments):
                    display.blit(
                        font.render(f'{enchantment.name} {decimal_to_roman(enchantment.level)}', False, (175, 175, 175)), 
                        (x + 15, y + 15 + (i + 1) * 22)
                    )
    except IndexError:
        pass
