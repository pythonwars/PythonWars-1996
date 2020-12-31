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
#   Ported to Python by Davion of MudBytes.net using Miniboa
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

import const
import fight
import game_utils
import handler_game
import interp
import merc


def cmd_rescue(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Rescue whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim == ch:
        ch.send("What about fleeing instead?\n")
        return

    if not ch.is_npc() and victim.is_npc():
        ch.send("Doesn't need your help!\n")
        return

    if ch.fighting == victim:
        ch.send("Too late.\n")
        return

    fch = victim.fighting
    if not fch:
        ch.send("That person is not fighting right now.\n")
        return

    if fight.is_safe(ch, fch) or fight.is_safe(ch, victim):
        return

    ch.wait_state(const.skill_table["rescue"].beats)

    if not ch.is_npc() and game_utils.number_percent() > ch.learned["rescue"]:
        ch.send("You fail the rescue.\n")
        return

    handler_game.act("You rescue $N!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n rescues you!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n rescues $N!", ch, None, victim, merc.TO_NOTVICT)
    fight.stop_fighting(fch, False)
    fight.stop_fighting(victim, False)
    fight.check_killer(ch, fch)
    fight.set_fighting(ch, fch)
    fight.set_fighting(fch, ch)


interp.register_command(
    interp.CmdType(
        name="rescue",
        cmd_fun=cmd_rescue,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
