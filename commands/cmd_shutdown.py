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
import game_utils
import handler_ch
import instance
import interp
import merc
import pywars
import settings


# noinspection PyUnusedLocal
def cmd_shutdown(ch, argument):
    buf = "Shutdown by {}.".format(ch.name)
    ch.cmd_echo(buf)
    game_utils.append_file(ch, settings.SHUTDOWN_FILE, buf)
    comm.done = True

    for d in instance.descriptor_list[:]:
        vch = handler_ch.ch_desc(d)
        if vch:
            vch.save(logout=True, force=True)
            comm.close_socket(d)

    if pywars.server:
        pywars.server.stop()


# noinspection PyUnusedLocal
def cmd_shutdow(ch, argument):
    ch.send("If you want to SHUTDOWN, spell it out.\n")


interp.register_command(
    interp.CmdType(
        name="shutdown",
        cmd_fun=cmd_shutdown,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="shutdow",
        cmd_fun=cmd_shutdow,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_NORMAL, show=False,
        default_arg=""
    )
)
