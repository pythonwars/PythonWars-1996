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
import interp
import merc


def cmd_skill(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        arg = "self"

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    wield1 = victim.get_eq("right_hand")
    wield2 = victim.get_eq("left_hand")

    dtype1 = merc.TYPE_HIT
    dtype2 = merc.TYPE_HIT

    if wield1 and wield1.item_type == merc.ITEM_WEAPON:
        dtype1 += wield1.value[3]

    if wield2 and wield2.item_type == merc.ITEM_WEAPON:
        dtype2 += wield2.value[3]

    dtype1 -= 1000
    dtype2 -= 1000

    skill_list = [(0, "totally unskilled"), (25, "slightly skilled"), (50, "reasonable"), (75, "fairly competent"),
                  (100, "highly skilled"), (125, "very dangerous"), (150, "extremely deadly"), (175, "an expert"),
                  (199, "a master"), (200, "a grand master"), (1000, "supremely skilled")]
    for (aa, bb) in skill_list:
        if victim.wpn[dtype1] <= aa:
            bufskill1 = bb
            break
    else:
        return

    for (aa, bb) in skill_list:
        if victim.wpn[dtype2] <= aa:
            bufskill2 = bb
            break
    else:
        return

    buf1 = ""
    buf2 = ""

    if ch == victim:
        if dtype1 == 0 and dtype2 == 0:
            buf1 = "You are {} at unarmed combat.\n".format(bufskill1)
        else:
            if dtype1 != 0:
                buf1 = "You are {} with {}.\n".format(bufskill1, wield1.short_descr)

            if dtype2 != 0:
                buf2 = "You are {} with {}.\n".format(bufskill2, wield2.short_descr)
    else:
        if dtype1 == 0 and dtype2 == 0:
            buf1 = "{} is {} at unarmed combat.\n".format(victim.name, bufskill1)
        else:
            if dtype1 != 0:
                buf1 = "{} is {} with {}.\n".format(victim.name, bufskill1, wield1.short_descr)

            if dtype2 != 0:
                buf2 = "{} is {} with {}.\n".format(victim.name, bufskill2, wield2.short_descr)

    if buf1:
        ch.send(buf1)

    if buf2:
        ch.send(buf2)

    ch.skillstance(victim)


interp.register_command(
    interp.CmdType(
        name="skill",
        cmd_fun=cmd_skill,
        position=merc.POS_MEDITATING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
