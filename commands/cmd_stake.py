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
import interp
import merc
import state_checks


def cmd_stake(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        ch.send("Stake whom?\n")
        return

    stake = ch.get_eq("right_hand")
    if not stake or stake.item_type != merc.ITEM_STAKE:
        stake = ch.get_eq("left_hand")
        if not stake or stake.item_type != merc.ITEM_STAKE:
            ch.send("How can you stake someone down without holding a stake?\n")
            return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if ch == victim:
        ch.not_self()
        return

    if not victim.is_vampire():
        ch.send("You can only stake vampires.\n")
        return

    if victim.position > merc.POS_MORTAL:
        ch.send("You can only stake down a vampire who is mortally wounded.\n")
        return

    handler_game.act("You plunge $p into $N's heart.", ch, stake, victim, merc.TO_CHAR)
    handler_game.act("$n plunges $p into $N's heart.", ch, stake, victim, merc.TO_NOTVICT)
    victim.send("You feel a stake plunged through your heart.\n")

    if victim.immune.is_set(merc.IMM_STAKE):
        return

    # Have to make sure they have enough blood to change back
    blood = victim.blood
    victim.blood = 666

    # To take care of vampires who have powers in affect.
    if victim.vampaff.is_set(merc.VAM_DISGUISED):
        victim.cmd_mask("self")

    if victim.immune.is_set(merc.IMM_SHIELDED):
        victim.cmd_shield("")

    if victim.is_affected(merc.AFF_SHADOWPLANE):
        victim.cmd_shadowplane("")

    if victim.vampaff.is_set(merc.VAM_FANGS):
        victim.cmd_fangs("")

    if victim.vampaff.is_set(merc.VAM_CLAWS):
        victim.cmd_claws("")

    if victim.vampaff.is_set(merc.VAM_NIGHTSIGHT):
        victim.cmd_nightsight("")

    if victim.is_affected(merc.AFF_SHADOWSIGHT):
        victim.cmd_shadowsight("")

    if victim.act.is_set(merc.PLR_HOLYLIGHT):
        victim.cmd_truesight("")

    if victim.vampaff.is_set(merc.VAM_CHANGED):
        victim.cmd_change("human")

    if victim.polyaff.is_set(merc.POLY_SERPENT):
        victim.cmd_serpent("")

    victim.powers[merc.UNI_RAGE] = 0
    victim.blood = blood
    victim.ch_class = state_checks.prefix_lookup(const.class_table, "human")
    ch.get(stake)
    victim.put(stake)
    ch.exp += 1000
    victim.home = merc.ROOM_VNUM_TEMPLE


interp.register_command(
    interp.CmdType(
        name="stake",
        cmd_fun=cmd_stake,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
