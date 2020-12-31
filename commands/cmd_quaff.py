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
import handler_magic
import interp
import merc


def cmd_quaff(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Quaff what?\n")
        return

    item = ch.get_item_carry(arg)
    if not item:
        ch.send("You do not have that potion.\n")
        return

    if item.item_type != merc.ITEM_POTION:
        ch.send("You can quaff only potions.\n")
        return

    handler_game.act("$n quaffs $p.", ch, item, None, merc.TO_ROOM)
    handler_game.act("You quaff $p.", ch, item, None, merc.TO_CHAR)
    handler_magic.obj_cast_spell(item.value[1], item.value[0], ch, ch, None)
    handler_magic.obj_cast_spell(item.value[2], item.value[0], ch, ch, None)
    handler_magic.obj_cast_spell(item.value[3], item.value[0], ch, ch, None)
    item.extract()

    if ch.position == merc.POS_FIGHTING:
        ch.wait_state(merc.PULSE_VIOLENCE // 2)


interp.register_command(
    interp.CmdType(
        name="quaff",
        cmd_fun=cmd_quaff,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
