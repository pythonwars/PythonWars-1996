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
def spl_quest(sn, level, ch, victim, target):
    if ch.practice < 1:
        ch.send("It costs at least 1 point of primal energy to create a quest card.\n")
        return

    obj_index = instance.item_templates[merc.OBJ_VNUM_QUESTCARD]
    if not obj_index:
        ch.send("Missing object, please inform an Immortal.\n")
        return

    item = object_creator.create_item(obj_index, 0)
    item.quest_object()
    ch.put(item)

    if ch.practice >= 50:
        ch.practice -= 50
        item.level = 50
    else:
        item.level = ch.practice
        ch.practice = 0

    handler_game.act("$p fades into existance in your hands.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p fades into existance in $n's hands.", ch, item, None, merc.TO_ROOM)
    item.questmaker = ch.name
    item.questowner = ch.name


const.register_spell(
    const.skill_type(
        name="quest",
        skill_level=2,
        spell_fun=spl_quest,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(611),
        min_mana=500,
        beats=12,
        noun_damage="",
        msg_off="!Quest!"
    )
)
