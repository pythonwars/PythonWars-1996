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


def check_hunt(ch):
    in_room = ch.in_room
    if not ch.is_npc() and game_utils.number_percent() > ch.learned["track"]:
        ch.send("You cannot sense any trails from this room.\n")
        ch.hunting = ""
        return

    direction = 0
    dir_list = [merc.DIR_NORTH, merc.DIR_EAST, merc.DIR_SOUTH, merc.DIR_WEST]
    for aa in dir_list:
        if check_track(ch, aa):
            direction = ch.in_room.track_dir[aa]
            break
    else:
        victim = ch.get_char_room(ch.hunting)
        if not victim:
            ch.send("You cannot sense any trails from this room.\n")
            ch.hunting = ""
            return

    if not ch.hunting:
        return

    victim = ch.get_char_room(ch.hunting)
    if victim:
        return

    handler_game.act("$n carefully examines the ground for tracks.", ch, None, None, merc.TO_ROOM)
    ch.move_char(direction)

    if in_room == ch.in_room or victim:
        ch.hunting = ""


def check_track(ch, direction):
    if not ch.hunting:
        return False

    victim = ch.get_char_room(ch.hunting)
    if victim:
        handler_game.act("You have found $N!", ch, None, victim, merc.TO_CHAR)
        ch.hunting = ""
        return True

    if ch.hunting not in ch.in_room.track[direction]:
        return False

    handler_game.act("You sense the trail of $t leading $T from here.", ch, ch.hunting, merc.dir_name[direction], merc.TO_CHAR)
    return True


# noinspection PyUnusedLocal
def cmd_track(ch, argument):
    if not ch.is_npc() and game_utils.number_percent() > ch.learned["track"]:
        ch.send("You cannot sense any trails from this room.\n")
        return

    found = False
    for direction in range(merc.MAX_DIR):
        if check_track(ch, direction):
            found = True

    if not found:
        ch.send("You cannot sense any trails from this room.\n")
        return

    handler_game.act("$n carefully examines the ground for tracks.", ch, None, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="track",
        cmd_fun=cmd_track,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
