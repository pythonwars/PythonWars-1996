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


# noinspection PyUnusedLocal
def cmd_shield(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_werewolf() or ch.powers[merc.WPOWER_OWL] < 2:
        if not ch.is_vampire():
            ch.huh()
            return

    if not ch.vampaff.is_set(merc.VAM_OBFUSCATE) and not ch.vampaff.is_set(merc.VAM_DOMINATE) and not ch.is_werewolf():
        ch.send("You are not trained in the Obfuscate or Dominate disciplines.\n")
        return

    if ch.is_vampire():
        if ch.blood < 60:
            ch.send("You have insufficient blood.\n")
            return

        ch.blood -= game_utils.number_range(50, 60)

    ch.immune.tog_bit(merc.IMM_SHIELDED)
    if ch.immune.is_set(merc.IMM_SHIELDED):
        ch.send("You shield your aura from those around you.\n")
    else:
        ch.send("You stop shielding your aura.\n")


interp.register_command(
    interp.CmdType(
        name="shield",
        cmd_fun=cmd_shield,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
