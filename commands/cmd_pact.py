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
import handler_game
import interp
import merc


def cmd_pact(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    can_sire = (ch.is_demon() or ch.special.is_set(merc.SPC_SIRE))
    if not can_sire:
        ch.send("You are not able to make a pact.\n")
        return

    if not ch.is_demon() and not ch.lord:
        ch.send("First you must find a demon lord.\n")
        return

    if not arg:
        ch.send("Make a pact with whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.is_mage():
        ch.send("You cannot make a pact with a mage.\n")
        return

    if victim.level != merc.LEVEL_AVATAR and not victim.is_immortal():
        ch.send("You can only make pacts with avatars.\n")
        return

    if not victim.immune.is_set(merc.IMM_DEMON):
        ch.send("You cannot make a pact with an unwilling person.\n")
        return

    if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
        ch.send("They have no soul to make a pact with!\n")
        return

    if victim.is_highlander():
        ch.send("You cannot make a pact with a highlander.\n")
        return

    if ch.exp < 666:
        ch.send("You cannot afford the 666 exp to make a pact.\n")
        return

    ch.exp -= 666
    handler_game.act("You make $N a demonic champion!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n makes $N a demonic champion!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n makes you a demonic champion!", ch, None, victim, merc.TO_VICT)
    victim.ch_class = ch.ch_class
    victim.special.set_bit(merc.SPC_CHAMPION)

    if victim.is_vampire():
        victim.mortalvamp()

    victim.act.rem_bit(merc.PLR_HOLYLIGHT)
    victim.act.rem_bit(merc.PLR_WIZINVIS)
    victim.special.rem_bit(merc.SPC_SIRE)
    victim.special.rem_bit(merc.SPC_ANARCH)
    victim.powers[merc.UNI_RAGE] = 0

    victim.morph = ""
    victim.clan = ""

    if ch.is_demon():
        victim.lord = ch.name
    else:
        victim.lord = ch.lord
    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="pact",
        cmd_fun=cmd_pact,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
