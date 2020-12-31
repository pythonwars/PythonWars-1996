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

import fight
import game_utils
import handler_game
import interp
import merc


def cmd_slay(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Slay whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.act.is_set(merc.PLR_GODLESS):
        ch.send("You failed.\n")
        return

    if not victim.is_npc() and victim.level >= ch.trust:
        ch.send("You failed.\n")
        return

    handler_game.act("You slay $M in cold blood!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n slays you in cold blood!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n slays $N in cold blood!", ch, None, victim, merc.TO_NOTVICT)
    fight.raw_kill(victim)


# noinspection PyUnusedLocal
def cmd_sla(ch, argument):
    ch.send("If you want to SLAY, spell it out.\n")


interp.register_command(
    interp.CmdType(
        name="slay",
        cmd_fun=cmd_slay,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="sla",
        cmd_fun=cmd_sla,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_NORMAL, show=False,
        default_arg=""
    )
)
