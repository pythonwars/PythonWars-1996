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

import const
import game_utils
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_control_weather(sn, level, ch, victim, target):
    if game_utils.str_cmp(victim, "better"):
        handler_game.weather_info.change += game_utils.dice(level // 3, 4)
    elif game_utils.str_cmp(victim, "worse"):
        handler_game.weather_info.change -= game_utils.dice(level // 3, 4)
    else:
        ch.send("Do you want it to get better or worse?\n")
        return

    ch.send("Ok.\n")


const.register_spell(
    const.skill_type(
        name="control weather",
        skill_level=99,
        spell_fun=spl_control_weather,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(11),
        min_mana=25,
        beats=12,
        noun_damage="",
        msg_off="!Control Weather!"
    )
)
