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


def cmd_smother(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        ch.send("Smother whom?\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if not victim.is_affected(merc.AFF_FLAMING):
        ch.send("But they are not on fire!\n")
        return

    if game_utils.number_percent() > ch.level * 2:
        handler_game.act("You try to smother the flames around $N but fail!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n tries to smother the flames around you but fails!", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n tries to smother the flames around $N but fails!", ch, None, victim, merc.TO_NOTVICT)

        if game_utils.number_percent() > 98 and not ch.is_affected(merc.AFF_FLAMING):
            handler_game.act("A spark of flame from $N's body sets you on fire!", ch, None, victim, merc.TO_CHAR)
            handler_game.act("A spark of flame from your body sets $n on fire!", ch, None, victim, merc.TO_VICT)
            handler_game.act("A spark of flame from $N's body sets $n on fire!", ch, None, victim, merc.TO_NOTVICT)
            ch.affected_by.set_bit(merc.AFF_FLAMING)
            ch.humanity()
        return

    handler_game.act("You manage to smother the flames around $M!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n manages to smother the flames around you!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n manages to smother the flames around $N!", ch, None, victim, merc.TO_NOTVICT)
    victim.affected_by.rem_bit(merc.AFF_FLAMING)
    ch.humanity()


interp.register_command(
    interp.CmdType(
        name="smother",
        cmd_fun=cmd_smother,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
