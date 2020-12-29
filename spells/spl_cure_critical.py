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
import merc


# noinspection PyUnusedLocal
def spl_cure_critical(sn, level, ch, victim, target):
    heal = game_utils.dice(3, 8) + level - 6
    victim.hit = min(victim.hit + heal, victim.max_hit)
    fight.update_pos(victim)
    victim.send("You feel better!\n")

    if ch != victim:
        ch.send("Ok.\n")

        if not ch.is_npc():
            ch.humanity()


const.register_spell(
    const.skill_type(
        name="cure critical",
        skill_level=99,
        spell_fun=spl_cure_critical,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(15),
        min_mana=20,
        beats=12,
        noun_damage="",
        msg_off="!Cure Critical!"
    )
)
