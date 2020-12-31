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
import handler_ch
import handler_game
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_guardian(sn, level, ch, victim, target):
    if ch.followers > 4:
        ch.send("Nothing happens.\n")
        return

    ch.followers += 1
    victim = object_creator.create_mobile(instance.npc_templates[merc.MOB_VNUM_GUARDIAN])
    victim.level = level
    victim.hit = 100 * level
    victim.max_hit = 100 * level
    victim.hitroll = level
    victim.damroll = level
    victim.armor = 100 - (level * 7)

    ch.cmd_say("Come forth, creature of darkness, and do my bidding!")
    ch.send("A demon bursts from the ground and bows before you.\n")
    handler_game.act("$N bursts from the ground and bows before $n.", ch, None, victim, merc.TO_ROOM)
    ch.in_room.put(victim)
    handler_ch.add_follower(victim, ch)

    aff = handler_game.AffectData(type=sn, duration=666, location=merc.APPLY_NONE, bitvector=merc.AFF_CHARM)
    victim.affect_join(aff)


const.register_spell(
    const.skill_type(
        name="guardian",
        skill_level=1,
        spell_fun=spl_guardian,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(600),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Guardian!"
    )
)
