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
import instance
import interp
import merc


def cmd_purge(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        # 'purge'
        for victim_id in ch.in_room.people[:]:
            victim = instance.characters[victim_id]

            mount = victim.mount
            if victim.is_npc() and not victim.desc and not mount:
                victim.extract(True)

        for item_id in ch.in_room.items:
            item = instance.items[item_id]

            item.extract()

        handler_game.act("$n purges the room!", ch, None, None, merc.TO_ROOM)
        ch.send("Ok.\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if not victim.is_npc():
        ch.not_pc()
        return

    if victim.desc:
        ch.send("Not on switched players.\n")
        return

    handler_game.act("$n purges $N.", ch, None, victim, merc.TO_NOTVICT)
    victim.extact(True)


interp.register_command(
    interp.CmdType(
        name="purge",
        cmd_fun=cmd_purge,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
