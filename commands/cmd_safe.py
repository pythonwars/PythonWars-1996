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

import handler_game
import interp
import merc


# noinspection PyUnusedLocal
def cmd_safe(ch, argument):
    if ch.in_room.room_flags.is_set(merc.ROOM_SAFE):
        ch.send("You cannot be attacked by other players here.\n")
    else:
        ch.send("You are not safe from player attacks in this room.\n")

    if not ch.is_vampire():
        return

    if ch.in_room.sector_type == merc.SECT_INSIDE:
        ch.send("You are inside, which means you are safe from sunlight.\n")
        return

    if handler_game.weather_info.sunlight == merc.SUN_DARK:
        ch.send("It is not yet light out, so you are safe from the sunlight...for now.\n")
        return

    if ch.in_room.is_dark():
        ch.send("This room is dark, and will protect you from the sunlight.\n")
        return

    ch.send("This room will provide you no protection from the sunlight.\n")


interp.register_command(
    interp.CmdType(
        name="safe",
        cmd_fun=cmd_safe,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
