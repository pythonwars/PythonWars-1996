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
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_vclan(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.clan or ch.special.is_set(merc.SPC_ANARCH):
        ch.send("But you don't belong to any clan!\n")
        return

    buf = ["The {} clan:\n".format(ch.clan)]
    buf += "[      Name      ] [ Gen ] [ Hits  % ] [ Mana  % ] [ Move  % ] [  Exp  ] [Blood]\n"

    for gch in list(instance.players.values()):
        if not gch.is_vampire() or not game_utils.str_cmp(ch.clan, gch.clan):
            continue

        buf += "[{:<16}] [  {}  ] [{:<6}{:3}] [{:<6}{:3}] [{:<6}{:3}] [{:7}] [ {:3} ]\n".format(ch.name, ch.powers[merc.UNI_GEN], gch.hit,
                                                                                                (gch.hit * 100 // gch.max_hit), gch.mana,
                                                                                                (gch.mana * 100 // gch.max_mana), gch.move,
                                                                                                (gch.move * 100 // gch.max_move), gch.exp, gch.blood)
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="vclan",
        cmd_fun=cmd_vclan,
        position=merc.POS_DEAD, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
