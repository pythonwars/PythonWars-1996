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

import comm
import handler_ch
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_reboot(ch, argument):
    ch.cmd_echo("Reboot by {}.".format(ch.name))
    comm.down = True

    for d in instance.descriptor_list[:]:
        vch = handler_ch.ch_desc(d)
        if vch:
            vch.save(logout=True, force=True)
            comm.close_socket(d)


# noinspection PyUnusedLocal
def cmd_reboo(ch, argument):
    ch.send("If you want to REBOOT, spell it out.\n")


interp.register_command(
    interp.CmdType(
        name="reboot",
        cmd_fun=cmd_reboot,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="reboo",
        cmd_fun=cmd_reboo,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_NORMAL, show=False,
        default_arg=""
    )
)
