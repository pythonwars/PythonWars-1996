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
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_remove_curse(sn, level, ch, victim, target):
    argument, arg = game_utils.read_word(handler_magic.target_name)

    if not arg:
        ch.send("Remove curse on what?\n")
        return

    victim = ch.get_char_world(arg)
    if victim:
        if victim.is_affected("curse"):
            victim.affect_strip("curse")
            victim.send("You feel better.\n")

            if ch != victim:
                ch.send("Ok.\n")

                if not ch.is_npc():
                    ch.humanity()
        return

    item = ch.get_item_carry(arg)
    if item:
        if item.flags.noremove:
            item.flags.noremove = False
            handler_game.act("$p flickers with energy.", ch, item, None, merc.TO_CHAR)
        elif item.flags.nodrop:
            item.flags.nodrop = False
            handler_game.act("$p flickers with energy.", ch, item, None, merc.TO_CHAR)
        return

    ch.send("No such creature or object to remove curse on.\n")


const.register_spell(
    const.skill_type(
        name="remove curse",
        skill_level=3,
        spell_fun=spl_remove_curse,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(35),
        min_mana=5,
        beats=12,
        noun_damage="",
        msg_off="!Remove Curse!"
    )
)
