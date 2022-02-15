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

import comm
import const
import game_utils
import handler_game
import interp
import merc


def cmd_empty(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Empty what?\n")
        return

    item = ch.get_item_here(arg)
    if not item:
        ch.send("You can't find it.\n")
        return

    if item.item_type == merc.ITEM_DRINK_CON:
        if item.value[1] <= 0:
            ch.send("It is already empty.\n")
            return

        liquid = item.value[2]
        if liquid not in const.liq_table:
            comm.notify(f"cmd_empty: bad liquid number {liquid}", merc.CONSOLE_WARNING)
            liquid = item.value[2] = "water"

        handler_game.act("$n empties $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_ROOM)
        handler_game.act("You empty $T from $p.", ch, item, const.liq_table[liquid].name, merc.TO_CHAR)
        item.value[1] = 0
    else:
        ch.send("You cannot empty that.\n")


interp.register_command(
    interp.CmdType(
        name="empty",
        cmd_fun=cmd_empty,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
