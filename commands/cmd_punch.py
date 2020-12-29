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
import fight
import game_utils
import handler_game
import interp
import merc


def cmd_punch(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.level < const.skill_table["punch"].skill_level:
        ch.send("First you should learn to punch.\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if fight.is_safe(ch, victim):
        return

    if victim.hit < victim.max_hit:
        ch.send("They are hurt and suspicious.\n")
        return

    if victim.position < merc.POS_FIGHTING:
        ch.send("You can only punch someone who is standing.\n")
        return

    ch.wait_state(const.skill_table["punch"].beats)

    if ch.is_npc() or game_utils.number_percent() < ch.learned["punch"]:
        dam = game_utils.number_range(1, 4)
    else:
        fight.damage(ch, victim, 0, "punch")
        return

    dam += ch.damroll

    if dam == 0:
        dam = 1

    if not victim.is_awake():
        dam *= 2

    if not ch.is_npc():
        dam += (dam * (ch.wpn[0] // 100))

    if dam <= 0:
        dam = 1

    if not victim.is_npc() and victim.is_werewolf() and victim.powers[merc.WPOWER_BOAR] > 3:
        fight.damage(ch, victim, 0, "punch")

        if game_utils.number_percent() <= 25 and not ch.arm_left.is_set(merc.LOST_ARM) and not ch.arm_left.is_set(merc.LOST_HAND):
            broke = False
            if not ch.arm_left.is_set(merc.LOST_FINGER_I) and not ch.arm_left.is_set(merc.BROKEN_FINGER_I):
                ch.arm_left.set_bit(merc.BROKEN_FINGER_I)
                broke = True
            if not ch.arm_left.is_set(merc.LOST_FINGER_M) and not ch.arm_left.is_set(merc.BROKEN_FINGER_M):
                ch.arm_left.set_bit(merc.BROKEN_FINGER_M)
                broke = True
            if not ch.arm_left.is_set(merc.LOST_FINGER_R) and not ch.arm_left.is_set(merc.BROKEN_FINGER_R):
                ch.arm_left.set_bit(merc.BROKEN_FINGER_R)
                broke = True
            if not ch.arm_left.is_set(merc.LOST_FINGER_L) and not ch.arm_left.is_set(merc.BROKEN_FINGER_L):
                ch.arm_left.set_bit(merc.BROKEN_FINGER_L)
                broke = True

            if broke:
                handler_game.act("The fingers on your left hand shatter under the impact of the blow!", ch, None, None, merc.TO_CHAR)
                handler_game.act("The fingers on $n's left hand shatter under the impact of the blow!", ch, None, None, merc.TO_ROOM)
        elif game_utils.number_percent() <= 25 and not ch.arm_right.is_set(merc.LOST_ARM) and not ch.arm_right.is_set(merc.LOST_HAND):
            broke = False
            if not ch.arm_right.is_set(merc.LOST_FINGER_I) and not ch.arm_right.is_set(merc.BROKEN_FINGER_I):
                ch.arm_right.set_bit(merc.BROKEN_FINGER_I)
                broke = True
            if not ch.arm_right.is_set(merc.LOST_FINGER_M) and not ch.arm_right.is_set(merc.BROKEN_FINGER_M):
                ch.arm_right.set_bit(merc.BROKEN_FINGER_M)
                broke = True
            if not ch.arm_right.is_set(merc.LOST_FINGER_R) and not ch.arm_right.is_set(merc.BROKEN_FINGER_R):
                ch.arm_right.set_bit(merc.BROKEN_FINGER_R)
                broke = True
            if not ch.arm_right.is_set(merc.LOST_FINGER_L) and not ch.arm_right.is_set(merc.BROKEN_FINGER_L):
                ch.arm_right.set_bit(merc.BROKEN_FINGER_L)
                broke = True

            if broke:
                handler_game.act("The fingers on your right hand shatter under the impact of the blow!", ch, None, None, merc.TO_CHAR)
                handler_game.act("The fingers on $n's right hand shatter under the impact of the blow! ", ch, None, None, merc.TO_ROOM)
        fight.stop_fighting(victim, True)
        return

    fight.damage(ch, victim, dam, "punch")

    if not victim or victim.position == merc.POS_DEAD or dam < 1:
        return

    if victim.position == merc.POS_FIGHTING:
        fight.stop_fighting(victim, True)

    if game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_NOSE) and not victim.head.is_set(merc.LOST_NOSE):
        handler_game.act("Your nose shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n's nose shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
        victim.head.set_bit(merc.BROKEN_NOSE)
    elif game_utils.number_percent() <= 25 and not victim.head.is_set(merc.BROKEN_JAW):
        handler_game.act("Your jaw shatters under the impact of the blow!", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n's jaw shatters under the impact of the blow!", victim, None, None, merc.TO_ROOM)
        victim.head.set_bit(merc.BROKEN_JAW)

    handler_game.act("You fall to the ground stunned!", victim, None, None, merc.TO_CHAR)
    handler_game.act("$n falls to the ground stunned!", victim, None, None, merc.TO_ROOM)
    victim.position = merc.POS_STUNNED


interp.register_command(
    interp.CmdType(
        name="punch",
        cmd_fun=cmd_punch,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
