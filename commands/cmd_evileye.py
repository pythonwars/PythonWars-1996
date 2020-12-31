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


def cmd_evileye(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    arg2 = argument

    if ch.is_npc() or not ch.vampaff.is_set(merc.VAM_DOMINATE):
        ch.huh()
        return

    if not arg1 or not arg2:
        ch.send("Format is: evileye <option> <value>\n"
                "Option ACTION is a text string action performed by you or the viewer.\n"
                "Option MESSAGE is a text string shown to the person looking at you.\n"
                "Option TOGGLE has values: spell, self, other.\n\n")

        if ch.poweraction:
            ch.send("Current action: {}.\n".format(ch.poweraction))

        if ch.powertype:
            ch.send("Current message: {}.\n".format(ch.powertype))

        ch.send("Current flags:")

        found = False
        if ch.spectype.is_set(merc.EYE_SPELL):
            ch.send(" Spell")
            found = True

        if ch.spectype.is_set(merc.EYE_SELFACTION):
            ch.send(" Self")
            found = True

        if ch.spectype.is_set(merc.EYE_ACTION):
            ch.send(" Other")
            found = True

        if not found:
            ch.send(" None")

        ch.send(".\n")
        return

    if game_utils.str_cmp(arg1, "action"):
        ch.poweraction = arg2
    elif game_utils.str_cmp(arg1, "message"):
        ch.powertype = arg2
    elif game_utils.str_cmp(arg1, "toggle"):
        if game_utils.str_cmp(arg2, "spell"):
            ch.spectype.tog_bit(merc.EYE_SPELL)
        elif game_utils.str_cmp(arg2, "self"):
            ch.spectype.tog_bit(merc.EYE_SELFACTION)
        elif game_utils.str_cmp(arg2, "other"):
            ch.spectype.tog_bit(merc.EYE_ACTION)
        else:
            ch.send("TOGGLE flag should be one of: spell, self, other.\n")
            return

        ch.send("{} flag toggled.\n".format(arg2[0].upper + arg2[1:].lower()))
    else:
        ch.cmd_evileye("")


interp.register_command(
    interp.CmdType(
        name="evileye",
        cmd_fun=cmd_evileye,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
