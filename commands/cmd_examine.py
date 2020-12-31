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
import interp
import merc


def cmd_examine(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Examine what?\n")
        return

    ch.cmd_look(arg)

    item = ch.get_item_here(arg)
    if item:
        if item.condition >= 100:
            buf = "You notice that {} is in perfect condition.\n".format(item.short_descr)
        elif item.condition >= 75:
            buf = "You notice that {} is in good condition.\n".format(item.short_descr)
        elif item.condition >= 50:
            buf = "You notice that {} is in average condition.\n".format(item.short_descr)
        elif item.condition >= 25:
            buf = "You notice that {} is in poor condition.\n".format(item.short_descr)
        else:
            buf = "You notice that {} is in awful condition.\n".format(item.short_descr)
        ch.send(buf)

        if item.item_type in [merc.ITEM_DRINK_CON, merc.ITEM_CONTAINER, merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC]:
            ch.send("When you look inside, you see:\n")
            ch.cmd_look("in {}".format(arg))


interp.register_command(
    interp.CmdType(
        name="examine",
        cmd_fun=cmd_examine,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
