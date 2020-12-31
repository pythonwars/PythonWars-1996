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


def cmd_consider(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Consider killing whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    handler_game.act("You examine $N closely, looking for $S weaknesses.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n examine $N closely, looking for $S weaknesses.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n examines you closely, looking for your weaknesses.", ch, None, victim, merc.TO_VICT)

    if not victim.is_npc():
        ch.cmd_skill(victim.name)

    if not victim.is_npc() and victim.is_vampire() and victim.extra.is_set(merc.EXTRA_FAKE_CON):
        con_hit = victim.fake_hit
        con_dam = victim.fake_dam
        con_ac = victim.fake_ac
        con_hp = victim.fake_hp
    else:
        con_hit = victim.hitroll
        con_dam = victim.damroll
        con_ac = victim.armor
        con_hp = victim.hit

    if con_hp < 1:
        con_hp = 1

    overall = 0

    diff = victim.level - ch.level + con_hit - ch.hitroll
    if diff <= -35:
        msg = "You are FAR more skilled than $M."
        overall += 3
    elif diff <= -15:
        msg = "$E is not as skilled as you are."
        overall += 2
    elif diff <= -5:
        msg = "$E doesn't seem quite as skilled as you."
        overall += 1
    elif diff <= 5:
        msg = "You are about as skilled as $M."
    elif diff <= 15:
        msg = "$E is slightly more skilled than you are."
        overall -= 1
    elif diff <= 35:
        msg = "$E seems more skilled than you are."
        overall -= 2
    else:
        msg = "$E is FAR more skilled than you."
        overall -= 3
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)

    diff = victim.level - ch.level + con_dam - ch.damroll
    if diff <= -35:
        msg = "You are FAR more powerful than $M."
        overall += 3
    elif diff <= -15:
        msg = "$E is not as powerful as you are."
        overall += 2
    elif diff <= -5:
        msg = "$E doesn't seem quite as powerful as you."
        overall += 1
    elif diff <= 5:
        msg = "You are about as powerful as $M."
    elif diff <= 15:
        msg = "$E is slightly more powerful than you are."
        overall -= 1
    elif diff <= 35:
        msg = "$E seems more powerful than you are."
        overall -= 2
    else:
        msg = "$E is FAR more powerful than you."
        overall -= 3
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)

    diff = ch.hit * 100 // con_hp
    if diff <= 10:
        msg = "$E is currently FAR healthier than you are."
        overall -= 3
    elif diff <= 50:
        msg = "$E is currently much healthier than you are."
        overall -= 2
    elif diff <= 75:
        msg = "$E is currently slightly healthier than you are."
        overall -= 1
    elif diff <= 125:
        msg = "$E is currently about as healthy as you are."
    elif diff <= 200:
        msg = "You are currently slightly healthier than $M."
        overall += 1
    elif diff <= 500:
        msg = "You are currently much healthier than $M."
        overall += 2
    else:
        msg = "You are currently FAR healthier than $M."
        overall += 3
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)

    diff = con_ac - ch.armor
    if diff <= -100:
        msg = "$E is FAR better armoured than you."
        overall -= 3
    elif diff <= -50:
        msg = "$E looks much better armoured than you."
        overall -= 2
    elif diff <= -25:
        msg = "$E looks better armoured than you."
        overall -= 1
    elif diff <= 25:
        msg = "$E seems about as well armoured as you."
    elif diff <= 50:
        msg = "You are better armoured than $M."
        overall += 1
    elif diff <= 100:
        msg = "You are much better armoured than $M."
        overall += 2
    else:
        msg = "You are FAR better armoured than $M."
        overall += 3
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)

    diff = overall
    if diff <= -11:
        msg = "Conclusion: $E would kill you in seconds."
    elif diff <= -7:
        msg = "Conclusion: You would need a lot of luck to beat $M."
    elif diff <= -3:
        msg = "Conclusion: You would need some luck to beat $N."
    elif diff <= 2:
        msg = "Conclusion: It would be a very close fight."
    elif diff <= 6:
        msg = "Conclusion: You shouldn't have a lot of trouble defeating $M."
    elif diff <= 10:
        msg = "Conclusion: $N is no match for you.  You can easily beat $M."
    else:
        msg = "Conclusion: $E wouldn't last more than a few seconds against you."
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="consider",
        cmd_fun=cmd_consider,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
