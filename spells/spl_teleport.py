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


# noinspection PyUnusedLocal
def spl_teleport(sn, level, ch, victim, target):
    if not victim.in_room or victim.in_room.room_flags.is_set(merc.ROOM_NO_RECALL) or victim.in_room.room_flags.is_set(merc.ROOM_SAFE) or \
            victim.in_room.room_flags.is_set(merc.ROOM_NO_TELEPORT) or (not ch.is_npc() and victim.fighting) or \
            (not victim.is_npc() and not victim.immune.is_set(merc.IMM_SUMMON)) or (victim != ch and handler_magic.saves_spell(level, victim)):
        ch.send("You failed.\n")
        return

    while True:
        to_room = game_utils.number_range(0, 65535)
        proomindex = instance.rooms[to_room]

        if proomindex and not proomindex.room_flags.is_set(merc.ROOM_PRIVATE) and not proomindex.room_flags.is_set(merc.ROOM_SOLITARY) and \
                proomindex.room_flags.is_set(merc.ROOM_NO_TELEPORT) and to_room not in [30008, 30002]:
            break

    handler_game.act("$n slowly fades out of existence.", victim, None, None, merc.TO_ROOM)
    victim.in_room.get(victim)
    proomindex.put(victim)
    handler_game.act("$n slowly fades into existence.", victim, None, None, merc.TO_ROOM)
    victim.cmd_look("auto")

    mount = ch.mount
    if mount:
        mount.in_room.get(mount)
        ch.in_room.put(mount)
        mount.cmd_look("auto")


const.register_spell(
    const.skill_type(
        name="teleport",
        skill_level=3,
        spell_fun=spl_teleport,
        target=merc.TAR_CHAR_SELF,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(2),
        min_mana=35,
        beats=12,
        noun_damage="",
        msg_off="!Teleport!"
    )
)
