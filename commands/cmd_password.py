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
import interp
import merc


def cmd_password(ch, argument):
    if ch.is_npc():
        return

    # Can't use read_word here because it smashes case.
    # So we just steal all its code.  Bleagh.
    # -- It actually doesn't now because it loads areas too. Davion.
    argument, arg1 = game_utils.read_word(argument, to_lower=False)
    argument, arg2 = game_utils.read_word(argument, to_lower=False)

    if not arg1 or not arg2:
        ch.send("Syntax: password <old> <new>\n")
        return

    if arg1 != ch.pwd:
        ch.wait_state(40)
        ch.send("Wrong password.  Wait 10 seconds.\n")
        return

    if len(arg2) < 5:
        ch.send("New password must be at least five characters long.\n")
        return

    ch.pwd = arg2
    ch.save(force=True)
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="password",
        cmd_fun=cmd_password,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NEVER, show=True,
        default_arg=""
    )
)
