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

import collections
import os
import sys

import comm
import game_utils
import handler_game
import handler_item
import handler_npc
import handler_room
import instance
import merc
import miniboa.terminal
import object_creator
import settings
import world_classes

area_instance = None


def load_areas():
    comm.notify("Loading Areas.", merc.CONSOLE_BOOT)

    index = 0
    narea_list = os.path.join(settings.AREA_DIR, settings.AREA_LIST)
    fp = open(narea_list, "r")

    area = fp.readline().strip()
    while area != "$":
        afp = open(os.path.join(settings.AREA_DIR, area), "r")
        comm.notify("Loading: {}".format(area), merc.CONSOLE_BOOT)
        index += 1
        load_area(afp.read(), index)
        area = fp.readline().strip()
        afp.close()
    fp.close()


def load_area(area, index):
    global area_instance

    if not area.strip():
        return

    area, w = game_utils.read_word(area, False)
    w = w[1:]
    while w != "$":
        if w == "AREA":
            parea = world_classes.Area(None)
            parea.index = index
            area, parea.name = game_utils.read_string(area)
            instance.area_templates[parea.name] = parea
            area_instance = world_classes.Area(parea)
        elif w == "HELPS":
            area = load_helps(area)
        elif w == "MOBILES":
            area = load_npcs(area, area_instance)
        elif w == "OBJECTS":
            area = load_objects(area, area_instance)
        elif w == "RESETS":
            area = load_resets(area, area_instance)
        elif w == "ROOMS":
            area = load_rooms(area, area_instance)
        elif w == "SHOPS":
            area = load_shops(area)
        elif w == "SPECIALS":
            area = load_specials(area)
        elif w == "$":
            break
        else:
            comm.notify("load_area: bad section name ({})".format(w), merc.CONSOLE_CRITICAL)
            sys.exit(1)

        area, w = game_utils.read_word(area, False)
        w = w[1:]


def load_helps(area):
    while True:
        nhelp = handler_game.HelpData()
        area, nhelp.level = game_utils.read_int(area)
        area, nhelp.keyword = game_utils.read_string(area)

        if nhelp.keyword == "$":
            del nhelp
            break

        instance.helps[nhelp.keyword] = nhelp
        area, nhelp.text = game_utils.read_string(area)
        nhelp.text = miniboa.terminal.escape(nhelp.text, "ANSI")

        if nhelp.keyword == "GREETING":
            nhelp.text = nhelp.text[1:] if nhelp.text[0] == "." else nhelp.text
            nhelp.text += " "
            instance.greeting_list.append(nhelp)
        instance.help_list.append(nhelp)
    return area


def load_npcs(area, parea):
    area, w = game_utils.read_word(area, False)
    w = w[1:]  # strip the pound
    while w != "0":
        vnum = int(w)
        if vnum in instance.npc_templates:
            comm.notify("load_npcs: vnum {} duplicated.".format(vnum), merc.CONSOLE_CRITICAL)
            sys.exit(1)

        npc = handler_npc.Npc()
        npc.vnum = vnum
        instance.npc_templates[npc.vnum] = npc
        npc.area = parea.name

        area, npc.name = game_utils.read_string(area)
        npc.name = npc.name.lower()
        area, npc.short_descr = game_utils.read_string(area)

        area, npc.long_descr = game_utils.read_string(area)
        npc.long_descr = miniboa.terminal.escape(npc.long_descr, "ANSI")
        area, npc.description = game_utils.read_string(area)
        npc.description = miniboa.terminal.escape(npc.description, "ANSI")

        area, act = game_utils.read_int(area)
        npc.act.bits = act | merc.ACT_IS_NPC
        area, affected_by = game_utils.read_int(area)
        npc.affected_by.bits = affected_by
        area, npc.alignment = game_utils.read_int(area)

        area, letter = game_utils.read_letter(area)
        area, level = game_utils.read_int(area)
        npc.level = game_utils.number_fuzzy(level)
        area, npc.hitroll = game_utils.read_int(area)
        area, npc.armor = game_utils.read_word(area)
        area, dummy = game_utils.read_int(area)
        area = game_utils.read_forward(area)
        area, dummy = game_utils.read_int(area)
        area = game_utils.read_forward(area)
        area, dummy = game_utils.read_int(area)
        area, dummy = game_utils.read_int(area)
        area = game_utils.read_forward(area)
        area, dummy = game_utils.read_int(area)
        area = game_utils.read_forward(area)
        area, dummy = game_utils.read_int(area)
        area, npc.gold = game_utils.read_int(area)
        area, dummy = game_utils.read_int(area)
        area, dummy = game_utils.read_int(area)
        area, dummy = game_utils.read_int(area)
        area, npc.sex = game_utils.read_int(area)

        area, w = game_utils.read_word(area, False)
        w = w[1:]  # strip the pound
    return area


def load_objects(area, parea):
    area, w = game_utils.read_word(area, False)
    w = w[1:]  # strip the pound
    while w != "0":
        vnum = int(w)
        if vnum in instance.item_templates:
            comm.notify("load_objects: vnum {} duplicated.".format(vnum), merc.CONSOLE_CRITICAL)
            sys.exit(1)

        flag_data = collections.namedtuple("item_flags", ("slots", "restrictions", "attributes", "weapon"))
        flag_data.slots = set({})
        flag_data.restrictions = set({})
        flag_data.weapon = set({})
        flag_data.attributes = set({})

        item = handler_item.Items(None)
        item.vnum = vnum
        instance.item_templates[item.vnum] = item
        item.area = parea.name
        area, item.name = game_utils.read_string(area)
        area, item.short_descr = game_utils.read_string(area)
        item.short_descr = miniboa.terminal.escape(item.short_descr, "ANSI")
        area, item.description = game_utils.read_string(area)
        item.description = miniboa.terminal.escape(item.description, "ANSI")
        area, dummy = game_utils.read_string(area)

        area, item_type = game_utils.read_int(area)
        item_list = [(1, merc.ITEM_LIGHT), (2, merc.ITEM_SCROLL), (3, merc.ITEM_WAND), (4, merc.ITEM_STAFF), (5, merc.ITEM_WEAPON),
                     (8, merc.ITEM_TREASURE), (9, merc.ITEM_ARMOR), (10, merc.ITEM_POTION), (12, merc.ITEM_FURNITURE), (15, merc.ITEM_CONTAINER),
                     (17, merc.ITEM_DRINK_CON), (18, merc.ITEM_KEY), (19, merc.ITEM_FOOD), (20, merc.ITEM_MONEY), (22, merc.ITEM_BOAT),
                     (23, merc.ITEM_CORPSE_NPC), (24, merc.ITEM_CORPSE_PC), (25, merc.ITEM_FOUNTAIN), (26, merc.ITEM_PILL), (27, merc.ITEM_PORTAL),
                     (28, merc.ITEM_EGG), (29, merc.ITEM_VOODOO), (30, merc.ITEM_STAKE), (31, merc.ITEM_MISSILE), (32, merc.ITEM_AMMO),
                     (33, merc.ITEM_QUEST), (34, merc.ITEM_QUESTCARD), (35, merc.ITEM_QUESTMACHINE), (36, merc.ITEM_SYMBOL), (37, merc.ITEM_BOOK),
                     (38, merc.ITEM_PAGE), (39, merc.ITEM_TOOL)]
        for (aa, bb) in item_list:
            if item_type == aa:
                item.item_type = bb
                break
        else:
            item.item_type = merc.ITEM_TRASH

        area, extra_bits = game_utils.read_int(area)
        game_utils.item_flags_from_bits(extra_bits, flag_data, "extra flags")
        area, wear_bits = game_utils.read_int(area)
        game_utils.item_flags_from_bits(wear_bits, flag_data, "wear flags")

        if item.item_type == merc.ITEM_LIGHT:
            flag_data.slots.update({"right_hand", "left_hand"})
        item.equips_to = flag_data.slots
        item.item_restrictions = flag_data.restrictions
        item.item_attributes = flag_data.attributes

        area, item.value[0] = game_utils.read_flags(area)
        area, item.value[1] = game_utils.read_flags(area)
        area, item.value[2] = game_utils.read_flags(area)
        area, item.value[3] = game_utils.read_flags(area)

        area, item.weight = game_utils.read_int(area)
        area, item.cost = game_utils.read_int(area)
        area, dummy = game_utils.read_int(area)

        area, w = game_utils.read_word(area, False)
        while w in ["A", "E", "Q"]:
            if w == "A":
                paf = handler_game.AffectData()
                paf.type = -1
                paf.duration = -1
                area, paf.location = game_utils.read_int(area)
                area, paf.modifier = game_utils.read_int(area)
                item.affected.append(paf)
            elif w == "E":
                edd = world_classes.ExtraDescrData()
                area, edd.keyword = game_utils.read_string(area)
                area, edd.description = game_utils.read_string(area)
                item.extra_descr.append(edd)
            elif w == "Q":
                area, item.chpoweron = game_utils.read_string(area)
                area, item.chpoweroff = game_utils.read_string(area)
                area, item.chpoweruse = game_utils.read_string(area)
                area, item.victpoweron = game_utils.read_string(area)
                area, item.victpoweroff = game_utils.read_string(area)
                area, item.victpoweruse = game_utils.read_string(area)
                area, sitem_bits = game_utils.read_flags(area)
                game_utils.item_flags_from_bits(sitem_bits, flag_data, "sitem flags")
                area, item.specpower = game_utils.read_int(area)

            area, w = game_utils.read_word(area, False)

        w = w[1:]  # strip the pound
    return area


def load_resets(area, parea):
    count = 0
    while True:
        count += 1
        area, letter = game_utils.read_letter(area)
        if letter == "S":
            break

        if letter == "*":
            area, t = game_utils.read_to_eol(area)
            continue

        reset = world_classes.Reset(None)
        reset.command = letter
        reset.area = parea.name
        area, number = game_utils.read_int(area)  # if_flag
        area, reset.arg1 = game_utils.read_int(area)
        area, reset.arg2 = game_utils.read_int(area)
        area, reset.arg3 = (area, 0) if letter in ["G", "R"] else game_utils.read_int(area)
        area, t = game_utils.read_to_eol(area)
        parea.reset_list.append(reset)
    return area


def load_rooms(area, parea):
    area, w = game_utils.read_word(area, False)
    w = w[1:]  # strip the pound
    while w != "0":
        vnum = int(w)
        if vnum in instance.room_templates:
            comm.notify("load_rooms: duplicate vnum {}".format(vnum), merc.CONSOLE_CRITICAL)
            sys.exit(1)

        room = handler_room.Room(None)
        room.vnum = vnum
        instance.room_templates[room.vnum] = room
        room.area = parea.name
        area, room.name = game_utils.read_string(area)
        area, room.description = game_utils.read_string(area)
        room.description = miniboa.terminal.escape(room.description, "ANSI")

        area, dummy = game_utils.read_int(area)  # area number
        area, room_flags = game_utils.read_int(area)
        room.room_flags.bits = room_flags
        area, room.sector_type = game_utils.read_int(area)

        area, w = game_utils.read_word(area, None)
        while w in ["S", "D0", "D1", "D2", "D3", "D4", "D5", "E", "T"]:
            if w == "S":
                pass
            elif w in ["D0", "D1", "D2", "D3", "D4", "D5"]:  # exit
                door = int(w[1:])
                if door not in range(merc.MAX_DIR):
                    comm.notify("load_rooms: vnum {} has bad door number".format(vnum), merc.CONSOLE_CRITICAL)
                    sys.exit(1)

                nexit = world_classes.Exit(None)
                area, nexit.description = game_utils.read_string(area)
                area, nexit.keyword = game_utils.read_string(area)
                area, exit_info = game_utils.read_int(area)
                nexit.exit_info.bits = exit_info
                area, nexit.key = game_utils.read_int(area)
                area, nexit.to_room_vnum = game_utils.read_int(area)
                room.exit[door] = nexit
            elif w == "E":
                edd = world_classes.ExtraDescrData()
                area, edd.keyword = game_utils.read_string(area)
                area, edd.description = game_utils.read_string(area)
                room.extra_descr.append(edd)
            elif w == "T":
                rt = handler_room.Roomtext()
                area, rt.input = game_utils.read_string(area)
                area, rt.output = game_utils.read_string(area)
                area, rt.choutput = game_utils.read_string(area)
                area, rt.name = game_utils.read_string(area)
                area, rt.type = game_utils.read_int(area)
                area, rt.power = game_utils.read_int(area)
                area, rt.mob = game_utils.read_int(area)
                room.roomtext.append(rt)
            else:
                comm.notify("load_rooms: bad flag DEST ({})".format(w), merc.CONSOLE_CRITICAL)
                sys.exit(1)
            area, w = game_utils.read_word(area, False)

        w = w[1:]  # strip the pound

        # Create our instances
        room_instance = object_creator.create_room(room)
        room_instance.environment = parea.instance_id
    return area


def load_shops(area):
    while True:
        area, keeper = game_utils.read_int(area)

        if keeper == 0:
            break

        shop = world_classes.Shop(None)
        shop.keeper = keeper
        instance.shop_templates[shop.keeper] = shop
        instance.npc_templates[shop.keeper].pshop = instance.shop_templates[shop.keeper]

        for r in range(merc.MAX_TRADE):
            area, shop.buy_type[r] = game_utils.read_int(area)

        area, shop.profit_buy = game_utils.read_int(area)
        area, shop.profit_sell = game_utils.read_int(area)
        area, shop.open_hour = game_utils.read_int(area)
        area, shop.close_hour = game_utils.read_int(area)
        area, t = game_utils.read_to_eol(area)
    return area


def load_specials(area):
    while True:
        area, letter = game_utils.read_letter(area)
        if letter == "*":
            area, t = game_utils.read_to_eol(area)
            continue
        elif letter == "S":
            return area
        elif letter == "M":
            area, vnum = game_utils.read_int(area)
            area, instance.npc_templates[vnum].spec_fun = game_utils.read_word(area, False)
        else:
            comm.notify("load_specials: letter not *MS ({})".format(letter), merc.CONSOLE_CRITICAL)
            sys.exit(1)
    return area
