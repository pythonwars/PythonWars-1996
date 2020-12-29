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


def cmd_ntrust(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Syntax: ntrust <char> <on/off>.\n")
        return

    if not arg2:
        ch.send("Do you wish to set ntrust ON or OFF?\n")
        return

    victim = ch.get_char_room(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if game_utils.str_cmp(arg2, "off"):
        if not victim.extra.is_set(merc.EXTRA_TRUSTED):
            ch.send("Their ntrust is already off.\n")
            return

        victim.extra.rem_bit(merc.EXTRA_NOTE_TRUST)
        ch.send("Note trust OFF.\n")
        victim.send("You are no longer note trusted.\n")
    elif game_utils.str_cmp(arg2, "on"):
        if victim.extra.is_set(merc.EXTRA_NOTE_TRUST):
            ch.send("Their ntrust is already on.\n")
            return

        victim.extra.set_bit(merc.EXTRA_NOTE_TRUST)
        ch.send("Note trust ON.\n")
        victim.send("You are now note trusted.\n")
    else:
        ch.send("Do you want to set their ntrust ON or OFF?\n")


interp.register_command(
    interp.CmdType(
        name="ntrust",
        cmd_fun=cmd_ntrust,
        position=merc.POS_DEAD, level=10,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
