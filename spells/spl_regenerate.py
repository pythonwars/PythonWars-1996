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


# noinspection PyUnusedLocal
def spl_regenerate(sn, level, ch, victim, target):
    handler_magic.target_name, arg1 = game_utils.read_word(handler_magic.target_name)
    handler_magic.target_name, arg2 = game_utils.read_word(handler_magic.target_name)

    if not arg1:
        ch.send("Which body part?\n")
        return

    if not arg2:
        ch.send("Regenerate which person?\n")
        return

    victim = ch.get_char_room(arg2)
    if not victim:
        ch.not_here(arg2)
        return

    if not victim.bleeding.empty():
        ch.send("You cannot regenerate someone who is still bleeding.\n")
        return

    item = ch.get_item_carry(arg1)
    if not item:
        ch.send("You are not carrying that item.\n")
        return

    teeth = 0
    tooth_list = [(merc.LOST_TOOTH_1, 1), (merc.LOST_TOOTH_2, 2), (merc.LOST_TOOTH_4, 4), (merc.LOST_TOOTH_8, 8), (merc.LOST_TOOTH_16, 16)]
    for (aa, bb) in tooth_list:
        if victim.head.is_set(aa):
            teeth += bb

    if item.vnum == merc.OBJ_VNUM_SLICED_ARM:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_ARM):
            ch.send("They don't need an arm.\n")
            return

        if victim.arm_left.is_set(merc.LOST_ARM):
            victim.arm_left.rem_bit(merc.LOST_ARM)
        elif victim.arm_right.is_set(merc.LOST_ARM):
            victim.arm_right.rem_bit(merc.LOST_ARM)

        handler_game.act("You press $p onto the stump of $N's shoulder.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the stump of $N's shoulder.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the stump of your shoulder.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SLICED_LEG:
        if not victim.leg_left.is_set(merc.LOST_LEG) and not victim.leg_right.is_set(merc.LOST_LEG):
            ch.send("They don't need a leg.\n")
            return

        if victim.leg_left.is_set(merc.LOST_LEG):
            victim.leg_left.rem_bit(merc.LOST_LEG)
        elif victim.leg_right.is_set(merc.LOST_LEG):
            victim.leg_right.rem_bit(merc.LOST_LEG)

        handler_game.act("You press $p onto the stump of $N's hip.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the stump of $N's hip.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the stump of your hip.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SQUIDGY_EYEBALL:
        if not victim.head.is_set(merc.LOST_EYE_L) and not victim.head.is_set(merc.LOST_EYE_R):
            ch.send("They don't need an eye.\n")
            return

        if victim.head.is_set(merc.LOST_EYE_L):
            victim.head.rem_bit(merc.LOST_EYE_L)
        elif victim.head.is_set(merc.LOST_EYE_R):
            victim.head.rem_bit(merc.LOST_EYE_R)

        handler_game.act("You press $p into $N's empty eye socket.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p into $N's empty eye socket.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p into your empty eye socket.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SLICED_EAR:
        if not victim.head.is_set(merc.LOST_EAR_L) and not victim.head.is_set(merc.LOST_EAR_R):
            ch.send("They don't need an ear.\n")
            return

        if victim.head.is_set(merc.LOST_EAR_L):
            victim.head.rem_bit(merc.LOST_EAR_L)
        elif victim.head.is_set(merc.LOST_EAR_R):
            victim.head.rem_bit(merc.LOST_EAR_R)

        handler_game.act("You press $p onto the side of $N's head.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the side of $N's head.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the side of your head.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SLICED_NOSE:
        if not victim.head.is_set(merc.LOST_NOSE):
            ch.send("They don't need a nose.\n")
            return

        victim.head.rem_bit(merc.LOST_NOSE)
        handler_game.act("You press $p onto the front of $N's face.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the front of $N's face.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the front of your face.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_HAND:
        if not victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_left.is_set(merc.LOST_HAND):
            victim.arm_left.rem_bit(merc.LOST_HAND)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.LOST_HAND):
            victim.arm_right.rem_bit(merc.LOST_HAND)
        else:
            ch.send("They don't need a hand.\n")
            return

        handler_game.act("You press $p onto the stump of $N's wrist.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the stump of $N's wrist.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the stump of your wrist.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_FOOT:
        if not victim.leg_left.is_set(merc.LOST_LEG) and victim.leg_left.is_set(merc.LOST_FOOT):
            victim.leg_left.rem_bit(merc.LOST_FOOT)
        elif not victim.leg_right.is_set(merc.LOST_LEG) and victim.leg_right.is_set(merc.LOST_FOOT):
            victim.leg_right.rem_bit(merc.LOST_FOOT)
        else:
            ch.send("They don't need a foot.\n")
            return

        handler_game.act("You press $p onto the stump of $N's ankle.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto the stump of $N's ankle.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto the stump of your ankle.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_THUMB:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_left.is_set(merc.LOST_THUMB):
            victim.arm_left.rem_bit(merc.LOST_THUMB)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_THUMB):
            victim.arm_right.rem_bit(merc.LOST_THUMB)
        else:
            ch.send("They don't need a thumb.\n")
            return

        handler_game.act("You press $p onto $N's hand.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto $N's hand.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto your hand.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_INDEX:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_left.is_set(merc.LOST_FINGER_I):
            victim.arm_left.rem_bit(merc.LOST_FINGER_I)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_FINGER_I):
            victim.arm_right.rem_bit(merc.LOST_FINGER_I)
        else:
            ch.send("They don't need an index finger.\n")
            return

        handler_game.act("You press $p onto $N's hand.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto $N's hand.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto your hand.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_MIDDLE:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_left.is_set(merc.LOST_FINGER_M):
            victim.arm_left.rem_bit(merc.LOST_FINGER_M)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_FINGER_M):
            victim.arm_right.rem_bit(merc.LOST_FINGER_M)
        else:
            ch.send("They don't need a middle finger.\n")
            return

        handler_game.act("You press $p onto $N's hand.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto $N's hand.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto your hand.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_RING:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_left.is_set(merc.LOST_FINGER_R):
            victim.arm_left.rem_bit(merc.LOST_FINGER_R)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_FINGER_R):
            victim.arm_right.rem_bit(merc.LOST_FINGER_R)
        else:
            ch.send("They don't need a ring finger.\n")
            return

        handler_game.act("You press $p onto $N's hand.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto $N's hand.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto your hand.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif item.vnum == merc.OBJ_VNUM_SEVERED_LITTLE:
        if not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_left.is_set(merc.LOST_FINGER_L):
            victim.arm_left.rem_bit(merc.LOST_FINGER_L)
        elif not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_FINGER_L):
            victim.arm_right.rem_bit(merc.LOST_FINGER_L)
        else:
            ch.send("They don't need a little finger.\n")
            return

        handler_game.act("You press $p onto $N's hand.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p onto $N's hand.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p onto your hand.", ch, item, victim, merc.TO_VICT)
        item.extract()
    elif teeth > 0:
        teeth = 0
        tooth_list = [(merc.LOST_TOOTH_1, 1), (merc.LOST_TOOTH_2, 2), (merc.LOST_TOOTH_4, 4), (merc.LOST_TOOTH_8, 8), (merc.LOST_TOOTH_16, 16)]
        for (aa, bb) in tooth_list:
            if victim.head.is_set(aa):
                victim.head.rem_bit(aa)

        teeth -= 1

        if teeth >= 16:
            teeth -= 16
            victim.head.set_bit(merc.LOST_TOOTH_16)

        if teeth >= 8:
            teeth -= 8
            victim.head.set_bit(merc.LOST_TOOTH_8)

        if teeth >= 4:
            teeth -= 4
            victim.head.set_bit(merc.LOST_TOOTH_4)

        if teeth >= 2:
            teeth -= 2
            victim.head.set_bit(merc.LOST_TOOTH_2)

        if teeth >= 1:
            teeth -= 1
            victim.head.set_bit(merc.LOST_TOOTH_1)

        handler_game.act("You press $p into $N's mouth.", ch, item, victim, merc.TO_CHAR)
        handler_game.act("$n presses $p into $N's mouth.", ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$n presses $p into your mouth.", ch, item, victim, merc.TO_VICT)
        item.extract()
    else:
        handler_game.act("There is nowhere to stick $p on $N.", ch, item, victim, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="regenerate",
        skill_level=1,
        spell_fun=spl_regenerate,
        target=merc.TAR_OBJ_INV,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(608),
        min_mana=100,
        beats=12,
        noun_damage="",
        msg_off="!Regenerate!"
    )
)
