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
#   Ported to Python by Davion of MudBytes.net using Miniboa
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
import settings


def cmd_log(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Log whom?\n")
        return

    if game_utils.str_cmp(arg, "all"):
        if settings.LOGALL:
            settings.LOGALL = False
            ch.send("Log ALL off.\n")
        else:
            settings.LOGALL = True
            ch.send("Log ALL on.\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    # No level check, gods can log anyone.
    victim.sentances.tog_bit(merc.SENT_LOG)
    if victim.sentances.is_set(merc.SENT_LOG):
        ch.send("LOG set.\n")
    else:
        ch.send("LOG removed.\n")


interp.register_command(
    interp.CmdType(
        name="log",
        cmd_fun=cmd_log,
        position=merc.POS_DEAD, level=9,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
