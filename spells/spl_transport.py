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
def spl_transport(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if not arg1:
        ch.send("Transport which object?\n")
        return

    if not arg2:
        ch.send("Transport who whom?\n")
        return

    victim = ch.get_char_world(arg2)
    if not victim:
        ch.not_npc(arg2)
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    if not victim.is_npc() and not victim.immune.is_set(merc.IMM_TRANSPORT):
        ch.send("You are unable to transport anything to them.\n")
        return

    handler_game.act("$p vanishes from your hands in an swirl of smoke.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$p vanishes from $n's hands in a swirl of smoke.", ch, item, None, merc.TO_ROOM)
    ch.get(item)
    victim.put(item)
    handler_game.act("$p appears in your hands in an swirl of smoke.", victim, item, None, merc.TO_CHAR)
    handler_game.act("$p appears in $n's hands in an swirl of smoke.", victim, item, None, merc.TO_ROOM)
    ch.save(force=True)
    victim.save(force=True)


const.register_spell(
    const.skill_type(
        name="transport",
        skill_level=1,
        spell_fun=spl_transport,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(607),
        min_mana=12,
        beats=24,
        noun_damage="",
        msg_off="!Transport!"
    )
)
