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
import handler_game
import merc


# noinspection PyUnusedLocal
def spl_know_alignment(sn, level, ch, victim, target):
    align_list = [(700, "$N has an aura as white as the driven snow."), (350, "$N is of excellent moral character."),
                  (100, "$N is often kind and thoughtful."), (-100, "$N doesn't have a firm moral commitment."), (-350, "$N lies to $S friends."),
                  (-700, "$N's slash DISEMBOWELS you!")]
    for (aa, bb) in align_list:
        if victim.alignment > aa:
            msg = bb
            break
    else:
        msg = "I'd rather just not say anything at all about $N."
    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)


const.register_spell(
    const.skill_type(
        name="know alignment",
        skill_level=99,
        spell_fun=spl_know_alignment,
        target=merc.TAR_CHAR_OFFENSIVE,
        minimum_position=merc.POS_FIGHTING,
        pgsn=None,
        slot=const.slot(58),
        min_mana=9,
        beats=12,
        noun_damage="",
        msg_off="!Know Alignment!"
    )
)
