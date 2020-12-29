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
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_portal(sn, level, ch, victim, target):
    handler_magic.target_name, arg = game_utils.read_word(handler_magic.target_name)

    if not arg:
        ch.send("Who do you wish to create a portal to?\n")
        return

    victim = ch.get_char_world(arg)
    if not victim or victim == ch or not victim.in_room or ch.is_npc() or victim.is_npc() or \
            (not victim.is_npc() and not victim.immune.is_set(merc.IMM_SUMMON)) or ch.in_room.room_flags.is_set(merc.ROOM_PRIVATE) or \
            ch.in_room.room_flags.is_set(merc.ROOM_SOLITARY) or ch.in_room.room_flags.is_set(merc.ROOM_NO_RECALL) or \
            victim.in_room.room_flags.is_set(merc.ROOM_PRIVATE) or victim.in_room.room_flags.is_set(merc.ROOM_SOLITARY) or \
            victim.in_room.room_flags.is_set(merc.ROOM_NO_RECALL) or victim.in_room == ch.in_room:
        ch.send("You failed.\n")
        return

    duration = game_utils.number_range(2, 3)

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PORTAL], 0)
    item.value[0] = victim.in_room.vnum
    item.value[3] = ch.in_room.vnum
    item.timer = duration
    item.flags.shadowplane = ch.is_affected(merc.AFF_SHADOWPLANE)
    ch.in_room.put(item)

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PORTAL], 0)
    item.value[0] = ch.in_room.vnum
    item.value[3] = victim.in_room.vnum
    item.timer = duration
    item.flags.shadowplane = victim.is_affected(merc.AFF_SHADOWPLANE)
    victim.in_room.put(item)
    handler_game.act("$p appears in front of $n.", ch, item, None, merc.TO_ROOM)
    handler_game.act("$p appears in front of you.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p appears in front of $n.", victim, item, None, merc.TO_ROOM)
    handler_game.act("$p appears in front of you.", ch, item, victim, merc.TO_VICT)


const.register_spell(
    const.skill_type(
        name="portal",
        skill_level=1,
        spell_fun=spl_portal,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(604),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="!Portal!"
    )
)
