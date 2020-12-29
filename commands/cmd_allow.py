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


def cmd_allow(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Remove which site from the ban list?\n")
        return

    for ban in instance.ban_list:
        if game_utils.str_cmp(ban.name, arg):
            instance.ban_list.remove(ban)
            del ban
            ch.send("Ok.\n")
            return

    ch.send("Site is not banned.\n")


interp.register_command(
    interp.CmdType(
        name="allow",
        cmd_fun=cmd_allow,
        position=merc.POS_DEAD, level=11,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
