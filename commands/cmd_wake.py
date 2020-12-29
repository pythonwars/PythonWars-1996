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
import handler_game
import interp
import merc


def cmd_wake(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.cmd_stand(argument)
        return

    if not ch.is_awake():
        ch.send("You are asleep yourself!\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_awake():
        handler_game.act("$N is already awake.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.is_affected(merc.AFF_SLEEP):
        handler_game.act("You can't wake $M!", ch, None, victim, merc.TO_CHAR)
        return

    if victim.position < merc.POS_SLEEPING:
        handler_game.act("$E doesn't respond!", ch, None, victim, merc.TO_CHAR)
        return

    handler_game.act("You wake $M.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n wakes you.", ch, None, victim, merc.TO_VICT, merc.POS_SLEEPING)
    victim.position = merc.POS_STANDING


interp.register_command(
    interp.CmdType(
        name="wake",
        cmd_fun=cmd_wake,
        position=merc.POS_SLEEPING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
