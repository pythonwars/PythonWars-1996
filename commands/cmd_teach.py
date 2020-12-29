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
import handler_game
import interp
import merc


def cmd_teach(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_mage():
        ch.huh()
        return

    if ch.level == merc.LEVEL_APPRENTICE:
        ch.send("You don't know enough to teach another.\n")
        return

    if not arg:
        ch.send("Teach whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if victim.is_immortal():
        ch.not_imm()
        return

    if victim.is_mage():
        ch.send("They are already a mage.\n")
        return

    if victim.level != merc.LEVEL_AVATAR:
        ch.send("You can only teach avatars.\n")
        return

    if victim.is_vampire() or victim.vampaff.is_set(merc.VAM_MORTAL):
        ch.send("You are unable to teach vampires!\n")
        return

    if victim.is_werewolf():
        ch.send("You are unable to teach werewolves!\n")
        return

    if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
        ch.send("You are unable to teach demons!\n")
        return

    if victim.is_highlander():
        ch.send("You are unable to teach highlanders.\n")
        return

    if not victim.immune.is_set(merc.IMM_VAMPIRE):
        ch.send("You cannot teach an unwilling person.\n")
        return

    if ch.exp < 100000:
        ch.send("You cannot afford the 100000 exp required to teach them.\n")
        return

    if victim.exp < 100000:
        ch.send("They cannot afford the 100000 exp required to learn from you.\n")
        return

    ch.exp -= 100000
    victim.exp -= 100000
    handler_game.act("You teach $N the basics of magic.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n teaches $N the basics of magic.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n teaches you the basics of magic.", ch, None, victim, merc.TO_VICT)
    victim.level = merc.LEVEL_APPRENTICE
    victim.trust = merc.LEVEL_APPRENTICE
    victim.send("You are now an apprentice.\n")
    victim.lord = ch.name
    victim.powers[merc.MPOWER_RUNE0] = ch.powers[merc.MPOWER_RUNE0]
    victim.ch_class = ch.ch_class
    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="teach",
        cmd_fun=cmd_teach,
        position=merc.POS_STANDING, level=5,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
