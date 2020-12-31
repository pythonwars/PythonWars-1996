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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_create_water(sn, level, ch, victim, target):
    item = victim
    if item.item_type != merc.ITEM_DRINK_CON:
        ch.send("It is unable to hold water.\n")
        return

    if item.value[2] != 0 and item.value[1] != 0:
        ch.send("It contains some other liquid.\n")
        return

    water = min(level * (4 if handler_game.weather_info.sky >= merc.SKY_RAINING else 2), item.value[0] - item.value[1])

    if water > 0:
        item.value[2] = 0
        item.value[1] += water

        if not game_utils.is_name("water", item.name):
            item.name = "{} water".format(item.name)

        handler_game.act("$p is filled.", ch, item, None, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="create water",
        skill_level=99,
        spell_fun=spl_create_water,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(13),
        min_mana=5,
        beats=12,
        noun_damage="",
        msg_off="!Create Water!"
    )
)
