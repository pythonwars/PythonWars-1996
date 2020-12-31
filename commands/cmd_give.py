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


def cmd_give(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Give what to whom?\n")
        return

    if arg1.isdigit():
        # 'give NNNN coins victim'

        amount = int(arg1)
        if amount <= 0 or (not game_utils.str_cmp(arg2, ["coins", "coin"])):
            ch.send("Sorry, you can't do that.\n")
            return

        argument, arg2 = game_utils.read_word(argument)

        if not arg2:
            ch.send("Give what to whom?\n")
            return

        victim = ch.get_char_room(arg2)
        if not victim:
            ch.not_here(arg2)
            return

        if victim.is_affected(merc.AFF_ETHEREAL):
            ch.send("You cannot give things to ethereal people.\n")
            return

        if ch.gold < amount:
            ch.send("You haven't got that much gold.\n")
            return

        ch.gold -= amount
        victim.gold += amount
        handler_game.act("$n gives you some gold.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n gives $N some gold.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("You give $N some gold.", ch, None, victim, merc.TO_CHAR)
        ch.send("Ok.\n")
        ch.save(force=True)
        victim.save(force=True)
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You do not have that item.\n")
        return

    if item.equipped_to:
        ch.send("You must remove it first.\n")
        return

    victim = ch.get_char_room(arg2)
    if not victim:
        ch.not_here(arg2)
        return

    if not ch.can_drop_item(item):
        ch.send("You can't let go of it.\n")
        return

    if victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot give things to ethereal people.\n")
        return

    if victim.carry_number + item.get_number() > victim.can_carry_n():
        handler_game.act("$N has $S hands full.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.carry_weight + item.get_weight() > victim.can_carry_w():
        handler_game.act("$N can't carry that much weight.", ch, None, victim, merc.TO_CHAR)
        return

    if not victim.can_see_item(item):
        handler_game.act("$N can't see it.", ch, None, victim, merc.TO_CHAR)
        return

    ch.get(item)
    victim.put(item)
    handler_game.act("$n gives $p to $N.", ch, item, victim, merc.TO_NOTVICT)
    handler_game.act("$n gives you $p.", ch, item, victim, merc.TO_VICT)
    handler_game.act("You give $p to $N.", ch, item, victim, merc.TO_CHAR)
    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="give",
        cmd_fun=cmd_give,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
