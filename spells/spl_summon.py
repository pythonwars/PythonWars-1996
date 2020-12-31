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
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_summon(sn, level, ch, victim, target):
    victim = ch.get_char_world(handler_magic.target_name)
    if not victim or victim == ch or not victim.in_room or victim.in_room.room_flags.is_set(merc.ROOM_SAFE) or \
            victim.in_room.room_flags.is_set(merc.ROOM_PRIVATE) or victim.in_room.room_flags.is_set(merc.ROOM_SOLITARY) or \
            victim.in_room.room_flags.is_set(merc.ROOM_NO_RECALL) or victim.level >= level + 3 or victim.fighting or \
            victim.in_room.area != ch.in_room.area or (victim.is_npc() and not victim.immune.is_set(merc.IMM_SUMMON)) or \
            (not victim.is_npc() and not victim.is_affected(merc.AFF_ETHEREAL)) or (victim.is_npc() and handler_magic.saves_spell(level, victim)):
        ch.send("You failed.\n")
        return

    handler_game.act("$n disappears suddenly.", victim, None, None, merc.TO_ROOM)
    victim.in_room.get(victim)
    ch.in_room.put(victim)
    handler_game.act("$n arrives suddenly.", victim, None, None, merc.TO_ROOM)
    handler_game.act("$N has summoned you!", victim, None, ch, merc.TO_CHAR)
    victim.cmd_look("auto")

    mount = victim.mount
    if mount:
        mount.in_room.get(mount)
        victim.in_room.put(mount)
        mount.cmd_look("auto")


const.register_spell(
    const.skill_type(
        name="summon",
        skill_level=3,
        spell_fun=spl_summon,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(40),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="!Summon!"
    )
)
