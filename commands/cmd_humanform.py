#  PythonWars copyright © 2020 by Paul Penner. All rights reserved. In order to
#  use this codebase you must comply with all licenses.
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

import handler_game
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_humanform(ch, argument):
    if ch.is_npc():
        return

    item = ch.chobj
    if not item:
        ch.send("You are already in human form.\n")
        return

    ch.obj_vnum = 0
    item.chobj = None
    ch.chobj = None
    ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
    ch.extra.rem_bit(merc.EXTRA_OSWITCH)
    ch.morph = ""
    handler_game.act("$p transforms into $n.", ch, item, None, merc.TO_ROOM)
    handler_game.act("Your reform your human body.", ch, item, None, merc.TO_CHAR)
    item.extract()

    if ch.in_room.vnum == merc.ROOM_VNUM_IN_OBJECT:
        ch.in_room.get(ch)
        room_id = instance.instances_by_room[merc.ROOM_VNUM_HELL][0]
        instance.rooms[room_id].put(ch)


interp.register_command(
    interp.CmdType(
        name="humanform",
        cmd_fun=cmd_humanform,
        position=merc.POS_SITTING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
