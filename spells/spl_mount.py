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
def spl_mount(sn, level, ch, victim, target):
    if ch.is_npc():
        return

    if ch.followers > 4:
        ch.send("Nothing happens.\n")
        return

    ch.followers += 1
    level = max(1, level)

    if ch.is_demon():
        victim = object_creator.create_mobile(instance.npc_templates[merc.MOB_VNUM_HOUND])
        victim.level = level * 2
        victim.armor = 0 - (10 * level)
        victim.hitroll = level * 2
        victim.damroll = level * 2
        victim.hit = 250 * level
        victim.max_hit = 250 * level
        victim.lord = ch.name
        ch.is_room.put(victim)
        handler_game.act("$N fades into existance.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$N fades into existance.", ch, None, victim, merc.TO_ROOM)
        return

    victim = object_creator.create_mobile(instance.npc_templates[merc.MOB_VNUM_MOUNT])
    victim.level = level
    victim.armor = 0 - (2 * level)
    victim.hitroll = level
    victim.damroll = level
    victim.hit = 100 * level
    victim.max_hit = 100 * level
    victim.lord = ch.name
    victim.affected_by.set_bit(merc.AFF_FLYING)

    if ch.is_good():
        victim.name = "mount white horse pegasus"
        victim.short_descr = "{}'s white pegasus".format(ch.name)
        victim.long_descr = "A beautiful white pegasus stands here.\n"
    elif ch.is_evil():
        victim.name = "mount griffin"
        victim.short_descr = "{}'s griffin".format(ch.name)
        victim.long_descr = "A vicious looking griffin stands here.\n"
    else:
        victim.name = "mount black horse nightmare"
        victim.short_descr = "{}'s black nightmare".format(ch.name)
        victim.long_descr = "A large black demonic horse stands here.\n"

    ch.in_room.put(victim)
    handler_game.act("$N fades into existance.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$N fades into existance.", ch, None, victim, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="mount",
        skill_level=2,
        spell_fun=spl_mount,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(618),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Mount!"
    )
)
