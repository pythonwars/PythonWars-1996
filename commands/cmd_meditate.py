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
def cmd_meditate(ch, argument):
    if ch.is_npc() or not ch.is_mage():
        ch.send("You are unable to attain the correct state of mind.\n")
        return

    pos = ch.position
    if pos == merc.POS_SLEEPING:
        ch.send("You are already sleeping.\n")
    elif pos == merc.POS_RESTING:
        ch.send("You are already resting.\n")
    elif pos == merc.POS_MEDITATING:
        ch.send("You are already meditating.\n")
    elif pos == merc.POS_SITTING:
        ch.send("You cross your legs and start meditating.\n")
        handler_game.act("$n crosses $s legs and starts meditating.", ch, None, None, merc.TO_ROOM)
        ch.position = merc.POS_MEDITATING
    elif pos == merc.POS_STANDING:
        ch.send("You sit down, cross your legs and start meditating.\n")
        handler_game.act("$n sits down, crosses $s legs and starts meditating.", ch, None, None, merc.TO_ROOM)
        ch.position = merc.POS_MEDITATING
    elif pos == merc.POS_FIGHTING:
        ch.send("You are already fighting!\n")


interp.register_command(
    interp.CmdType(
        name="meditate",
        cmd_fun=cmd_meditate,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
