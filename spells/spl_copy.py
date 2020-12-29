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
import merc
import state_checks


# noinspection PyUnusedLocal
def spl_copy(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if ch.is_npc():
        return

    if not arg1 or not arg2:
        ch.send("Syntax is: cast 'copy' <rune> <page>.\n")
        return

    rune = ch.get_item_carry(arg1)
    if not rune:
        ch.send("You are not carrying that rune.\n")
        return

    if rune.item_type != merc.ITEM_SYMBOL:
        ch.send("That item isn't a rune.\n")
        return

    page = ch.get_item_carry(arg2)
    if not page:
        ch.send("You are not carrying that page.\n")
        return

    if page.item_type != merc.ITEM_PAGE:
        ch.send("That item isn't a page.\n")
        return

    if page.value[1] > 0 and not state_checks.is_set(ch.powers[merc.MPOWER_RUNE1], page.value[1]):
        ch.send("You don't understand how that rune works.\n")
        return

    if page.value[2] > 0 and not state_checks.is_set(ch.powers[merc.MPOWER_RUNE2], page.value[2]):
        ch.send("You don't understand how that glyph works.\n")
        return

    if page.value[3] > 0 and not state_checks.is_set(ch.powers[merc.MPOWER_RUNE3], page.value[3]):
        ch.send("You don't understand how that sigil works.\n")
        return

    if rune.value[1] == merc.RUNE_MASTER:
        if page.quest.is_set(merc.QUEST_MASTER_RUNE):
            ch.send("There is already a master rune draw on this page.\n")
            return
        elif sum([page.value[0], page.value[1], page.value[2], page.value[3]]) > 0:
            ch.send("There is already a spell on this page.\n")
            return
        else:
            handler_game.act("You copy $p rune onto $P.", ch, rune, page, merc.TO_CHAR)
            handler_game.act("$n copies $p rune onto $P.", ch, rune, page, merc.TO_ROOM)
            page.quest.set_bit(merc.QUEST_MASTER_RUNE)
        return
    elif page.quest.is_set(merc.QUEST_MASTER_RUNE):
        ch.send("There is already a master rune draw on this page.\n")
        return
    elif rune.value[1] > 0 and not state_checks.is_set(page.value[1], rune.value[1]):
        page.value[1] += rune.value[1]
    elif rune.value[1] > 0:
        ch.send("That rune has already been copied onto the page.\n")
        return
    elif rune.value[2] > 0 and not state_checks.is_set(page.value[2], rune.value[2]):
        page.value[2] += rune.value[2]
    elif rune.value[2] > 0:
        ch.send("That glyph has already been copied onto the page.\n")
        return
    elif rune.value[3] > 0 and not state_checks.is_set(page.value[3], rune.value[3]):
        page.value[3] += rune.value[3]
    elif rune.value[3] > 0:
        ch.send("That glyph has already been copied onto the page.\n")
        return

    handler_game.act("You copy $p onto $P.", ch, rune, page, merc.TO_CHAR)
    handler_game.act("$n copies $p onto $P.", ch, rune, page, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="copy",
        skill_level=4,
        spell_fun=spl_copy,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(552),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Copy!"
    )
)
