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

import game_utils
import handler_game
import interp
import merc


def cmd_mount(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Mount what?\n")
        return

    if ch.is_affected(merc.AFF_POLYMORPH) and not ch.vampaff.is_set(merc.VAM_DISGUISED):
        ch.send("You cannot ride in this form.\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if ch.mounted > 0:
        ch.send("You are already riding.\n")
        return

    if not victim.is_npc() or victim.mounted > 0 or (victim.is_npc() and not victim.act.is_set(merc.ACT_MOUNT)):
        ch.send("You cannot mount them.\n")
        return

    if victim.position < merc.POS_STANDING:
        if victim.position < merc.POS_SLEEPING:
            handler_game.act("$N is too badly hurt for that.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_SLEEPING:
            handler_game.act("First you better wake $m up.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_RESTING:
            handler_game.act("First $e better stand up.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_MEDITATING:
            handler_game.act("First $e better stand up.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_SITTING:
            handler_game.act("First $e better stand up.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_SLEEPING:
            handler_game.act("First you better wake $m up.", ch, None, victim, merc.TO_CHAR)
        elif victim.position == merc.POS_FIGHTING:
            handler_game.act("Not while $e's fighting.", ch, None, victim, merc.TO_CHAR)
        return

    if not ch.is_npc() and ch.stance[0] != -1:
        ch.cmd_stance("")

    ch.mounted = merc.IS_RIDING
    victim.mounted = merc.IS_MOUNT
    ch.mount = victim
    victim.mount = ch
    handler_game.act("You clamber onto $N's back.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n clambers onto $N's back.", ch, None, victim, merc.TO_ROOM)


interp.register_command(
    interp.CmdType(
        name="mount",
        cmd_fun=cmd_mount,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
