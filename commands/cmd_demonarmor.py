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


def cmd_demonarmor(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_demon() and not ch.special.is_set(merc.SPC_CHAMPION):
        ch.huh()
        return

    if not arg:
        ch.send("Please specify which piece of demon armor you wish to make: Ring Collar\n"
                "Plate Helmet Leggings Boots Gauntlets Sleeves Cape Belt Bracer Visor.\n")
        return

    arg_list = [("ring", 29650), ("collar", 29651), ("plate", 29652), ("helmet", 29653), ("leggings", 29654), ("boots", 29655),
                ("gauntlets", 29656), ("sleeves", 29657), ("cape", 29658), ("belt", 29659), ("bracer", 29660), ("visor", 29661)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg, aa):
            vnum = bb
            break
    else:
        ch.cmd_demonarmor("")
        return

    if ch.powers[merc.DEMON_TOTAL] < 5000 or ch.powers[merc.DEMON_CURRENT] < 5000:
        ch.send("It costs 5000 points of power to create a piece of demon armour.\n")
        return

    item_index = instance.item_templates[vnum]
    if not item_index:
        ch.send("Missing object, please inform an Immortal.\n")
        return

    ch.powers[merc.DEMON_TOTAL] -= 5000
    ch.powers[merc.DEMON_CURRENT] -= 5000

    item = object_creator.create_item(item_index, 50)
    ch.put(item)
    handler_game.act("$p appears in your hands in a blast of flames.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p appears in $n's hands in a blast of flames.", ch, item, None, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="demonarmor",
        cmd_fun=cmd_demonarmor,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
