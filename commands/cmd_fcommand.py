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


# TODO - Known broken - NPCs can't access command interpreter (as of yet)
def cmd_fcommand(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire() and ch.level < merc.LEVEL_APPRENTICE:
        ch.huh()
        return

    if ch.is_vampire() and not ch.vampaff.is_set(merc.VAM_DOMINATE):
        ch.send("You are not trained in the Dominate discipline.\n")
        return

    victim = ch.familiar
    if not victim:
        ch.send("But you don't have a familiar!\n")
        return

    if not argument:
        ch.send("What do you wish to make your familiar do?\n")
        return

    victim.interpret(argument)


interp.register_command(
    interp.CmdType(
        name="[",
        cmd_fun=cmd_fcommand,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="fcommand",
        cmd_fun=cmd_fcommand,
        position=merc.POS_STANDING, level=4,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
