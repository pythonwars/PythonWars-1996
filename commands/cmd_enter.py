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
import handler_room
import instance
import interp
import merc


# Designed for the portal spell, but can also have other uses...KaVir
# V0 = Where the portal will take you.
# V1 = Number of uses (0 is infinate).
# V2 = if 2, cannot be entered.
# V3 = The room the portal is currently in.
def cmd_enter(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Enter what?\n")
        return

    item = ch.get_item_list(arg, ch.in_room.items)
    if not item:
        handler_game.act("I see no $T here.", ch, None, arg, merc.TO_CHAR)
        return

    if item.item_type != merc.ITEM_PORTAL:
        handler_game.act("You cannot enter that.", ch, None, arg, merc.TO_CHAR)
        return

    if ch.is_affected(merc.AFF_SHADOWPLANE) and not item.flags.shadowplane:
        ch.send("You are too insubstantual.\n")
        return
    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and item.flags.shadowplane:
        ch.send("It is too insubstantual.\n")
        return

    if item.value[2] in [2, 3]:
        handler_game.act("It seems to be closed.", ch, None, arg, merc.TO_CHAR)
        return

    to_instance_id = instance.instances_by_room[item.value[0]][0]
    proomindex = instance.rooms[to_instance_id]
    location = ch.in_room
    if not proomindex:
        handler_game.act("You are unable to enter.", ch, None, arg, merc.TO_CHAR)
        return

    handler_game.act("You step into $p.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n steps into $p.", ch, item, None, merc.TO_ROOM)
    ch.in_room.get(ch)
    proomindex.put(ch)
    handler_game.act("$n steps out of $p.", ch, item, None, merc.TO_ROOM)
    ch.in_room.get(ch)
    location.put(ch)

    if item.value[1] != 0:
        item.value[1] -= 1
        if item.value[1] < 1:
            handler_game.act("$p vanishes.", ch, item, None, merc.TO_CHAR)
            handler_game.act("$p vanishes.", ch, item, None, merc.TO_ROOM)
            item.extract()

    ch.in_room.get(ch)
    proomindex.put(ch)

    for portal_id in ch.in_room.items:
        portal = instance.items[portal_id]

        if item.value[0] == portal.value[3] and item.value[3] == portal.value[0]:
            if ch.is_affected(merc.AFF_SHADOWPLANE) and portal.flags.shadowplane:
                ch.affected_by.rem_bit(merc.AFF_SHADOWPLANE)
                break
            elif not ch.is_affected(merc.AFF_SHADOWPLANE) and portal.flags.shadowplane:
                ch.affected_by.set_bit(merc.AFF_SHADOWPLANE)
                break

            if portal.value[1] != 0:
                portal.value[1] -= 1
                if portal.value[1] < 1:
                    handler_game.act("$p vanishes.", ch, portal, None, merc.TO_CHAR)
                    handler_game.act("$p vanishes.", ch, portal, None, merc.TO_ROOM)
                    portal.extract()

    ch.cmd_look("auto")

    mount = ch.mount
    if mount:
        mount.in_room.get(mount)
        ch.in_room.put(mount)


interp.register_command(
    interp.CmdType(
        name="enter",
        cmd_fun=cmd_enter,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
