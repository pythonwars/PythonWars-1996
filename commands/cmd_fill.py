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

import const
import game_utils
import handler_game
import instance
import interp
import merc


def cmd_fill(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Fill what?\n")
        return

    obj = ch.get_item_carry(arg)
    if not obj:
        ch.send("You do not have that item.\n")
        return

    fountain = None
    for f_id in ch.in_room.items:
        f = instance.items[f_id]
        if f.item_type == merc.ITEM_FOUNTAIN:
            fountain = f
            break

    if not fountain:
        ch.send("There is no fountain here!\n")
        return

    if ch.is_affected(merc.AFF_SHADOWPLANE) and fountain.in_room and not fountain.flags.shadowplane:
        ch.send("You are too insubstantual.\n")
        return
    elif not ch.is_affected(merc.AFF_SHADOWPLANE) and fountain.in_room and fountain.flags.shadowplane:
        ch.send("It is too insubstantual.\n")
        return

    if ch.is_affected(merc.AFF_ETHEREAL):
        ch.send("You cannot fill containers while ethereal.\n")
        return

    if obj.item_type != merc.ITEM_DRINK_CON:
        ch.send("You can't fill that.\n")
        return

    if obj.value[1] >= obj.value[0]:
        ch.send("Your container is already full.\n")
        return

    if obj.value[2] != fountain.value[2] and obj.value[1] > 0:
        ch.send("You cannot mix two different liquids.\n")
        return

    handler_game.act("$n dips $p into $P.", ch, obj, fountain, merc.TO_ROOM)
    handler_game.act("You dip $p into $P.", ch, obj, fountain, merc.TO_CHAR)
    obj.value[2] = fountain.value[2]
    obj.value[1] = obj.value[0]
    liquid = obj.value[2]
    handler_game.act("You fill $p with $P.", ch, obj, const.liq_table[liquid].name, merc.TO_CHAR)
    handler_game.act("$n fills $p with $P.", ch, obj, const.liq_table[liquid].name, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="fill",
        cmd_fun=cmd_fill,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
