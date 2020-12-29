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
import interp
import merc


def cmd_compare(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Compare what to what?\n")
        return

    item1 = ch.get_item_carry(arg1)
    if not item1:
        ch.send("You do not have that item.\n")
        return

    if not arg2:
        item2 = None
        for obj in ch.inventory[:]:
            if obj.equipped_to and ch.can_see_item(obj) and item1.item_type == obj.item_type and \
                    (item1.equips_to & obj.equips_to & ~merc.ITEM_TAKE) != 0:
                item2 = obj
                break

        if not item2:
            ch.send("You aren't wearing anything comparable.\n")
            return
    else:
        item2 = ch.get_item_carry(arg2)
        if not item2:
            ch.send("You do not have that item.\n")
            return

    msg = None
    value1 = 0
    value2 = 0

    if item1 == item2:
        msg = "You compare $p to itself.  It looks about the same."
    elif item1.item_type != item2.item_type:
        msg = "You can't compare $p and $P."
    else:
        if item1.item_type == merc.ITEM_ARMOR:
            value1 = item1.value[0]
            value2 = item2.value[0]
        elif item1.item_type == merc.ITEM_WEAPON:
            value1 = item1.value[1] + item1.value[2]
            value2 = item2.value[1] + item2.value[2]
        else:
            msg = "You can't compare $p and $P."

    if not msg:
        if value1 == value2:
            msg = "$p and $P look about the same."
        elif value1 > value2:
            msg = "$p looks better than $P."
        else:
            msg = "$p looks worse than $P."
    handler_game.act(msg, ch, item1, item2, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="compare",
        cmd_fun=cmd_compare,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
