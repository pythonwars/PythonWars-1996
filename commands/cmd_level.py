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


# noinspection PyUnusedLocal
def cmd_level(ch, argument):
    if ch.is_npc():
        return

    buf = ["---------------------------=[Weapon Levels]=--------------------------------\n"]
    col = 0
    level_list = [("Slice", merc.WPN_SLICE), ("Stab", merc.WPN_STAB), ("Slash", merc.WPN_SLASH), ("Whip", merc.WPN_WHIP), ("Claw", merc.WPN_CLAW),
                  ("Blast", merc.WPN_BLAST), ("Pound", merc.WPN_POUND), ("Crush", merc.WPN_CRUSH), ("Grep", merc.WPN_GREP), ("Bite", merc.WPN_BITE),
                  ("Pierce", merc.WPN_PIERCE), ("Suck", merc.WPN_SUCK), ("Unarmed", merc.WPN_UNARMED)]
    for (aa, bb) in level_list:
        buf += "{:8}: {:<4}  ".format(aa, ch.wpn[bb])

        col += 1
        if col % 5 == 0:
            buf += "\n"
    if col % 5 != 0:
        buf += "\n"

    buf += "\n---------------------------=[Stance Levels]=--------------------------------\n"
    col = 0
    level_list = [("Viper", merc.STANCE_VIPER), ("Crane", merc.STANCE_CRANE), ("Crab", merc.STANCE_CRAB), ("Mongoose", merc.STANCE_MONGOOSE),
                  ("Bull", merc.STANCE_BULL), ("Mantis", merc.STANCE_MANTIS), ("Dragon", merc.STANCE_DRAGON), ("Tiger", merc.STANCE_TIGER),
                  ("Monkey", merc.STANCE_MONKEY), ("Swallow", merc.STANCE_SWALLOW)]
    for (aa, bb) in level_list:
        buf += "{:8}: {:<4}".format(aa, ch.stance[bb])

        col += 1
        if col % 5 == 0:
            buf += "\n"
    if col % 5 != 0:
        buf += "\n"

    buf += "\n---------------------------=[Spell Levels]=---------------------------------\n"
    col = 0
    level_list = [("Purple", merc.PURPLE_MAGIC), ("Blue", merc.BLUE_MAGIC), ("Red", merc.RED_MAGIC), ("Green", merc.GREEN_MAGIC),
                  ("Yellow", merc.YELLOW_MAGIC)]
    for (aa, bb) in level_list:
        buf += "{:8}: {:<4}".format(aa, ch.spl[bb])

        col += 1
        if col % 5 == 0:
            buf += "\n"
    if col % 5 != 0:
        buf += "\n"

    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="level",
        cmd_fun=cmd_level,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
