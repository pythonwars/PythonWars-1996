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
import instance
import interp
import merc


def cmd_order(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg or not argument:
        ch.send("Order whom to do what?\n")
        return

    if ch.is_affected(merc.AFF_CHARM):
        ch.send("You feel like taking, not giving, orders.\n")
        return

    if game_utils.str_cmp(arg, "all"):
        fall = True
        victim = None
    else:
        fall = False

        victim = ch.get_char_room(arg)
        if not victim:
            ch.not_here(arg)
            return

        if ch == victim:
            ch.not_self()
            return

        if (not victim.is_affected(merc.AFF_CHARM) or instance.characters[victim.master] != ch) and not (ch.is_vampire() and victim.is_vampire()):
            ch.send("Do it yourself!\n")
            return

        if ch.is_vampire() and victim.is_vampire() and (ch.powers[merc.UNI_GEN] != 2 or not game_utils.str_cmp(ch.clan, victim.clan)):
            handler_game.act("$N ignores your order.", ch, None, victim, merc.TO_CHAR)
            handler_game.act("You ignore $n's order.", ch, None, victim, merc.TO_VICT)
            return

    found = False
    for och_id in ch.in_room.people[:]:
        och = instance.characters[och_id]

        if och == ch:
            continue

        if (ch.is_affected(merc.AFF_CHARM) and instance.characters[och.master] == ch and (fall or och == victim)) or \
                (ch.powers[merc.UNI_GEN] == 2 and (fall or och == victim) and game_utils.str_cmp(ch.clan, och.clan)):
            found = True
            handler_game.act("$n orders you to '$t'.", ch, argument, och, merc.TO_VICT)
            och.interpret(argument)
        elif not ch.is_npc() and not och.is_npc() and (fall or och == victim) and ch.is_vampire() and och.is_vampire() and \
                ch.powers[merc.UNI_GEN] < och.powers[merc.UNI_GEN] and game_utils.str_cmp(ch.clan, och.clan):
            found = True
            handler_game.act("$n orders you to '$t'.", ch, argument, och, merc.TO_VICT)
            och.interpret(argument)

    if found:
        ch.send("Ok.\n")
    else:
        ch.send("You have no followers here.\n")


interp.register_command(
    interp.CmdType(
        name="order",
        cmd_fun=cmd_order,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
