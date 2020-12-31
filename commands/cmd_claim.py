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


def cmd_claim(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.exp < 500:
        ch.send("It costs 500 exp to claim ownership of an item.\n")
        return

    if not arg:
        ch.send("What object do you wish to claim ownership of?\n")
        return

    item = ch.get_item_carry(arg)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    if item.item_type in [merc.ITEM_QUEST, merc.ITEM_AMMO, merc.ITEM_EGG, merc.ITEM_VOODOO, merc.ITEM_MONEY, merc.ITEM_TREASURE, merc.ITEM_PAGE] or \
            item.flags.artifact:
        ch.send("You cannot claim that item.\n")
        return
    elif item.chobj and not item.chobj.is_npc() and item.chobj.obj_vnum != 0:
        ch.send("You cannot claim that item.\n")
        return

    if item.questowner:
        if game_utils.str_cmp(ch.name, item.questowner):
            ch.send("But you already own it!\n")
        else:
            ch.send("Someone else has already claimed ownership to it.\n")
        return

    ch.exp -= 500
    item.questowner = ch.name
    handler_game.act("You are now the owner of $p.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n is now the owner of $p.", ch, item, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="claim",
        cmd_fun=cmd_claim,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
