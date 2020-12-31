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

import game_utils
import handler_game
import interp
import merc


def cmd_travel(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        if not ch.dempower.is_set(merc.DEM_TRAVEL):
            ch.send("You haven't been granted the gift of travel.\n")
            return
    else:
        ch.huh()
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.level != merc.LEVEL_AVATAR or (not victim.special.is_set(merc.SPC_CHAMPION) and not victim.is_demon()):
        ch.send("Nothing happens.\n")
        return

    if not victim.in_room:
        ch.send("Nothing happens.\n")
        return

    if victim.position != merc.POS_STANDING:
        ch.send("You are unable to focus on their location.\n")
        return

    ch.send("You sink into the ground.\n")
    handler_game.act("$n sinks into the ground.", ch, None, None, merc.TO_ROOM)
    ch.in_room.get(ch)
    victim.in_room.put(ch)
    ch.cmd_look("")
    ch.send("You rise up out of the ground.\n")
    handler_game.act("$n rises up out of the ground.", ch, None, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="travel",
        cmd_fun=cmd_travel,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
