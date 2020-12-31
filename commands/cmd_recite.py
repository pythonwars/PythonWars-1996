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


def cmd_recite(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    scroll = ch.get_item_carry(arg1)
    if not scroll:
        ch.send("You do not have that scroll.\n")
        return

    if scroll.item_type != merc.ITEM_SCROLL:
        ch.send("You can recite only scrolls.\n")
        return

    item = None

    if not arg2:
        victim = ch
    else:
        victim = ch.get_char_room(arg2)
        item = ch.get_item_here(arg2)
        if not victim and not item:
            ch.send("You can't find it.\n")
            return

    handler_game.act("$n recites $p.", ch, scroll, None, merc.TO_ROOM)
    handler_game.act("You recite $p.", ch, scroll, None, merc.TO_CHAR)
    handler_magic.obj_cast_spell(scroll.value[1], item.value[0], ch, victim, item)
    handler_magic.obj_cast_spell(scroll.value[2], item.value[0], ch, victim, item)
    handler_magic.obj_cast_spell(scroll.value[3], item.value[0], ch, victim, item)
    scroll.extract()

    if ch.position == merc.POS_FIGHTING:
        ch.wait_state(merc.PULSE_VIOLENCE // 2)


interp.register_command(
    interp.CmdType(
        name="recite",
        cmd_fun=cmd_recite,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
