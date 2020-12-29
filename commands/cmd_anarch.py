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

import comm
import interp
import merc


# noinspection PyUnusedLocal
def cmd_anarch(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if ch.clan:
        ch.send("But you are already in a clan!\n")
        return

    if ch.special.is_set(merc.SPC_INCONNU):
        ch.send("But you are already an Inconnu!\n")
        return

    if ch.special.is_set(merc.SPC_ANARCH):
        ch.send("You are no longer an Anarch.\n")
        comm.info("{} is no longer an Anarch!".format(ch.name))
        ch.special.rem_bit(merc.SPC_ANARCH)
        return

    ch.send("You are now an Anarch.\n")
    comm.info("{} is now an Anarch!".format(ch.name))
    ch.special.set_bit(merc.SPC_ANARCH)


interp.register_command(
    interp.CmdType(
        name="anarch",
        cmd_fun=cmd_anarch,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
