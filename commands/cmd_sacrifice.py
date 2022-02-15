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
import state_checks


def cmd_sacrifice(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Sacrifice what?\n")
        return

    item = ch.get_item_list(arg, ch.in_room.items)
    if not item:
        ch.send("You can't find it.\n")
        return

    if not item.flags.take or item.item_type in [merc.ITEM_QUEST, merc.ITEM_MONEY, merc.ITEM_TREASURE, merc.ITEM_QUESTCARD] or \
            item.flags.artifact or item.questowner and not game_utils.str_cmp(ch.name, item.questowner):
        handler_game.act("You are unable to drain any energy from $p.", ch, item, None, merc.TO_CHAR)
        return
    elif item.chobj and not item.chobj.is_npc() and item.chobj.obj_vnum != 0:
        handler_game.act("You are unable to drain any energy from $p.", ch, item, None, merc.TO_CHAR)
        return

    expgain = item.cost // 100
    expgain = state_checks.urange(1, expgain, 50)
    ch.exp += expgain
    handler_game.act(f"You drain {expgain} exp of energy from $p.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p disintegrates into a fine powder.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n drains the energy from $p.", ch, item, None, merc.TO_ROOM)
    handler_game.act("$p disintegrates into a fine powder.", ch, item, None, merc.TO_ROOM)

    if item.points > 0 and not ch.is_npc() and item.item_type != merc.ITEM_PAGE:
        handler_game.act(f"You receive a refund of {item.points} quest points from $p.", ch, item, None, merc.TO_CHAR)
        ch.quest += item.points
    item.extract()


interp.register_command(
    interp.CmdType(
        name="sacrifice",
        cmd_fun=cmd_sacrifice,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
