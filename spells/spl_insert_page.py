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
def spl_insert_page(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if not arg1 or not arg2:
        ch.send("Syntax is: cast 'insert page' <page> <book>.\n")
        return

    page = ch.get_item_carry(arg1)
    if not page:
        ch.send("You are not carrying that page.\n")
        return

    if page.item_type != merc.ITEM_PAGE:
        ch.send("That item isn't a page.\n")
        return

    book = ch.get_item_carry(arg2)
    if not book:
        ch.send("You are not carrying that book.\n")
        return

    if book.item_type != merc.ITEM_BOOK:
        ch.send("That item isn't a book.\n")
        return

    if state_checks.is_set(book.value[1], merc.CONT_CLOSED):
        ch.send("First you need to open it!\n")
        return

    ch.get(page)
    book.put(page)
    book.value[3] += 1
    book.value[2] = book.value[3]
    book.value[0] = book.value[3]
    page.specpower = book.value[3] + 1
    handler_game.act("You insert $p into $P.", ch, page, book, merc.TO_CHAR)
    handler_game.act("$n inserts $p into $P.", ch, page, book, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="insert page",
        skill_level=4,
        spell_fun=spl_insert_page,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(553),
        min_mana=10,
        beats=12,
        noun_damage="",
        msg_off="!Insert Page!"
    )
)
