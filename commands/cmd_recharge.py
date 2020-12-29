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
import instance
import interp
import merc
import state_checks
import object_creator


def cmd_recharge(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Syntax: recharge <quest card> <quest machine>\n")
        return

    card = ch.get_item_carry(arg1)
    if not card:
        ch.send("You are not carrying that object.\n")
        return

    if card.item_type != merc.ITEM_QUESTCARD:
        ch.send("That is not a quest card.\n")
        return

    machine = ch.get_item_here(arg2)
    if not machine:
        ch.send("There is nothing for you to recharge it with.\n")
        return

    if machine.item_type != merc.ITEM_QUESTMACHINE:
        ch.send("That is not a quest machine.\n")
        return

    count = 0
    for i in range(4):
        if card.value[i] == -1:
            count += 1

    if count == 4:
        card.quest_object()
    else:
        ch.send("You have not yet completed the current quest.\n")
        return

    handler_game.act("You place $p into a small slot in $P.", ch, card, machine, merc.TO_CHAR)
    handler_game.act("$n places $p into a small slot in $P.", ch, card, machine, merc.TO_ROOM)
    handler_game.act("$P makes a few clicks and returns $p.", ch, card, machine, merc.TO_CHAR)
    handler_game.act("$P makes a few clicks and returns $p.", ch, card, machine, merc.TO_ROOM)
    value = state_checks.urange(1, card.level, 50)

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PROTOPLASM], 0)
    item.name = "quest token"
    item.short_descr = "a {} point quest token".format(value)
    item.description = "A {} point quest token lies on the floor.".format(value)
    item.value[0] = value
    item.level = value
    item.cost = value * 1000
    item.item_type = merc.ITEM_QUEST
    item.questmaker = ch.name
    ch.put(item)
    handler_game.act("You take $p from $P.", ch, item, machine, merc.TO_CHAR)
    handler_game.act("$n takes $p from $P.", ch, item, machine, merc.TO_ROOM)

    if not ch.is_npc():
        ch.score[merc.SCORE_NUM_QUEST] += 1
        ch.score[merc.SCORE_QUEST] += value

    comm.info("{} has completed a quest!".format(ch.name if not ch.is_npc() else ch.short_descr))
    ch.save(force=True)


interp.register_command(
    interp.CmdType(
        name="recharge",
        cmd_fun=cmd_recharge,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
