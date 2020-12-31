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
import instance
import interp
import merc


def cmd_throw(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    item = ch.get_eq("right_hand")
    if not item:
        item = ch.get_eq("left_hand")
        if not item:
            ch.send("You are not holding anything to throw.\n")
            return

    if not arg1:
        ch.send("Which direction do you wish to throw?\n")
        return

    if game_utils.str_cmp(arg1, ["n", "north"]):
        door = merc.DIR_NORTH
        arg1 = "north"
        rev_dir = "south"
    elif game_utils.str_cmp(arg1, ["e", "east"]):
        door = merc.DIR_EAST
        arg1 = "east"
        rev_dir = "west"
    elif game_utils.str_cmp(arg1, ["s", "south"]):
        door = merc.DIR_SOUTH
        arg1 = "south"
        rev_dir = "north"
    elif game_utils.str_cmp(arg1, ["w", "west"]):
        door = merc.DIR_WEST
        arg1 = "west"
        rev_dir = "east"
    elif game_utils.str_cmp(arg1, ["u", "up"]):
        door = merc.DIR_UP
        arg1 = "up"
        rev_dir = "down"
    elif game_utils.str_cmp(arg1, ["d", "down"]):
        door = merc.DIR_DOWN
        arg1 = "down"
        rev_dir = "up"
    else:
        ch.send("You can only throw north, south, east, west, up or down.\n")
        return

    location = ch.in_room

    handler_game.act("You hurl $p $T.", ch, item, arg1, merc.TO_CHAR)
    handler_game.act("$n hurls $p $T.", ch, item, arg1, merc.TO_ROOM)

    # First room
    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        handler_game.act("$p bounces off the $T wall.", ch, item, arg1, merc.TO_CHAR)
        handler_game.act("$p bounces off the $T wall.", ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        return

    pexit = ch.in_room.exit[door]
    if pexit.exit_info.is_set(merc.EX_CLOSED):
        handler_game.act("$p bounces off the $T door.", ch, item, arg1, merc.TO_CHAR)
        handler_game.act("$p bounces off the $T door.", ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        return

    ch.in_room.get(ch)
    to_room.put(ch)

    victim = ch.get_char_room(arg2)
    if victim:
        handler_game.act("$p comes flying in from the {} and lands in $N's hands.".format(rev_dir), ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$p comes flying in from the {} and lands in your hands.".format(rev_dir), ch, item, victim, merc.TO_VICT)
        ch.get(item)
        victim.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    # Second room
    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        handler_game.act("$p comes flying in from the {} and strikes $T wall.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    pexit = ch.in_room.exit[door]
    if pexit.exit_info.is_set(merc.EX_CLOSED):
        handler_game.act("$p comes flying in from the {} and strikes the $T door.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    handler_game.act("$p comes flying in from the {} and carries on $T.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
    ch.in_room.get(ch)
    to_room.put(ch)

    victim = ch.get_char_room(arg2)
    if victim:
        handler_game.act("$p comes flying in from the {} and lands in $N's hands.".format(rev_dir), ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$p comes flying in from the {} and lands in your hands.".format(rev_dir), ch, item, victim, merc.TO_VICT)
        ch.get(item)
        victim.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    # Third room
    pexit = ch.in_room.exit[door]
    to_room = instance.rooms[pexit.to_room] if pexit else None
    if not pexit or not to_room:
        handler_game.act("$p comes flying in from the {} and strikes $T wall.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    pexit = ch.in_room.exit[door]
    if pexit.exit_info.is_set(merc.EX_CLOSED):
        handler_game.act("$p comes flying in from the {} and strikes the $T door.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    handler_game.act("$p comes flying in from the {} and carries on $T.".format(rev_dir), ch, item, arg1, merc.TO_ROOM)
    ch.in_room.get(ch)
    to_room.put(ch)

    victim = ch.get_char_room(arg2)
    if victim:
        handler_game.act("$p comes flying in from the {} and lands in $N's hands.".format(rev_dir), ch, item, victim, merc.TO_NOTVICT)
        handler_game.act("$p comes flying in from the {} and lands in your hands.".format(rev_dir), ch, item, victim, merc.TO_VICT)
        ch.get(item)
        victim.put(item)
        ch.in_room.get(ch)
        location.put(ch)
        return

    handler_game.act("$p comes flying in from the {} and drops at your feet.".format(rev_dir), ch, item, None, merc.TO_ROOM)
    ch.get(item)
    ch.in_room.put(item)

    # Move them back
    ch.in_room.get(ch)
    location.put(ch)

    ch.save(force=True)

    if victim and not victim.is_npc():
        victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="throw",
        cmd_fun=cmd_throw,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
