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

import game_utils
import interp
import merc


def cmd_ostat(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Ostat what?\n")
        return

    item = ch.get_item_world(arg)
    if not item:
        ch.send("Nothing like that in hell, earth, or heaven.\n")
        return

    nm1 = item.questmaker if item.questmaker else "None"
    nm2 = item.questowner if item.questowner else "None"

    buf = ["Name: {}.\n".format(item.name)]
    buf += "Vnum: {}.  Type: {}.\n".format(item.vnum, item.item_type)
    buf += "Short description: {}.\nLong description: {}\n".format(item.short_descr, item.description)
    buf += "Object creator: {}.  Object owner: {}.  Quest points: {}.\n".format(nm1, nm2, item.points)

    if not item.quest.empty():
        buf += "Quest selections:"

        quest_list = [(merc.QUEST_STR, "Str"), (merc.QUEST_DEX, "Dex"), (merc.QUEST_INT, "Int"), (merc.QUEST_WIS, "Wis"), (merc.QUEST_CON, "Con"),
                      (merc.QUEST_HIT, "Hp"), (merc.QUEST_MANA, "Mana"), (merc.QUEST_MOVE, "Move"), (merc.QUEST_HITROLL, "Hit"),
                      (merc.QUEST_DAMROLL, "Dam"), (merc.QUEST_AC, "Ac")]
        for (aa, bb) in quest_list:
            if item.quest.is_set(aa):
                buf += " " + bb
        buf += ".\n"

    buf += "Wear bits: {}.  Extra bits: {}.\n".format(item.equips_to_names, item.item_attribute_names)
    buf += "Weight: {}/{}.\n".format(item.weight, item.get_weight())
    buf += "Cost: {}.  Timer: {}.  Level: {}.\n".format(item.cost, item.timer, item.level)
    buf += "In room: {}.  In object: {}.  Carried by: {}.\n".format(0 if not item.in_room else item.in_room.vnum,
                                                                    "(none)" if not item.in_item else item.in_item.short_descr,
                                                                    "(none)" if not item.in_living else item.in_living.name)
    buf += "Values: {}.\n".format([v for v in item.value])

    if item.extra_descr:
        buf += "Extra description keywords: '"

        extra_descr = list(item.extra_descr)
        extra_descr.extend(item.extra_descr)
        for edd in extra_descr:
            buf += edd.keyword + " "
        buf += "'\n"

    affected = list(item.affected)
    for paf in affected:
        buf += "Affects {} by {}.\n".format(merc.affect_loc_name(paf.location), paf.modifier)
    ch.send("".join(buf))


interp.register_command(
    interp.CmdType(
        name="ostat",
        cmd_fun=cmd_ostat,
        position=merc.POS_DEAD, level=7,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
