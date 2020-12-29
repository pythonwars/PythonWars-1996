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


def cmd_freeze(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Freeze whom?\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    if victim.trust >= ch.trust:
        ch.send("You failed.\n")
        return

    victim.sentances.tog_bit(merc.SENT_FREEZE)
    if victim.sentances.is_set(merc.SENT_FREEZE):
        victim.send("You can't do ANYthing!\n")
        ch.send("FREEZE set.\n")
    else:
        victim.send("You can play again.\n")
        ch.send("FREEZE removed.\n")

    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="freeze",
        cmd_fun=cmd_freeze,
        position=merc.POS_DEAD, level=9,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
