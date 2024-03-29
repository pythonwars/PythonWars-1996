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


def cmd_group(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        leader = ch.leader if ch.leader else ch

        buf = [f"{leader.pers(ch)}'s group:\n"]
        for gch in list(instance.characters.values()):
            if gch.is_same_group(ch):
                buf += f"[{gch.pers(ch).capitalize():<16}] {gch.hit:4}/{gch.max_hit:4} hp {gch.mana:4}/{gch.max_mana:4} mana {gch.move:4}/{gch.max_move:4} mv {gch.exp:5} xp\n"
        ch.send("".join(buf))
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch.master or (ch.leader and ch.leader != ch):
        ch.send("But you are following someone else!\n")
        return

    if instance.characters[victim.master] != ch and ch != victim:
        handler_game.act("$N isn't following you.", ch, None, victim, merc.TO_CHAR)
        return

    if victim.is_same_group(ch) and ch != victim:
        victim.leader = None
        handler_game.act("$n removes $N from $s group.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n removes you from $s group.", ch, None, victim, merc.TO_VICT)
        handler_game.act("You remove $N from your group.", ch, None, victim, merc.TO_CHAR)
        return

    victim.leader = ch
    handler_game.act("$N joins $n's group.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("You join $n's group.", ch, None, victim, merc.TO_VICT)
    handler_game.act("$N joins your group.", ch, None, victim, merc.TO_CHAR)


interp.register_command(
    interp.CmdType(
        name="group",
        cmd_fun=cmd_group,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
