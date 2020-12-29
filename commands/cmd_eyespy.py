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

import game_utils
import handler_game
import instance
import interp
import merc
import object_creator


# noinspection PyUnusedLocal
def cmd_eyespy(ch, argument):
    if ch.head.is_set(merc.LOST_EYE_L) and ch.head.is_set(merc.LOST_EYE_R):
        ch.send("But you don't have any more eyes to pluck out!\n")
        return

    if not ch.head.is_set(merc.LOST_EYE_L) and game_utils.number_range(1, 2) == 1:
        handler_game.act("You pluck out your left eyeball and throw it to the ground.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n plucks out $s left eyeball and throws it to the ground.", ch, None, None, merc.TO_ROOM)
    elif not ch.head.is_set(merc.LOST_EYE_R):
        handler_game.act("You pluck out your right eyeball and throw it to the ground.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n plucks out $s right eyeball and throws it to the ground.", ch, None, None, merc.TO_ROOM)
    else:
        handler_game.act("You pluck out your left eyeball and throw it to the ground.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n plucks out $s left eyeball and throws it to the ground.", ch, None, None, merc.TO_ROOM)

    familiar = ch.familiar
    if familiar:
        object_creator.make_part(ch, "eyeball")
        return

    mob_index = instance.npc_templates[merc.MOB_VNUM_EYE]
    if not mob_index:
        ch.send("Error - please inform an Immortal.\n")
        return

    victim = object_creator.create_mobile(mob_index)
    ch.in_room.put(victim)
    ch.familiar = victim
    victim.wizard = ch


interp.register_command(
    interp.CmdType(
        name="eyespy",
        cmd_fun=cmd_eyespy,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
