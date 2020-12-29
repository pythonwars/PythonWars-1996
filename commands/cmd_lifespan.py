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
import interp
import merc


def cmd_lifespan(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not ch.dempower.is_set(merc.DEM_LIFESPAN):
        ch.send("You haven't been granted the gift of lifespan.\n")
        return

    item = ch.chobj
    if not item:
        ch.huh()
        return

    if not item.chobj or item.chobj != ch:
        ch.huh()
        return

    if not ch.head.is_set(merc.LOST_HEAD):
        ch.send("You cannot change your lifespan in this form.\n")
        return

    if game_utils.str_cmp(arg, ["l", "long"]):
        item.timer = 0
    elif game_utils.str_cmp(arg, ["s", "short"]):
        item.timer = 1
    else:
        ch.send("Do you wish to have a long or short lifespan?\n")
        return

    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="lifespan",
        cmd_fun=cmd_lifespan,
        position=merc.POS_RESTING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
