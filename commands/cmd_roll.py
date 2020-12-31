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
import interp
import merc


def cmd_roll(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not ch.dempower.is_set(merc.DEM_MOVE):
        ch.send("You haven't been granted the gift of movement.\n")
        return

    item = ch.chobj
    if not item:
        ch.huh()
        return

    if not item.chobj or item.chobj != ch:
        ch.huh()
        return

    if not item.in_room:
        ch.send("You are unable to move.\n")
        return

    if game_utils.str_cmp(arg, ["n", "north"]):
        ch.cmd_north("")
    elif game_utils.str_cmp(arg, ["s", "south"]):
        ch.cmd_south("")
    elif game_utils.str_cmp(arg, ["e", "east"]):
        ch.cmd_east("")
    elif game_utils.str_cmp(arg, ["w", "west"]):
        ch.cmd_west("")
    elif game_utils.str_cmp(arg, ["u", "up"]):
        ch.cmd_up("")
    elif game_utils.str_cmp(arg, ["d", "down"]):
        ch.cmd_down("")
    else:
        ch.send("Do you wish to roll north, south, east, west, up or down?\n")
        return

    item.in_room.get(item)
    ch.in_room.put(item)


interp.register_command(
    interp.CmdType(
        name="roll",
        cmd_fun=cmd_roll,
        position=merc.POS_RESTING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
