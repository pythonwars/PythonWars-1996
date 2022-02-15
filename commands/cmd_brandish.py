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

import comm
import const
import handler_game
import handler_magic
import instance
import interp
import merc


# noinspection PyUnusedLocal
def cmd_brandish(ch, argument):
    staff = ch.get_eq("right_hand")
    if not staff or staff.item_type != merc.ITEM_STAFF:
        staff = ch.get_eq("left_hand")
        if not staff or staff.item_type != merc.ITEM_STAFF:
            ch.send("You hold nothing in your hand.\n")
            return

    sn = staff.value[3]
    if not sn or not const.skill_table[sn].spell_fun:
        comm.notify(f"cmd_brandish: bad sn {sn}", merc.CONSOLE_ERROR)
        return

    ch.wait_state(merc.PULSE_VIOLENCE * 2)

    if staff.value[2] > 0:
        handler_game.act("$n brandishes $p.", ch, staff, None, merc.TO_ROOM)
        handler_game.act("You brandish $p.", ch, staff, None, merc.TO_CHAR)

        for vch_id in ch.in_room.people[:]:
            vch = instance.characters[vch_id]
            target = const.skill_table[sn].target
            if target in [merc.TAR_IGNORE, merc.TAR_CHAR_SELF]:
                if vch != ch:
                    continue
            elif target == merc.TAR_CHAR_OFFENSIVE:
                if vch.is_npc() if ch.is_npc() else not vch.is_npc():
                    continue
            elif target == merc.TAR_CHAR_DEFENSIVE:
                if not vch.is_npc() if ch.is_npc() else vch.is_npc():
                    continue
            else:
                comm.notify(f"cmd_brandish: bad target for sn {sn}", merc.CONSOLE_ERROR)
                return

            handler_magic.obj_cast_spell(staff.value[3], staff.value[0], ch, vch, None)

    staff.value[2] -= 1
    if staff.value[2] <= 0:
        handler_game.act("$n's $p blazes bright and is gone.", ch, staff, None, merc.TO_ROOM)
        handler_game.act("Your $p blazes bright and is gone.", ch, staff, None, merc.TO_CHAR)
        staff.extract()


interp.register_command(
    interp.CmdType(
        name="brandish",
        cmd_fun=cmd_brandish,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
