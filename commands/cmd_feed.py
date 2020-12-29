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


def cmd_feed(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if not victim.is_vampire():
        ch.send("Blood does them no good at all.\n")
        return

    if not victim.immune.is_set(merc.IMM_VAMPIRE):
        ch.send("They refuse to drink your blood.\n")
        return

    if ch.blood < 20:
        ch.send("You don't have enough blood.\n")
        return

    blood = game_utils.number_range(5, 10)
    ch.blood -= (blood * 2)
    victim.blood += blood

    handler_game.act("You cut open your wrist and feed some blood to $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n cuts open $s wrist and feeds some blood to $N.", ch, None, victim, merc.TO_NOTVICT)

    if victim.position < merc.POS_RESTING:
        victim.send("You feel some blood poured down your throat.\n")
    else:
        handler_game.act("$n cuts open $s wrist and feeds you some blood.", ch, None, victim, merc.TO_VICT)


interp.register_command(
    interp.CmdType(
        name="feed",
        cmd_fun=cmd_feed,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
