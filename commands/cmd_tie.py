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

import comm
import game_utils
import handler_game
import interp
import merc


def cmd_tie(ch, argument):
    argument, arg = game_utils.read_word(argument)

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.extra.is_set(merc.EXTRA_TIED_UP):
        ch.send("But they are already tied up!\n")
        return

    if victim.position > merc.POS_STUNNED or victim.hit > 0:
        ch.send("You can only tie up a defenceless person.\n")
        return

    handler_game.act("You quickly tie up $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n quickly ties up $N.", ch, None, victim, merc.TO_ROOM)
    victim.send("You have been tied up!\n")
    victim.extra.set_bit(merc.EXTRA_TIED_UP)
    comm.info("{} has been tied up by {}.".format(victim.name, ch.name))


interp.register_command(
    interp.CmdType(
        name="tie",
        cmd_fun=cmd_tie,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
