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
import instance
import interp
import merc


def cmd_complete(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Syntax: complete <quest card> <object>\n")
        return

    qitem = ch.get_item_carry(arg1)
    if not qitem:
        ch.send("You are not carrying that object.\n")
        return

    if qitem.item_type != merc.ITEM_QUESTCARD:
        ch.send("That is not a quest card.\n")
        return

    count = 0
    for i in range(4):
        if qitem.value[i] == -1:
            count += 1

    if not arg2:
        if count == 4:
            ch.send("This quest card has been completed.\n")
            return

        buf = ["You still need to find the following:\n"]
        for i in range(4):
            if qitem.value[i] != -1:
                obj_index = instance.item_templates[qitem.value[i]]
                if obj_index:
                    buf += f"     {obj_index.short_descr[0].upper() + obj_index.short_descr[1:]}.\n"
        ch.send("".join(buf))
        return

    if count == 4:
        handler_game.act("But $p has already been completed!", ch, qitem, None, merc.TO_CHAR)
        return

    item = ch.get_item_carry(arg2)
    if not item:
        ch.send("You are not carrying that object.\n")
        return

    if item.questmaker:
        ch.send("You cannot use that item.\n")
        return

    if item.vnum in [30037, 30041]:
        ch.send("That item has lost its quest value, you must collect a new one.\n")
        return

    found = False
    for i in range(4):
        if qitem.value[i] != -1:
            obj_index = instance.item_templates[qitem.value[i]]
            if obj_index and game_utils.str_cmp(item.short_descr, obj_index.short_descr):
                qitem.value[i] = -1
                found = True

    count = 0
    for i in range(4):
        if qitem.value[i] == -1:
            count += 1

    if not found:
        ch.send("That item is not required.\n")
        return

    handler_game.act("You touch $p to $P, and $p vanishes!", ch, item, qitem, merc.TO_CHAR)
    handler_game.act("$n touches $p to $P, and $p vanishes!", ch, item, qitem, merc.TO_ROOM)
    ch.get(item)
    item.extract()

    if count >= 4:
        handler_game.act("$p has been completed!", ch, qitem, None, merc.TO_CHAR)
    elif count == 3:
        handler_game.act("$p now requires one more object!", ch, qitem, None, merc.TO_CHAR)
    elif count == 2:
        handler_game.act("$p now requires two more objects!", ch, qitem, None, merc.TO_CHAR)
    elif count == 1:
        handler_game.act("$p now requires three more objects!", ch, qitem, None, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="complete",
        cmd_fun=cmd_complete,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
