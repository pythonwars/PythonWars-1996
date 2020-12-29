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
import state_checks


# noinspection PyUnusedLocal
def spl_remove_page(sn, level, ch, victim, target):
    handler_magic.target_name, arg = game_utils.read_word(handler_magic.target_name)

    if not arg:
        ch.send("Syntax is: cast 'remove page' <book>.\n")
        return

    book = ch.get_item_carry(arg)
    if not book:
        ch.send("You are not carrying that book.\n")
        return

    if book.item_type != merc.ITEM_BOOK:
        ch.send("That item isn't a book.\n")
        return

    if state_checks.is_set(book.value[1], merc.CONT_CLOSED):
        ch.send("First you need to open it!\n")
        return

    if book.value[2] == 0:
        ch.send("You cannot remove the index page!\n")
        return

    page = book.get_page(book.value[2])
    if not page:
        ch.send("The page seems to have been torn out.\n")
        return

    book.get(page)
    ch.put(page)
    page.value[0] = 0
    handler_game.act("You remove $p from $P.", ch, page, book, merc.TO_CHAR)
    handler_game.act("$n removes $p from $P.", ch, page, book, merc.TO_ROOM)

    count = 0
    for page_id in book.inventory[:]:
        page = instance.items[page_id]

        count += 1
        page.value[0] = count

    book.value[3] = count
    if book.value[2] > book.value[3]:
        book.value[2] = book.value[3]


const.register_spell(
    const.skill_type(
        name="remove page",
        skill_level=4,
        spell_fun=spl_remove_page,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(564),
        min_mana=10,
        beats=12,
        noun_damage="",
        msg_off="!Remove Page!"
    )
)
