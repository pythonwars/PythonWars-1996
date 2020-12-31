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

import fight
import game_utils
import handler_game
import handler_room
import interp
import merc


# noinspection PyUnusedLocal
def cmd_recall(ch, argument):
    handler_game.act("Your body flickers with green energy.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n's body flickers with green energy.", ch, None, None, merc.TO_ROOM)

    location = handler_room.get_room_by_vnum(ch.home)
    if not location:
        location = handler_room.get_room_by_vnum(merc.ROOM_VNUM_TEMPLE)
        if not location:
            ch.send("You are completely lost.\n")
            return

    if ch.in_room == location:
        return

    if ch.in_room.room_flags.is_set(merc.ROOM_NO_RECALL) or ch.is_affected(merc.AFF_CURSE):
        ch.send("You are unable to recall.\n")
        return

    victim = ch.fighting
    if victim:
        if game_utils.number_bits(1) == 0:
            ch.wait_state(4)
            ch.send("You failed!\n")
            return

        ch.send("You recall from combat!\n")
        fight.stop_fighting(ch, True)

    handler_game.act("$n disappears.", ch, None, None, merc.TO_ROOM)
    ch.in_room.get(ch)
    location.put(ch)
    handler_game.act("$n appears in the room.", ch, None, None, merc.TO_ROOM)
    ch.cmd_look("auto")

    mount = ch.mount
    if mount:
        mount.in_room.get(mount)
        location.put(mount)


interp.register_command(
    interp.CmdType(
        name="recall",
        cmd_fun=cmd_recall,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="/",
        cmd_fun=cmd_recall,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
