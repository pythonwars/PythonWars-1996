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


def cmd_oclone(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Make a clone of what object?\n")
        return

    item = ch.get_item_world(arg)
    if not item:
        ch.send("Nothing like that in hell, earth, or heaven.\n")
        return

    if not ch.is_judge() and (not item.questmaker or not game_utils.str_cmp(ch.name, item.questmaker)):
        ch.send("You can only clone your own creations.\n")
        return

    clone_item = object_creator.create_item(instance.item_templates[item.vnum], 0)
    ch.put(clone_item)
    handler_game.act("You create a clone of $p.", ch, item, None, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="oclone",
        cmd_fun=cmd_oclone,
        position=merc.POS_DEAD, level=8,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
