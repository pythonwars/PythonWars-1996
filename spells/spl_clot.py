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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_clot(sn, level, ch, victim, target):
    if victim.bleeding.is_set(merc.BLEEDING_HEAD):
        handler_game.act("$n's head stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your head stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_HEAD)
    elif victim.bleeding.is_set(merc.BLEEDING_THROAT):
        handler_game.act("$n's throat stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your throat stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_THROAT)
    elif victim.bleeding.is_set(merc.BLEEDING_ARM_L):
        handler_game.act("The stump of $n's left arm stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your left arm stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_ARM_L)
    elif victim.bleeding.is_set(merc.BLEEDING_ARM_R):
        handler_game.act("The stump of $n's right arm stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your right arm stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_ARM_R)
    elif victim.bleeding.is_set(merc.BLEEDING_LEG_L):
        handler_game.act("The stump of $n's left leg stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your left leg stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_LEG_L)
    elif victim.bleeding.is_set(merc.BLEEDING_LEG_R):
        handler_game.act("The stump of $n's right leg stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your right leg stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_LEG_R)
    elif victim.bleeding.is_set(merc.BLEEDING_HAND_L):
        handler_game.act("The stump of $n's left wrist stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your left wrist stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_HAND_L)
    elif victim.bleeding.is_set(merc.BLEEDING_HAND_R):
        handler_game.act("The stump of $n's right wrist stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your right wrist stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_HAND_R)
    elif victim.bleeding.is_set(merc.BLEEDING_FOOT_L):
        handler_game.act("The stump of $n's left ankle stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your left ankle stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_FOOT_L)
    elif victim.bleeding.is_set(merc.BLEEDING_FOOT_R):
        handler_game.act("The stump of $n's right ankle stops bleeding.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The stump of your right ankle stops bleeding.", victim, None, None, merc.TO_CHAR)
        victim.bleeding.rem_bit(merc.BLEEDING_FOOT_R)
    else:
        ch.send("They have no wounds to clot.\n")

    if not ch.is_npc() and victim != ch:
        ch.humanity()


const.register_spell(
    const.skill_type(
        name="clot",
        skill_level=1,
        spell_fun=spl_clot,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(609),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="!Clot!"
    )
)
