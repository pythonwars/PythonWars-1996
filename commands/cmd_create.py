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
import object_creator


def cmd_create(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        itemtype = merc.ITEM_TRASH
    else:
        type_list = [("light", merc.ITEM_LIGHT), ("scroll", merc.ITEM_SCROLL), ("wand", merc.ITEM_WAND), ("staff", merc.ITEM_STAFF),
                     ("weapon", merc.ITEM_WEAPON), ("treasure", merc.ITEM_TREASURE), (["armor", "armour"], merc.ITEM_ARMOR),
                     ("potion", merc.ITEM_POTION), ("furniture", merc.ITEM_FURNITURE), ("trash", merc.ITEM_TRASH),
                     ("container", merc.ITEM_CONTAINER), ("drink", merc.ITEM_DRINK_CON), ("key", merc.ITEM_KEY), ("food", merc.ITEM_FOOD),
                     ("money", merc.ITEM_MONEY), ("boat", merc.ITEM_BOAT), ("corpse", merc.ITEM_CORPSE_NPC), ("fountain", merc.ITEM_FOUNTAIN),
                     ("pill", merc.ITEM_PILL), ("portal", merc.ITEM_PORTAL), ("egg", merc.ITEM_EGG), ("stake", merc.ITEM_STAKE),
                     ("missile", merc.ITEM_MISSILE)]
        for (aa, bb) in type_list:
            if game_utils.str_cmp(arg1, aa):
                itemtype = bb
                break
        else:
            itemtype = merc.ITEM_TRASH

    if not arg2 or not arg2.isdigit():
        level = 0
    else:
        level = int(arg2)
        if level not in merc.irange(1, 50):
            ch.send("Level should be within range 1 to 50.\n")
            return

    if merc.OBJ_VNUM_PROTOPLASM not in instance.item_templates:
        ch.send("Error...missing object, please inform an Immortal.\n")
        return

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PROTOPLASM], level)
    item.item_type = itemtype
    ch.put(item)
    item.questmaker = ch.name
    handler_game.act("You reach up into the air and draw out a ball of protoplasm.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n reaches up into the air and draws out a ball of protoplasm.", ch, item, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="create",
        cmd_fun=cmd_create,
        position=merc.POS_STANDING, level=8,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
