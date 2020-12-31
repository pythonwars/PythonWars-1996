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
import instance
import interp
import merc


def cmd_mwhere(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Mwhere whom?\n")
        return

    buf = []
    found = False
    for victim in list(instance.npcs.values()):
        if victim.in_room and game_utils.is_name(arg, victim.name):
            found = True
            buf += "[{:5}] {:<28} [{:5}] {}\n".format(victim.vnum, victim.short_descr, victim.in_room.vnum, victim.in_room.name)

    if not found:
        buf += "You didn't find any {}.".format(arg)
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="mwhere",
        cmd_fun=cmd_mwhere,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
