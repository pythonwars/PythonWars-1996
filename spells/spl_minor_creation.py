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
import instance
import merc
import object_creator


# noinspection PyUnusedLocal
def spl_minor_creation(sn, level, ch, victim, target):
    handler_magic.target_name, arg = game_utils.read_word(handler_magic.target_name)

    arg_list = [("potion", merc.ITEM_POTION), ("scroll", merc.ITEM_SCROLL), ("wand", merc.ITEM_WAND), ("staff", merc.ITEM_STAFF),
                ("pill", merc.ITEM_PILL)]
    for (aa, bb) in arg_list:
        if game_utils.str_cmp(arg, aa):
            itemtype = bb
            itemkind = aa
            break
    else:
        ch.send("Item can be one of: Potion, Scroll, Wand, Staff or Pill.\n")
        return

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PROTOPLASM], 0)
    item.item_type = itemtype
    item.name = f"{ch.name} {itemkind}"
    item.short_descr = f"{ch.name}'s {itemkind}"
    item.description = f"{ch.name}'s {itemkind} lies here."
    item.weight = 10
    item.questmaker = ch.name
    ch.put(item)
    handler_game.act("$p suddenly appears in your hands.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p suddenly appears in $n's hands.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="minor creation",
        skill_level=4,
        spell_fun=spl_minor_creation,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(612),
        min_mana=500,
        beats=12,
        noun_damage="",
        msg_off="!Minor Creation!"
    )
)
