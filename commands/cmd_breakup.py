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

import comm
import game_utils
import handler_game
import interp
import merc


def cmd_breakup(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.marriage:
        if ch.extra.is_set(merc.EXTRA_MARRIED):
            ch.send("You'll have to get divorced.\n")
            return
    else:
        ch.send("But you are not even engaged!\n")
        return

    if not arg:
        ch.send("Who do you wish to break up with?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.marriage:
        if victim.extra.is_set(merc.EXTRA_MARRIED):
            ch.send("They'll have to get divorced.\n")
            return
    else:
        ch.send("But they are not even engaged!\n")
        return

    if game_utils.str_cmp(ch.name, victim.marriage) and game_utils.str_cmp(victim.name, ch.marriage):
        victim.marriage = ""
        ch.marriage = ""
        handler_game.act("You break off your engagement with $M.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n breaks off $n engagement with $N.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n breaks off $s engagement with you.", ch, None, victim, merc.TO_VICT)
        ch.save(force=True)
        victim.save(force=True)
        comm.info("{} and {} have broken up!".format(ch.name, victim.name))

    ch.send("You are not engaged to them.\n")


# noinspection PyUnusedLocal
def cmd_breaku(ch, argument):
    ch.huh()


interp.register_command(
    interp.CmdType(
        name="breakup",
        cmd_fun=cmd_breakup,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="breaku",
        cmd_fun=cmd_breaku,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
