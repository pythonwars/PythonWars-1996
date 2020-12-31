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
import fight
import game_utils
import handler_game
import instance
import merc


# noinspection PyUnusedLocal
def spl_earthquake(sn, level, ch, victim, target):
    ch.send("The earth trembles beneath your feet!\n")
    handler_game.act("$n makes the earth tremble and shiver.", ch, None, None, merc.TO_ROOM)

    for vch in list(instance.characters.values()):
        if not vch.in_room:
            continue

        if vch.in_room == ch.in_room:
            if vch != ch and (not vch.is_npc() if ch.is_npc() else vch.is_npc()):
                fight.damage(ch, vch, level + game_utils.dice(2, 8), sn)
            continue

        if vch.in_room.area == ch.in_room.area:
            vch.send("The earth trembles and shivers.\n")


const.register_spell(
    const.skill_type(
        name="earthquake",
        skill_level=99,
        spell_fun=spl_earthquake,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(23),
        min_mana=15,
        beats=12,
        noun_damage="earthquake",
        msg_off="!Earthquake!"
    )
)
