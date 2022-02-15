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

import game_utils
import handler_game
import instance
import interp
import merc


# 'Split' originally by Gnort, God of Chaos.
def cmd_split(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Split how much?\n")
        return

    amount = int(arg)
    if amount < 0:
        ch.send("Your group wouldn't like that.\n")
        return

    if amount == 0:
        ch.send("You hand out zero coins, but no one notices.\n")
        return

    if ch.gold < amount:
        ch.send("You don't have that much gold.\n")
        return

    members = 0
    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]

        if gch.is_same_group(ch):
            members += 1

    if members < 2:
        ch.send("Just keep it all.\n")
        return

    share = amount // members
    extra = amount % members

    if share == 0:
        ch.send("Don't even bother, cheapskate.\n")
        return

    ch.gold -= amount
    ch.gold += share + extra
    ch.send(f"You split {amount:,} gold coins.  Your share is {share + extra:,} gold coins.\n")

    buf = f"$n splits {amount:,} gold coins.  Your share is {share:,} gold coins."
    for gch_id in ch.in_room.people[:]:
        gch = instance.characters[gch_id]

        if gch != ch and gch.is_same_group(ch):
            handler_game.act(buf, ch, None, gch, merc.TO_VICT)
            gch.gold += share


interp.register_command(
    interp.CmdType(
        name="split",
        cmd_fun=cmd_split,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
