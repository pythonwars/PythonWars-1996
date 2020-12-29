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
import instance
import merc


# noinspection PyUnusedLocal
def spl_mass_invis(sn, level, ch, victim, target):
    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]

        if not gch.is_same_group(ch) or gch.is_affected(merc.AFF_INVISIBLE):
            continue

        handler_game.act("$n slowly fades out of existence.", gch, None, None, merc.TO_ROOM)
        gch.send("You slowly fade out of existence.\n")
        aff = handler_game.AffectData(type=sn, duration=24, location=merc.APPLY_NONE, bitvector=merc.AFF_INVISIBLE)
        gch.affect_join(aff)
    ch.send("Ok.\n")


const.register_spell(
    const.skill_type(
        name="mass invis",
        skill_level=4,
        spell_fun=spl_mass_invis,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(69),
        min_mana=20,
        beats=24,
        noun_damage="",
        msg_off="!Mass Invis!"
    )
)
