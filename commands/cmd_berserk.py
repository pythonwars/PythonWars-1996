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
import fight
import game_utils
import handler_game
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_berserk(ch, argument):
    if ch.is_npc():
        return

    if ch.level < const.skill_table["berserk"].skill_level:
        ch.send("You are not wild enough to go berserk.\n")
        return

    ch.wait_state(const.skill_table["berserk"].beats)

    if game_utils.number_percent() > ch.learned["berserk"]:
        handler_game.act("You rant and rave, but nothing much happens.", ch, None, None, merc.TO_CHAR)
        handler_game.act("$n gets a wild look in $s eyes, but nothing much happens.", ch, None, None, merc.TO_ROOM)
        return

    handler_game.act("You go BERSERK!", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n goes BERSERK!", ch, None, None, merc.TO_ROOM)

    number_hit = 0
    for vch_id in ch.in_room.people[:]:
        vch = instance.characters[vch_id]

        if number_hit > 4:
            continue

        if not vch.is_npc() and vch.chobj:
            continue

        if ch == vch or not ch.can_see(vch):
            continue

        mount = ch.mount
        if mount and mount == vch:
            continue

        fight.multi_hit(ch, vch, merc.TYPE_UNDEFINED)
        number_hit += 1

    ch.beastlike()


interp.register_command(
    interp.CmdType(
        name="berserk",
        cmd_fun=cmd_berserk,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
