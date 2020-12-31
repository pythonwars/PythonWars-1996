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

import game_utils
import interp
import merc


def cmd_trust(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax: trust <char> <trust>\n"
                "Trust being one of: None, Builder, Questmaker, Enforcer, Judge, or Highjudge.\n")
        return

    victim = ch.get_char_room(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    arg_list = [("none", 0), ("builder", merc.LEVEL_BUILDER), ("questmaker", merc.LEVEL_QUESTMAKER), ("enforcer", merc.LEVEL_ENFORCER),
                ("judge", merc.LEVEL_JUDGE), ("highjudge", merc.LEVEL_HIGHJUDGE)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg2, aa):
            level = bb
            break
    else:
        ch.cmd_trust("")
        return

    if level >= ch.trust:
        ch.send("Limited to below your trust.\n")
        return

    ch.send("Ok.\n")
    victim.trust = level


interp.register_command(
    interp.CmdType(
        name="trust",
        cmd_fun=cmd_trust,
        position=merc.POS_DEAD, level=11,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
