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

import comm
import game_utils
import interp
import merc


def cmd_marry(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax: marry <person> <person>\n")
        return

    victim1 = ch.get_char_room(arg1)
    if not victim1:
        ch.not_here(arg1)
        return

    victim2 = ch.get_char_room(arg2)
    if not victim2:
        ch.not_here(arg2)
        return

    if victim1.is_npc() or victim2.is_npc():
        ch.not_npc()
        return

    if victim1.act.is_set(merc.PLR_GODLESS) and ch.level < merc.NO_GODLESS:
        ch.send("You failed.\n")
        return

    if victim2.act.is_set(merc.PLR_GODLESS) and ch.level < merc.NO_GODLESS:
        ch.send("You failed.\n")
        return

    if game_utils.str_cmp(victim1.name, victim2.marriage) and game_utils.str_cmp(victim2.name, victim1.marriage):
        victim1.extra.set_bit(merc.EXTRA_MARRIED)
        victim2.extra.set_bit(merc.EXTRA_MARRIED)
        victim1.save(force=True)
        victim2.save(force=True)
        comm.info(f"{victim1.name} and {victim2.name} are now married!")
        return

    ch.send("But they are not yet engaged!\n")


interp.register_command(
    interp.CmdType(
        name="marry",
        cmd_fun=cmd_marry,
        position=merc.POS_DEAD, level=9,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
