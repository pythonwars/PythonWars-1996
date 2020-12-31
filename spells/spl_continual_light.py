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
import handler_game
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_continual_light(sn, level, ch, victim, target):
    light = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_LIGHT_BALL], 0)
    ch.in_room.put(light)
    handler_game.act("$n twiddles $s thumbs and $p appears.", ch, light, None, merc.TO_ROOM)
    handler_game.act("You twiddle your thumbs and $p appears.", ch, light, None, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="continual light",
        skill_level=1,
        spell_fun=spl_continual_light,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(57),
        min_mana=7,
        beats=12,
        noun_damage="",
        msg_off="!Continual Light!"
    )
)
