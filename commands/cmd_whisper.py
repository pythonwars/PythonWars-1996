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


def cmd_whisper(ch, argument):
    if ch.extra.is_set(merc.EXTRA_GAGGED):
        ch.send("Not with a gag on!\n")
        return

    argument, arg = game_utils.read_word(argument)

    if not arg or not argument:
        ch.send("Usage: whisper <person> <message>\n")
        return

    victim = ch.get_char_world(arg)
    if not victim or victim.in_room != ch.in_room:
        ch.not_here(arg)
        return

    if not victim.is_awake():
        handler_game.act("$E cannot hear you.", ch, None, victim, merc.TO_CHAR)
        return

    if not victim.is_npc() and not victim.desc:
        handler_game.act("$E is currently link dead.", ch, None, victim, merc.TO_CHAR)
        return

    handler_game.act("You whisper to $N '$t'.", ch, argument, victim, merc.TO_CHAR)
    handler_game.act("$n whispers to you '$t'.", ch, argument, victim, merc.TO_VICT)
    handler_game.act("$n whispers something to $N.", ch, None, victim, merc.TO_NOTVICT)


interp.register_command(
    interp.CmdType(
        name="whisper",
        cmd_fun=cmd_whisper,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
