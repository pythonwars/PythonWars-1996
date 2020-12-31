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
def cmd_champions(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not ch.lord and not ch.is_demon():
        ch.send("But you don't follow any demon!\n")
        return

    lord = ch.name if ch.is_demon() else ch.lord
    buf = ["The champions of {}:\n".format(lord)]
    buf += "[      Name      ] [ Hits ] [ Mana ] [ Move ] [  Exp  ] [       Power        ]\n"

    for gch in list(instance.players.values()):
        if not gch.is_demon() and not gch.special.is_set(merc.SPC_CHAMPION):
            continue

        if game_utils.str_cmp(ch.lord, lord) or game_utils.str_cmp(ch.name, lord):
            buf += "[{:<16}] [{:<6}] [{:<6}] [{:<6}] [{:7}] [ {:<9}{:9} ]\n".format(gch.name, gch.hit, gch.mana, gch.move, gch.exp,
                                                                                    gch.powers[merc.DEMON_CURRENT], gch.powers[merc.DEMON_TOTAL])

    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="champions",
        cmd_fun=cmd_champions,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
