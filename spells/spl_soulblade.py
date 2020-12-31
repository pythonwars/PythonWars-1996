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
import handler_game
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_soulblade(sn, level, ch, victim, target):
    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_SOULBLADE], 0)
    wpn_list = [(merc.WPN_SLICE, "blade"), (merc.WPN_STAB, "blade"), (merc.WPN_WHIP, "whip"), (merc.WPN_CLAW, "claw"), (merc.WPN_BLAST, "blaster"),
                (merc.WPN_POUND, "mace"), (merc.WPN_CRUSH, "mace"), (merc.WPN_GREP, "grepper"), (merc.WPN_BITE, "biter"), (merc.WPN_PIERCE, "blade"),
                (merc.WPN_SUCK, "sucker")]
    for (aa, bb) in wpn_list:
        if ch.wpn[aa] > ch.wpn[merc.WPN_SLASH]:
            wpntype = aa
            wpnname = bb
    else:
        wpntype = merc.WPN_SLASH
        wpnname = "blade"

    # First we name the weapon
    item.name = "{} soul {}".format(ch.name, wpnname)
    short_descr = ch.short_descr if ch.is_npc() else ch.name
    item.short_descr = "{}'s soul {}".format(short_descr[0].upper() + short_descr[1:], wpnname)
    item.long_descr = "{}'s soul {} is lying here.".format(short_descr[0].upper() + short_descr[1:], wpnname)

    item.level = ch.level if ch.is_npc() else (ch.spl[2] // 4) if (ch.spl[2] > 4) else 1
    item.level = min(item.level, 60)
    item.value[0] = 13034
    item.value[1] = 10
    item.value[2] = 20
    item.value[3] = wpntype
    item.questmaker = ch.name

    if not ch.is_npc():
        item.questowner = ch.name

    ch.put(item)
    handler_game.act("$p fades into existance in your hand.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p fades into existance in $n's hand.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="soulblade",
        skill_level=1,
        spell_fun=spl_soulblade,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(601),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Soulblade!"
    )
)
