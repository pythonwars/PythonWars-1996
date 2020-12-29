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
import handler_magic
import interp
import merc


def cmd_zap(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg and not ch.fighting:
        ch.send("Zap whom or what?\n")
        return

    wand = ch.get_eq("right_hand")
    if not wand or wand.item_type != merc.ITEM_WAND:
        wand = ch.get_eq("left_hand")
        if not wand or wand.item_type != merc.ITEM_WAND:
            ch.send("You hold nothing in your hand.\n")
            return

    item = None
    if not arg:
        if ch.fighting:
            victim = ch.fighting
        else:
            ch.send("Zap whom or what?\n")
            return
    else:
        victim = ch.get_char_room(arg)
        item = ch.get_item_here(arg)
        if not victim and not item:
            ch.send("You can't find it.\n")
            return

    ch.wait_state(merc.PULSE_VIOLENCE * 2)

    if wand.value[2] > 0:
        if victim:
            handler_game.act("$n zaps $N with $p.", ch, wand, victim, merc.TO_ROOM)
            handler_game.act("You zap $N with $p.", ch, wand, victim, merc.TO_CHAR)
        else:
            handler_game.act("$n zaps $P with $p.", ch, wand, item, merc.TO_ROOM)
            handler_game.act("You zap $P with $p.", ch, wand, item, merc.TO_CHAR)

        handler_magic.obj_cast_spell(wand.value[3], wand.value[0], ch, victim, item)

    wand.value[2] -= 1
    if wand.value[2] <= 0:
        handler_game.act("$n's $p explodes into fragments.", ch, wand, None, merc.TO_ROOM)
        handler_game.act("Your $p explodes into fragments.", ch, wand, None, merc.TO_CHAR)
        wand.extract()


interp.register_command(
    interp.CmdType(
        name="zap",
        cmd_fun=cmd_zap,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
