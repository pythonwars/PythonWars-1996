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
import const
import data_loader
import database.read.read_tables as read
import game_utils
import handler_game
import handler_item
import instance
import merc
import object_creator
import settings
import state_checks
import update


def boot_db():
    import handler_npc
    import handler_room
    import world_classes

    init_time()
    init_instance()
    read.read_tables()
    data_loader.load_areas()
    world_classes.Note.load()

    area_update()
    object_creator.setup_exits()
    update.instance_number_save()

    results = (
        "------------------------[ Templates ]------------------------",
        f" Areas    : {world_classes.Area.template_count:6,}    NPCs     : {handler_npc.Npc.template_count:6,}    Items    : {handler_item.Items.template_count:6,}",
        f" Rooms    : {handler_room.Room.template_count:6,}    Shops    : {len(instance.shop_templates):6,}",
        f" Total    : {world_classes.Area.template_count + handler_npc.Npc.template_count + handler_item.Items.template_count + handler_room.Room.template_count + len(instance.shop_templates):6,}",
        "------------------------[ Instances ]------------------------",
        f" Areas    : {world_classes.Area.instance_count:6,}    NPCs     : {handler_npc.Npc.instance_count:6,}    Items    : {handler_item.Items.instance_count:6,}",
        f" Rooms    : {handler_room.Room.instance_count:6,}    Resets   : {world_classes.Reset.load_count:6,}    Helps    : {len(instance.help_list):6,}",
        f" Socials  : {len(const.social_table):6,}    Notes    : {len(instance.note_list):6,}",
        f" Total    : {world_classes.Area.instance_count + handler_npc.Npc.instance_count + handler_item.Items.instance_count + handler_room.Room.instance_count + world_classes.Reset.load_count + len(instance.note_list) + len(instance.help_list) + len(const.social_table):6,}",
        "------------------------[ Snap Shot ]------------------------"
    )
    spaces = "\n" + " " * 51
    comm.notify(spaces.join(results), merc.CONSOLE_BOOT)


def init_instance():
    # First lets add the bad terms we dont want to pass during instancing, while copying attributes
    instance.not_to_instance.append("instance_id")
    instance.not_to_instance.append("act")

    try:
        with open(settings.INSTANCE_FILE, "x+") as fp:
            fp.write("0")
    except FileExistsError:
        with open(settings.INSTANCE_FILE, "r") as fp:
            dummy, instance.max_instance_id = game_utils.read_int(fp.read())

    if instance.max_instance_id == 0 or not instance.max_instance_id:
        comm.notify("First run, or problem with the instance, setting to 6000", merc.CONSOLE_WARNING)
        instance.max_instance_id = 6000
    else:
        comm.notify(f"Global Instance Tracker, instances thus far: {instance.max_instance_id}", merc.CONSOLE_INFO)


def fix_exits():
    for k, r in instance.room_templates.items():
        for e in r.template_exit[:]:
            if e and type(e.template_to_room) == int:
                if e.template_to_room not in instance.room_templates:
                    comm.notify(f"fix_exits: Failed to find to_room for {r.template_vnum}: {e.template_to_room}", merc.CONSOLE_ERROR)
                    e.template_to_room = None
                    r.template_exit.remove(e)
                else:
                    e.template_to_room = instance.room_templates[e.template_to_room]


# Repopulate areas periodically.
def area_update():
    for area_id, area in instance.areas.items():
        area.age += 1
        if area.age < 3:
            continue

        # Check for PC's.
        if area.player_count > 0 and area.age == 15 - 1:
            for ch in list(instance.players.values()):
                if ch.is_awake() and ch.in_room and ch.in_room.area == area:
                    ch.send("You hear an agonised scream in the distance.\n")

        # Check age and reset.
        # Note: Mud School resets every 3 minutes (not 15).
        if not area.empty and (area.player_count == 0 or area.age >= 15):
            reset_area(area)
            area.age = game_utils.number_range(0, 3)
            school_instance_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
            school_instance = instance.rooms[school_instance_id]
            if school_instance and area_id == school_instance.area:
                area.age = 15 - 3
            elif area.player_count == 0:
                area.empty = True


def m_reset(preset, last, level, npc):
    if preset.arg1 not in instance.npc_templates.keys():
        comm.notify(f"m_reset: 'M': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        npc_template = instance.npc_templates[preset.arg1]

    if preset.arg3 not in instance.room_templates.keys():
        comm.notify(f"reset_area: 'R': bad vnum {preset.arg3}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        room_instance_id = instance.instances_by_room[preset.arg3][0]
        room_instance = instance.global_instances[room_instance_id]

    level = state_checks.urange(0, npc_template.level - 2, merc.LEVEL_HERO)
    if npc_template.count >= preset.arg2:
        last = False
        return last, level, npc

    npc = object_creator.create_mobile(npc_template)

    # Check for pet shop.
    if room_instance.vnum - 1 in instance.room_templates.keys():
        prev_room_instance_id = instance.instances_by_room[room_instance.vnum - 1][0]
        prev_room_instance = instance.global_instances[prev_room_instance_id]
        if prev_room_instance.room_flags.is_set(merc.ROOM_PET_SHOP):
            npc.act.set_bit(merc.ACT_PET)

    if room_instance.is_dark():
        npc.affected_by.set_bit(merc.AFF_INFRARED)

    # set area
    npc.area = room_instance.area

    room_instance.put(npc)
    level = state_checks.urange(0, npc.level - 2, merc.LEVEL_HERO)
    last = True
    return last, level, npc


def o_reset(parea, preset, last, level, npc):
    if preset.arg1 not in instance.item_templates.keys():
        comm.notify(f"o_reset: 'O': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        item_template = instance.item_templates[preset.arg1]

    if preset.arg3 not in instance.room_templates.keys():
        comm.notify(f"o_reset: 'R': bad vnum {preset.arg3}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        room_instance_id = instance.instances_by_room[preset.arg3][0]
        room_instance = instance.global_instances[room_instance_id]

    if parea.player_count > 0 or handler_item.count_obj_list(item_template, room_instance.items) > 0:
        last = False
        return last, level, npc

    item = object_creator.create_item(item_template, game_utils.number_range(1, 50))
    item.cost = 0
    room_instance.put(item)
    last = True
    return last, level, npc


def p_reset(parea, preset, last, level, npc):
    if preset.arg1 not in instance.item_templates.keys():
        comm.notify(f"p_reset: 'P': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        item_template = instance.item_templates[preset.arg1]

    if preset.arg3 not in instance.item_templates.keys():
        comm.notify(f"p_reset: 'P': bad vnum {preset.arg3}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        item_to_template = instance.item_templates[preset.arg3]

    item_to = None
    item_to_list = instance.instances_by_item.get(item_to_template.vnum, None)
    if item_to_list:
        item_to = instance.global_instances[item_to_list[0]]

    if parea.player_count > 0 or not item_to or not item_to.in_room or handler_item.count_obj_list(item_template, item_to.inventory) > 0:
        last = False
        return last, level, npc

    item = object_creator.create_item(item_template, game_utils.number_range(1, 50))
    item_to.put(item)
    last = True
    return last, level, npc


def g_e_reset(preset, last, level, npc):
    if preset.arg1 not in instance.item_templates.keys():
        comm.notify(f"g_e_reset: 'E' or 'G': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        item_template = instance.item_templates[preset.arg1]

    if not last:
        return last, level, npc

    if not npc:
        comm.notify(f"g_e_reset: 'E' or 'G': None mob for vnum {preset.arg1}", merc.CONSOLE_WARNING)
        last = False
        return last, level, npc

    if npc.pshop:
        if item_template.item_type in [merc.ITEM_PILL, merc.ITEM_POTION]:
            olevel = game_utils.number_range(0, 10)
        elif item_template.item_type == merc.ITEM_SCROLL:
            olevel = game_utils.number_range(5, 15)
        elif item_template.item_type == merc.ITEM_WAND:
            olevel = game_utils.number_range(10, 20)
        elif item_template.item_type == merc.ITEM_STAFF:
            olevel = game_utils.number_range(15, 25)
        elif item_template.item_type in [merc.ITEM_ARMOR, merc.ITEM_WEAPON]:
            olevel = game_utils.number_range(5, 15)
        else:
            olevel = 0

        item = object_creator.create_item(item_template, olevel)
        item.flags.shop_inventory = True
    else:
        item = object_creator.create_item(item_template, game_utils.number_range(1, 50))
    npc.put(item)

    if preset.command == "E":
        npc.equip(item, True)

    last = True
    return last, level, npc


def d_reset(preset, last, level, npc):
    if preset.arg1 not in instance.room_templates.keys():
        comm.notify(f"d_reset: 'D': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        room_instance_id = instance.instances_by_room[preset.arg1][0]
        room_instance = instance.global_instances[room_instance_id]

    pexit = room_instance.exit[preset.arg2]
    if not pexit:
        return last, level, npc

    if preset.arg3 == 0:
        pexit.exit_info.rem_bit(merc.EX_CLOSED)
        pexit.exit_info.rem_bit(merc.EX_LOCKED)
    elif preset.arg3 == 1:
        pexit.exit_info.set_bit(merc.EX_CLOSED)
        pexit.exit_info.rem_bit(merc.EX_LOCKED)
    elif preset.arg3 == 2:
        pexit.exit_info.set_bit(merc.EX_CLOSED)
        pexit.exit_info.set_bit(merc.EX_LOCKED)
    last = True
    return last, level, npc


def r_reset(preset, last, level, npc):
    if preset.arg1 not in instance.room_templates.keys():
        comm.notify(f"r_reset: 'R': bad vnum {preset.arg1}", merc.CONSOLE_WARNING)
        return last, level, npc
    else:
        room_instance_id = instance.instances_by_room[preset.arg1][0]
        room_instance = instance.global_instances[room_instance_id]

    for d0 in merc.irange(preset.arg2 - 1):
        d1 = game_utils.number_range(d0, preset.arg2 - 1)
        pexit = room_instance.exit[d0]
        room_instance.exit[d0] = room_instance.exit[d1]
        room_instance.exit[d1] = pexit
    return last, level, npc


def reset_area(parea):
    npc = None
    last = True
    level = 0

    for preset in parea.reset_list[:]:
        if preset.command == "M":
            last, level, npc = m_reset(preset, last, level, npc)
        elif preset.command == "O":
            last, level, npc = o_reset(parea, preset, last, level, npc)
        elif preset.command == "P":
            last, level, npc = p_reset(parea, preset, last, level, npc)
        elif preset.command in ["G", "E"]:
            last, level, npc = g_e_reset(preset, last, level, npc)
        elif preset.command == "D":
            last, level, npc = d_reset(preset, last, level, npc)
        elif preset.command == "R":
            last, level, npc = r_reset(preset, last, level, npc)
        else:
            comm.notify(f"reset_area: bad command ({preset.command})", merc.CONSOLE_CRITICAL)
            sys.exit(1)


def init_time():
    lhour = int(merc.current_time - 650336715) // (merc.PULSE_TICK // merc.PULSE_PER_SECOND)
    handler_game.time_info.hour = lhour % 24
    lday = lhour // 24
    handler_game.time_info.day = int(lday % 35)
    lmonth = lday // 35
    handler_game.time_info.month = lmonth % 17
    handler_game.time_info.year = lmonth // 17

    if handler_game.time_info.hour < 5:
        handler_game.weather_info.sunlight = merc.SUN_DARK
    elif handler_game.time_info.hour < 6:
        handler_game.weather_info.sunlight = merc.SUN_RISE
    elif handler_game.time_info.hour < 19:
        handler_game.weather_info.sunlight = merc.SUN_LIGHT
    elif handler_game.time_info.hour < 20:
        handler_game.weather_info.sunlight = merc.SUN_SET
    else:
        handler_game.weather_info.sunlight = merc.SUN_DARK

    handler_game.weather_info.change = 0
    handler_game.weather_info.mmhg = 960

    if 7 <= handler_game.time_info.month <= 12:
        handler_game.weather_info.mmhg += game_utils.number_range(1, 50)
    else:
        handler_game.weather_info.mmhg += game_utils.number_range(1, 80)

    if handler_game.weather_info.mmhg <= 980:
        handler_game.weather_info.sky = merc.SKY_LIGHTNING
    elif handler_game.weather_info.mmhg <= 1000:
        handler_game.weather_info.sky = merc.SKY_RAINING
    elif handler_game.weather_info.mmhg <= 1020:
        handler_game.weather_info.sky = merc.SKY_CLOUDY
    else:
        handler_game.weather_info.sky = merc.SKY_CLOUDLESS
