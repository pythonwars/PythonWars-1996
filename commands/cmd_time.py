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

import handler_game
import interp
import merc
import sys_utils


day_name = ["the Moon", "the Bull", "Deception", "Thunder", "Freedom",
            "the Great Gods", "the Sun"]
month_name = ["Winter", "the Winter Wolf", "the Frost Giant", "the Old Forces",
              "the Grand Struggle", "the Spring", "Nature", "Futility", "the Dragon",
              "the Sun", "the Heat", "the Battle", "the Dark Shades", "the Shadows",
              "the Long Shadows", "the Ancient Darkness", "the Great Evil"]


# noinspection PyUnusedLocal
def cmd_time(ch, argument):
    day = handler_game.time_info.day + 1

    if day in merc.irange(5, 19):
        suf = "th"
    elif day % 10 == 1:
        suf = "st"
    elif day % 10 == 2:
        suf = "nd"
    elif day % 10 == 3:
        suf = "rd"
    else:
        suf = "th"

    ch.send("It is {} o'clock {}, Day of {}, {}{} the Month of {}.\n".format(
        12 if (handler_game.time_info.hour % 12 == 0) else handler_game.time_info.hour % 12,
        "pm" if handler_game.time_info.hour >= 12 else "am",
        day_name[day % 7], day, suf, month_name[handler_game.time_info.month]))
    ch.send("God Wars started up at {}\n".format(sys_utils.systimestamp(merc.boot_time)))
    ch.send("The system time is {}\n".format(sys_utils.systimestamp(merc.current_time)))


interp.register_command(
    interp.CmdType(
        name="time",
        cmd_fun=cmd_time,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
