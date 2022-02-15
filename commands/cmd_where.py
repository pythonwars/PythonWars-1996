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
import instance
import interp
import merc


def cmd_where(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        buf = ["Players near you:\n"]
        found = False
        for victim in list(instance.players.values()):
            if victim.in_room and victim.in_room.area == ch.in_room.area and not victim.chobj and ch.can_see(victim):
                found = True
                buf += f"{victim.name:<28} {victim.in_room.name}\n"

        if not found:
            buf += "None\n"
        ch.send("".join(buf))
    else:
        found = False
        for victim in list(instance.characters.values()):
            if victim.in_room and victim.in_room.area == ch.in_room.area and not victim.is_affected(merc.AFF_HIDE) and not victim.is_affected(merc.AFF_SNEAK) and \
                    ch.can_see(victim) and game_utils.is_name(arg, victim.name):
                found = True
                ch.send(f"{victim.pers(ch):<28} {victim.in_room.area}\n")
                break

        if not found:
            handler_game.act("You didn't find any $T.", ch, None, arg, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="where",
        cmd_fun=cmd_where,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
