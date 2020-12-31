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


def cmd_qstat(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Which item?\n")
        return

    item = ch.get_item_carry(arg)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    buf = ["Object {}.\n".format(item.short_descr)]
    buf += "Owner when worn: {}\n".format(item.chpoweron)
    buf += "Other when worn: {}\n".format(item.victpoweron)
    buf += "Owner when removed: {}\n".format(item.chpoweroff)
    buf += "Other when removed: {}\n".format(item.victpoweroff)
    buf += "Owner when used: {}\n".format(item.chpoweruse)
    buf += "Other when used: {}\n".format(item.victpoweruse)
    buf += "Type: {}.\n".format(repr(item.spectype))
    buf += "Power: {}.\n".format(item.specpower)
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="qstat",
        cmd_fun=cmd_qstat,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
