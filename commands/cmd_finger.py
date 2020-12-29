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

import handler_pc
import interp
import merc
import nanny
import state_checks
import sys_utils
import tables


def cmd_finger(ch, argument):
    if not argument:
        ch.send("Usage: finger <victim>\n")
        return

    if not nanny.check_parse_name(argument):
        ch.send("Thats an illegal name.\n")
        return

    ch_dummy = nanny.CharDummy()
    ch_dummy.stub = handler_pc.Pc.load_stub(argument, silent=True)
    if not ch_dummy.stub:
        ch.send("That player doesn't exist.\n")
        del ch_dummy
        return

    buf = ["--------------------------------------------------------------------------------\n"]
    buf += "{}{}.\n".format(ch_dummy.stub["name"], ch_dummy.stub["title"])
    buf += "--------------------------------------------------------------------------------\n"

    if ch.is_immortal():
        buf += "Last connected from {} at {}.\n".format(ch_dummy.stub["last_host"], sys_utils.systimestamp(ch_dummy.stub["last_time"]))
    else:
        buf += "Last connected from ***.***.***.*** at {}.\n".format(sys_utils.systimestamp(ch_dummy.stub["last_time"]))

    buf += "--------------------------------------------------------------------------------\n"
    buf += "Sex: {}. ".format(tables.sex_table[ch_dummy.stub["sex"]].capitalize())
    buf += ch.other_age(is_self=False)

    if ch_dummy.stub["level"] >= merc.LEVEL_IMMORTAL:
        level_list = [(merc.LEVEL_HIGHJUDGE, " High Judge"), (merc.LEVEL_JUDGE, " Judge"), (merc.LEVEL_ENFORCER, "n Enforcer"),
                      (merc.LEVEL_QUESTMAKER, " Quest Maker"), (merc.LEVEL_BUILDER, " Builder")]
        for (aa, bb) in level_list:
            if ch_dummy.stub["level"] == aa:
                buf += "They are a{}, ".format(bb)
                break
        else:
            buf += "They are an Implementor, "
    else:
        level_list = [(1, "n Avatar"), (5, "n Immortal"), (10, " Godling"), (15, " Demigod"), (20, " Lesser God"), (25, " Greater God")]
        for (aa, bb) in level_list:
            if ch_dummy.stub["race"] < aa:
                buf += "They are a{}, ".format(bb)
                break
        else:
            buf += "They are a Supreme God, "

    played = ch_dummy.stub["played"]
    played = (2 * (played // 7200)) if played > 0 else 0
    buf += "and have been playing for {} hours.\n".format(played)

    if ch_dummy.stub["marriage"]:
        buf += "They are {} to {}.\n".format("married" if state_checks.is_set(ch_dummy.stub["extra"], merc.EXTRA_MARRIED) else "engaged",
                                             ch_dummy.stub["marriage"])

    buf += "Player kills: {}, Player Deaths: {}.\n".format(ch_dummy.stub["pkills"], ch_dummy.stub["pdeaths"])
    buf += "Mob kills: {}, Mob Deaths: {}.\n".format(ch_dummy.stub["mkills"], ch_dummy.stub["mdeaths"])
    buf += "--------------------------------------------------------------------------------\n"

    if ch_dummy.stub["email"]:
        buf += "Email: {}\n".format(ch_dummy.stub["email"])
        buf += "--------------------------------------------------------------------------------\n"
    ch.send("".join(buf))
    del ch_dummy


interp.register_command(
    interp.CmdType(
        name="finger",
        cmd_fun=cmd_finger,
        position=merc.POS_SITTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
