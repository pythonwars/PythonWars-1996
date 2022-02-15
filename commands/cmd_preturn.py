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
import handler_pc
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_preturn(ch, argument):
    if ch.is_npc():
        return

    arg = ch.pload.title()
    if not ch.pload or game_utils.str_cmp(ch.name, arg):
        ch.huh()
        return

    pload = handler_pc.Pc.load(player_name=arg, silent=True)
    if not pload:
        ch.send("That player doesn't exist.\n")
        return

    d = ch.desc
    ch.send(f"You transform back into {arg}.\n")
    handler_game.act("$n transforms back into $t.", ch, arg, None, merc.TO_ROOM)
    ch.save(force=True)

    if ch and ch.desc:
        ch.extract(True)
    elif ch:
        ch.extract(True)

    if ch.desc:
        ch.desc.character = pload

    if ch.in_room:
        ch.in_room.put(ch)
    else:
        room_id = instance.instances_by_room[merc.ROOM_VNUM_TEMPLE][0]
        instance.rooms[room_id].put(ch)
    ch.pload = ""


interp.register_command(
    interp.CmdType(
        name="preturn",
        cmd_fun=cmd_preturn,
        position=merc.POS_DEAD, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
