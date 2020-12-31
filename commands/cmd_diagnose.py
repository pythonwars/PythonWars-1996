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
import interp
import merc


def check_left_arm(ch, victim):
    if victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.LOST_ARM):
        handler_game.act("$N has lost both of $S arms.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_ARM_L) and victim.bleeding.is_set(merc.BLEEDING_ARM_R):
            handler_game.act("...Blood is spurting from both stumps.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_ARM_L):
            handler_game.act("...Blood is spurting from the left stump.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_ARM_R):
            handler_game.act("...Blood is spurting from the right stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.arm_left.is_set(merc.LOST_ARM):
        handler_game.act("$N has lost $S left arm.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_ARM_L):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.arm_left.is_set(merc.BROKEN_ARM) and victim.arm_right.is_set(merc.BROKEN_ARM):
        handler_game.act("$N arms are both broken.", ch, None, victim, merc.TO_CHAR)
    elif victim.arm_left.is_set(merc.BROKEN_ARM):
        handler_game.act("$N's left arm is broken.", ch, None, victim, merc.TO_CHAR)

    if victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_HAND) and not victim.arm_right.is_set(merc.LOST_ARM):
        handler_game.act("$N has lost both of $S hands.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_HAND_L) and victim.bleeding.is_set(merc.BLEEDING_HAND_R):
            handler_game.act("...Blood is spurting from both stumps.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_HAND_L):
            handler_game.act("...Blood is spurting from the left stump.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_HAND_R):
            handler_game.act("...Blood is spurting from the right stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.arm_left.is_set(merc.LOST_HAND):
        handler_game.act("$N has lost $S left hand.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_HAND_L):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    fingers = 0
    part_list = [merc.LOST_FINGER_I, merc.LOST_FINGER_M, merc.LOST_FINGER_R, merc.LOST_FINGER_L]
    for part in part_list:
        if victim.arm_left.is_set(part):
            fingers += 1

    finger = "finger{}".format("" if fingers == 1 else "s")
    if fingers > 0 and victim.arm_left.is_set(merc.LOST_THUMB):
        handler_game.act("$N has lost {} {} and $S thumb from $S left hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif fingers > 0:
        handler_game.act("$N has lost {} {} from $S left hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif victim.arm_left.is_set(merc.LOST_THUMB):
        handler_game.act("$N has lost the thumb from $S left hand.", ch, None, victim, merc.TO_CHAR)

    fingers = 0
    part_list = [(merc.BROKEN_FINGER_I, merc.LOST_FINGER_I), (merc.BROKEN_FINGER_M, merc.LOST_FINGER_M),
                 (merc.BROKEN_FINGER_R, merc.LOST_FINGER_R), (merc.BROKEN_FINGER_L, merc.LOST_FINGER_L)]
    for (aa, bb) in part_list:
        if victim.arm_left.is_set(aa) and not victim.arm_left.is_set(bb):
            fingers += 1

    finger = "finger{}".format("" if fingers == 1 else "s")
    if fingers > 0 and victim.arm_left.is_set(merc.BROKEN_THUMB) and not victim.arm_left.is_set(merc.LOST_THUMB):
        handler_game.act("$N has broken {} {} and $S thumb on $S left hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif fingers > 0:
        handler_game.act("$N has broken {} {} on $S left hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif victim.arm_left.is_set(merc.BROKEN_THUMB) and not victim.arm_left.is_set(merc.LOST_THUMB):
        handler_game.act("$N has broken the thumb on $S left hand.", ch, None, victim, merc.TO_CHAR)


def check_right_arm(ch, victim):
    if victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.LOST_ARM):
        return

    if victim.arm_right.is_set(merc.LOST_ARM):
        handler_game.act("$N has lost $S right arm.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_ARM_R):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    if not victim.arm_left.is_set(merc.BROKEN_ARM) and victim.arm_right.is_set(merc.BROKEN_ARM):
        handler_game.act("$N's right arm is broken.", ch, None, victim, merc.TO_CHAR)
    elif victim.arm_left.is_set(merc.LOST_ARM) and victim.arm_right.is_set(merc.BROKEN_ARM):
        handler_game.act("$N's right arm is broken.", ch, None, victim, merc.TO_CHAR)

    if victim.arm_left.is_set(merc.LOST_HAND) and victim.arm_right.is_set(merc.LOST_HAND):
        return

    if victim.arm_right.is_set(merc.LOST_HAND):
        handler_game.act("$N has lost $S right hand.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_HAND_R):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    fingers = 0
    part_list = [merc.LOST_FINGER_I, merc.LOST_FINGER_M, merc.LOST_FINGER_R, merc.LOST_FINGER_I]
    for part in part_list:
        if victim.arm_right.is_set(part):
            fingers += 1

    finger = "finger{}".format("" if fingers == 1 else "s")
    if fingers > 0 and victim.arm_right.is_set(merc.LOST_THUMB):
        handler_game.act("$N has lost {} {} and $S thumb from $S right hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif fingers > 0:
        handler_game.act("$N has lost {} {} from $S right hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif victim.arm_right.is_set(merc.LOST_THUMB):
        handler_game.act("$N has lost the thumb from $S right hand.", ch, None, victim, merc.TO_CHAR)

    fingers = 0
    part_list = [(merc.BROKEN_FINGER_I, merc.LOST_FINGER_I), (merc.BROKEN_FINGER_M, merc.LOST_FINGER_M),
                 (merc.BROKEN_FINGER_R, merc.LOST_FINGER_R), (merc.BROKEN_FINGER_L, merc.LOST_FINGER_L)]
    for (aa, bb) in part_list:
        if victim.arm_right.is_set(aa) and not victim.arm_right.is_set(bb):
            fingers += 1

    finger = "finger{}".format("" if fingers == 1 else "s")
    if fingers > 0 and victim.arm_right.is_set(merc.BROKEN_THUMB) and not victim.arm_right.is_set(merc.LOST_THUMB):
        handler_game.act("$N has broken {} {} and $S thumb on $S right hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif fingers > 0:
        handler_game.act("$N has broken {} {} on $S right hand.".format(fingers, finger), ch, None, victim, merc.TO_CHAR)
    elif victim.arm_right.is_set(merc.BROKEN_THUMB) and not victim.arm_right.is_set(merc.LOST_THUMB):
        handler_game.act("$N has broken the thumb on $S right hand.", ch, None, victim, merc.TO_CHAR)


def check_left_leg(ch, victim):
    if victim.leg_left.is_set(merc.LOST_LEG) and victim.leg_right.is_set(merc.LOST_LEG):
        handler_game.act("$N has lost both of $S legs.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_LEG_L) and victim.bleeding.is_set(merc.BLEEDING_LEG_R):
            handler_game.act("...Blood is spurting from both stumps.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_LEG_L):
            handler_game.act("...Blood is spurting from the left stump.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_LEG_R):
            handler_game.act("...Blood is spurting from the right stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.leg_left.is_set(merc.LOST_LEG):
        handler_game.act("$N has lost $S left leg.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_LEG_L):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.leg_left.is_set(merc.BROKEN_LEG) and victim.leg_right.is_set(merc.BROKEN_LEG):
        handler_game.act("$N legs are both broken.", ch, None, victim, merc.TO_CHAR)
    elif victim.leg_left.is_set(merc.BROKEN_LEG):
        handler_game.act("$N's left leg is broken.", ch, None, victim, merc.TO_CHAR)

    if victim.leg_left.is_set(merc.LOST_FOOT) and victim.leg_right.is_set(merc.LOST_FOOT):
        handler_game.act("$N has lost both of $S feet.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_FOOT_L) and victim.bleeding.is_set(merc.BLEEDING_FOOT_R):
            handler_game.act("...Blood is spurting from both stumps.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_FOOT_L):
            handler_game.act("...Blood is spurting from the left stump.", ch, None, victim, merc.TO_CHAR)
        elif victim.bleeding.is_set(merc.BLEEDING_FOOT_R):
            handler_game.act("...Blood is spurting from the right stump.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.leg_left.is_set(merc.LOST_FOOT):
        handler_game.act("$N has lost $S left foot.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_FOOT_L):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    toes = 0
    part_list = [merc.LOST_TOE_A, merc.LOST_TOE_B, merc.LOST_TOE_C, merc.LOST_TOE_D]
    for part in part_list:
        if victim.leg_left.is_set(part):
            toes += 1

    toe = "toe{}".format("" if toes == 1 else "s")
    if toes > 0 and victim.leg_left.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has lost {} {} and $S big toe from $S left foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif toes > 0:
        handler_game.act("$N has lost {} {} from $S left foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif victim.leg_left.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has lost the big toe from $S left foot.", ch, None, victim, merc.TO_CHAR)

    toes = 0
    part_list = [(merc.BROKEN_TOE_A, merc.LOST_TOE_A), (merc.BROKEN_TOE_B, merc.LOST_TOE_B),
                 (merc.BROKEN_TOE_C, merc.LOST_TOE_C), (merc.BROKEN_TOE_D, merc.LOST_TOE_D)]
    for (aa, bb) in part_list:
        if victim.leg_left.is_set(aa) and not victim.leg_left.is_set(bb):
            toes += 1

    toe = "toe{}".format("" if toes == 1 else "s")
    if toes > 0 and victim.leg_left.is_set(merc.BROKEN_TOE_BIG) and not victim.leg_left.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has broken {} {} and $S big toe from $S left foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif toes > 0:
        handler_game.act("$N has broken {} {} on $S left foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif victim.leg_left.is_set(merc.BROKEN_TOE_BIG) and not victim.leg_left.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has broken the big toe on $S left foot.", ch, None, victim, merc.TO_CHAR)


def check_right_leg(ch, victim):
    if victim.leg_left.is_set(merc.LOST_LEG) and victim.leg_right.is_set(merc.LOST_LEG):
        return

    if victim.leg_right.is_set(merc.LOST_LEG):
        handler_game.act("$N has lost $S right leg.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_LEG_R):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    if not victim.leg_left.is_set(merc.BROKEN_LEG) and victim.leg_right.is_set(merc.BROKEN_LEG):
        handler_game.act("$N's right leg is broken.", ch, None, victim, merc.TO_CHAR)

    if victim.leg_left.is_set(merc.LOST_FOOT) and victim.leg_right.is_set(merc.LOST_FOOT):
        return

    if victim.leg_right.is_set(merc.LOST_FOOT):
        handler_game.act("$N has lost $S right foot.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_FOOT_R):
            handler_game.act("...Blood is spurting from the stump.", ch, None, victim, merc.TO_CHAR)
        return

    toes = 0
    part_list = [merc.LOST_TOE_A, merc.LOST_TOE_B, merc.LOST_TOE_C, merc.LOST_TOE_D]
    for part in part_list:
        if victim.leg_right.is_set(part):
            toes += 1

    toe = "toe{}".format("" if toes == 1 else "s")
    if toes > 0 and victim.leg_right.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has lost {} {} and $S big toe from $S right foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif toes > 0:
        handler_game.act("$N has lost {} {} from $S right foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif victim.leg_right.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has lost the big toe from $S right foot.", ch, None, victim, merc.TO_CHAR)

    toes = 0
    part_list = [(merc.BROKEN_TOE_A, merc.LOST_TOE_A), (merc.BROKEN_TOE_B, merc.LOST_TOE_B),
                 (merc.BROKEN_TOE_C, merc.LOST_TOE_C), (merc.BROKEN_TOE_D, merc.LOST_TOE_D)]
    for (aa, bb) in part_list:
        if victim.leg_right.is_set(aa) and not victim.leg_right.is_set(bb):
            toes += 1

    toe = "toe{}".format("" if toes == 1 else "s")
    if toes > 0 and victim.leg_right.is_set(merc.BROKEN_TOE_BIG) and not victim.leg_right.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has broken {} {} and $S big toe on $S right foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif toes > 0:
        handler_game.act("$N has broken {} {} on $S right foot.".format(toes, toe), ch, None, victim, merc.TO_CHAR)
    elif victim.leg_right.is_set(merc.BROKEN_TOE_BIG) and not victim.leg_right.is_set(merc.LOST_TOE_BIG):
        handler_game.act("$N has broken the big toe on $S right foot.", ch, None, victim, merc.TO_CHAR)


def cmd_diagnose(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Who do you wish to diagnose?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    handler_game.act("$n examines $N carefully, diagnosing $S injuries.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n examines you carefully, diagnosing your injuries.", ch, None, victim, merc.TO_VICT)
    handler_game.act("Your diagnoses of $N reveals the following...", ch, None, victim, merc.TO_CHAR)
    ch.send("--------------------------------------------------------------------------------\n")

    if victim.head.empty() and victim.body.empty() and victim.arm_left.empty() and victim.arm_right.empty() and victim.leg_left.empty() and \
            victim.leg_right.empty() and victim.bleeding.empty():
        handler_game.act("$N has no apparent injuries.", ch, None, victim, merc.TO_CHAR)
        ch.send("--------------------------------------------------------------------------------\n")
        return

    # Check head
    if victim.head.is_set(merc.LOST_EYE_L) and victim.head.is_set(merc.LOST_EYE_R):
        handler_game.act("$N has lost both of $S eyes.", ch, None, victim, merc.TO_CHAR)
    elif victim.head.is_set(merc.LOST_EYE_L):
        handler_game.act("$N has lost $S left eye.", ch, None, victim, merc.TO_CHAR)
    elif victim.head.is_set(merc.LOST_EYE_R):
        handler_game.act("$N has lost $S right eye.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.LOST_EAR_L) and victim.head.is_set(merc.LOST_EAR_R):
        handler_game.act("$N has lost both of $S ears.", ch, None, victim, merc.TO_CHAR)
    elif victim.head.is_set(merc.LOST_EAR_L):
        handler_game.act("$N has lost $S left ear.", ch, None, victim, merc.TO_CHAR)
    elif victim.head.is_set(merc.LOST_EAR_R):
        handler_game.act("$N has lost $S right ear.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.LOST_NOSE):
        handler_game.act("$N has lost $S nose.", ch, None, victim, merc.TO_CHAR)
    elif victim.head.is_set(merc.BROKEN_NOSE):
        handler_game.act("$N has got a broken nose.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.BROKEN_JAW):
        handler_game.act("$N has got a broken jaw.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.LOST_HEAD):
        handler_game.act("$N has had $S head cut off.", ch, None, victim, merc.TO_CHAR)

        if victim.bleeding.is_set(merc.BLEEDING_HEAD):
            handler_game.act("...Blood is spurting from the stump of $S neck.", ch, None, victim, merc.TO_CHAR)
    else:
        if victim.body.is_set(merc.BROKEN_NECK):
            handler_game.act("$N has got a broken neck.", ch, None, victim, merc.TO_CHAR)

        if victim.body.is_set(merc.CUT_THROAT):
            handler_game.act("$N has had $S throat cut open.", ch, None, victim, merc.TO_CHAR)

            if victim.bleeding.is_set(merc.BLEEDING_THROAT):
                handler_game.act("...Blood is pouring from the wound.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.BROKEN_SKULL):
        handler_game.act("$N has got a broken skull.", ch, None, victim, merc.TO_CHAR)

    teeth = 0
    part_list = [(merc.LOST_TOOTH_1, 1), (merc.LOST_TOOTH_2, 2), (merc.LOST_TOOTH_4, 4), (merc.LOST_TOOTH_8, 8), (merc.LOST_TOOTH_16, 16)]
    for (aa, bb) in part_list:
        if victim.head.is_set(aa):
            teeth += bb

    if teeth > 0:
        handler_game.act("$N has had {} teeth knocked out.".format(teeth), ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.LOST_TONGUE):
        handler_game.act("$N has had $S tongue ripped out.", ch, None, victim, merc.TO_CHAR)

    if victim.head.is_set(merc.LOST_HEAD):
        ch.send("--------------------------------------------------------------------------------\n")
        return

    # Check body
    ribs = 0
    part_list = [(merc.BROKEN_RIBS_1, 1), (merc.BROKEN_RIBS_2, 2), (merc.BROKEN_RIBS_4, 4), (merc.BROKEN_RIBS_8, 8), (merc.BROKEN_RIBS_16, 16)]
    for (aa, bb) in part_list:
        if victim.body.is_set(aa):
            ribs += bb

    if ribs > 0:
        handler_game.act("$N has got {} broken ribs.".format(ribs), ch, None, victim, merc.TO_CHAR)

    if victim.body.is_set(merc.BROKEN_SPINE):
        handler_game.act("$N has got a broken spine.", ch, None, victim, merc.TO_CHAR)

    # Check arms and legs
    check_left_arm(ch, victim)
    check_right_arm(ch, victim)
    check_left_leg(ch, victim)
    check_right_leg(ch, victim)
    ch.send("--------------------------------------------------------------------------------\n")


interp.register_command(
    interp.CmdType(
        name="diagnose",
        cmd_fun=cmd_diagnose,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
