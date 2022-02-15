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

import handler_game
import handler_pc
import interp
import merc


# noinspection PyUnusedLocal
def cmd_report(ch, argument):
    hit_str = handler_pc.Pc.col_scale(ch.hit, ch.hit, ch.max_hit)
    mana_str = handler_pc.Pc.col_scale(ch.mana, ch.mana, ch.max_mana)
    move_str = handler_pc.Pc.col_scale(ch.move, ch.move, ch.max_move)
    exp_str = handler_pc.Pc.col_scale(ch.exp, ch.exp, 1000)

    buf = f"{hit_str}/#C{ch.max_hit:,}#n hp {mana_str}/#C{ch.max_mana:,}#n mana {move_str}/#C{ch.max_move:,}#n mv {exp_str} xp.\n"
    ch.send(f"You report: {buf}")
    handler_game.act(f"$n reports: {buf}", ch, None, None, merc.TO_ROOM, merc.POS_DEAD)


interp.register_command(
    interp.CmdType(
        name="report",
        cmd_fun=cmd_report,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
