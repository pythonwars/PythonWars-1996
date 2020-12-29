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
import object_creator


def cmd_token(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc() or (ch.quest < 1 and not ch.is_judge()):
        ch.send("You are unable to make a quest token.\n")
        return

    if not arg1 or not arg1.isdigit():
        ch.send("Please specify a value for the quest token.\n")
        return

    value = int(arg1)
    if value not in merc.irange(1, 100):
        ch.send("Quest token should have a value between 1 and 100.\n")
        return

    if ch.quest < value and not ch.is_judge():
        ch.send("You only have {:,} quest points left to put into tokens.\n".format(ch.quest))
        return

    if arg2:
        victim = ch.get_char_room(arg2)
        if not victim:
            ch.not_here(arg2)
            return
    else:
        victim = None

    obj_index = instance.item_templates[merc.OBJ_VNUM_PROTOPLASM]
    if not obj_index:
        ch.send("Error...missing object, please inform an Immortal.\n")
        return

    ch.quest -= value
    if ch.quest < 0:
        ch.quest = 0

    item = object_creator.create_item(obj_index, 1)
    item.value[0] = value
    item.cost = value * 1000
    item.item_type = merc.ITEM_QUEST
    item.questmaker = ch.name
    item.name = "quest token"
    item.short_descr = "a {:,} point quest token".format(value)
    item.description = "A {:,} point quest token lies on the floor.".format(value)
    ch.put(item)

    if victim and victim != ch:
        handler_game.act("You reach behind $N's ear and produce $p.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n reaches behind $N's ear and produces $p.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n reaches behind your ear and produces $p.", ch, item, victim, merc.TO_VICT)
    else:
        handler_game.act("You snap your fingers and reveal $p.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n snaps $s fingers and reveals $p.", ch, item, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="token",
        cmd_fun=cmd_token,
        position=merc.POS_STANDING, level=2,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
