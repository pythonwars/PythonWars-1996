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
import nanny


def cmd_pload(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc() or not ch.desc or not ch.in_room:
        return

    if not arg:
        ch.send("Syntax: pload <name>\n")
        return

    for wch in list(instance.players.values()):
        if game_utils.str_cmp(arg, wch.name):
            handler_game.act("$N is currently logged into the Mud.", ch, None, wch, merc.TO_CHAR)
            return

    arg = arg.title()
    if not nanny.check_parse_name(arg):
        ch.send("Thats an illegal name.\n")
        return

    pload = handler_pc.Pc.load(player_name=arg, silent=True)
    if not pload:
        ch.send("That player doesn't exist.\n")
        return

    ch.send("You transform into {}.\n".format(arg))
    handler_game.act("$n transforms into $t.", ch, arg, None, merc.TO_ROOM)
    d = ch.desc
    ch.save(force=True)
    in_room = ch.in_room
    ch.extract(True)
    d.character = None

    d.character = pload
    ch = d.character
    in_room.put(ch)


interp.register_command(
    interp.CmdType(
        name="pload",
        cmd_fun=cmd_pload,
        position=merc.POS_DEAD, level=12,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
