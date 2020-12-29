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
def spl_improve(sn, level, ch, victim, target):
    item = victim
    if item.flags.artifact:
        ch.send("Not on artifacts.\n")
        return

    if item.vnum != merc.OBJ_VNUM_PROTOPLASM:
        ch.send("You cannot enhance this object.\n")
        return

    if item.quest.is_set(merc.QUEST_IMPROVED):
        ch.send("This item has already been improved.\n")
        return
    elif item.points < 750 and item.item_type != merc.ITEM_WEAPON:
        ch.send("The object must be worth at least 750 quest points.\n")
        return
    elif item.points < 1500 and item.item_type == merc.ITEM_WEAPON:
        ch.send("The object must be worth at least 1500 quest points.\n")
        return

    item.quest.rem_bit(merc.QUEST_STR)
    item.quest.rem_bit(merc.QUEST_DEX)
    item.quest.rem_bit(merc.QUEST_INT)
    item.quest.rem_bit(merc.QUEST_WIS)
    item.quest.rem_bit(merc.QUEST_CON)
    item.quest.rem_bit(merc.QUEST_HITROLL)
    item.quest.rem_bit(merc.QUEST_DAMROLL)
    item.quest.rem_bit(merc.QUEST_HIT)
    item.quest.rem_bit(merc.QUEST_MANA)
    item.quest.rem_bit(merc.QUEST_MOVE)
    item.quest.rem_bit(merc.QUEST_AC)
    item.quest.set_bit(merc.QUEST_IMPROVED)
    handler_game.act("$p flickers for a moment.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p flickers for a moment.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="improve",
        skill_level=1,
        spell_fun=spl_improve,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(566),
        min_mana=1500,
        beats=12,
        noun_damage="",
        msg_off="!Improve!"
    )
)
