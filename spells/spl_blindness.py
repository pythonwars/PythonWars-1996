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
import handler_game
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_blindness(sn, level, ch, victim, target):
    if victim.is_affected(merc.AFF_BLIND) or handler_magic.saves_spell(level, victim):
        return

    aff = handler_game.AffectData(type=sn, location=merc.APPLY_HITROLL, modifier=-4, duration=1 + level, bitvector=merc.AFF_BLIND)
    victim.affect_add(aff)

    victim.send("You are blinded!\n")

    if victim != ch:
        handler_game.act("$N is blinded!", ch, None, victim, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="blindness",
        skill_level=2,
        spell_fun=spl_blindness,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(4),
        min_mana=5,
        beats=12,
        noun_damage="",
        msg_off="You can see again."
    )
)
