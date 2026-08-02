from constants import ITEM_TYPES, Item

#Print Item List
def print_cheats(screen, name):
    screen.print("CODE   ITEM NAME")
    screen.print('-' * 25)
    for i in range(len(name)):
        screen.print((str(i) + ' ' * (7 - len(str(i))) + str(name[i])))

#/give command
def give(screen, item_id):
    item_id = item_id.replace(' ', '') #REMOVE WHITESPACES
    # CALCULATE CODE AND AMOUNT
    if ',' in item_id and item_id[-1] != ',':
        comma = item_id.index(',')
        code = item_id[0:comma]
        amount = item_id[comma + 1:len(item_id)]
    else:
        code = item_id
        amount = 1
    try:
        code = int(code)
        amount = int(amount)
        length = len(list(ITEM_TYPES.keys())) - 1
        if 0 <= code <= length:
            add_item = Item(list(ITEM_TYPES.keys())[code], amount, None, list(ITEM_TYPES.values())[code].max_durability)
            return add_item
        else:
            screen.print(f"Please enter a number between 0 and {length}.")
            return None
    except ValueError:
        screen.print("Invalid Input")

#/teleport command
def teleport(screen, internalX, internalY, coords):
    if ',' in coords:
        try:
            x = coords[0:coords.index(',')]
            y = coords[coords.index(',') + 1:]
            x = int(x)
            y = int(y)
            internalX = x
            internalY = y
        except ValueError:
            screen.print("Invalid input")
    else:
        screen.print("Invalid input")
    return internalX, internalY

#/enchant command
def enchant(screen, player, enchantment):
    if player.hotbar_item is not None:
        enchantment = enchantment.replace(' ', '') #remove whitespaces
        if ',' in enchantment and enchantment[-1] != ',':
            comma = enchantment.index(',')
            name = enchantment[0:comma]
            lvl = enchantment[comma + 1:len(enchantment)]
            try:
                lvl = int(lvl)
                if name == "protection" or name == "efficiency" or name == "unbreaking":
                    enchantments = player.hotbar_item.enchantments
                    if enchantments is not None:
                        enchantments.append([name.capitalize(), lvl])
                    else:
                        enchantments = [[name.capitalize(), lvl]]
                    return Item(player.hotbar_item.name, player.hotbar_item.number, enchantments, player.hotbar_item.durability)
            except ValueError:
                screen.print("Invalid Input")
    else:
        screen.print("No item in selected hotbar slot")
    return None

#/experience command
def experience(screen, player, level):
    try:
        level = int(level)
        if level > 0:
            player.experience_points += level
    except ValueError:
        screen.print("Invalid Input")