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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_heal(sn, level, ch, victim, target):
    victim.hit = min(victim.hit + 100, victim.max_hit)
    fight.update_pos(victim)
    victim.send("A warm feeling fills your body.\n")

    if ch == victim:
        handler_game.act("$n heals $mself.", ch, None, None, merc.TO_ROOM)
    else:
        handler_game.act("$n heals $N.", ch, None, victim, merc.TO_NOTVICT)
        ch.send("Ok.\n")

        if not ch.is_npc():
            ch.humanity()


const.register_spell(
    const.skill_type(
        name="heal",
        skill_level=3,
        spell_fun=spl_heal,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(28),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="!Heal!"
    )
)
