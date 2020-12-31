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


# noinspection PyUnusedLocal
def cmd_relevel(ch, argument):
    if game_utils.str_cmp(ch.name, ["List", "of", "imps"]):
        ch.level = merc.MAX_LEVEL
        ch.trust = merc.MAX_LEVEL
        ch.send("Done.\n")
    elif game_utils.str_cmp(ch.name, ["List", "of", "HJs"]):
        ch.level = merc.MAX_LEVEL - 1
        ch.trust = merc.MAX_LEVEL - 1
        ch.send("Done.\n")
    else:
        ch.huh()


interp.register_command(
    interp.CmdType(
        name="relevel",
        cmd_fun=cmd_relevel,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=False,
        default_arg=""
    )
)
