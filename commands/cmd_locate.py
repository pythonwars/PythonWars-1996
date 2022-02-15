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


# noinspection PyUnusedLocal
def cmd_locate(ch, argument):
    if ch.is_npc():
        return

    buf = []
    found = False
    for item in list(instance.items.values()):
        if not ch.can_see_item(item) or not item.questowner or not game_utils.str_cmp(ch.name, item.questowner):
            continue

        found = True
        in_item = item
        while in_item.in_item:
            in_item = in_item.in_item

        if in_item.in_living:
            buf += f"{item.short_descr} created by {item.questmaker} and carried by {in_item.in_living.pers(ch)}.\n"
        else:
            buf += "{} created by {} and in {}.\n".format(item.short_descr, item.questmaker, "somewhere" if not in_item.in_room else in_item.in_room.name)

    if not found:
        buf += "You cannot locate any items belonging to you.\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="locate",
        cmd_fun=cmd_locate,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
