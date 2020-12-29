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
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_poison(sn, level, ch, victim, target):
    # Ghosts cannot be poisoned - KaVir
    if victim.is_npc() and victim.is_affected(merc.AFF_ETHEREAL):
        return

    if not victim.is_npc() and victim.is_vampire() and victim.vampaff.is_set(merc.VAM_SERPENTIS):
        return
    elif not victim.is_npc() and victim.is_werewolf() and victim.powers[merc.WPOWER_SPIDER] > 2:
        return

    if handler_magic.saves_spell(level, victim):
        return

    aff = handler_game.AffectData(type=sn, duration=level, location=merc.APPLY_STR, modifier=0 - game_utils.number_range(1, 3),
                                  bitvector=merc.AFF_POISON)
    victim.affect_join(aff)
    victim.send("You feel very sick.\n")

    if ch != victim:
        handler_game.act("$N looks very sick as your poison takes affect.", ch, None, victim, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="poison",
        skill_level=3,
        spell_fun=spl_poison,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(33),
        min_mana=10,
        beats=12,
        noun_damage="poison",
        msg_off="You feel less sick."
    )
)
