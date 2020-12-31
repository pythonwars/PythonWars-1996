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
def spl_sanctuary(sn, level, ch, victim, target):
    if victim.is_affected(merc.AFF_SANCTUARY):
        return

    aff = handler_game.AffectData(type=sn, duration=game_utils.number_fuzzy(level // 8), location=merc.APPLY_NONE, bitvector=merc.AFF_SANCTUARY)
    victim.affect_add(aff)
    handler_game.act("$n is surrounded by a white aura.", victim, None, None, merc.TO_ROOM)
    victim.send("You are surrounded by a white aura.\n")


const.register_spell(
    const.skill_type(
        name="sanctuary",
        skill_level=4,
        spell_fun=spl_sanctuary,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(36),
        min_mana=75,
        beats=12,
        noun_damage="",
        msg_off="The white aura around your body fades."
    )
)
