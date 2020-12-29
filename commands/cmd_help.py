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

import game_utils
import instance
import interp
import merc


def cmd_help(ch, argument):
    if not argument:
        argument = "summary"

    found = [h for h in instance.help_list if h.level <= ch.trust and game_utils.is_name(argument, h.keyword)]
    for phelp in found:
        if phelp.level >= 0 and not game_utils.str_cmp(phelp.keyword, "imotd"):
            ch.send(phelp.keyword + "\n")

        text = phelp.text[1:] if phelp.text[0] == "." else phelp.text
        ch.send(text + "\n")
        return

    ch.send("No help on that word.\n")


interp.register_command(
    interp.CmdType(
        name="help",
        cmd_fun=cmd_help,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="credits",
        cmd_fun=cmd_help,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg="diku"
    )
)
interp.register_command(
    interp.CmdType(
        name="wizlist",
        cmd_fun=cmd_help,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg="wizlist"
    )
)
