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


def cmd_release(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Syntax: release <object>\n")
        return

    item = ch.get_item_carry(arg)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    victim = item.chobj
    if not item:
        ch.send("There is nobody bound in that item.\n")
        return

    ch.send("Ok.\n")
    victim.obj_vnum = 0
    item.chobj = None
    victim.chobj = None
    victim.affected_by.rem_bit(merc.AFF_POLYMORPH)
    victim.extra.rem_bit(merc.EXTRA_OSWITCH)
    victim.morph = ""
    handler_game.act("A white vapour pours out of $p and forms into $n.", victim, item, None, merc.TO_ROOM)
    handler_game.act("Your spirit floats out of $p and reforms its body.", victim, item, None, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="release",
        cmd_fun=cmd_release,
        position=merc.POS_DEAD, level=1,
        log=merc.LOG_NEVER, show=True,
        default_arg=""
    )
)
