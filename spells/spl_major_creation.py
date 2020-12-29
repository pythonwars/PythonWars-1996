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
import handler_magic
import instance
import merc
import object_creator
import state_checks


# noinspection PyUnusedLocal
def spl_major_creation(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if ch.is_npc():
        return

    if not arg1:
        ch.send("Item can be one of: Rune, Glyph, Sigil, Book, Page or Pen.\n")
        return

    itemname = ""
    vn = 0
    itempower = 0

    # The Rune is the foundation/source of the spell.
    # The Glyphs form the focus/purpose of the spell.
    # The Sigils form the affects of the spell.
    if game_utils.str_cmp(arg1, "rune"):
        if not arg2:
            ch.send("You know of no such Rune.\n")
            return

        itemtype = merc.ITEM_SYMBOL
        vn = 1
        itemkind = "rune"

        rune_list = [("fire", merc.RUNE_FIRE), ("air", merc.RUNE_AIR), ("earth", merc.RUNE_EARTH), ("water", merc.RUNE_WATER),
                     ("dark", merc.RUNE_DARK), ("light", merc.RUNE_LIGHT), ("life", merc.RUNE_LIFE), ("death", merc.RUNE_DEATH),
                     ("mind", merc.RUNE_MIND), ("spirit", merc.RUNE_SPIRIT), ("mastery", merc.RUNE_MASTER)]
        for (aa, bb) in rune_list:
            if game_utils.str_cmp(arg2, aa):
                itemname = aa
                itempower = bb
                break
        else:
            ch.send("You know of no such Rune.\n")
            return

        if not state_checks.is_set(ch.powers[vn], itempower):
            ch.send("You know of no such Rune.\n")
            return
    elif game_utils.str_cmp(arg1, "glyph"):
        if not arg2:
            ch.send("You know of no such Glyph.\n")
            return

        itemtype = merc.ITEM_SYMBOL
        vn = 2
        itemkind = "glyph"

        glyph_list = [("creation", merc.GLYPH_CREATION), ("destruction", merc.GLYPH_DESTRUCTION), ("summoning", merc.GLYPH_SUMMONING),
                      ("transformation", merc.GLYPH_TRANSFORMATION), ("transportation", merc.GLYPH_TRANSPORTATION),
                      ("enhancement", merc.GLYPH_ENHANCEMENT), ("reduction", merc.GLYPH_DESTRUCTION), ("control", merc.GLYPH_CONTROL),
                      ("protection", merc.GLYPH_PROTECTION), ("information", merc.GLYPH_INFORMATION)]
        for (aa, bb) in glyph_list:
            if game_utils.str_cmp(arg2, aa):
                itemname = aa
                itempower = bb
                break
        else:
            ch.send("You know of no such Glyph.\n")
            return

        if not state_checks.is_set(ch.powers[vn], itempower):
            ch.send("You know of no such Glyph.\n")
            return
    elif game_utils.str_cmp(arg1, "sigil"):
        if not arg2:
            ch.send("You know of no such Sigil.\n")
            return

        itemtype = merc.ITEM_SYMBOL
        vn = 3
        itemkind = "sigil"

        sigil_list = [("self", merc.SIGIL_SELF), ("targeting", merc.SIGIL_TARGETING), ("area", merc.SIGIL_AREA), ("object", merc.SIGIL_OBJECT)]
        for (aa, bb) in sigil_list:
            if game_utils.str_cmp(arg2, aa):
                itemname = aa
                itempower = bb
                break
        else:
            ch.send("You know of no such Sigil.\n")
            return

        if not state_checks.is_set(ch.powers[vn], itempower):
            ch.send("You know of no such Sigil.\n")
            return
    elif game_utils.str_cmp(arg1, "book"):
        itemtype = merc.ITEM_BOOK
        itemkind = "book"
    elif game_utils.str_cmp(arg1, "page"):
        itemtype = merc.ITEM_PAGE
        itemkind = "page"
    elif game_utils.str_cmp(arg1, "pen"):
        itemtype = merc.ITEM_TOOL
        itemkind = "pen"
    else:
        ch.send("Item can be one of: Rune, Glyph, Sigil, Book, Page or Pen.\n")
        return

    item = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_PROTOPLASM], 0)
    item.item_type = itemtype

    if itemtype == merc.ITEM_SYMBOL:
        buf = "{} {}".format(itemkind, itemname)
        item.value[vn] = itempower
    else:
        buf = "{}".format(itemkind)

    if itemtype == merc.ITEM_TOOL:
        item.value[0] = merc.TOOL_PEN
        item.weight = 1
        item.flags.take = True
        item.hold = True
    elif itemtype == merc.ITEM_BOOK:
        item.weight = 50
        item.flags.take = True
        item.hold = True

    item.name = buf

    if itemtype == merc.ITEM_SYMBOL:
        item.short_descr = "a {} of {}".format(itemkind, itemname)
    else:
        item.short_descr = "a {}".format(itemkind)

    item.description = "A {} lies here.".format(itemkind)
    item.questmaker = ch.name
    ch.put(item)
    handler_game.act("$p suddenly appears in your hands.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p suddenly appears in $n's hands.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="major creation",
        skill_level=4,
        spell_fun=spl_major_creation,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(551),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Major Creation!"
    )
)
