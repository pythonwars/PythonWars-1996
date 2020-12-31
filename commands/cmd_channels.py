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


def cmd_channels(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not arg:
        if not ch.is_npc() and ch.sentances.is_set(merc.SENT_SILENCE):
            ch.send("You are silenced.\n")
            return

        buf = ["Channels:"]
        buf += " +CHAT" if not ch.channels.is_set(merc.CHANNEL_CHAT) else " -chat"

        if ch.is_immortal():
            buf += " +IMMTALK" if not ch.channels.is_set(merc.CHANNEL_IMMTALK) else " -immtalk"

        buf += " +MUSIC" if not ch.channels.is_set(merc.CHANNEL_MUSIC) else " -music"
        buf += " +QUESTION" if not ch.channels.is_set(merc.CHANNEL_QUESTION) else " -question"
        buf += " +SHOUT" if not ch.channels.is_set(merc.CHANNEL_SHOUT) else " -shout"
        buf += " +HOWL" if not ch.channels.is_set(merc.CHANNEL_HOWL) else " -howl"

        if ch.is_mage() or ch.is_immortal():
            buf += " +MAGE" if ch.channels.is_set(merc.CHANNEL_MAGETALK) else " -mage"

        if ch.is_demon() or ch.is_immortal():
            buf += " +PRAY" if ch.channels.is_set(merc.CHANNEL_PRAY) else " -pray"

        buf += " +INFO" if ch.channels.is_set(merc.CHANNEL_INFO) else " -info"

        if ch.is_vampire() or ch.is_immortal():
            buf += " +VAMP" if ch.channels.is_set(merc.CHANNEL_VAMPTALK) else " -vamp"

        buf += " +TELL" if not ch.channels.is_set(merc.CHANNEL_TELL) else " -tell"
        buf += ".\n"
        ch.send("".join(buf))
    else:
        if arg[0] == "+":
            fclear = True
        elif arg[0] == "-":
            fclear = False
        else:
            ch.send("Channels -channel or +channel?\n")
            return

        arg = arg[1:]
        arg_list = [("chat", merc.CHANNEL_CHAT), ("music", merc.CHANNEL_MUSIC), ("question", merc.CHANNEL_QUESTION), ("shout", merc.CHANNEL_SHOUT),
                    ("yell", merc.CHANNEL_YELL), ("howl", merc.CHANNEL_HOWL), ("info", merc.CHANNEL_INFO), ("tell", merc.CHANNEL_TELL)]
        if game_utils.str_cmp(arg, "immtalk") and ch.is_immortal():
            bit = merc.CHANNEL_IMMTALK
        elif game_utils.str_cmp(arg, "mage") and (ch.is_immortal() or ch.is_mage()):
            bit = merc.CHANNEL_MAGETALK
        elif game_utils.str_cmp(arg, "pray") and (ch.is_immortal() or ch.is_demon()):
            bit = merc.CHANNEL_PRAY
        elif game_utils.str_cmp(arg, "vamp") and (ch.is_immortal() or ch.is_vampire()):
            bit = merc.CHANNEL_VAMPTALK
        else:
            for (aa, bb) in arg_list:
                if game_utils.str_cmp(arg, aa):
                    bit = bb
                    break
            else:
                ch.send("Set or clear which channel?\n")
                return

        if fclear:
            ch.channels.rem_bit(bit)
        else:
            ch.channels.set_bit(bit)
        ch.send("Ok.\n")


interp.register_command(
    interp.CmdType(
        name="channels",
        cmd_fun=cmd_channels,
        position=merc.POS_DEAD, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
