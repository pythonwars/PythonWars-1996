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

import comm
import game_utils
import handler_game
import interp
import merc


def cmd_accept(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.marriage:
        if ch.extra.is_set(merc.EXTRA_MARRIED):
            ch.send("But you are already married!\n")
        else:
            ch.send("But you are already engaged!\n")
        return

    if not arg:
        ch.send("Who's proposal of marriage do you wish to accept?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.marriage:
        if victim.extra.is_set(merc.EXTRA_MARRIED):
            ch.send("But they are already married!\n")
        else:
            ch.send("But they are already engaged!\n")
        return

    if not victim.propose or victim.propose != ch:
        ch.send("But they haven't proposed to you!\n")
        return

    if (ch.sex == merc.SEX_MALE and victim.sex == merc.SEX_FEMALE) or (ch.sex == merc.SEX_FEMALE and victim.sex == merc.SEX_MALE):
        victim.propose = None
        ch.propose = None
        victim.marriage = ch.name
        ch.marriage = victim.name
        handler_game.act("You accept $S offer of marriage.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n accepts $N's offer of marriage.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n accepts your offer of marriage.", ch, None, victim, merc.TO_VICT)
        ch.save(force=True)
        victim.save(force=True)
        comm.info("{} and {} are now engaged!".format(ch.name, victim.name))
        return

    ch.send("I don't think that would be a very good idea...\n")


# noinspection PyUnusedLocal
def cmd_accep(ch, argument):
    ch.huh()


interp.register_command(
    interp.CmdType(
        name="accept",
        cmd_fun=cmd_accept,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
interp.register_command(
    interp.CmdType(
        name="accep",
        cmd_fun=cmd_accep,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
