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
import interp
import merc


# noinspection PyUnusedLocal
def cmd_dismount(ch, argument):
    if ch.mounted == 0:
        ch.send("But you are not riding!\n")
        return

    victim = ch.mount
    if not victim:
        ch.send("But you are not riding!\n")
        return

    handler_game.act("You clamber off $N's back.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n clambers off $N's back.", ch, None, victim, merc.TO_ROOM)
    ch.mounted = merc.IS_ON_FOOT
    victim.mounted = merc.IS_ON_FOOT
    ch.mount = None
    victim.mount = None


interp.register_command(
    interp.CmdType(
        name="dismount",
        cmd_fun=cmd_dismount,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
