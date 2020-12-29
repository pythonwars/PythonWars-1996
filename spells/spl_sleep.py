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
def spl_sleep(sn, level, ch, victim, target):
    if victim.is_affected(merc.AFF_SLEEP) or level < victim.level or (not victim.is_npc() and victim.immune.is_set(merc.IMM_SLEEP)) or \
            (victim.is_npc() and victim.is_affected(merc.AFF_ETHEREAL)) or handler_magic.saves_spell(level, victim):
        return

    aff = handler_game.AffectData(type=sn, duration=4 * level, location=merc.APPLY_NONE, bitvector=merc.AFF_SLEEP)
    victim.affect_add(aff)

    if victim.is_awake():
        victim.send("You feel very sleepy ..... zzzzzz.\n")
        handler_game.act("$n goes to sleep.", victim, None, None, merc.TO_ROOM)
        victim.position = merc.POS_SLEEPING


const.register_spell(
    const.skill_type(
        name="sleep",
        skill_level=3,
        spell_fun=spl_sleep,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(38),
        min_mana=15,
        beats=12,
        noun_damage="",
        msg_off="You feel less tired."
    )
)
