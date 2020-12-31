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

import handler_game
import interp
import merc


def cmd_reply(ch, argument):
    if not ch.is_npc() and ch.sentances.is_set(merc.SENT_SILENCE):
        ch.send("Your message didn't get through.\n")
        return

    if ch.extra.is_set(merc.EXTRA_GAGGED):
        ch.send("Your message didn't get through.\n")
        return

    if not argument:
        ch.send("Usage: reply <message>\n")
        return

    victim = ch.reply
    if not victim:
        ch.not_here("")
        return

    if not ch.is_immortal() and not victim.is_awake():
        handler_game.act("$E can't hear you.", ch, None, victim, merc.TO_CHAR)
        return

    if not victim.is_npc() and not victim.desc:
        handler_game.act("$E is currently link dead.", ch, None, victim, merc.TO_CHAR)
        return

    handler_game.act("#WYou tell $N '$t'.#n", ch, argument, victim, merc.TO_CHAR)
    handler_game.act("#W$n tells you '$t'.#n", ch, argument, victim, merc.TO_VICT, merc.POS_DEAD)
    victim.reply = ch


interp.register_command(
    interp.CmdType(
        name="reply",
        cmd_fun=cmd_reply,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
