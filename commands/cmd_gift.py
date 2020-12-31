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


def cmd_gift(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.exp < 500:
        ch.send("It costs 500 exp to make a gift of an item.\n")
        return

    if not arg1 or not arg2:
        ch.send("Make a gift of which object to whom?\n")
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    victim = ch.get_char_room(arg2)
    if not victim:
        ch.not_here(arg2)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if not item.questowner:
        ch.send("That item has not yet been claimed.\n")
        return

    if not game_utils.str_cmp(ch.name, item.questowner):
        ch.send("But you don't own it!\n")
        return

    ch.exp -= 500
    item.questowner = victim.name
    handler_game.act("You grant ownership of $p to $N.", ch, item, victim, merc.TO_CHAR)
    handler_game.act("$n grants ownership of $p to $N.", ch, item, victim, merc.TO_NOTVICT)
    handler_game.act("$n grants ownership of $p to you.", ch, item, victim, merc.TO_VICT)


interp.register_command(
    interp.CmdType(
        name="gift",
        cmd_fun=cmd_gift,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
