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
import handler_magic
import instance
import merc


# noinspection PyUnusedLocal
def spl_faerie_fog(sn, level, ch, victim, target):
    handler_game.act("$n conjures a cloud of purple smoke.", ch, None, None, merc.TO_ROOM)
    ch.send("You conjure a cloud of purple smoke.\n")

    for ich_id in ch.in_room.people[:]:
        ich = instance.characters[ich_id]

        if ich == ch or (not ich.is_npc() and ich.act.is_set(merc.PLR_WIZINVIS)) or handler_magic.saves_spell(level, ich) or ich.invis_level > 0:
            continue

        ich.affect_strip("invisibility")
        ich.affect_strip("mass invis")
        ich.affect_strip("sneak")
        ich.affected_by.rem_bit(merc.AFF_HIDE)
        ich.affected_by.rem_bit(merc.AFF_INVISIBLE)
        ich.affected_by.rem_bit(merc.AFF_SNEAK)
        handler_game.act("$n is revealed! ", ich, None, None, merc.TO_ROOM)
        ich.send("You are revealed! \n")


const.register_spell(
    const.skill_type(
        name="faerie fog",
        skill_level=99,
        spell_fun=spl_faerie_fog,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(73),
        min_mana=12,
        beats=12,
        noun_damage="faerie fog",
        msg_off="!Faerie Fog!"
    )
)
