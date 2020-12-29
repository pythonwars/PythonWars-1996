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

import game_utils
import interp
import living
import merc
import state_checks


def cmd_read(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("What do you wish to read?\n")
        return

    item = ch.get_item_here(arg)
    if not item:
        ch.send("You don't have that book.\n")
        return

    if item.item_type == merc.ITEM_PAGE:
        buf = ["{}.\n".format("Untitled page" if not item.victpoweruse else item.victpoweruse.capitalize())]

        if not item.chpoweruse:
            if not item.are_runes():
                buf += "This page is blank.\n"
            elif ch.is_affected(merc.AFF_DETECT_MAGIC) and not item.quest.is_set(merc.QUEST_MASTER_RUNE) and not item.spectype.is_set(merc.ADV_STARTED):
                buf += living.Living.show_runes(item, False)
            else:
                buf += "This page is blank.\n"
            ch.send("".join(buf))
            return

        buf += "--------------------------------------------------------------------------------\n"
        buf += item.chpoweruse + "\n"
        buf += "--------------------------------------------------------------------------------\n"

        if ch.is_affected(merc.AFF_DETECT_MAGIC) and not item.quest.is_set(merc.QUEST_MASTER_RUNE) and not item.spectype.is_set(merc.ADV_STARTED):
            buf += living.Living.show_runes(item, False)
        ch.send("".join(buf))
        return

    if item.item_type != merc.ITEM_BOOK:
        ch.send("That's not a book.\n")
        return

    if state_checks.is_set(item.value[1], merc.CONT_CLOSED):
        if not item.victpoweruse:
            ch.send("The book is untitled.\n")
        else:
            ch.send("The book is titled '{}'.\n".format(item.victpoweruse))
        return

    if item.value[2] == 0:
        buf = ["Index page.\n"]

        if item.value[3] <= 0:
            buf += "<No pages>\n"
            ch.send("".join(buf))
            return

        for page in merc.irange(1, item.value[3]):
            buf += "Page {}:".format(page)
            buf += ch.show_page(item, page, True)
    else:
        buf = ["Page {}:".format(item.value[2])]
        buf += ch.show_page(item, item.value[2], False)
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="read",
        cmd_fun=cmd_read,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
