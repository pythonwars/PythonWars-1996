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
import merc


# noinspection PyUnusedLocal
def spl_enchant_weapon(sn, level, ch, victim, target):
    item = victim
    if item.item_type != merc.ITEM_WEAPON or item.flags.enchanted or item.flags.artifact or item.chobj:
        ch.send("You are unable to enchant this weapon.\n")
        return

    aff = handler_game.AffectData(type=sn, duration=-1, location=merc.APPLY_HITROLL, modifier=level // 5)
    item.affect_add(aff)
    aff = handler_game.AffectData(type=sn, duration=-1, location=merc.APPLY_DAMROLL, modifier=level // 10)
    item.affect_add(aff)

    if ch.is_good():
        item.flags.anti_evil = True
        item.flags.enchanted = True
        handler_game.act("$p glows blue.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$p glows blue.", ch, item, None, merc.TO_ROOM)
    elif ch.is_evil():
        item.flags.anti_good = True
        item.flags.enchanted = True
        handler_game.act("$p glows red.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$p glows red.", ch, item, None, merc.TO_ROOM)
    else:
        item.flags.anti_evil = True
        item.flags.anti_good = True
        item.flags.enchanted = True
        handler_game.act("$p glows yellow.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$p glows yellow.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="enchant weapon",
        skill_level=1,
        spell_fun=spl_enchant_weapon,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(24),
        min_mana=100,
        beats=24,
        noun_damage="",
        msg_off="!Enchant Weapon!"
    )
)
