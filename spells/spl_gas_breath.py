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
import instance
import merc


# noinspection PyUnusedLocal
def spl_gas_breath(sn, level, ch, victim, target):
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]

        if not vch.is_npc() if ch.is_npc() else vch.is_npc():
            hpch = max(10, ch.hit)
            dam = game_utils.number_range(hpch // 16 + 1, hpch // 8)

            if handler_magic.saves_spell(level, vch):
                dam //= 2

            fight.damage(ch, vch, 0 if (not vch.is_npc() and vch.is_vampire()) else dam, sn)


const.register_spell(
    const.skill_type(
        name="gas breath",
        skill_level=1,
        spell_fun=spl_gas_breath,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(203),
        min_mana=50,
        beats=12,
        noun_damage="blast of gas",
        msg_off="!Gas Breath!"
    )
)
