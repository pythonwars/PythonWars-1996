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
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_web(sn, level, ch, victim, target):
    handler_game.act("You point your finger at $N and a web flies from your hand!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n points $s finger at $N and a web flies from $s hand!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n points $s finger at you and a web flies from $s hand!", ch, None, victim, merc.TO_VICT)

    if victim.is_affected(merc.AFF_WEBBED):
        ch.send("But they are already webbed!\n")
        return

    if fight.is_safe(ch, victim):
        return

    if handler_magic.saves_spell(level, victim) and victim.position >= merc.POS_FIGHTING:
        victim.send("You dodge the web!\n")
        handler_game.act("$n dodges the web!", victim, None, None, merc.TO_ROOM)
        return

    aff = handler_game.AffectData(type=sn, location=merc.APPLY_AC, modifier=200, duration=game_utils.number_range(1, 2), bitvector=merc.AFF_WEBBED)
    victim.affect_join(aff)
    victim.send("You are coated in a sticky web!\n")
    handler_game.act("$n is coated in a sticky web!", victim, None, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="web",
        skill_level=99,
        spell_fun=spl_web,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(561),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="The web surrounding you breaks away."
    )
)
