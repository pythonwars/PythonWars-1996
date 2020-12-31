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
import interp
import merc


def cmd_clanname(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire() and not ch.is_werewolf():
        ch.huh()
        return

    if ch.powers[merc.UNI_GEN] != 1:
        ch.huh()
        return

    if not arg:
        if ch.is_vampire():
            ch.send("Who's clan do you wish to name?\n")
        else:
            ch.send("Who do you wish to give a tribe to?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.powers[merc.UNI_GEN] != 2:
        if victim.is_werewolf():
            ch.send("Only greater werewolves may own a tribe.\n")
        else:
            ch.send("Only the Antediluvians may have clans.\n")
        return

    if victim.clan:
        ch.send("But they already have a clan!\n")
        return

    length = len(argument)
    if length not in merc.irange(3, 13) or not argument.isalpha():
        ch.send("Clan name should be between 3 and 13 letters long.\n")
        return

    victim.clan = argument
    ch.send("{} name set.\n".format("Clan" if victim.is_vampire() else "Tribe"))


interp.register_command(
    interp.CmdType(
        name="clanname",
        cmd_fun=cmd_clanname,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
