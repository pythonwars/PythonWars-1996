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

import interp
import merc


def cmd_description(ch, argument):
    if argument:
        if argument[0] == '-':
            if not ch.description:
                ch.send("No lines left to remove.\n")
                return
            buf = ch.description.split('\n')
            buf.pop()
            ch.description = '\n'.join(buf)
            if len(buf) > 1:
                ch.send("Your description is:\n")
                ch.send(ch.description if ch.description else "(None).\n")
                return
            else:
                ch.description = ""
                ch.send("Description cleared.\n")
                return
        if argument[0] == '+':
            argument = argument[1:].lstrip()

            if len(argument) + len(ch.description) >= 1024:
                ch.send("Description too long.\n")
                return
            ch.description += argument + "\n"

    ch.send("Your description is:\n")
    ch.send(ch.description if ch.description else "(None).\n")


interp.register_command(
    interp.CmdType(
        name="description",
        cmd_fun=cmd_description,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
