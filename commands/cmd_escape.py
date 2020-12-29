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

import comm
import handler_game
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_escape(ch, argument):
    if ch.is_npc() or not ch.is_hero():
        return

    if ch.position >= merc.POS_SLEEPING:
        ch.send("You can only do this if you are dying.\n")
        return

    location = instance.rooms[merc.ROOM_VNUM_TEMPLE]
    if not location:
        ch.send("You are completely lost.\n")
        return

    if ch.in_room == location:
        return

    ch.move = 0
    ch.mana = 0
    handler_game.act("$n fades out of existance.", ch, None, None, merc.TO_ROOM)
    ch.in_room.get(ch)
    location.put(ch)
    handler_game.act("$n fades into existance.", ch, None, None, merc.TO_ROOM)
    ch.cmd_look("auto")
    comm.info("{} has escaped defenceless from a fight.".format(ch.name))


interp.register_command(
    interp.CmdType(
        name="escape",
        cmd_fun=cmd_escape,
        position=merc.POS_DEAD, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
