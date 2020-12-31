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
import interp
import merc
import state_checks
import world_classes


def cmd_oset(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)
    arg3 = argument

    if ch.is_npc():
        return

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax: oset <object> <field>  <value>\n"
                "or:     oset <object> <string> <value>\n"
                "or:     oset <object> <affect> <value>\n\n"
                "Field being one of:\n"
                "  value0 value1 value2 value3\n"
                "  level weight cost timer morph\n\n"
                "String being one of:\n"
                "  name short long ed type extra wear owner\n\n"
                "Affect being one of:\n"
                "  str dex int wis con\n"
                "  hit dam ac hp mana move\n")
        return

    obj = ch.get_item_world(arg1)
    if not obj:
        ch.send("Nothing like that in heaven or earth.\n")
        return

    if obj.carried_by and not obj.carried_by.is_npc() and obj.carried_by.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and \
            not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    if not ch.is_judge() and (not obj.questmaker or not game_utils.str_cmp(ch.name, obj.questmaker)):
        ch.send("You don't have permission to change that item.\n")
        return

    # Snarf the value (which need not be numeric).
    value = int(arg3) if arg3.isdigit else -1

    # Set something.
    if game_utils.str_cmp(arg2, ["value0", "v0"]):
        if obj.item_type == merc.ITEM_WEAPON and not ch.is_judge():
            ch.send("You are not authorised to create spell weapons.\n")
            return
        elif obj.item_type == merc.ITEM_QUEST:
            ch.send("You cannot change a quest tokens value with oset.\n")
            return
        elif obj.item_type == merc.ITEM_ARMOR and value > 15:
            obj.value[0] = 15
        else:
            obj.value[0] = value
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, ["value1", "v1"]):
        if obj.item_type == merc.ITEM_WEAPON and value > 10:
            obj.value[1] = 10
        else:
            obj.value[1] = value
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, ["value2", "v2"]):
        if obj.item_type == merc.ITEM_WEAPON and value > 20:
            obj.value[2] = 20
        else:
            obj.value[2] = value
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, ["value3", "v3"]):
        if obj.item_type == merc.ITEM_ARMOR and not ch.is_judge():
            ch.send("You are not authorised to create spell armour.\n")
        else:
            obj.value[3] = value
            ch.send("Ok.\n")
            obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "level"):
        value = state_checks.urange(1, value, 50)
        if not ch.is_judge():
            ch.send("You are not authorised to change an items level.\n")
        else:
            obj.level = value
            ch.send("Ok.\n")
            obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "weight"):
        obj.weight = value
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "cost"):
        if value > 100000 and not ch.is_judge():
            ch.send("Don't be so damn greedy!\n")
        else:
            obj.cost = value
            ch.send("Ok.\n")
            obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "timer"):
        obj.timer = value
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, ["hitroll", "hit"]):
        ch.oset_affect(obj, value, merc.APPLY_HITROLL, False)
        return
    elif game_utils.str_cmp(arg2, ["damroll", "dam"]):
        ch.oset_affect(obj, value, merc.APPLY_DAMROLL, False)
        return
    elif game_utils.str_cmp(arg2, ["armor", "ac"]):
        ch.oset_affect(obj, value, merc.APPLY_AC, False)
        return
    elif game_utils.str_cmp(arg2, ["hitpoints", "hp"]):
        ch.oset_affect(obj, value, merc.APPLY_HIT, False)
        return
    elif game_utils.str_cmp(arg2, "mana"):
        ch.oset_affect(obj, value, merc.APPLY_MANA, False)
        return
    elif game_utils.str_cmp(arg2, ["move", "movement"]):
        ch.oset_affect(obj, value, merc.APPLY_MOVE, False)
        return
    elif game_utils.str_cmp(arg2, ["str", "strength"]):
        ch.oset_affect(obj, value, merc.APPLY_STR, False)
        return
    elif game_utils.str_cmp(arg2, ["dex", "dexterity"]):
        ch.oset_affect(obj, value, merc.APPLY_DEX, False)
        return
    elif game_utils.str_cmp(arg2, ["int", "intelligence"]):
        ch.oset_affect(obj, value, merc.APPLY_INT, False)
        return
    elif game_utils.str_cmp(arg2, ["wis", "wisdom"]):
        ch.oset_affect(obj, value, merc.APPLY_WIS, False)
        return
    elif game_utils.str_cmp(arg2, ["con", "constitution"]):
        ch.oset_affect(obj, value, merc.APPLY_CON, False)
        return

    if game_utils.str_cmp(arg2, "type"):
        if not ch.is_judge():
            ch.send("You are not authorised to change an item type.\n")
            return

        item_list = [("light", merc.ITEM_LIGHT), ("scroll", merc.ITEM_SCROLL), ("wand", merc.ITEM_WAND), ("staff", merc.ITEM_STAFF),
                     ("weapon", merc.ITEM_WEAPON), ("treasure", merc.ITEM_TREASURE), (["armor", "armour"], merc.ITEM_ARMOR),
                     ("potion", merc.ITEM_POTION), ("furniture", merc.ITEM_FURNITURE), ("trash", merc.ITEM_TRASH), ("container", merc.ITEM_CONTAINER),
                     ("drink", merc.ITEM_DRINK_CON), ("key", merc.ITEM_KEY), ("food", merc.ITEM_FOOD), ("money", merc.ITEM_MONEY),
                     ("boat", merc.ITEM_BOAT), ("corpse", merc.ITEM_CORPSE_NPC), ("fountain", merc.ITEM_FOUNTAIN), ("pill", merc.ITEM_PILL),
                     ("portal", merc.ITEM_PORTAL), ("stake", merc.ITEM_STAKE)]
        for (aa, bb) in item_list:
            if game_utils.str_cmp(arg3, aa):
                obj.item_type = bb
                break
        else:
            ch.send("Type can be one of: Light, Scroll, Wand, Staff, Weapon, Treasure, Armor,\n"
                    "Potion, Furniture, Trash, Container, Drink, Key, Food, Money, Boat, Corpse,\n"
                    "Fountain, Pill, Portal, Stake.\n")
            return
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "owner"):
        if ch.is_npc():
            ch.send("Not while switched.\n")
            return

        if not ch.is_judge() and (not obj.questmaker or not game_utils.str_cmp(ch.name, obj.questmaker)):
            ch.send("Someone else has already changed this item.\n")
            return

        victim = ch.get_char_world(arg3)
        if not victim:
            ch.not_here(arg3)
            return

        if victim.is_npc():
            ch.not_npc()
            return

        obj.questmaker = ch.name
        obj.questowner = victim.name
        ch.send("Ok.\n")
        return

    if game_utils.str_cmp(arg2, "name"):
        obj.name = arg3
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "short"):
        obj.short_descr = arg3
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "long"):
        obj.description = arg3
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    if game_utils.str_cmp(arg2, "ed"):
        argument, arg3 = game_utils.read_word(argument)

        if not argument:
            ch.send("Syntax: oset <object> ed <keyword> <string>\n")
            return

        edd = world_classes.ExtraDescrData(keyword=arg3, description=argument)
        obj.extra_descr.append(edd)
        ch.send("Ok.\n")
        obj.questmaker = ch.name
        return

    # Generate usage message.
    ch.cmd_oset("")


interp.register_command(
    interp.CmdType(
        name="oset",
        cmd_fun=cmd_oset,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
