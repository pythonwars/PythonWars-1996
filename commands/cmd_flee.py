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
#   Ported to Python by Davion of MudBytes.net using Miniboa
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

import fight
import game_utils
import handler_ch
import handler_game
import handler_room
import instance
import interp
import merc
import state_checks


# noinspection PyUnusedLocal
def cmd_flee(ch, argument):
    victim = ch.fighting
    if not victim:
        if ch.position == merc.POS_FIGHTING:
            ch.position = merc.POS_STANDING
        ch.send("You aren't fighting anyone.\n")
        return

    if ch.is_affected(merc.AFF_WEBBED):
        ch.send("You are unable to move with all this sticky webbing on.\n")
        return

    if not ch.is_npc() and ch.powers[merc.UNI_RAGE] >= 0:
        if ch.is_vampire() and game_utils.number_percent() <= ch.powers[merc.UNI_RAGE]:
            ch.send("Your inner beast refuses to let you run!\n")
            ch.wait_state(merc.PULSE_VIOLENCE)
            return
        elif ch.is_werewolf() and game_utils.number_percent() <= ch.powers[merc.UNI_RAGE] * 0.3:
            ch.send("Your rage is too great!\n")
            ch.wait_state(merc.PULSE_VIOLENCE)
            return

    was_in = ch.in_room
    for attempt in range(6):
        door = handler_room.number_door()

        pexit = was_in.exit[door]
        if not pexit or not pexit.to_room or pexit.exit_info.is_set(merc.EX_CLOSED) or \
                (ch.is_npc() and state_checks.is_set(instance.rooms[pexit.to_room].room_flags, merc.ROOM_NO_MOB)):
            continue

        handler_ch.move_char(ch, door)

        now_in = ch.in_room
        if now_in == was_in:
            continue

        ch.in_environment = was_in.instance_id
        handler_game.act("$n has fled!", ch, None, None, merc.TO_ROOM)
        ch.in_environment = now_in.instance_id

        if not ch.is_npc():
            ch.send("You flee from combat!  Coward!\n")

        fight.stop_fighting(ch, True)
        return

    ch.send("You were unable to escape!\n")


interp.register_command(
    interp.CmdType(
        name="flee",
        cmd_fun=cmd_flee,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
