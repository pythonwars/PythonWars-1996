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


# Do_prompt from Morgenes from Aldara Mud
def cmd_prompt(ch, argument):
    if ch.is_npc():
        return

    if not argument:
        ch.cmd_help("prompt")
        return

    if game_utils.str_cmp(argument, "on"):
        if ch.extra.is_set(merc.EXTRA_PROMPT):
            ch.send("But you already have customised prompt on!\n")
        else:
            ch.send("Ok.\n")
            ch.extra.set_bit(merc.EXTRA_PROMPT)
    elif game_utils.str_cmp(argument, "off"):
        if not ch.extra.is_set(merc.EXTRA_PROMPT):
            ch.send("But you already have customised prompt off!\n")
        else:
            ch.send("Ok.\n")
            ch.extra.rem_bit(merc.EXTRA_PROMPT)
    elif game_utils.str_cmp(argument, "clear"):
        ch.prompt = ""
    else:
        argument = argument[:50] if len(argument) > 50 else argument
        ch.prompt = argument
        ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="prompt",
        cmd_fun=cmd_prompt,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
