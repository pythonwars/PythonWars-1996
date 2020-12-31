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

import const
import game_utils
import handler_magic
import instance
import merc


# noinspection PyUnusedLocal
def spl_locate_object(sn, level, ch, victim, target):
    count = 0
    found = False

    for item in list(instance.items.values()):
        if not ch.can_see_item(item) or not game_utils.is_name(handler_magic.target_name, item.name):
            continue

        found = True
        in_item = item
        while in_item.in_item:
            in_item = in_item.in_item

        if in_item.in_living and ch.can_see(in_item.in_living):
            buf = "{} is carried by {}.\n".format(item.short_descr, in_item.in_living.pers(ch))
        else:
            buf = "{} is in {}.\n".format(item.short_descr, "somewhere" if not in_item.in_room else in_item.in_room.name)
        ch.send(buf[0].upper() + buf[1:])

        if count > 50:
            break
        else:
            count += 1

    if not found:
        ch.send("Nothing like that in hell, earth, or heaven.\n")


const.register_spell(
    const.skill_type(
        name="locate object",
        skill_level=3,
        spell_fun=spl_locate_object,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(31),
        min_mana=20,
        beats=18,
        noun_damage="",
        msg_off="!Locate Object!"
    )
)
