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


def cmd_clearvamp(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Clear who's clan?\n")
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

    if victim.is_vampire():
        victim.mortalvamp()

    victim.lord = ""
    victim.clan = ""
    victim.powers[merc.UNI_GEN] = 0
    victim.powers[merc.UNI_AFF] = 0
    victim.powers[merc.UNI_CURRENT] = -1

    victim.special.rem_bit(merc.SPC_SIRE)
    victim.special.rem_bit(merc.SPC_PRINCE)
    victim.special.rem_bit(merc.SPC_ANARCH)
    victim.powers[merc.UNI_RAGE] = 0
    victim.rank = merc.AGE_CHILDE
    ch.send("Ok.\n")


# noinspection PyUnusedLocal
def cmd_clearvam(ch, argument):
    ch.send("If you want to CLEARVAMP, spell it out.\n")


interp.register_command(
    interp.CmdType(
        name="clearvamp",
        cmd_fun=cmd_clearvamp,
        position=merc.POS_STANDING, level=11,
        log=merc.LOG_ALWAYS, show=False,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="clearvam",
        cmd_fun=cmd_clearvam,
        position=merc.POS_STANDING, level=11,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
