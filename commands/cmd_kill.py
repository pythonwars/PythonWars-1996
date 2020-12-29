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

import fight
import game_utils
import handler_game
import instance
import interp
import merc


def cmd_kill(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Kill whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim == ch:
        ch.send("You cannot kill yourself.\n")
        return

    if fight.is_safe(ch, victim):
        return

    if ch.is_affected(merc.AFF_CHARM) and instance.characters[ch.master] == victim:
        handler_game.act("$N is your beloved master.", ch, None, victim, merc.TO_CHAR)
        return

    if ch.position == merc.POS_FIGHTING:
        ch.send("You do the best you can!\n")
        return

    ch.wait_state(merc.PULSE_VIOLENCE)
    fight.check_killer(ch, victim)

    if not ch.is_npc() and ch.is_werewolf() and game_utils.number_range(1, 3) == 1 and \
            ch.powers[merc.WPOWER_BOAR] > 1 and victim.position == merc.POS_STANDING:
        handler_game.act("You charge into $N, knocking $M from $S feet.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n charge into $N, knocking $M from $S feet.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n charge into you, knocking you from your feet.", ch, None, victim, merc.TO_VICT)
        victim.position = merc.POS_STUNNED
        fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)
        fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)
        return

    fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)


interp.register_command(
    interp.CmdType(
        name="kill",
        cmd_fun=cmd_kill,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
