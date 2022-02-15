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

import fight
import game_utils
import handler_game
import interp
import merc


# Voodoo skill by KaVir
def cmd_voodoo(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1:
        ch.send("Who do you wish to use voodoo magic on?\n")
        return

    item = ch.get_eq("left_hand")
    if not item:
        item = ch.get_eq("right_hand")
        if not item:
            ch.send("You are not holding a voodoo doll.\n")
            return

    victim = ch.get_char_world(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    part1 = f"{victim.name} voodoo doll"
    part2 = item.name

    if not game_utils.str_cmp(part1, part2):
        ch.send(f"But you are holding {item.short_descr}, not {victim.name}!\n")
        return

    if game_utils.str_cmp(arg2, "stab"):
        ch.wait_state(merc.PULSE_VIOLENCE)
        handler_game.act("You stab a pin through $p.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n stabs a pin through $p.", ch, item, None, merc.TO_ROOM)

        if not victim.is_npc() and victim.immune.is_set(merc.IMM_VOODOO):
            return

        handler_game.act("You feel an agonising pain in your chest!", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n clutches $s chest in agony!", victim, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg2, "burn"):
        ch.wait_state(merc.PULSE_VIOLENCE)
        handler_game.act("You set fire to $p.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n sets fire to $p.", ch, item, None, merc.TO_ROOM)
        handler_game.act("$p burns to ashes.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$p burns to ashes.", ch, item, None, merc.TO_ROOM)
        ch.get(item)
        item.extract()

        if not victim.is_npc() and victim.immune.is_set(merc.IMM_VOODOO) or victim.is_affected(merc.AFF_FLAMING):
            return

        victim.affected_by.set_bit(merc.AFF_FLAMING)
        handler_game.act("You suddenly burst into flames!", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n suddenly bursts into flames!", victim, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg2, "throw"):
        ch.wait_state(merc.PULSE_VIOLENCE)
        handler_game.act("You throw $p to the ground.", ch, item, None, merc.TO_CHAR)
        handler_game.act("$n throws $p to the ground.", ch, item, None, merc.TO_ROOM)
        ch.get(item)
        ch.in_room.put(item)

        if not victim.is_npc() and victim.immuen.is_set(merc.IMM_VOODOO) or victim.position < merc.POS_STANDING:
            return

        if victim.position == merc.POS_FIGHTING:
            fight.stop_fighting(victim, True)

        handler_game.act("A strange force picks you up and hurls you to the ground!", victim, None, None, merc.TO_CHAR)
        handler_game.act("$n is hurled to the ground by a strange force.", victim, None, None, merc.TO_ROOM)
        victim.position = merc.POS_RESTING
        victim.hit = victim.hit - game_utils.number_range(ch.level, (5 * ch.level))
        fight.update_pos(victim)

        if victim.position == merc.POS_DEAD and not victim.is_npc():
            ch.killperson(victim)
            return
    else:
        ch.send("You can 'stab', 'burn' or 'throw' the doll.\n")


interp.register_command(
    interp.CmdType(
        name="voodoo",
        cmd_fun=cmd_voodoo,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
