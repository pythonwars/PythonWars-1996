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

import const
import game_utils
import handler_game
import interp
import merc


def cmd_readaura(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.itemaff.is_set(merc.ITEMA_VISION):
        if not ch.is_vampire():
            ch.huh()
            return

        if not ch.vampaff.is_set(merc.VAM_AUSPEX):
            ch.send("You are not trained in the Auspex discipline.\n")
            return

    if not arg:
        ch.send("Read the aura on what?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        item = ch.get_item_carry(arg)
        if not item:
            ch.send("Read the aura on what?\n")
            return

        if not ch.itemaff.is_set(merc.ITEMA_VISION):
            if ch.blood < 50:
                ch.send("You have insufficient blood.\n")
                return

            ch.blood -= game_utils.number_range(40, 50)

        handler_game.act("$n examines $p intently.", ch, item, None, merc.TO_ROOM)
        const.skill_table["identify"].spell_fun("identify", ch.level, ch, item, merc.TARGET_ITEM)
        return

    if not ch.itemaff.is_set(merc.ITEMA_VISION):
        if ch.blood < 50:
            ch.send("You have insufficient blood.\n")
            return

        ch.blood -= game_utils.number_range(40, 50)

        if not victim.is_npc() and victim.immune.is_set(merc.IMM_SHIELDED):
            ch.send("You are unable to read their aura.\n")
            return

    handler_game.act("$n examines $N intently.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n examines you intently.", ch, None, victim, merc.TO_VICT)
    buf = []

    if victim.is_npc():
        buf += "{} is an NPC.\n".format(victim.short_descr)
    else:
        level_list = [(12, "Implementor"), (11, "High Judge"), (10, "Judge"), (9, "Enforcer"), (8, "Quest Maker"), (7, "Builder")]
        for (aa, bb) in level_list:
            if victim.level >= aa:
                buf += "{} is an {}.\n".format(victim.name, bb)
                break
        else:
            if victim.level >= 3:
                buf += "{} is an Avatar.\n".format(victim.name)
            else:
                buf += "{} is a Mortal.\n".format(victim.name)

    if not victim.is_npc():
        buf += "Str:{}, Int:{}, Wis:{}, Dex:{}, Con:{}.\n".format(victim.stat(merc.STAT_STR), victim.stat(merc.STAT_INT), victim.stat(merc.STAT_WIS),
                                                                  victim.stat(merc.STAT_DEX), victim.stat(merc.STAT_CON))

    buf += "Hp:{}/{}, Mana:{}/{}, Move:{}/{}.\n".format(victim.hit, victim.max_hit, victim.mana, victim.max_mana, victim.move, victim.max_move)

    if not victim.is_npc():
        buf += "Hitroll:{}, Damroll:{}, AC:{}.\n".format(victim.hitroll, victim.damroll, victim.armor)
    else:
        buf += "AC:{}.\n".format(victim.armor)

    if not victim.is_npc():
        buf += "Status:{}, ".format(victim.race)

        if victim.is_npc():
            buf += "Blood:{}, ".format(victim.blood)

    buf += "Alignment:{}.\n".format(victim.alignment)

    if not victim.is_npc() and victim.is_vampire():
        buf += "Disciplines:"
        disc_list = [(merc.VAM_PROTEAN, "Protean"), (merc.VAM_CELERITY, "Celerity"), (merc.VAM_FORTITUDE, "Fortitude"), (merc.VAM_POTENCE, "Potence"),
                     (merc.VAM_OBFUSCATE, "Obfuscate"), (merc.VAM_OBTENEBRATION, "Obtenebration"), (merc.VAM_SERPENTIS, "Serpentis"),
                     (merc.VAM_AUSPEX, "Auspex"), (merc.VAM_DOMINATE, "Dominate"), (merc.VAM_PRESENCE, "Presence")]
        for (aa, bb) in disc_list:
            if victim.vampaff.is_set(aa):
                buf += " " + bb
        buf += ".\n"
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="readaura",
        cmd_fun=cmd_readaura,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
