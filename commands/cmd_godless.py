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
import interp
import merc


def cmd_godless(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        ch.send("Do you wish to switch it ON or OFF?\n")
        return

    if ch.level != 3 and not ch.act.is_set(merc.PLR_GODLESS):
        ch.send("Sorry, you must be level 3.\n")
        return

    if ch.act.is_set(merc.PLR_GODLESS) and game_utils.str_cmp(arg, "off"):
        ch.act.rem_bit(merc.PLR_GODLESS)
        ch.send("You now obey the gods.\n")
        comm.info(f"{ch.name} now follows the whims of the gods.")
    elif not ch.act.is_set(merc.PLR_GODLESS) and game_utils.str_cmp(arg, "off"):
        ch.send("But you already obey the gods!\n")
    elif not ch.act.is_set(merc.PLR_GODLESS) and game_utils.str_cmp(arg, "on"):
        ch.act.set_bit(merc.PLR_GODLESS)
        ch.send("You no longer obey the gods.\n")
        comm.info(f"{ch.name} has rejected the gods.")
    elif ch.act.is_set(merc.PLR_GODLESS) and game_utils.str_cmp(arg, "on"):
        ch.send("But you have already rejected the gods!\n")
    else:
        ch.send("Do you wish to switch it ON or OFF?\n")


interp.register_command(
    interp.CmdType(
        name="godless",
        cmd_fun=cmd_godless,
        position=merc.POS_DEAD, level=3,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
