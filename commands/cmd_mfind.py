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


def cmd_mfind(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Mfind whom?\n")
        return

    buf = []
    fall = game_utils.str_cmp(arg, "all")
    nmatch = 0

    # Yeah, so iterating over all vnum's takes 10,000 loops.
    # Get_mob_index is fast, and I don't feel like threading another link.
    # Do you?
    # -- Furey
    for mob in list(instance.npc_templates.values()):
        if fall or game_utils.is_name(arg, mob.name):
            nmatch += 1
            buf += f"[{mob.vnum:5}] {mob.short_descr}\n"

    if nmatch == 0:
        buf += "Nothing like that in hell, earth, or heaven.\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="mfind",
        cmd_fun=cmd_mfind,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
