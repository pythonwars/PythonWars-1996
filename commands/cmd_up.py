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

import handler_ch
import interp
import merc


# noinspection PyUnusedLocal
def cmd_up(ch, argument):
    if ch.is_affected(merc.AFF_WEBBED):
        ch.send("You are unable to move with all this sticky webbing on.\n")
        return

    in_room = ch.in_room
    handler_ch.move_char(ch, merc.DIR_UP)

    if not ch.is_npc() and ch.in_room != in_room:
        old_room = ch.in_room
        ch.in_room.get(ch)
        in_room.put(ch)
        handler_ch.add_tracks(ch, merc.DIR_UP)
        ch.in_room.get(ch)
        old_room.put(ch)


interp.register_command(
    interp.CmdType(
        name="up",
        cmd_fun=cmd_up,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
