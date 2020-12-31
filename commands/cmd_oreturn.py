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

import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_oreturn(ch, argument):
    if ch.is_npc():
        return

    if not ch.extra.is_set(merc.EXTRA_OSWITCH) and not ch.head.is_set(merc.LOST_HEAD):
        ch.send("You are not oswitched.\n")
        return

    item = ch.chobj
    if item:
        item.chobj = None

    ch.chobj = None
    ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
    ch.extra.rem_bit(merc.EXTRA_OSWITCH)
    ch.head.rem_bit(merc.LOST_HEAD)
    ch.morph = ""
    ch.in_room.get(ch)
    to_instance_id = instance.instances_by_room[merc.ROOM_VNUM_ALTAR][0]
    instance.rooms[to_instance_id].put(ch)
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="oreturn",
        cmd_fun=cmd_oreturn,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
