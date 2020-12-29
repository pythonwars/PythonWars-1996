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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_mend(sn, level, ch, victim, target):
    ribs = 0
    rib_list = [(merc.BROKEN_RIBS_1, 1), (merc.BROKEN_RIBS_2, 2), (merc.BROKEN_RIBS_4, 4), (merc.BROKEN_RIBS_8, 8), (merc.BROKEN_RIBS_16, 16)]
    for (aa, bb) in rib_list:
        if victim.body.is_set(aa):
            ribs += bb

    if ribs > 0:
        for (aa, bb) in rib_list:
            victim.body.rem_bit(aa)

        ribs -= 1

        if ribs >= 16:
            ribs -= 16
            victim.body.set_bit(merc.BROKEN_RIBS_16)

        if ribs >= 8:
            ribs -= 8
            victim.body.set_bit(merc.BROKEN_RIBS_8)

        if ribs >= 4:
            ribs -= 4
            victim.body.set_bit(merc.BROKEN_RIBS_4)

        if ribs >= 2:
            ribs -= 2
            victim.body.set_bit(merc.BROKEN_RIBS_2)

        if ribs >= 1:
            ribs -= 1
            victim.body.set_bit(merc.BROKEN_RIBS_1)

        handler_game.act("One of $n's ribs snap back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("One of your ribs snap back into place.", victim, None, None, merc.TO_CHAR)
    elif victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
        handler_game.act("$n's nose snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your nose snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.body.rem_bit(merc.BROKEN_NOSE)
    elif victim.head.is_set(merc.BROKEN_JAW):
        handler_game.act("$n's jaw snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your jaw snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.body.rem_bit(merc.BROKEN_JAW)
    elif victim.head.is_set(merc.BROKEN_SKULL):
        handler_game.act("$n's skull knits itself back together.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your skull knits itself back together.", victim, None, None, merc.TO_CHAR)
        victim.head.rem_bit(merc.BROKEN_SKULL)
    elif victim.body.is_set(merc.BROKEN_SPINE):
        handler_game.act("$n's spine knits itself back together.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your spine knits itself back together.", victim, None, None, merc.TO_CHAR)
        victim.body.rem_bit(merc.BROKEN_SPINE)
    elif victim.body.is_set(merc.BROKEN_NECK):
        handler_game.act("$n's neck snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your neck snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.body.rem_bit(merc.BROKEN_NECK)
    elif victim.arm_left.is_set(merc.BROKEN_ARM) and not victim.arm_left.is_set(merc.LOST_ARM):
        handler_game.act("$n's left arm snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left arm snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_ARM)
    elif victim.arm_right.is_set(merc.BROKEN_ARM) and not victim.arm_right.is_set(merc.LOST_ARM):
        handler_game.act("$n's right arm snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right arm snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_ARM)
    elif victim.leg_left.is_set(merc.BROKEN_LEG) and not victim.leg_left.is_set(merc.LOST_LEG):
        handler_game.act("$n's left leg snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left leg snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_LEG)
    elif victim.leg_right.is_set(merc.BROKEN_LEG) and not victim.leg_right.is_set(merc.LOST_LEG):
        handler_game.act("$n's right leg snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right leg snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.leg_right.rem_bit(merc.BROKEN_LEG)
    elif victim.arm_left.is_set(merc.BROKEN_THUMB) and not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and \
            not victim.arm_left.is_set(merc.LOST_THUMB):
        handler_game.act("$n's left thumb snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left thumb snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_THUMB)
    elif victim.arm_left.is_set(merc.BROKEN_FINGER_I) and not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and \
            not victim.arm_left.is_set(merc.LOST_FINGER_I):
        handler_game.act("$n's left index finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left index finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_FINGER_I)
    elif victim.arm_left.is_set(merc.BROKEN_FINGER_M) and not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and \
            not victim.arm_left.is_set(merc.LOST_FINGER_M):
        handler_game.act("$n's left middle finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left middle finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_FINGER_M)
    elif victim.arm_left.is_set(merc.BROKEN_FINGER_R) and not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and \
            not victim.arm_left.is_set(merc.LOST_FINGER_R):
        handler_game.act("$n's left ring finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left ring finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_FINGER_R)
    elif victim.arm_left.is_set(merc.BROKEN_FINGER_L) and not victim.arm_left.is_set(merc.LOST_ARM) and not victim.arm_left.is_set(merc.LOST_HAND) and \
            not victim.arm_left.is_set(merc.LOST_FINGER_L):
        handler_game.act("$n's left little finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your left little finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_left.rem_bit(merc.BROKEN_FINGER_L)
    elif victim.arm_right.is_set(merc.BROKEN_THUMB) and not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and \
            not victim.arm_right.is_set(merc.LOST_THUMB):
        handler_game.act("$n's right thumb snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right thumb snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_THUMB)
    elif victim.arm_right.is_set(merc.BROKEN_FINGER_I) and not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and \
            not victim.arm_right.is_set(merc.LOST_FINGER_I):
        handler_game.act("$n's right index finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right index finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_FINGER_I)
    elif victim.arm_right.is_set(merc.BROKEN_FINGER_M) and not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and \
            not victim.arm_right.is_set(merc.LOST_FINGER_M):
        handler_game.act("$n's right middle finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right middle finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_FINGER_M)
    elif victim.arm_right.is_set(merc.BROKEN_FINGER_R) and not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and \
            not victim.arm_right.is_set(merc.LOST_FINGER_R):
        handler_game.act("$n's right ring finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right ring finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_FINGER_R)
    elif victim.arm_right.is_set(merc.BROKEN_FINGER_L) and not victim.arm_right.is_set(merc.LOST_ARM) and not victim.arm_right.is_set(merc.LOST_HAND) and \
            not victim.arm_right.is_set(merc.LOST_FINGER_L):
        handler_game.act("$n's right little finger snaps back into place.", victim, None, None, merc.TO_ROOM)
        handler_game.act("Your right little finger snaps back into place.", victim, None, None, merc.TO_CHAR)
        victim.arm_right.rem_bit(merc.BROKEN_FINGER_L)
    elif victim.body.is_set(merc.CUT_THROAT):
        if victim.bleeding.is_set(merc.BLEEDING_THROAT):
            ch.send("But their throat is still bleeding!\n")
            return

        handler_game.act("The wound in $n's throat closes up.", victim, None, None, merc.TO_ROOM)
        handler_game.act("The wound in your throat closes up.", victim, None, None, merc.TO_CHAR)
        victim.body.rem_bit(merc.CUT_THROAT)
    else:
        ch.send("They have no bones to mend.\n")

    if not ch.is_npc() and victim != ch:
        ch.humanity()


const.register_spell(
    const.skill_type(
        name="mend",
        skill_level=1,
        spell_fun=spl_mend,
        target=merc.TAR_CHAR_DEFENSIVE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(610),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="!Mend!"
    )
)
