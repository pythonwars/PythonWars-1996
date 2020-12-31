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


def cmd_command(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire():
        ch.huh()
        return

    if not ch.vampaff.is_set(merc.VAM_DOMINATE):
        ch.send("You are not trained in the dominate discipline.\n")
        return

    if ch.spl[merc.RED_MAGIC] < 1:
        ch.send("Your mind is too weak.\n")
        return

    if not arg or not argument:
        ch.send("Command whom to do what?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if not victim.is_npc() and victim.level != 3:
        ch.send("You can only command other avatars.\n")
        return

    if victim.is_npc():
        buf = "I think {} wants to {}".format(victim.short_descr, argument)
    elif not victim.is_npc() and victim.is_affected(merc.AFF_POLYMORPH):
        buf = "I think {} wants to {}".format(victim.morph, argument)
    else:
        buf = "I think {} wants to {}".format(victim.name, argument)
    ch.cmd_say(buf)

    if victim.is_npc() and victim.level >= (ch.spl[merc.RED_MAGIC] // 8):
        handler_game.act("You shake off $N's suggestion.", victim, None, ch, merc.TO_CHAR)
        handler_game.act("$n shakes off $N's suggestion.", victim, None, ch, merc.TO_NOTVICT)
        handler_game.act("$n shakes off your suggestion.", victim, None, ch, merc.TO_VICT)
        handler_game.act("$s mind is too strong to overcome.", victim, None, ch, merc.TO_VICT)
        return
    elif victim.spl[merc.BLUE_MAGIC] >= (ch.spl[merc.RED_MAGIC] // 2):
        handler_game.act("You shake off $N's suggestion.", victim, None, ch, merc.TO_CHAR)
        handler_game.act("$n shakes off $N's suggestion.", victim, None, ch, merc.TO_NOTVICT)
        handler_game.act("$n shakes off your suggestion.", victim, None, ch, merc.TO_VICT)
        handler_game.act("$s mind is too strong to overcome.", victim, None, ch, merc.TO_VICT)
        return

    handler_game.act("You blink in confusion.", victim, None, None, merc.TO_CHAR)
    handler_game.act("$n blinks in confusion.", victim, None, None, merc.TO_ROOM)
    ch.cmd_say("Yes, you're right, I do...")
    victim.interpret(argument)


interp.register_command(
    interp.CmdType(
        name="command",
        cmd_fun=cmd_command,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
