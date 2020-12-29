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


# noinspection PyUnusedLocal
def cmd_poison(ch, argument):
    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_SERPENTIS):
        ch.send("You are not trained in the Serpentis discipline.\n")
        return

    item = ch.get_eq("right_hand")
    if not item or item.item_type != merc.ITEM_WEAPON:
        item = ch.get_eq("left_hand")
        if not item or item.item_type != merc.ITEM_WEAPON:
            ch.send("You must wield the weapon you wish to poison.\n")
            return

    if item.value[0] != 0:
        ch.send("This weapon cannot be poisoned.\n")
        return

    if ch.blood < 15:
        ch.send("You have insufficient blood.\n")
        return

    ch.blood -= game_utils.number_range(5, 15)
    handler_game.act("You run your tongue along $p, poisoning it.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n runs $s tongue along $p, poisoning it.", ch, item, None, merc.TO_ROOM)
    item.value[0] = 53
    item.timer = game_utils.number_range(10, 20)


interp.register_command(
    interp.CmdType(
        name="poison",
        cmd_fun=cmd_poison,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
