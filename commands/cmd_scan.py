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
import instance
import interp
import merc


def spydirection(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        return

    if game_utils.str_cmp(arg, ["n", "north"]):
        door = merc.DIR_NORTH
    elif game_utils.str_cmp(arg, ["e", "east"]):
        door = merc.DIR_EAST
    elif game_utils.str_cmp(arg, ["s", "south"]):
        door = merc.DIR_SOUTH
    elif game_utils.str_cmp(arg, ["w", "west"]):
        door = merc.DIR_WEST
    elif game_utils.str_cmp(arg, ["u", "up"]):
        door = merc.DIR_UP
    elif game_utils.str_cmp(arg, ["d", "down"]):
        door = merc.DIR_DOWN
    else:
        return

    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        ch.send("   No exit.\n")
        return

    if pexit.exit_info.is_set(merc.EX_CLOSED):
        ch.send("   Closed door.\n")
        return

    ch.in_room.get(ch)
    to_room.put(ch)

    is_empty = True
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]

        if vch == ch or not ch.can_see(vch):
            continue

        if vch.is_npc():
            buf = "   {}\n".format(vch.short_descr)
        elif vch.is_affected(merc.AFF_POLYMORPH):
            buf = "   {} (Player)\n".format(vch.morph)
        else:
            buf = "   {} (Player)\n".format(vch.name)
        ch.send(buf)
        is_empty = False

    if is_empty:
        ch.send("   Nobody here.\n")


# noinspection PyUnusedLocal
def cmd_scan(ch, argument):
    location = ch.in_room

    ch.send("[North]\n")
    spydirection(ch, "n")
    ch.in_room.get(ch)
    location.put(ch)

    ch.send("[East]\n")
    spydirection(ch, "e")
    ch.in_room.get(ch)
    location.put(ch)

    ch.send("[South]\n")
    spydirection(ch, "s")
    ch.in_room.get(ch)
    location.put(ch)

    ch.send("[West]\n")
    spydirection(ch, "w")
    ch.in_room.get(ch)
    location.put(ch)

    ch.send("[Up]\n")
    spydirection(ch, "u")
    ch.in_room.get(ch)
    location.put(ch)

    ch.send("[Down]\n")
    spydirection(ch, "d")
    ch.in_room.get(ch)
    location.put(ch)


interp.register_command(
    interp.CmdType(
        name="scan",
        cmd_fun=cmd_scan,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
