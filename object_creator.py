#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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

import sys

import comm
import fight  # JINNOTE - 12/14/2020 @ 5:54 PM - Removing this import is causing circular import issue for some reason...
import game_utils
import handler_item
import handler_npc
import handler_room
import instance
import merc
import special
import world_classes


def create_room(room_template):
    if room_template is None:
        comm.notify("create_room: No roomTemplate given", merc.CONSOLE_CRITICAL)
        sys.exit(1)

    room = handler_room.Room(room_template)
    return room


def setup_exits():
    for room in instance.rooms.values():
        if room.exit:
            for door, pexit in enumerate(room.exit):
                if pexit:
                    iexit = world_classes.Exit(pexit)
                    room.exit[door] = iexit


def create_mobile(npc_template):
    if not npc_template:
        comm.notify("create_mobile: no npc_template", merc.CONSOLE_CRITICAL)
        sys.exit(1)

    npc = handler_npc.Npc(npc_template)
    npc.id = game_utils.get_mob_id(npc=True)
    npc.level = max(1, game_utils.number_fuzzy(npc_template.level))
    npc.armor = game_utils.interpolate(npc.level, 100, -100)

    if npc_template.spec_fun:
        npc.spec_fun = special.spec_table[npc_template.spec_fun]

    tempvalue = min(30000, npc.level * 8 + game_utils.number_range(npc.level * npc.level // 4, npc.level * npc.level))
    npc.max_hit = tempvalue
    npc.hit = npc.max_hit
    npc.hitroll = npc.level
    npc.damroll = npc.level

    # link the mob to the world list
    npc_template.count += 1
    return npc


# Create an instance of an object.
def create_item(item_template, level, prev_instance_id: int = None):
    if not item_template:
        comm.notify("create_item: no item_template", merc.CONSOLE_INFO)
        sys.exit(1)

    item = handler_item.Items(item_template)
    if not prev_instance_id:
        pass  # item.instancer()
    else:
        item.instance_id = prev_instance_id

    item.level = level

    if item.vnum in merc.irange(29500, 29599):
        item.flags.artifact = True
        item.condition = 100
        item.toughness = 100
        item.resistance = 1
        item.level = 60
        item.cost = 1000000
    elif item.vnum in merc.irange(29600, 29699):
        item.flags.relic = True
        item.condition = 100
        item.toughness = 100
        item.resistance = 1
    else:
        item.condition = 100
        item.toughness = 5
        item.resistance = 25

    # Mess with object properties.
    if item.item_type == merc.ITEM_SCROLL:
        item.value[0] = game_utils.number_fuzzy(item.value[0])
    elif item.item_type in [merc.ITEM_WAND, merc.ITEM_STAFF]:
        item.value[0] = game_utils.number_fuzzy(item.value[0])
        item.value[1] = game_utils.number_fuzzy(item.value[1])
        item.value[2] = item.value[1]
    elif item.item_type == merc.ITEM_WEAPON:
        if not item.flags.artifact and not item.flags.relic:
            item.value[1] = game_utils.number_range(1, 10)
            item.value[2] = game_utils.number_range(item.value[1] + 1, item.value[1] * 2)
    elif item.item_type == merc.ITEM_ARMOR:
        if not item.flags.artifact and not item.flags.relic:
            item.value[0] = game_utils.number_range(5, 15)
    elif item.item_type in [merc.ITEM_POTION, merc.ITEM_PILL]:
        item.value[0] = game_utils.number_fuzzy(game_utils.number_fuzzy(item.value[0]))
    elif item.item_type == merc.ITEM_MONEY:
        item.value[0] = item.cost
    elif item.item_type in [merc.ITEM_LIGHT, merc.ITEM_TREASURE, merc.ITEM_FURNITURE, merc.ITEM_TRASH, merc.ITEM_CONTAINER, merc.ITEM_DRINK_CON,
                            merc.ITEM_KEY, merc.ITEM_FOOD, merc.ITEM_BOAT, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC, merc.ITEM_FOUNTAIN,
                            merc.ITEM_PORTAL, merc.ITEM_EGG, merc.ITEM_VOODOO, merc.ITEM_STAKE, merc.ITEM_MISSILE, merc.ITEM_AMMO, merc.ITEM_QUEST,
                            merc.ITEM_QUESTCARD, merc.ITEM_QUESTMACHINE, merc.ITEM_SYMBOL, merc.ITEM_BOOK, merc.ITEM_PAGE, merc.ITEM_TOOL]:
        pass
    else:
        comm.notify(f"create_item: bad item_type {item_template.vnum} ({item.item_type})", merc.CONSOLE_WARNING)

    item_template.count += 1
    return item


# duplicate an object exactly -- except contents
def clone_item(parent, clone):
    if not parent or not clone:
        return

    # start fixing the object
    clone = handler_item.Items(parent)
    return clone


# Create a 'money' obj.
def create_money(gold):
    if gold <= 0:
        comm.notify("create_money: zero or negative gold", merc.CONSOLE_WARNING)
        gold = 1

    if gold == 1:
        item = create_item(instance.item_templates[merc.OBJ_VNUM_MONEY_ONE], 0)
    else:
        item = create_item(instance.item_templates[merc.OBJ_VNUM_MONEY_SOME], 0)
        item.short_descr = item.short_descr % gold
        item.value[0] = gold
    return item


# Make a corpse out of a character.
def make_corpse(ch):
    if ch.is_npc():
        name = ch.short_descr
        corpse = create_item(instance.item_templates[merc.OBJ_VNUM_CORPSE_NPC], 0)
        corpse.timer = game_utils.number_range(4, 8)
        corpse.value[2] = ch.vnum
    else:
        name = ch.name
        corpse = create_item(instance.item_templates[merc.OBJ_VNUM_CORPSE_PC], 0)
        corpse.timer = game_utils.number_range(25, 40)

    # Why should players keep their gold?
    if ch.gold > 0:
        gold = create_money(ch.gold)

        if ch.is_affected(merc.AFF_SHADOWPLANE):
            gold.flags.shadowplane = True
        corpse.put(gold)
        ch.gold = 0

    corpse.short_descr = corpse.short_descr % name
    corpse.description = corpse.description % name

    for item_id in ch.equipped.values():
        if not item_id:
            continue

        item = instance.items[item_id]
        ch.unequip(item.equipped_to, silent=True, forced=True)

    for item_id in ch.inventory[:]:
        item = instance.items[item_id]

        ch.get(item)

        if item.flags.vanish:
            item.extract()
        else:
            if ch.is_affected(merc.AFF_SHADOWPLANE):
                item.flags.shadowplane = True
            corpse.put(item)

    if ch.is_affected(merc.AFF_SHADOWPLANE):
        corpse.flags.shadowplane = True
    ch.in_room.put(corpse)


def make_part(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        return

    arg_list = [("head", merc.OBJ_VNUM_SEVERED_HEAD), ("arm", merc.OBJ_VNUM_SLICED_ARM), ("leg", merc.OBJ_VNUM_SLICED_LEG),
                ("heart", merc.OBJ_VNUM_TORN_HEART), ("turd", merc.OBJ_VNUM_TORN_HEART), ("entrails", merc.OBJ_VNUM_SPILLED_ENTRAILS),
                ("brain", merc.OBJ_VNUM_QUIVERING_BRAIN), ("eyeball", merc.OBJ_VNUM_SQUIDGY_EYEBALL), ("blood", merc.OBJ_VNUM_SPILT_BLOOD),
                ("face", merc.OBJ_VNUM_RIPPED_FACE), ("windpipe", merc.OBJ_VNUM_TORN_WINDPIPE), ("cracked_head", merc.OBJ_VNUM_CRACKED_HEAD),
                ("ear", merc.OBJ_VNUM_SLICED_EAR), ("nose", merc.OBJ_VNUM_SLICED_NOSE), ("tooth", merc.OBJ_VNUM_KNOCKED_TOOTH),
                ("tongue", merc.OBJ_VNUM_TORN_TONGUE), ("hand", merc.OBJ_VNUM_SEVERED_HAND), ("foot", merc.OBJ_VNUM_SEVERED_FOOT),
                ("thumb", merc.OBJ_VNUM_SEVERED_THUMB), ("index", merc.OBJ_VNUM_SEVERED_INDEX), ("middle", merc.OBJ_VNUM_SEVERED_MIDDLE),
                ("ring", merc.OBJ_VNUM_SEVERED_RING), ("little", merc.OBJ_VNUM_SEVERED_LITTLE), ("toe", merc.OBJ_VNUM_SEVERED_TOE)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg, aa):
            vnum = bb
            break
    else:
        return

    name = ch.short_descr if ch.is_npc() else ch.name

    item = create_item(instance.item_templates[vnum], 0)
    item.timer = game_utils.number_range(2, 5) if ch.is_npc() else -1

    if game_utils.str_cmp(arg, "head"):
        if ch.is_npc():
            item.value[1] = ch.vnum
        else:
            ch.chobj = item
            item.chobj = ch
            item.timer = game_utils.number_range(2, 3)
    elif game_utils.str_cmp(arg, "brain") and not ch.is_npc() and ch.is_affected(merc.AFF_POLYMORPH) and ch.head.is_set(merc.LOST_HEAD):
        if ch.chobj:
            ch.chobj.chobj = None
        ch.chobj = item
        item.chobj = ch
        item.timer = game_utils.number_range(2, 3)

    # For blood :) KaVir
    if vnum == merc.OBJ_VNUM_SPILT_BLOOD:
        item.timer = 2

    # For voodoo dolls - KaVir
    item.name = item.name % name if not ch.is_npc() else "mob"

    if vnum != merc.OBJ_VNUM_SPILT_BLOOD:
        item.short_descr = item.short_descr % name
        item.description = item.description % name

    if ch.is_affected(merc.AFF_SHADOWPLANE):
        item.flags.shadowplane = True
    ch.in_room.put(item)
