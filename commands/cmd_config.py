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

import game_utils
import interp
import merc


def cmd_config(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        buf = ["[ Keyword  ] Option\n"]
        buf += "[+ANSI     ] You have ansi colour on.\n" if ch.act.is_set(merc.PLR_ANSI) else "[-ansi     ] You have ansi colour off.\n"
        buf += "[+AUTOEXIT ] You automatically see exits.\n" if ch.act.is_set(merc.PLR_AUTOEXIT) else "[-autoexit ] You don't automatically see exits.\n"
        buf += "[+AUTOLOOT ] You automatically loot corpses.\n" if ch.act.is_set(merc.PLR_AUTOLOOT) else "[-autoloot ] You don't automatically loot corpses.\n"
        buf += "[+AUTOSAC  ] You automatically sacrifice corpses.\n" if ch.act.is_set(merc.PLR_AUTOSAC) else "[-autosac  ] You don't automatically sacrifice corpses.\n"
        buf += "[+BLANK    ] You have a blank line before your prompt.\n" if ch.act.is_set(merc.PLR_BLANK) else "[-blank    ] You have no blank line before your prompt.\n"
        buf += "[+BRIEF    ] You see brief descriptions.\n" if ch.act.is_set(merc.PLR_BRIEF) else "[-brief    ] You see long descriptions.\n"
        buf += "[+COMBINE  ] You see object lists in combined format.\n" if ch.act.is_set(merc.PLR_COMBINE) else "[-combine  ] You see object lists in single format.\n"
        buf += "[+PROMPT   ] You have a prompt.\n" if ch.act.is_set(merc.PLR_PROMPT) else "[-prompt   ] You don't have a prompt.\n"
        buf += "[+TELNETGA ] You receive a telnet GA sequence.\n" if ch.act.is_set(merc.PLR_TELNET_GA) else "[-telnetga ] You don't receive a telnet GA sequence.\n"
        buf += "[+SILENCE  ] You are silenced.\n" if ch.sentances.is_set(merc.SENT_SILENCE) else ""
        buf += "[-emote    ] You can't emote.\n" if ch.sentances.is_set(merc.SENT_NO_EMOTE) else ""
        buf += "[-tell     ] You can't use 'tell'.\n" if ch.sentances.is_set(merc.SENT_NO_TELL) else ""
        ch.send("".join(buf))
    else:
        if arg[0] == "+":
            fset = True
        elif arg[0] == "-":
            fset = False
        else:
            ch.send("Config -option or +option?\n")
            return

        arg = arg[1:]
        arg_list = [("ansi", merc.PLR_ANSI), ("autoexit", merc.PLR_AUTOEXIT), ("autoloot", merc.PLR_AUTOLOOT), ("autosac", merc.PLR_AUTOSAC),
                    ("blank", merc.PLR_BLANK), ("brief", merc.PLR_BRIEF), ("combine", merc.PLR_COMBINE), ("prompt", merc.PLR_PROMPT),
                    ("telnetga", merc.PLR_TELNET_GA)]
        for (aa, bb) in arg_list:
            if game_utils.str_cmp(arg, aa):
                bit = bb
                break
        else:
            ch.send("Config which option?\n")
            return

        if fset:
            ch.act.set_bit(bit)
        else:
            ch.act.rem_bit(bit)
        ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="config",
        cmd_fun=cmd_config,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
