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
import instance
import interp
import merc
import state_checks
import tables


def cmd_mstat(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Mstat whom?\n")
        return

    victim = ch.get_char_world(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.act.is_set(merc.PLR_GODLESS) and ch.trust < merc.NO_GODLESS and not ch.extra.is_set(merc.EXTRA_ANTI_GODLESS):
        ch.send("You failed.\n")
        return

    buf = ["Name: {}\n".format(victim.name)]
    buf += "Vnum: {}.  Sex: {}.  Room: {}.\n".format(0 if not victim.is_npc() else victim.vnum, tables.sex_table[victim.sex],
                                                     0 if not victim.in_room else victim.in_room.vnum)
    buf += "Str: {}.  Int: {}.  Wis: {}.  Dex: {}.  Con: {}.\n".format(victim.stat(merc.STAT_STR), victim.stat(merc.STAT_INT),
                                                                       victim.stat(merc.STAT_WIS), victim.stat(merc.STAT_DEX),
                                                                       victim.stat(merc.STAT_CON))
    buf += "Hp: {}/{}.  Mana: {}/{}.  Move: {}/{}.  Primal: {}.\n".format(victim.hit, victim.max_hit, victim.mana, victim.max_mana,
                                                                          victim.move, victim.max_move, victim.practice)
    buf += "Lv: {}.  Align: {}.  AC: {}.  Gold: {}.  Exp: {}.\n".format(victim.level, victim.alignment, victim.armor, victim.gold, victim.exp)
    buf += "Hitroll: {}.  Damroll: {}.  Position: {}.  Wimpy: {}.\n".format(victim.hitroll, victim.damroll, tables.position_table[victim.position].name,
                                                                            victim.wimpy)
    buf += "Fighting: {}.\n".format(victim.fighting.name if victim.fighting else "(none)")

    if not victim.is_npc():
        buf += "Saving throw: {}.\n".format(victim.saving_throw)

        if victim.is_vampire() or victim.is_werewolf():
            buf += "Clan: {}. ".format(victim.clan if victim.clan else "None")
            buf += "Rage: {}. ".format(victim.powers[merc.UNI_RAGE])

            if victim.is_vampire():
                buf += "Beast: {}. ".format(victim.beast)
                buf += "Blood: {}.".format(victim.blood)
            buf += "\n"

        if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
            if victim.special.is_set(merc.SPC_CHAMPION):
                buf += "Lord: {}. ".format(victim.lord if victim.lord else "None")

            buf += "Demonic armor: {} pieces. ".format(victim.powers[merc.DEMON_POWER])
            buf += "Power: {} ({}).\n".format(victim.powers[merc.DEMON_CURRENT], victim.powers[merc.DEMON_TOTAL])

    buf += "Carry number: {}.  Carry weight: {}.\n".format(victim.carry_number, state_checks.get_carry_weight(victim))
    buf += "Age: {}.  Played: {}.  Timer: {}.  Act: {}.\n".format(victim.get_age(), victim.played, victim.timer, repr(victim.act))
    buf += "Master: {}.  Leader: {}.  Affected by: {}.\n".format(instance.characters[victim.master].name if victim.master else "(none)",
                                                                 victim.leader.name if victim.leader else "(none)", repr(victim.affected_by))
    buf += "Short description: {}.\nLong  description: {}".format(victim.short_descr, victim.long_descr if victim.long_descr else "(none).\n")

    if victim.is_npc() and victim.spec_fun:
        buf += "Mobile has spec fun.\n"

    for paf in victim.affected:
        buf += "Spell: '{}' modifies {} by {} for {} hours with bits {}.\n".format(paf.type, merc.affect_loc_name(paf.location), paf.modifier,
                                                                                   paf.duration, merc.affect_bit_name(paf.bitvector))
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="mstat",
        cmd_fun=cmd_mstat,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
