import math
import pygame

from tilecraft.constants import Item

def DurabilityBar(durability, max_durability):
    durabilityPercent = math.floor((durability / max_durability) * 100)
    if durabilityPercent == 100:
        return None
    elif 75 < durabilityPercent <= 99:
        return "#00ff00"
    elif 50 < durabilityPercent <= 75:
        return "#ffff00"
    elif 25 < durabilityPercent <= 50:
        return "#ff8000"
    elif 5 < durabilityPercent <= 25:
        return "#ff0000"
    elif 0 < durabilityPercent <= 5:
        return "#000000"

def RenderDurabilityBar(display, x, y, durability, max_durability):
    colour = DurabilityBar(durability, max_durability)
    if colour is not None:
        pygame.draw.rect(display, (0, 0, 0), (x + 5, y + 72, 72, 5))
        pygame.draw.rect(display, colour, (x + 5, y + 72, math.floor(72 * durability / max_durability), 5))


#Convert Numbers to Roman Numerals
def DecimalToRoman(num):
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


#Info Box for Items (with and without enchantments)
def TextBox(display: pygame.Surface, item: Item, x: int, y: int, font: pygame.font.Font):
    try:
        if item is not None: #Check to prevent crashes
            length_list = [len(item.name * 15)]
            if item.enchantments is not None:
                width = (1 + len(item.enchantments)) * 37
                for i in item.enchantments:
                    length_list.append(len(str(i[0]) + DecimalToRoman(str(i[1]))) * 15)
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
                if item.enchantments is not None:
                    for i in range(len(item.enchantments)):
                        display.blit(font.render(f'{item.enchantments[i][0]} {DecimalToRoman(item.enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
                display.blit(font.render(f"Durability: {item.durability}/{item.max_durability}", False, (175, 175, 175)), (x + 15, y + width - 20))
            else: #EVERYTHING ELSE
                if item.enchantments is not None:
                    for i in range(len(item.enchantments)):
                        display.blit(font.render(f'{item.enchantments[i][0]} {DecimalToRoman(item.enchantments[i][1])}', False, (175, 175, 175)), (x + 15, y + 15 + (i + 1) * 22))
    except IndexError:
        pass
