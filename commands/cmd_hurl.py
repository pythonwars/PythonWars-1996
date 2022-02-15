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
import fight
import game_utils
import handler_game
import instance
import interp
import merc


# Hurl skill by KaVir
def cmd_hurl(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not ch.is_npc() and ch.learned["hurl"] < 1:
        ch.send("Maybe you should learn the skill first?\n")
        return

    if not arg1:
        ch.send("Who do you wish to hurl?\n")
        return

    victim = ch.get_char_room(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if ch == victim:
        ch.not_self()
        return

    if fight.is_safe(ch, victim):
        return

    mount = victim.mount
    if mount and victim.mounted == merc.IS_MOUNT:
        ch.send("But they have someone on their back!\n")
        return

    if mount and victim.mounted == merc.IS_RIDING:
        ch.send("But they are riding!\n")
        return

    if not victim.is_npc() and victim.immune.is_set(merc.IMM_HURL):
        ch.send("You are unable to get their feet of the ground.\n")
        return

    if victim.is_npc() and victim.level > 900:
        ch.send("You are unable to get their feet of the ground.\n")
        return

    if victim.hit < victim.max_hit or (victim.position == merc.POS_FIGHTING and victim.fighting != ch):
        handler_game.act("$N is hurt and suspicious, and you are unable to approach $M.", ch, None, victim, merc.TO_CHAR)
        return

    ch.wait_state(const.skill_table["hurl"].beats)

    if not ch.is_npc() and game_utils.number_percent() > ch.learned["hurl"]:
        ch.send("You are unable to get their feet of the ground.\n")
        fight.multi_hit(victim, ch, merc.TYPE_UNDEFINED)
        return

    if not arg2:
        door = game_utils.number_range(0, 3)
    else:
        if game_utils.str_cmp(arg2, ["n", "north"]):
            door = merc.DIR_NORTH
        elif game_utils.str_cmp(arg2, ["e", "east"]):
            door = merc.DIR_EAST
        elif game_utils.str_cmp(arg2, ["s", "south"]):
            door = merc.DIR_SOUTH
        elif game_utils.str_cmp(arg2, ["w", "west"]):
            door = merc.DIR_WEST
        else:
            ch.send("You can only hurl people north, south, east or west.\n")
            return

    if door == merc.DIR_NORTH:
        direction = "north"
        rev_dir = 2
    elif door == merc.DIR_EAST:
        direction = "east"
        rev_dir = 3
    elif door == merc.DIR_SOUTH:
        direction = "south"
        rev_dir = 0
    else:
        direction = "west"
        rev_dir = 1

    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        handler_game.act("$n hurls $N into the $t wall.", ch, direction, victim, merc.TO_NOTVICT)
        handler_game.act("You hurl $N into the $t wall.", ch, direction, victim, merc.TO_CHAR)
        handler_game.act("$n hurls you into the $t wall.", ch, direction, victim, merc.TO_VICT)

        dam = game_utils.number_range(ch.level, (ch.level * 4))
        victim.hit -= dam
        fight.update_pos(victim)

        if victim.is_npc() and not ch.is_npc():
            ch.mkill += 1

        if not victim.is_npc() and ch.is_npc():
            victim.mdeath += 1

        if victim.position == merc.POS_DEAD:
            fight.raw_kill(victim)
            return
        return

    pexit = victim.in_room.exit[door]
    if pexit.exit_info.is_set(merc.EX_CLOSED) and not victim.is_affected(merc.AFF_PASS_DOOR) and not victim.is_affected(merc.AFF_ETHEREAL):
        pexit.exit_info.rem_bit(merc.EX_LOCKED)
        pexit.exit_info.rem_bit(merc.EX_CLOSED)
        handler_game.act("$n hoists $N in the air and hurls $M $t.", ch, direction, victim, merc.TO_NOTVICT)
        handler_game.act("You hoist $N in the air and hurl $M $t.", ch, direction, victim, merc.TO_CHAR)
        handler_game.act(f"$n hurls you $t, smashing you through the {pexit.keyword}.", ch, direction, victim, merc.TO_VICT)
        handler_game.act("There is a loud crash as $n smashes through the $d.", victim, None, pexit.keyword, merc.TO_ROOM)

        to_room = pexit.to_room
        pexit_rev = instance.rooms[to_room].exit[rev_dir]
        if to_room and pexit_rev and pexit_rev.to_room == ch.in_room and pexit_rev.keyword:
            pexit_rev.exit_info.rem_bit(merc.EX_LOCKED)
            pexit_rev.exit_info.rem_bit(merc.EX_CLOSED)

            if door == 0:
                direction = "south"
            elif door == 1:
                direction = "west"
            elif door == 2:
                direction = "north"
            else:
                direction = "east"

            victim.in_room.get(victim)
            to_room.put(victim)

            handler_game.act("$n comes smashing in through the $t $d.", victim, direction, pexit.keyword, merc.TO_ROOM)

            dam = game_utils.number_range(ch.level, (ch.level * 6))
            victim.hit -= dam
            fight.update_pos(victim)

            if victim.is_npc() and not ch.is_npc():
                ch.mkill += 1

            if not victim.is_npc() and ch.is_npc():
                victim.mdeath += 1

            if victim.position == merc.POS_DEAD:
                fight.raw_kill(victim)
    else:
        handler_game.act("$n hurls $N $t.", ch, direction, victim, merc.TO_NOTVICT)
        handler_game.act("You hurl $N $t.", ch, direction, victim, merc.TO_CHAR)
        handler_game.act("$n hurls you $t.", ch, direction, victim, merc.TO_VICT)

        if door == 0:
            direction = "south"
        elif door == 1:
            direction = "west"
        elif door == 2:
            direction = "north"
        else:
            direction = "east"

        victim.in_room.get(victim)
        to_room.put(victim)

        handler_game.act("$n comes flying in from the $t.", victim, direction, None, merc.TO_ROOM)

        dam = game_utils.number_range(ch.level, (ch.level * 2))
        victim.hit -= dam
        fight.update_pos(victim)

        if victim.is_npc() and not ch.is_npc():
            ch.mkill += 1

        if not victim.is_npc() and ch.is_npc():
            victim.mdeath += 1

        if victim.position == merc.POS_DEAD:
            fight.raw_kill(victim)


interp.register_command(
    interp.CmdType(
        name="hurl",
        cmd_fun=cmd_hurl,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
