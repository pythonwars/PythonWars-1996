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

import game_utils
import handler_game
import interp
import merc


def cmd_pray(ch, argument):
    handler_game.act("You mutter a few prayers.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n mutters a quick prayer.", ch, None, None, merc.TO_ROOM)

    if ch.is_npc() or (not ch.is_immortal() and not game_utils.str_cmp(ch.ch_class.name, "demon")):
        return

    if not argument:
        if ch.special.is_set(merc.SPC_DEMON_LORD):
            ch.send("What do you wish to pray?\n")
            return

        if ch.powers[merc.DEMON_CURRENT] < 1:
            ch.send("Nothing happens.\n")
            return

        victim = ch.get_char_world(ch.lord)
        if not victim:
            ch.send("Nothing happens.\n")
            return

        handler_game.act("You hear $n's prayers in your mind.", ch, None, victim, merc.TO_VICT)
        victim.send("You feel energy pour into your body.\n")

        if ch.powers[merc.DEMON_CURRENT] == 1:
            ch.send("You receive a single point of energy.\n")
        else:
            ch.send(f"You receive {ch.powers[merc.DEMON_CURRENT]:,} points of energy.\n")

        handler_game.act("$n is briefly surrounded by a halo of energy.", victim, None, None, merc.TO_ROOM)
        victim.powers[merc.DEMON_CURRENT] += ch.powers[merc.DEMON_CURRENT]
        victim.powers[merc.DEMON_TOTAL] += ch.powers[merc.DEMON_CURRENT]
        ch.powers[merc.DEMON_CURRENT] = 0
        return

    if ch.channels.is_set(merc.CHANNEL_PRAY):
        ch.send("But you're not even on the channel!\n")
        return

    ch.talk_channel(argument, merc.CHANNEL_PRAY, "pray")


interp.register_command(
    interp.CmdType(
        name="pray",
        cmd_fun=cmd_pray,
        position=merc.POS_MEDITATING, level=1,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
