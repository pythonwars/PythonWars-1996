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
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_lightning_breath(sn, level, ch, victim, target):
    if victim.itemaff.is_set(merc.ITEMA_SHOCKSHIELD):
        return

    hpch = max(10, ch.hit)
    dam = game_utils.number_range(hpch // 16 + 1, hpch // 8)

    if handler_magic.saves_spell(level, victim):
        dam //= 2

    fight.damage(ch, victim, 0 if (not victim.is_npc() and victim.immune.is_set(merc.IMM_LIGHTNING)) else dam, sn)


const.register_spell(
    const.skill_type(
        name="lightning breath",
        skill_level=1,
        spell_fun=spl_lightning_breath,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(204),
        min_mana=50,
        beats=12,
        noun_damage="blast of lightning",
        msg_off="!Lightning Breath!"
    )
)
