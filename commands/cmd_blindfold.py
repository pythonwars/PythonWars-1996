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


def cmd_blindfold(ch, argument):
    argument, arg = game_utils.read_word(argument)

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim == ch and not victim.extra.is_set(merc.EXTRA_BLINDFOLDED) and victim.extra.is_set(merc.EXTRA_TIED_UP):
        ch.send("You cannot blindfold yourself!\n")
        return

    if not victim.extra.is_set(merc.EXTRA_TIED_UP) and not victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
        ch.send("You can only blindfold someone who is tied up!\n")
        return

    if not victim.extra.is_set(merc.EXTRA_BLINDFOLDED):
        handler_game.act("You place a blindfold over $N's eyes.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n places a blindfold over $N's eyes.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n places a blindfold over your eyes.", ch, None, victim, merc.TO_VICT)
        victim.extra.set_bit(merc.EXTRA_BLINDFOLDED)
        return

    if ch == victim:
        handler_game.act("You remove the blindfold from your eyes.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n removes the blindfold from $s eyes.", ch, None, victim, merc.TO_ROOM)
        victim.extra.rem_bit(merc.EXTRA_BLINDFOLDED)
        return

    handler_game.act("You remove the blindfold from $N's eyes.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n removes the blindfold from $N's eyes.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n removes the blindfold from your eyes.", ch, None, victim, merc.TO_VICT)
    victim.extra.rem_bit(merc.EXTRA_BLINDFOLDED)


interp.register_command(
    interp.CmdType(
        name="blindfold",
        cmd_fun=cmd_blindfold,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
