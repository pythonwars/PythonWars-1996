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
import fight
import game_utils
import handler_game
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_chill_touch(sn, level, ch, victim, target):
    dam_each = [9, 10, 10, 10, 11, 11, 12, 12, 13, 13, 13, 14, 14, 14, 15, 15, 15, 16, 16, 16, 17, 17, 17, 18, 18, 18, 19, 19, 19, 20, 20,
                20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24, 25, 25, 25, 26, 26, 26, 27, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = game_utils.number_range(dam_each[level] // 2, dam_each[level] * 2)

    no_dam = (not victim.is_npc() and victim.immune.is_set(merc.IMM_COLD))
    if not no_dam and (not handler_magic.saves_spell(level, victim) or victim.is_npc() or not victim.is_vampire()):
        aff = handler_game.AffectData(type=sn, duration=6, location=merc.APPLY_STR, modifier=-1)
        victim.affect_add(aff)
    else:
        dam //= 2

    fight.damage(ch, victim, 0 if no_dam else dam, sn)


const.register_spell(
    const.skill_type(
        name="chill touch",
        skill_level=99,
        spell_fun=spl_chill_touch,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(8),
        min_mana=15,
        beats=12,
        noun_damage="chilling touch",
        msg_off="You feel less cold."
    )
)
