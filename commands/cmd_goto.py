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

import fight
import game_utils
import handler_game
import instance
import interp
import merc


def cmd_goto(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Goto where?\n")
        return

    location = game_utils.find_location(ch, arg)
    if not location:
        ch.send("No such location.\n")
        return

    if location.is_private():
        ch.send("That room is private right now.\n")
        return

    if ch.fighting:
        fight.stop_fighting(ch, True)

    for rch_id in ch.in_room.people[:]:
        rch = instance.characters[rch_id]
        if rch.trust >= ch.invis_level:
            if ch.is_npc() and ch.bamfout:
                handler_game.act("$t", ch, ch.bamfout, rch, merc.TO_VICT)
            else:
                handler_game.act("$n leaves in a swirling mist.", ch, None, rch, merc.TO_VICT)

    location.put(ch.in_room.get(ch))

    for rch_id in ch.in_room.people[:]:
        rch = instance.characters[rch_id]
        if rch.trust >= ch.invis_level:
            if ch.is_npc() and ch.bamfin:
                handler_game.act("$t", ch, ch.bamfin, rch, merc.TO_VICT)
            else:
                handler_game.act("$n appears in a swirling mist.", ch, None, rch, merc.TO_VICT)

    ch.cmd_look("auto")

    mount = ch.mount
    if mount:
        ch.in_room.put(mount.in_room.get(mount))
        mount.cmd_look("")


interp.register_command(
    interp.CmdType(
        name="goto",
        cmd_fun=cmd_goto,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
