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
import instance
import interp
import merc
import object_creator


def cmd_qmake(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Do you wish to qmake a MACHINE or a CARD?\n")
        return

    if game_utils.str_cmp(arg, "card"):
        obj_index = instance.item_templates[merc.OBJ_VNUM_QUESTCARD]
        if not obj_index:
            ch.send("Missing object, please inform an Immortal.\n")
            return

        item = object_creator.create_item(obj_index, 0)
        item.quest_object()
        ch.put(item)
    elif game_utils.str_cmp(arg, "machine"):
        obj_index = instance.item_templates[merc.OBJ_VNUM_QUESTMACHINE]
        if not obj_index:
            ch.send("Missing object, please inform an Immortal.\n")
            return

        item = object_creator.create_item(obj_index, 0)
        ch.in_room.put(item)
    else:
        ch.cmd_qmake("")
        return
    ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="qmake",
        cmd_fun=cmd_qmake,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
