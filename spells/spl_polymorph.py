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
import game_utils
import handler_game
import handler_magic
import merc


# noinspection PyUnusedLocal
def spl_polymorph(sn, level, ch, victim, target):
    if ch.is_affected(merc.AFF_POLYMORPH):
        ch.send("You cannot polymorph from this form.\n")
        return

    if ch.position == merc.POS_FIGHTING or ch.is_affected(sn):
        return

    if game_utils.str_cmp(handler_magic.target_name, "frog"):
        if not ch.is_npc() and ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        handler_game.act("$n polymorphs into a frog!", ch, None, None, merc.TO_ROOM)
        ch.send("You polymorph into a frog!\n")
        ch.clear_stats()

        aff = handler_game.AffectData(type=sn, duration=game_utils.number_range(3, 5), location=merc.APPLY_POLY, modifier=merc.POLY_FROG,
                                      bitvector=merc.AFF_POLYMORPH)
        ch.affect_join(aff)
        ch.morph = "{} the frog".format(ch.name)
    elif game_utils.str_cmp(handler_magic.target_name, "fish"):
        if not ch.is_npc() and ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        handler_game.act("$n polymorphs into a fish!", ch, None, None, merc.TO_ROOM)
        ch.send("You polymorph into a fish!\n")
        ch.clear_stats()

        aff = handler_game.AffectData(type=sn, duration=game_utils.number_range(3, 5), location=merc.APPLY_POLY, modifier=merc.POLY_FISH,
                                      bitvector=merc.AFF_POLYMORPH)
        ch.affect_join(aff)
        ch.morph = "{} the fish".format(ch.name)
    elif game_utils.str_cmp(handler_magic.target_name, "raven"):
        if not ch.is_npc() and ch.stance[0] != -1:
            ch.cmd_stance("")

        if ch.mounted == merc.IS_RIDING:
            ch.cmd_dismount("")

        handler_game.act("$n polymorphs into a raven!", ch, None, None, merc.TO_ROOM)
        ch.send("You polymorph into a raven!\n")
        ch.clear_stats()

        aff = handler_game.AffectData(type=sn, duration=game_utils.number_range(3, 5), location=merc.APPLY_AC, modifier=-150,
                                      bitvector=merc.AFF_POLYMORPH)
        ch.affect_join(aff)

        aff.bitvector = merc.AFF_POLYMORPH if ch.is_affected(merc.AFF_FLYING) else (merc.AFF_POLYMORPH + merc.AFF_FLYING)
        ch.affect_join(aff)

        aff.location = merc.APPLY_POLY
        aff.modifier = merc.POLY_RAVEN
        ch.affect_join(aff)
        ch.morph = "{} the raven".format(ch.name)
    else:
        ch.send("You can polymorph into a frog, a fish, or an raven.\n")


const.register_spell(
    const.skill_type(
        name="polymorph",
        skill_level=4,
        spell_fun=spl_polymorph,
        target=merc.TAR_IGNORE,
        minimum_position=merc.POS_STANDING,
        pgsn=None,
        slot=const.slot(562),
        min_mana=50,
        beats=12,
        noun_damage="",
        msg_off="You resume your normal form."
    )
)
