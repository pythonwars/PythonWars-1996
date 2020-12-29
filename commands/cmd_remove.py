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


def cmd_remove(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Remove what?\n")
        return

    if game_utils.str_cmp(arg, "all"):
        for loc, item_id in ch.equipped.items():
            if item_id and loc not in ["left_scabbard", "right_scabbard"]:
                ch.unequip(loc, True)
        return

    item = ch.get_item_wear(arg)
    if not item or item.equipped_to in ["left_scabbard", "right_scabbard"]:
        ch.send("You do not have that item.\n")
        return

    ch.unequip(item.equipped_to, True)


interp.register_command(
    interp.CmdType(
        name="remove",
        cmd_fun=cmd_remove,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
