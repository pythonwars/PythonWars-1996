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
def spl_dispel_magic(sn, level, ch, victim, target):
    if victim != ch and (handler_magic.saves_spell(level, victim) or level < victim.level):
        ch.send("You failed.\n")
        return

    if not victim.affected:
        ch.send("Nothing happens.\n")
        return

    for aff in victim.affected[:]:
        victim.affect_remove(aff)

    if ch == victim:
        handler_game.act("You remove all magical affects from yourself.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n has removed all magical affects from $mself.", ch, None, None, merc.TO_ROOM)
    else:
        handler_game.act("You remove all magical affects from $N.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has removed all magical affects from $N.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n has removed all magical affects from you.", ch, None, victim, merc.TO_VICT)


const.register_spell(
    const.skill_type(
        name="dispel magic",
        skill_level=1,
        spell_fun=spl_dispel_magic,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(59),
        min_mana=15,
        beats=12,
        noun_damage="",
        msg_off="!Dispel Magic!"
    )
)
