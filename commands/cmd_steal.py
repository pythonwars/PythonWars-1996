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


def cmd_steal(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not arg1 or not arg2:
        ch.send("Steal what from whom?\n")
        return

    victim = ch.get_char_room(arg2)
    if not victim:
        ch.not_here(arg2)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_immortal():
        ch.not_imm()
        return

    ch.wait_state(const.skill_table["steal"].beats)
    percent = game_utils.number_percent() + (10 if victim.is_awake() else -50)

    if (ch.level + game_utils.number_range(1, 20) < victim.level) or (not ch.is_npc() and not victim.is_npc() and ch.level < 3) or \
            (not ch.is_npc() and not victim.is_npc() and victim.level < 3) or (victim.position == merc.POS_FIGHTING) or \
            (not victim.is_npc() and victim.immune.is_set(merc.IMM_STEAL)) or (not victim.is_npc() and victim.is_immortal()) or \
            (not ch.is_npc() and percent > ch.learned["steal"]):
        # Failure.
        ch.send("Oops.\n")
        handler_game.act("$n tried to steal from you.", ch, None, victim, merc.TO_VICT)
        handler_game.act("$n tried to steal from $N.", ch, None, victim, merc.TO_NOTVICT)
        victim.cmd_shout("{} is a bloody thief!".format(ch.name))

        if not ch.is_npc():
            if victim.is_npc():
                fight.multi_hit(victim, ch, merc.TYPE_UNDEFINED)
            else:
                ch.save(force=True)
        return

    if game_utils.str_cmp(arg1, ["coin", "coins", "gold"]):
        amount = victim.gold * game_utils.number_range(1, 10) // 100
        if amount <= 0:
            ch.send("You couldn't get any gold.\n")
            return

        ch.gold += amount
        victim.gold -= amount
        ch.send("Bingo!  You got {:,} gold coins.\n".format(amount))
        ch.save(force=True)
        victim.save(force=True)
        return

    item = victim.get_item_carry(arg1)
    if not item:
        ch.send("You can't find it.\n")
        return

    if not victim.can_drop_item(item) or item.flags.loyal or item.flags.inventory:
        ch.send("You can't pry it away.\n")
        return

    if ch.carry_number + 1 > ch.can_carry_n():
        ch.send("You have your hands full.\n")
        return

    if ch.carry_weight + item.get_obj_weight() > ch.can_carry_w():
        ch.send("You can't carry that much weight.\n")
        return

    victim.get(item)
    ch.put(item)
    ch.send("You got it!\n")
    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="steal",
        cmd_fun=cmd_steal,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
