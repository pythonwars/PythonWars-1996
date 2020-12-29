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
import handler_game
import interp
import merc


def cmd_incognito(ch, argument):
    # RT code for taking a level argument
    argument, arg = game_utils.read_word(argument)

    if not arg:
        if ch.incog_level:
            ch.incog_level = 0
            handler_game.act("$n is no longer cloaked.", ch, None, None, merc.TO_ROOM)
            ch.send("You are no longer cloaked.\n")
        else:
            ch.incog_level = ch.trust
            handler_game.act("$n cloaks $s presence.", ch, None, None, merc.TO_ROOM)
            ch.send("You cloak your presence.\n")
    else:
        level = int(arg) if arg.isdigit() else -1
        if level not in merc.irange(2, ch.level):
            ch.send("Incog level must be between 2 and your level.\n")
            return

        ch.reply = None
        ch.incog_level = level
        handler_game.act("$n cloaks $s presence.", ch, None, None, merc.TO_ROOM)
        ch.send("You cloak your presence.\n")


interp.register_command(
    interp.CmdType(
        name="incog",
        cmd_fun=cmd_incognito,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
