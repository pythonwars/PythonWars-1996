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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_mana(sn, level, ch, victim, target):
    if not ch.is_npc() and not ch.is_vampire() and ch.vampaff.is_set(merc.VAM_CELERITY):
        if ch.move < 25:
            ch.send("You are too exhausted to do that.\n")
            return

        ch.move -= 25
    else:
        if ch.move < 50:
            ch.send("You are too exhausted to do that.\n")
            return

        ch.move -= 50

    victim.mana = min(victim.mana + level + 10, victim.max_mana)
    fight.update_pos(ch)
    fight.update_pos(victim)

    if ch == victim:
        ch.send("You draw in energy from your surrounding area.\n")
        handler_game.act("$n draws in energy from $s surrounding area.", ch, None, None, merc.TO_ROOM)
        return

    handler_game.act("You draw in energy from around you and channel it into $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n draws in energy and channels it into $N.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n draws in energy and channels it into you.", ch, None, victim, merc.TO_VICT)

    if not ch.is_npc() and ch != victim:
        ch.humanity()


const.register_spell(
    const.skill_type(
        name="mana",
        skill_level=1,
        spell_fun=spl_mana,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(602),
        min_mana=0,
        beats=12,
        noun_damage="",
        msg_off="!Mana!"
    )
)
