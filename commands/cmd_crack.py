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
import object_creator


def crack_head(ch, item, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if not game_utils.str_cmp(arg2, "mob") and item.chobj and not item.chobj.is_npc() and item.chobj.is_affected(merc.AFF_POLYMORPH):
        victim = item.chobj
        object_creator.make_part(victim, "cracked_head")
        object_creator.make_part(victim, "brain")
        victim.morph = f"the quivering brain of {victim.name}"
    elif game_utils.str_cmp(arg2, "mob"):
        if item.value[1] not in instance.npc_templates:
            return

        victim = object_creator.create_mobile(instance.npc_templates[item.value[1]])
        ch.in_room.put(victim)
        object_creator.make_part(victim, "cracked_head")
        object_creator.make_part(victim, "brain")
        victim.extract(True)
    else:
        if 30002 not in instance.npc_templates:
            return

        victim = object_creator.create_mobile(instance.npc_templates[30002])
        victim.short_descr = arg2[0].upper() + arg2[1:]
        ch.in_room.put(victim)
        object_creator.make_part(victim, "cracked_head")
        object_creator.make_part(victim, "brain")
        victim.extract(True)


# noinspection PyUnusedLocal
def cmd_crack(ch, argument):
    item = ch.get_eq("right_hand")
    if not item or item.vnum != merc.OBJ_VNUM_SEVERED_HEAD:
        item = ch.get_eq("left_hand")
        if not item or item.vnum != merc.OBJ_VNUM_SEVERED_HEAD:
            ch.send("You are not holding any heads.\n")
            return

    handler_game.act("You hurl $p at the floor.", ch, item, None, merc.TO_CHAR)
    handler_game.act("$n hurls $p at the floor.", ch, item, None, merc.TO_ROOM)
    handler_game.act("$p cracks open, leaking brains out across the floor.", ch, item, None, merc.TO_CHAR)

    if item.chobj:
        handler_game.act("$p cracks open, leaking brains out across the floor.", ch, item, item.chobj, merc.TO_NOTVICT)
        handler_game.act("$p crack open, leaking brains out across the floor.", ch, item, item.chobj, merc.TO_VICT)
    else:
        handler_game.act("$p cracks open, leaking brains out across the floor.", ch, item, None, merc.TO_ROOM)

    crack_head(ch, item, item.name)
    ch.get(item)
    item.extract()


interp.register_command(
    interp.CmdType(
        name="crack",
        cmd_fun=cmd_crack,
        position=merc.POS_STANDING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
