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

import handler_item
import interp
import merc


# noinspection PyUnusedLocal
def cmd_equipment(ch, argument):
    buf = ["You are using:\n"]

    found = False
    for slot, item_id in ch.equipped.items():
        item = ch.get_eq(slot)
        if not item:
            continue

        buf += merc.eq_slot_strings[slot]
        if ch.can_see_item(item):
            buf += handler_item.format_item_to_char(item, ch, True) + "\n"
        else:
            ch.send("something.\n")
        found = True

    if not found:
        buf += "Nothing.\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="equipment",
        cmd_fun=cmd_equipment,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)