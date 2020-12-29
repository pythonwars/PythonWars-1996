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
import handler_game
import interp
import merc


def cmd_mask(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_OBFUSCATE):
        ch.send("You are not trained in the Obfuscate discipline.\n")
        return

    if not arg:
        ch.send("Change to look like whom?\n")
        return

    if ch.is_affected(merc.AFF_POLYMORPH) and not ch.vampaff.is_set(merc.VAM_DISGUISED):
        ch.send("Not while polymorphed.\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.is_immortal() and victim != ch:
        ch.send("You can only mask avatars or lower.\n")
        return

    if ch.blood < 40:
        ch.send("You have insufficient blood.\n")
        return

    ch.blood -= game_utils.number_range(30, 40)

    if ch == victim:
        if not ch.is_affected(merc.AFF_POLYMORPH) and not ch.is_vampaff.is_set(merc.VAM_DISGUISED):
            ch.send("You already look like yourself!\n")
            return

        handler_game.act("Your form shimmers and transforms into $t.", ch, ch.name, victim, merc.TO_CHAR)
        handler_game.act("$t's form shimmers and transforms into $T.", ch, ch.morph, ch.name, merc.TO_ROOM)
        ch.affected_by.rem_bit(merc.AFF_POLYMORPH)
        ch.vampaff.rem_bit(merc.VAM_DISGUISED)
        ch.morph = ""
        return

    if ch.vampaff.is_set(merc.VAM_DISGUISED):
        handler_game.act("Your form shimmers and transforms into a clone of $N.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n's form shimmers and transforms into a clone of $N.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n's form shimmers and transforms into a clone of you!", ch, None, victim, merc.TO_VICT)
        ch.morph = victim.name
        return

    handler_game.act("Your form shimmers and transforms into a clone of $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n's form shimmers and transforms into a clone of $N.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n's form shimmers and transforms into a clone of you!", ch, None, victim, merc.TO_VICT)
    ch.affected_by.set_bit(merc.AFF_POLYMORPH)
    ch.vampaff.set_bit(merc.VAM_DISGUISED)
    ch.morph = victim.name


interp.register_command(
    interp.CmdType(
        name="mask",
        cmd_fun=cmd_mask,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
