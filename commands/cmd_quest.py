#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
#
#  GodWars improvements copyright © 1995, 1996 by Richard Woolcock.
#
#  ROM 2.4 is copyright 1993-1998 Russ Taylor.  ROM has been brought to
#  you by the ROM consortium:  Russ Taylor (rtaylor@hypercube.org),
#  Gabrielle Taylor (gtaylor@hypercube.org), and Brian Moore (zump@rom.org).
#
#  Ported to Python by Davion of MudBytes.net using Miniboa
#  (https://code.google.com/p/miniboa/).
#
#  In order to use any part of this Merc Diku Mud, you must comply with
#  both the original Diku license in 'license.doc' as well the Merc
#  license in 'license.txt'.  In particular, you may not remove either of
#  these copyright notices.
#
#  Much time and thought has gone into this software, and you are
#  benefiting.  We hope that you share your changes too.  What goes
#  around, comes around.

import game_utils
import handler_game
import instance
import interp
import merc
import object_creator
import settings
import world_classes


def cmd_quest(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if arg1 and game_utils.str_cmp(arg1, "create"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to create new objects.\n")
            return

        if ch.quest == 0:
            ch.send("You must first earn some quest points.\n")
            return

        if not arg2:
            ch.send("Syntax: quest create <object> <field>\n"
                    "Object being one of: Light (10 QP), Weapon < type > (50 QP), Armor(30 QP),\n"
                    "Container(10 QP), Boat(10 QP), Fountain < type > (10 QP), Stake(10 QP).\n")
            return

        type_list = [("light", merc.ITEM_LIGHT, 10), ("weapon", merc.ITEM_WEAPON, 50), (["armor", "armour"], merc.ITEM_ARMOR, 20),
                     ("container", merc.ITEM_CONTAINER, 10), ("boat", merc.ITEM_BOAT, 10), ("fountain", merc.ITEM_FOUNTAIN, 10),
                     ("stake", merc.ITEM_STAKE, 10)]
        for (aa, bb, cc) in type_list:
            if game_utils.str_cmp(arg2, aa):
                add = bb
                value = 10
                break
        else:
            ch.cmd_quest("create")
            return

        if ch.quest < value:
            ch.send(f"You don't have the required {value} quest points.\n")
            return

        if merc.OBJ_VNUM_PROTOPLASM not in instance.item_templates:
            ch.send("Error...missing object, please inform an Immortal.\n")
            return

        item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PROTOPLASM], 25)
        item.weight = 1
        item.cost = 1000
        item.item_type = add

        if add == merc.ITEM_WEAPON:
            if not arg3:
                ch.send("Please specify weapon type: Slice, Stab, Slash, Whip, Claw, Blast, Pound,\n"
                        "Crush, Pierce, or Suck.\n")
                item.extract()
                return

            wpn_list = [("slice", merc.WPN_SLICE), ("stab", merc.WPN_STAB), ("slash", merc.WPN_SLASH), ("whip", merc.WPN_WHIP), ("claw", merc.WPN_CLAW),
                        ("blast", merc.WPN_BLAST), ("pound", merc.WPN_POUND), ("crush", merc.WPN_CRUSH), ("pierce", merc.WPN_PIERCE),
                        ("suck", merc.WPN_SUCK)]
            for (aa, bb) in wpn_list:
                if game_utils.str_cmp(arg3, aa):
                    item.value[3] = bb
                    break
            else:
                ch.cmd_quest("create weapon")
                item.extract()
                return

            item.value[1] = 10
            item.value[2] = 20
            item.level = 50
        elif add == merc.ITEM_FOUNTAIN:
            if not arg3:
                ch.send("Please specify fountain contents: Water, Beer, Wine, Ale, Darkale, Whisky,\n"
                        "Firebreather, Specialty, Slime, Milk, Tea, Coffee, Blood, Saltwater.\n")
                item.extract()
                return

            item_list = [("water", 0), ("beer", 1), ("wine", 2), ("ale", 3), ("darkale", 4), ("whisky", 5), ("firebreather", 7), ("specialty", 8),
                         ("slime", 9), ("milk", 10), ("tea", 11), ("coffee", 12), ("blood", 13), ("saltwater", 14)]
            for (aa, bb) in item_list:
                if game_utils.str_cmp(arg3, aa):
                    item.value[2] = bb
                    break
            else:
                ch.cmd_quest("create fountain")
                item.extract()
                return

            item.value[0] = 1000
            item.value[1] = 1000
        elif add == merc.ITEM_CONTAINER:
            item.value[0] = 999
        elif add == merc.ITEM_LIGHT:
            item.value[2] = -1
        elif add == merc.ITEM_ARMOR:
            item.value[0] = 15

        ch.quest -= value
        ch.put(item)
        item.quest.set_bit(merc.QUEST_FREENAME)
        item.questmaker = ch.name
        item.questowner = ch.name
        handler_game.act("You reach up into the air and draw out a ball of protoplasm.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n reaches up into the air and draws out a ball of protoplasm.", ch, item, None, merc.TO_ROOM)
        return

    if not arg1 or not arg2:
        ch.send("- - - - - - - - - - ----====[ QUEST ITEM COSTS ]====---- - - - - - - - - - -\n"
                "Create: Creates a new personalized object, costing between 10 and 50 QP.\n"
                "Name/Short/Long: Rename the object.  1 QP for all three.\n"
                "Protection: Sets AC on armour at 1 QP per point.\n"
                "Min/Max: Sets min/max damage on weapon at 1 QP per point.\n"
                "Weapon: Sets weapon type for 10 QP.\n"
                "Extra (add/remove): Glow(1/1), Hum(1/1), Invis(1/1), Anti-Good(1/10),\n"
                "                    Anti-Neutral(1/10), Anti-Evil(1/10), Loyal(10/1).\n"
                "Wear: Select location, costs 20 QP's.  Type 'quest <obj> wear' to see locations.\n"
                "Power: Spell power for spell weapons.  Costs 1 QP per power point.\n"
                "Spell: Spell weapons or affect.  Costs 50 QP.\n"
                "Transporter: Future transportation to that room.  Costs 50 QP.\n"
                "Special: Set activate/twist/press/pull flags.\n"
                "You-in/You-out/Other-in/Other-out: Renames for transporter actions.\n"
                "You-wear/You-remove/You-use: What you see when you wear/remove/use.\n"
                "Other-wear/Other-remove/Other-use: What others see when you wear/remove/use.\n"
                "Weight: Set objects weight to 1.  Costs 10 QP.\n"
                "Str, Dex, Int, Wis, Con... max =   3 each, at  20 quest points per +1 stat.\n"
                "Hp, Mana, Move............ max =  25 each, at   5 quest points per point.\n"
                "Hitroll, Damroll.......... max =   5 each, at  30 quest points per point.\n"
                "Ac........................ max = -25,      at  10 points per point.\n"
                "- - - - - - - - - - ----====[ QUEST ITEM COSTS ]====---- - - - - - - - - - -\n")
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    if item.item_type in [merc.ITEM_QUEST, merc.ITEM_AMMO, merc.ITEM_EGG, merc.ITEM_VOODOO, merc.ITEM_MONEY, merc.ITEM_TREASURE,
                          merc.ITEM_TOOL, merc.ITEM_SYMBOL, merc.ITEM_PAGE] or item.flags.artifact:
        ch.send("You cannot quest-change that item.\n")
        return

    if not ch.is_immortal() and (not item.questowner or not game_utils.str_cmp(ch.name, item.questowner)):
        ch.send("You can only change an item you own.\n")
        return

    # Snarf the value (which need not be numeric).
    value = int(arg3) if arg3.isdigit() else 0

    if game_utils.str_cmp(arg2, "protection"):
        if not arg3:
            ch.send("How much armor class?\n")
            return

        if item.item_type != merc.ITEM_ARMOR:
            ch.send("That item is not armor.\n")
            return

        if item.item_type == merc.ITEM_ARMOR and (value + item.value[0]) > 15:
            if item.value[0] < 15:
                ch.send(f"The armor class can be increased by {15 - item.value[0]}.\n")
            else:
                ch.send("The armor class cannot be increased any further.\n")
            return

        if ch.quest < value:
            ch.send("You don't have enough quest points.\n")
            return

        item.value[0] += value
        if item.value < 0:
            item.value[0] = 0

        ch.send("Ok.\n")
        if value < 1:
            value = 1

        ch.quest -= value
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "min"):
        if not arg3:
            ch.send("How much min damage?\n")
            return

        if item.item_type != merc.ITEM_WEAPON:
            ch.send("That item is not a weapon.\n")
            return

        if item.item_type == merc.ITEM_WEAPON and (value + item.value[1]) > 10:
            if item.value[1] < 10:
                ch.send(f"The minimum damage can be increased by {10 - item.value[1]}.\n")
            else:
                ch.send("The minimum damage cannot be increased any further.\n")
            return

        if ch.quest < value:
            ch.send("You don't have enough quest points.\n")
            return

        item.value[1] += value
        if item.value[1] < 1:
            item.value[1] = 1

        ch.send("Ok.\n")
        if value < 1:
            value = 1

        ch.quest -= value
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "max"):
        if not arg3:
            ch.send("How much max damage?\n")
            return

        if item.item_type != merc.ITEM_WEAPON:
            ch.send("That item is not a weapon.\n")
            return

        if item.item_type == merc.ITEM_WEAPON and (value + item.value[2]) > 20:
            if item.value[2] < 20:
                ch.send(f"The maximum damage can be increased by {20 - item.value[2]}.\n")
            else:
                ch.send("The maximum damage cannot be increased any further.\n")
            return

        if ch.quest < value:
            ch.send("You don't have enough quest points.\n")
            return

        item.value[2] += value
        if item.value[2] < 0:
            item.value[2] = 0

        ch.send("Ok.\n")
        if value < 1:
            value = 1

        ch.quest -= value
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "weapon"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to change weapon types.\n")
            return

        if item.item_type == merc.ITEM_WEAPON:
            if item.flags.relic:
                ch.send("Not on a relic.\n")
                return

            if ch.quest < 10:
                ch.send("You don't have enough quest points.\n")
                return

            if not arg3:
                ch.send("Please specify weapon type: Slice, Stab, Slash, Whip, Claw, Blast, Pound,\n"
                        "Crush, Pierce, or Suck.\n")
                return

            wpn_list = [("slice", merc.WPN_SLICE), ("stab", merc.WPN_STAB), ("slash", merc.WPN_SLASH), ("whip", merc.WPN_WHIP), ("claw", merc.WPN_CLAW),
                        ("blast", merc.WPN_BLAST), ("pound", merc.WPN_POUND), ("crush", merc.WPN_CRUSH), ("pierce", merc.WPN_PIERCE),
                        ("suck", merc.WPN_SUCK)]
            for (aa, bb) in wpn_list:
                if game_utils.str_cmp(arg3, aa):
                    value = bb
                    break
            else:
                ch.send("Please specify weapon type: Slice, Stab, Slash, Whip, Claw, Blast, Pound,\n"
                        "Crush, Pierce, or Suck.\n")
                return

            if item.value[3] == value:
                ch.send("It is already that weapon type.\n")
                return

            item.value[3] = value
            ch.quest -= 10
            ch.send("Ok.\n")
            item.questmaker = ch.name
        else:
            ch.send("That item is not a weapon.\n")
        return

    if game_utils.str_cmp(arg2, "extra"):
        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if not arg3:
            ch.send("Enter one of: Glow, Hum, Invis, Anti-good, Anti-evil, Anti-neutral, Loyal,\n"
                    "Silver.\n")
            return

        if game_utils.str_cmp(arg3, "glow"):
            value = item.flags.glow
            add = 1
            remove = 1
        elif game_utils.str_cmp(arg3, "hum"):
            value = item.flags.hum
            add = 1
            remove = 1
        elif game_utils.str_cmp(arg3, "invis"):
            value = item.flags.invis
            add = 1
            remove = 1
        elif game_utils.str_cmp(arg3, "anti-good"):
            value = item.flags.anti_good
            add = 1
            remove = 10
        elif game_utils.str_cmp(arg3, "anti-evil"):
            value = item.flags.anti_evil
            add = 1
            remove = 10
        elif game_utils.str_cmp(arg3, "anti-neutral"):
            value = item.flags.anti_neutral
            add = 1
            remove = 10
        elif game_utils.str_cmp(arg3, "loyal"):
            value = item.flags.loyal
            add = 10
            remove = 1
        elif game_utils.str_cmp(arg3, "silver"):
            value = item.flags.silver
            add = 100
            remove = 0
        else:
            ch.send("Enter one of: Glow, Hum, Invis, Anti-good, Anti-evil, Anti-neutral, Loyal,\n"
                    "Silver.\n")
            return

        if game_utils.str_cmp(arg3, "silver"):
            if item.flags.silver:
                ch.send("That item is already silver.\n")
                return

            if ch.quest < add:
                ch.send(f"Sorry, you need {add} quest points to set that flag.\n")
                return

            ch.quest -= add
            item.flags.silver = True
        elif value:
            if ch.quest < remove:
                ch.send(f"Sorry, you need {remove} quest points to remove that flag.\n")
                return

            ch.quest -= remove
            value = False
        else:
            if ch.quest < add:
                ch.send(f"Sorry, you need {add} quest points to set that flag.\n")
                return

            ch.quest -= add
            value = True

        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "wear"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to change object wear locations.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if not arg3:
            ch.send("Wear location can be from: Finger, Neck, Body, Head, Legs, Hands, Arms,\n"
                    "About, Waist, Wrist, Hold, Face.\n")
            return

        if game_utils.str_cmp(arg3, "finger"):
            value = merc.ITEM_WEAR_FINGER
        elif game_utils.str_cmp(arg3, "neck"):
            value = merc.ITEM_WEAR_NECK
        elif game_utils.str_cmp(arg3, "body"):
            value = merc.ITEM_WEAR_BODY
        elif game_utils.str_cmp(arg3, "head"):
            value = merc.ITEM_WEAR_HEAD
        elif game_utils.str_cmp(arg3, "legs"):
            value = merc.ITEM_WEAR_LEGS
        elif game_utils.str_cmp(arg3, "feet"):
            value = merc.ITEM_WEAR_FEET
        elif game_utils.str_cmp(arg3, "hands"):
            value = merc.ITEM_WEAR_HANDS
        elif game_utils.str_cmp(arg3, "arms"):
            value = merc.ITEM_WEAR_ARMS
        elif game_utils.str_cmp(arg3, "about"):
            value = merc.ITEM_WEAR_ABOUT
        elif game_utils.str_cmp(arg3, "waist"):
            value = merc.ITEM_WEAR_WAIST
        elif game_utils.str_cmp(arg3, "wrist"):
            value = merc.ITEM_WEAR_WRIST
        elif game_utils.str_cmp(arg3, "hold"):
            value = merc.ITEM_WIELD
        elif game_utils.str_cmp(arg3, "face"):
            value = merc.ITEM_WEAR_FACE
        else:
            ch.send("Wear location can be from: Finger, Neck, Body, Head, Legs, Hands, Arms,\n"
                    "About, Waist, Wrist, Hold, Face.\n")
            return

        if item.flags.take:
            value += 1

        if item.wear_flags == value or item.wear_flags == (value + 1):
            handler_game.act("But $p is already worn in that location!", ch, item, None, merc.TO_CHAR)
            return

        if value != merc.ITEM_WIELD and value != (merc.ITEM_WIELD + 1) and item.item_type == merc.ITEM_WEAPON:
            handler_game.act("You can only HOLD a weapon.", ch, item, None, merc.TO_CHAR)
            return

        if ch.quest < 20 and not (item.vnum == 30037 and item.wear_flags == 1):
            ch.send("It costs 20 quest points to change a location.\n")
            return

        if not (item.vnum == 30037 and item.wear_flags == 1):
            ch.quest -= 20

        item.wear_flags = value
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "replacespell"):
        if item.flags.relic and not ch.is_demon():
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if not arg3:
            ch.send("Spell weapons: Acid, Dark, Holy, Vampiric, Flaming, Electrified, Poisonous.\n"
                    "Spell affects: Blind, Seeinvis, Fly,Infravision, Invis, Passdoor, Protection,\n"
                    "Sanct, Sneak, Shockshield,Fireshield, Iceshield, Acidshield, Seehidden.\n")
            return

        spl_list = [("acid", 1, True), ("dark", 4, True), ("holy", 30, True), ("vampiric", 34, True), ("flaming", 37, True), ("electrified", 48, True),
                    ("poisonous", 53, True), ("infravision", 1, False), ("seeinvis", 2, False), ("fly", 3, False), ("blind", 4, False),
                    ("invis", 5, False), ("passdoor", 6, False), ("protection", 7, False), ("sanct", 8, False), ("sneak", 9, False),
                    ("shockshield", 10, False), ("fireshield", 11, False), ("iceshield", 12, False), ("acidshield", 13, False), ("seehidden", 60, False)]
        for (aa, bb, cc) in spl_list:
            if game_utils.str_cmp(arg3, aa):
                weapon = 0 if not cc else cc
                affect = 0 if not cc else cc
                break
        else:
            ch.send("Spell weapons: Dark, Holy, Vampiric, Flaming, Electrified, Poisonous.\n"
                    "Spell affects: Blind, Seeinvis, Fly,Infravision, Invis, Passdoor, Protection,\n"
                    "Sanct, Sneak, Shockshield, Fireshield, Iceshield, Acidshield, Seehidden.\n")
            return

        if item.item_type != merc.ITEM_WEAPON and weapon > 0:
            ch.send("You can only put that power on a weapon.\n")
            return
        elif item.item_type not in [merc.ITEM_WEAPON, merc.ITEM_ARMOR] and affect > 0:
            ch.send("You can only put that power on a weapon or a piece of armour.\n")
            return

        if ch.quest < 50:
            ch.send("It costs 50 quest points to create a spell weapon or affect.\n")
            return

        if weapon > 0:
            if item.value[0] >= 1000:
                item.value[0] = ((item.value[0] // 1000) * 1000)
            else:
                item.value[0] = 0
            item.value[0] += weapon
        elif affect > 0:
            if item.item_type == merc.ITEM_WEAPON:
                if item.value[0] >= 1000:
                    item.value[0] -= ((item.value[0] // 1000) * 1000)
                item.value[0] += (affect * 1000)
            elif item.item_type == merc.ITEM_ARMOR:
                item.value[3] = affect

        ch.quest -= 50
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "spell"):
        if item.flags.relic and not ch.is_demon():
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if not arg3:
            ch.send("Spell weapons: Acid, Dark, Holy, Vampiric, Flaming, Electrified, Poisonous.\n"
                    "Spell affects: Blind, Seeinvis, Fly, Infravision, Invis, Passdoor, Protection,\n"
                    "Sanct, Sneak, Shockshield, Fireshield, Iceshield, Acidshield, Seehidden.\n")
            return

        spl_list = [("acid", 1, True), ("dark", 4, True), ("holy", 30, True), ("vampiric", 34, True), ("flaming", 37, True), ("electrified", 48, True),
                    ("poisonous", 53, True), ("infravision", 1, False), ("seeinvis", 2, False), ("fly", 3, False), ("blind", 4, False),
                    ("invis", 5, False), ("passdoor", 6, False), ("protection", 7, False), ("sanct", 8, False), ("sneak", 9, False),
                    ("shockshield", 10, False), ("fireshield", 11, False), ("iceshield", 12, False), ("acidshield", 13, False), ("seehidden", 60, False)]
        for (aa, bb, cc) in spl_list:
            if game_utils.str_cmp(arg3, aa):
                weapon = 0 if not cc else cc
                affect = 0 if not cc else cc
                break
        else:
            ch.send("Spell weapons: Acid, Dark, Holy, Vampiric, Flaming, Electrified, Poisonous.\n"
                    "Spell affects: Blind, Seeinvis, Fly, Infravision, Invis, Passdoor, Protection,\n"
                    "Sanct, Sneak, Shockshield, Fireshield, Iceshield, Acidshield, Seehidden.\n")
            return

        if item.item_type != merc.ITEM_WEAPON and weapon > 0:
            ch.send("You can only put that power on a weapon.\n")
            return
        elif item.item_type not in [merc.ITEM_WEAPON, merc.ITEM_ARMOR] and affect > 0:
            ch.send("You can only put that power on a weapon or a piece of armour.\n")
            return

        if ch.quest < 50:
            ch.send("It costs 50 quest points to create a spell weapon or affect.\n")
            return

        if weapon > 0:
            if item.value[0] - ((item.value[0] // 1000) * 1000) != 0:
                ch.send("That item already has a spell weapon power.  If you wish to replace the \n"
                        "current spell power, use the format: quest <object> replacespell <spell>.\n")
                return

            if item.value[0] >= 1000:
                item.value[0] = ((item.value[0] // 1000) * 1000)
            else:
                item.value[0] = 0
            item.value[0] += weapon
        elif affect > 0:
            if item.item_type == merc.ITEM_WEAPON:
                if item.value[0] >= 1000:
                    ch.send("That item already has a spell affect power.  If you wish to replace the \n"
                            "current spell power, use the format: quest <object> replacespell <spell>.\n")
                    return

                if item.value[0] >= 1000:
                    item.value[0] -= ((item.value[0] // 1000) * 1000)

                item.value[0] += (affect * 1000)
            elif item.item_type == merc.ITEM_ARMOR:
                if item.value[3] > 0:
                    ch.send("That item already has a spell affect power.  If you wish to replace the\n"
                            "current spell power, use the format: quest <object> replacespell <spell>.\n")
                    return

                item.value[3] = affect

        ch.quest -= 50
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "power"):
        if not arg3:
            ch.send("Please specify the amount of power.\n")
            return

        if item.item_type != merc.ITEM_WEAPON:
            ch.send("Only weapons have a spell power.\n")
            return

        if item.level >= 50:
            ch.send("This weapon can hold no more spell power.\n")
            return

        if value + item.level > 50:
            ch.send(f"You can only add {50 - item.level} more spell power to this weapon.\n")
            return

        if ch.quest < value:
            ch.send("You don't have enough quest points to increase the spell power.\n")
            return

        item.level += value
        if item.level < 0:
            item.level = 0

        if value < 1:
            value = 1

        ch.quest -= value
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "weight"):
        if item.weight < 2:
            ch.send("You cannot reduce the weight of this item any further.\n")
            return

        if ch.quest < 10:
            ch.send("It costs 10 quest point to remove the weight of an object.\n")
            return

        item.weight = 1
        ch.quest -= 10
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "transporter"):
        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("This item is already a transporter.\n")
            return
        elif item.spectype.is_set(merc.SITEM_TRANSPORTER):
            ch.send("This item is already a teleporter.\n")
            return
        elif item.spectype.is_set(merc.SITEM_SPELL):
            ch.send("This item is already a spell caster.\n")
            return
        elif item.spectype.is_set(merc.SITEM_OBJECT):
            ch.send("This item is already an object creator.\n")
            return
        elif item.spectype.is_set(merc.SITEM_MOBILE):
            ch.send("This item is already a creature creator.\n")
            return
        elif item.spectype.is_set(merc.SITEM_ACTION):
            ch.send("This item is already a commanding device.\n")
            return

        if ch.quest < 50:
            ch.send("It costs 50 quest point to create a transporter.\n")
            return

        item.spectype.set_bit(merc.SITEM_ACTIVATE)
        item.spectype.set_bit(merc.SITEM_TELEPORTER)
        item.specpower = ch.in_room.vnum
        ch.quest -= 50
        ch.send("Ok.\n")
        item.questmaker = ch.name
        item.chpoweron = "You transform into a fine mist and seep into the ground."
        item.victpoweron = "$n transforms into a fine mist and seeps into the ground."
        item.chpoweroff = "You seep up from the ground and reform your body."
        item.victpowreoff = "A fine mist seeps up from the ground and reforms into $n."
        item.chpoweruse = "You activate $p."
        item.victpoweruse = "$n activates $p."
        return

    if game_utils.str_cmp(arg2, "retransporter"):
        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if not item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("This item is not a transporter.\n")
            return
        elif item.spectype.is_set(merc.SITEM_TRANSPORTER):
            ch.send("This item is already a teleporter.\n")
            return
        elif item.spectype.is_set(merc.SITEM_SPELL):
            ch.send("This item is already a spell caster.\n")
            return
        elif item.spectype.is_set(merc.SITEM_OBJECT):
            ch.send("This item is already an object creator.\n")
            return
        elif item.spectype.is_set(merc.SITEM_MOBILE):
            ch.send("This item is already a creature creator.\n")
            return
        elif item.spectype.is_set(merc.SITEM_ACTION):
            ch.send("This item is already a commanding device.\n")
            return

        if ch.quest < 50:
            ch.send("It costs 50 quest point to create a transporter.\n")
            return

        item.spectype.set_bit(merc.SITEM_ACTIVATE)
        item.spectype.set_bit(merc.SITEM_TELEPORTER)
        item.specpower = ch.in_room.vnum
        ch.quest -= 50
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if not arg3:
        ch.send("- - - - - - - - - - ----====[ QUEST ITEM COSTS ]====---- - - - - - - - - - -\n"
                "Create: Creates a new personalized object, costing between 10 and 50 QP.\n"
                "Name/Short/Long: Rename the object.  1 QP for all three.\n"
                "Protection: Sets AC on armour at 1 QP per point.\n"
                "Min/Max: Sets min/max damage on weapon at 1 QP per point.\n"
                "Weapon: Sets weapon type for 10 QP.\n"
                "Extra (add/remove): Glow(1/1), Hum(1/1), Invis(1/1), Anti-Good(1/10),\n"
                "                    Anti-Neutral(1/10), Anti-Evil(1/10), Loyal(10/1).\n"
                "Wear: Select location, costs 20 QP's.  Type 'quest <obj> wear' to see locations.\n"
                "Power: Spell power for spell weapons.  Costs 1 QP per power point.\n"
                "Spell: Spell weapons or affect.  Costs 50 QP.\n"
                "Transporter: Future transportation to that room.  Costs 50 QP.\n"
                "Special: Set activate/twist/press/pull flags.\n"
                "You-in/You-out/Other-in/Other-out: Renames for transporter actions.\n"
                "You-wear/You-remove/You-use: What you see when you wear/remove/use.\n"
                "Other-wear/Other-remove/Other-use: What others see when you wear/remove/use.\n"
                "Weight: Set objects weight to 1.  Costs 10 QP.\n"
                "Str, Dex, Int, Wis, Con... max =   3 each, at  20 quest points per +1 stat.\n"
                "Hp, Mana, Move............ max =  25 each, at   5 quest points per point.\n"
                "Hitroll, Damroll.......... max =   5 each, at  30 quest points per point.\n"
                "Ac........................ max = -25,      at  10 points per point.\n"
                "- - - - - - - - - - ----====[ QUEST ITEM COSTS ]====---- - - - - - - - - - -\n")
        return

    if item.item_type != merc.ITEM_BOOK:
        if game_utils.str_cmp(arg2, ["hitroll", "hit"]):
            ch.oset_affect(item, value, merc.APPLY_HITROLL, True)
            return
        elif game_utils.str_cmp(arg2, ["damroll", "dam"]):
            ch.oset_affect(item, value, merc.APPLY_DAMROLL, True)
            return
        elif game_utils.str_cmp(arg2, ["armor", "ac"]):
            ch.oset_affect(item, value, merc.APPLY_AC, True)
            return
        elif game_utils.str_cmp(arg2, ["hitpoints", "hp"]):
            ch.oset_affect(item, value, merc.APPLY_HIT, True)
            return
        elif game_utils.str_cmp(arg2, "mana"):
            ch.oset_affect(item, value, merc.APPLY_MANA, True)
            return
        elif game_utils.str_cmp(arg2, ["move", "movement"]):
            ch.oset_affect(item, value, merc.APPLY_MOVE, True)
            return
        elif game_utils.str_cmp(arg2, ["str", "strength"]):
            ch.oset_affect(item, value, merc.APPLY_STR, True)
            return
        elif game_utils.str_cmp(arg2, ["dex", "dexterity"]):
            ch.oset_affect(item, value, merc.APPLY_DEX, True)
            return
        elif game_utils.str_cmp(arg2, ["int", "intelligence"]):
            ch.oset_affect(item, value, merc.APPLY_INT, True)
            return
        elif game_utils.str_cmp(arg2, ["wis", "wisdom"]):
            ch.oset_affect(item, value, merc.APPLY_WIS, True)
            return
        elif game_utils.str_cmp(arg2, ["con", "constitution"]):
            ch.oset_affect(item, value, merc.APPLY_CON, True)
            return

    if game_utils.str_cmp(arg2, "name"):
        value = 1

        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to rename objects.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if not item.quest.is_set(merc.QUEST_NAME) and (item.quest.is_set(merc.QUEST_SHORT) or item.quest.is_set(merc.QUEST_LONG)):
            item.quest.set_bit(merc.QUEST_NAME)
            value = 0
        elif item.quest.is_set(merc.QUEST_NAME):
            item.quest.rem_bit(merc.QUEST_SHORT)
            item.quest.rem_bit(merc.QUEST_LONG)
        else:
            item.quest.set_bit(merc.QUEST_NAME)

        if item.quest.is_set(merc.QUEST_FREENAME):
            value = 0
            item.quest.rem_bit(merc.QUEST_FREENAME)

        if ch.quest < value:
            ch.send("It costs 1 quest point to rename an object.\n")
            return

        if len(arg3) < 3:
            ch.send("Name should be at least 3 characters long.\n")
            return

        ch.quest -= value
        item.name = arg3.lower()
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "short"):
        value = 1

        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to rename objects.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if not item.quest.is_set(merc.QUEST_SHORT) and (item.quest.is_set(merc.QUEST_NAME) or item.quest.is_set(merc.QUEST_LONG)):
            item.quest.set_bit(merc.QUEST_SHORT)
            value = 0
        elif item.quest.is_set(merc.QUEST_SHORT):
            item.quest.rem_bit(merc.QUEST_NAME)
            item.quest.rem_bit(merc.QUEST_LONG)
        else:
            item.quest.set_bit(merc.QUEST_SHORT)

        if item.quest.is_set(merc.QUEST_FREENAME):
            value = 0
            item.quest.rem_bit(merc.QUEST_FREENAME)

        if ch.quest < value:
            ch.send("It costs 1 quest point to rename an object.\n")
            return

        if len(arg3) < 3:
            ch.send("Name should be at least 3 characters long.\n")
            return

        ch.quest -= value
        item.short_descr = arg3
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "long"):
        value = 1

        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to rename objects.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if not item.quest.is_set(merc.QUEST_LONG) and (item.quest.is_set(merc.QUEST_NAME) or item.quest.is_set(merc.QUEST_SHORT)):
            item.quest.set_bit(merc.QUEST_LONG)
            value = 0
        elif item.quest.is_set(merc.QUEST_LONG):
            item.quest.rem_bit(merc.QUEST_NAME)
            item.quest.rem_bit(merc.QUEST_SHORT)
        else:
            item.quest.set_bit(merc.QUEST_LONG)

        if item.quest.is_set(merc.QUEST_FREENAME):
            value = 0
            item.quest.rem_bit(merc.QUEST_FREENAME)

        if ch.quest < value:
            ch.send("It costs 1 quest point to rename an object.\n")
            return

        if len(arg3) < 3:
            ch.send("Name should be at least 3 characters long.\n")
            return

        ch.quest -= value
        item.description = arg3[0].upper() + arg3[1:]
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "ed"):
        argument, arg3 = game_utils.read_word(argument)

        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not allowed to rename objects.\n")
            return

        if item.quest.relic:
            ch.send("Not on a relic.\n")
            return

        if not argument:
            ch.send("Syntax: quest <object> ed <keyword> <string>\n")
            return

        edd = world_classes.ExtraDescrData(keyword=arg3, description=argument[0].upper() + argument[1:] + "\n")
        item.extra_descr.append(edd)
        ch.send("Ok.\n")
        item.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "special"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if not arg3:
            ch.send("Please enter ACTIVATE, TWIST, PRESS or PULL.\n")
            return

        arg_list = [("press", merc.SITEM_PRESS), ("activate", merc.SITEM_ACTIVATE), ("pull", merc.SITEM_PULL), ("twist", merc.SITEM_TWIST)]
        for (aa, bb) in arg_list:
            if game_utils.str_cmp(arg3, aa):
                item.spectype.rem_bit(merc.SITEM_ACTIVATE)
                item.spectype.rem_bit(merc.SITEM_TWIST)
                item.spectype.rem_bit(merc.SITEM_PRESS)
                item.spectype.rem_bit(merc.SITEM_PULL)
                item.spectype.set_bit(bb)
                break
        else:
            ch.send("Please enter ACTIVATE, TWIST, PRESS or PULL.\n")
            return

        ch.send(f"{arg3[0].upper() + arg3[1:].lower()} flag set.\n")
        return

    if game_utils.str_cmp(arg2, ["you-out", "you-wear"]):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.quest.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if game_utils.str_cmp(arg2, "you-out") and not item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("That item is not a transporter.\n")
            return

        if game_utils.str_cmp(arg2, "you-wear") and item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("Not on a transporter.\n")
            return

        buf = item.chpoweron if item.chpoweron else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweron = ""
        elif item.chpowron and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweron = buf + "\n" + arg3
        else:
            item.chpoweron = arg3
        ch.send("Ok.\n")
    elif game_utils.str_cmp(arg2, ["other-out", "other-wear"]):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if game_utils.str_cmp(arg2, "other-out") and not item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("That item is not a transporter.\n")
            return

        if game_utils.str_cmp(arg2, "other-wear") and item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("Not on a transporter.\n")
            return

        buf = item.victpoweron if item.victpoweron else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweron = ""
        elif item.victpoweron and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweron = buf + "\n" + arg3
        else:
            item.victpoweron = arg3
        ch.send("Ok.\n")
    elif game_utils.str_cmp(arg2, ["you-in", "you-remove"]):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if game_utils.str_cmp(arg2, "you-in") and not item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("That item is not a transporter.\n")
            return

        if game_utils.str_cmp(arg2, "you-remove") and item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("Not on a transporter.\n")
            return

        buf = item.chpoweroff if item.chpoweroff else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweroff = ""
        elif item.chpoweroff and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweroff = buf + "\n" + arg3
        else:
            item.chpoweroff = arg3
        ch.send("Ok.\n")
    elif game_utils.str_cmp(arg2, ["other-in", "other-remove"]):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        if game_utils.str_cmp(arg2, "other-in") and not item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("That item is not a transporter.\n")
            return

        if game_utils.str_cmp(arg2, "other-remove") and item.spectype.is_set(merc.SITEM_TELEPORTER):
            ch.send("Not on a transporter.\n")
            return

        buf = item.victpoweroff if item.victpoweroff else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweroff = ""
        elif item.victpoweroff and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweroff = buf + "\n" + arg3
        else:
            item.victpoweroff = arg3
        ch.send("Ok.\n")
    elif game_utils.str_cmp(arg2, "you-use"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        buf = item.chpoewruse if item.chpoweruse else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.chpoweruse = ""
        elif item.chpoweruse and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.chpoweruse = buf + "\n" + arg3
        else:
            item.chpoweruse = arg3
        ch.send("Ok.\n")
    elif game_utils.str_cmp(arg2, "other-use"):
        if not ch.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("You are not permitted to change an object in this way.\n")
            return

        if item.flags.relic:
            ch.send("Not on a relic.\n")
            return

        if item.item_type == merc.ITEM_BOOK:
            ch.send("Not on a book.\n")
            return

        buf = item.victpoweruse if item.victpoweruse else ""

        if game_utils.str_cmp(arg3, "clear"):
            item.victpoweruse = ""
        elif item.victpoweruse and buf:
            if len(buf) + len(arg3) >= settings.MAX_STRING_LENGTH - 4:
                ch.send("Line too long.\n")
                return
            else:
                item.victpoweruse = buf + "\n" + arg3
        else:
            item.victpoweruse = arg3
        ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="quest",
        cmd_fun=cmd_quest,
        position=merc.POS_SITTING, level=2,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
