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
def spl_charm_person(sn, level, ch, victim, target):
    if ch == victim:
        ch.send("You like yourself even better!\n")
        return

    if not victim.is_npc() and victim.immune.is_set(merc.IMM_CHARM):
        ch.send("You failed.\n")
        return

    # I don't want people charming ghosts and stuff - KaVir
    if victim.is_npc() and victim.is_affected(merc.AFF_ETHEREAL):
        ch.send("You failed.\n")
        return

    if victim.is_immortal():
        ch.send("You can cast puny mortal magic on immortals!\n")
        return

    if victim.is_affected(merc.AFF_CHARM) or ch.is_affected(merc.AFF_CHARM) or level < victim.level or handler_magic.saves_spell(level, victim):
        return

    if victim.master:
        victim.stop_follower()

    victim.add_follower(ch)
    aff = handler_game.AffectData(type=sn, duration=game_utils.number_fuzzy(level // 4), bitvector=merc.AFF_CHARM)
    victim.affect_add(aff)
    handler_game.act("Isn't $n just so nice?", ch, None, victim, merc.TO_VICT)

    if ch != victim:
        ch.send("Ok.\n")


const.register_spell(
    const.skill_type(
        name="charm person",
        skill_level=99,
        spell_fun=spl_charm_person,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(7),
        min_mana=20,
        beats=12,
        noun_damage="charm person",
        msg_off=""
    )
)
