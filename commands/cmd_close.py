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
import handler_room
import instance
import interp
import merc
import state_checks


def cmd_close(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Close what?\n")
        return

    item = ch.get_item_here(arg)
    if item:
        # 'close object'
        if item.item_type not in [merc.ITEM_CONTAINER, merc.ITEM_BOOK]:
            ch.send("That's not a container.\n")
            return

        if state_checks.is_set(item.value[1], merc.CONT_CLOSED):
            ch.send("It's already closed.\n")
            return

        if not state_checks.is_set(item.value[1], merc.CONT_CLOSEABLE) and item.item_type != merc.ITEM_BOOK:
            ch.send("You can't do that.\n")
            return

        state_checks.set_bit(item.value[1], merc.CONT_CLOSED)

        if item.item_type == merc.ITEM_BOOK:
            item.value[2] = 0

        ch.send("Ok.\n")
        handler_game.act("$n closes $p.", ch, item, None, merc.TO_ROOM)
        return

    door = handler_room.find_door(ch, arg)
    if door >= 0:
        # 'close door'
        pexit = ch.in_room.exit[door]
        if pexit.exit_info.is_set(merc.EX_CLOSED):
            ch.send("It's already closed.\n")
            return

        pexit.exit_info.set_bit(merc.EX_CLOSED)
        handler_game.act("$n closes the $d.", ch, item, pexit.keyword, merc.TO_ROOM)
        ch.send("Ok.\n")

        # close the other side
        to_room = instance.rooms[pexit.to_room]
        pexit_rev = to_room.exit[merc.rev_dir[door]] if pexit.to_room else None
        if to_room and pexit_rev and pexit_rev.to_room == ch.in_room.instance_id:
            pexit_rev.exit_info.set_bit(merc.EX_CLOSED)
            for rch_id in to_room.people[:]:
                rch = instance.characters[rch_id]
                handler_game.act("The $d closes.", rch, None, pexit_rev.keyword, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="close",
        cmd_fun=cmd_close,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
