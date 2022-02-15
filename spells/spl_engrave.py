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
def spl_engrave(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if ch.is_npc():
        return

    if not arg1 or not arg2:
        ch.send("What spell do you wish to engrave, and on what?\n")
        return

    sn = handler_magic.find_spell(ch, arg2)
    if not sn or not sn.spell_fun or (not ch.is_npc() and ch.level < sn.skill_level):
        ch.send("You can't do that.\n")
        return

    if ch.learned[sn] < 100:
        ch.send("You are not adept at that spell.\n")
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that.\n")
        return

    if item.item_type != merc.ITEM_STAFF:
        ch.send("That is not a staff.\n")
        return

    if item.value[0] != 0 or item.value[1] != 0 or item.value[2] != 0 or item.value[3] != 0:
        ch.send("You need an unenchanted staff.\n")
        return

    item_list = [(merc.PURPLE_MAGIC, "purple"), (merc.RED_MAGIC, "red"), (merc.BLUE_MAGIC, "blue"), (merc.GREEN_MAGIC, "green"),
                 (merc.YELLOW_MAGIC, "yellow")]
    for (aa, bb) in item_list:
        if sn.target == aa:
            item.value[0] = ch.spl[aa] // 4
            col = bb
            break
    else:
        ch.send("Oh dear...big bug...please inform an Immortal.\n")
        return

    item.value[1] = (item.value[0] // 10) + 1
    item.value[2] = (item.value[0] // 10) + 1
    item.value[3] = sn
    item.name = f"{ch.name} staff {col} {sn.name}"
    item.short_descr = f"{ch.name}'s {col} staff of {sn.name}"
    item.description = f"A {col} staff is lying here."
    item.flags.take = True
    item.hold = True
    handler_game.act("You engrave $p.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n engraves $p.", ch, item, None, merc.TO_ROOM)


const.register_spell(
    const.skill_type(
        name="engrave",
        skill_level=4,
        spell_fun=spl_engrave,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(616),
        min_mana=300,
        beats=12,
        noun_damage="",
        msg_off="!Engrave!"
    )
)
