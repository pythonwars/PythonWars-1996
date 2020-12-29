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


def cmd_favour(ch, argument):
    argument, arg1 = game_utils.read_word(argument)
    argument, arg2 = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire() and (not ch.special.is_set(merc.SPC_PRINCE) or ch.powers[merc.UNI_GEN] != 2):
        ch.huh()
        return

    if not arg1 or not arg2:
        ch.send("Syntax is: favour <target> <prince/sire>\n")
        return

    victim = ch.get_char_room(arg1)
    if not victim:
        ch.not_here(arg1)
        return

    if ch == victim:
        ch.not_self()
        return

    if not victim.is_npc():
        ch.not_npc()
        return

    if not victim.is_vampire():
        ch.send("But they are not a vampire!\n")
        return

    if not game_utils.str_cmp(victim.clan, ch.clan) and game_utils.str_cmp(arg2, "induct"):
        ch.send("You can only grant your favour to someone in your clan.\n")
        return

    if ch.powers[merc.UNI_GEN] >= victim.powers[merc.UNI_GEN]:
        ch.send("You can only grant your favour to someone of a lower generation.\n")
        return

    if game_utils.str_cmp(arg2, "prince") and ch.powers[merc.UNI_GEN] == 2:
        if victim.special.is_set(merc.SPC_PRINCE):
            handler_game.act("You remove $N's prince privilages!", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n removes $N's prince privilages!", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n removes your prince privilages!", ch, None, victim, merc.TO_VICT)
            victim.special.rem_bit(merc.SPC_SIRE)
            victim.special.rem_bit(merc.SPC_PRINCE)
            return

        handler_game.act("You make $N a prince!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has made $N a prince!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n has made you a prince!", ch, None, victim, merc.TO_VICT)
        victim.special.set_bit(merc.SPC_PRINCE)
        victim.special.rem_bit(merc.SPC_SIRE)
    elif game_utils.str_cmp(arg2, "sire") and (ch.powers[merc.UNI_GEN] == 2 or victim.special.is_set(merc.SPC_PRINCE)):
        if victim.special.is_set(merc.SPC_SIRE):
            handler_game.act("You remove $N's permission to sire a childe!", ch, None, victim, merc.TO_CHAR)
            handler_game.act("$n has removed $N's permission to sire a childe!", ch, None, victim, merc.TO_NOTVICT)
            handler_game.act("$n has remove your permission to sire a childe!", ch, None, victim, merc.TO_VICT)
            victim.special.rem_bit(merc.SPC_SIRE)
            return

        handler_game.act("You grant $N permission to sire a childe!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has granted $N permission to sire a childe!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n has granted you permission to sire a childe!", ch, None, victim, merc.TO_VICT)
        victim.special.set_bit(merc.SPC_SIRE)
    elif game_utils.str_cmp(arg2, "outcast") and victim.powers[merc.UNI_GEN] > 2 and ch.powers[merc.UNI_GEN] == 2:
        handler_game.act("You make $N a Caitiff!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has made $N a Caitiff!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n has made you a Caitiff!", ch, None, victim, merc.TO_VICT)
        victim.clan = ""
    elif game_utils.str_cmp(arg2, "outcast") and victim.powers[merc.UNI_GEN] > 2 and not victim.special.is_set(merc.SPC_PRINCE) and \
            ch.special.is_set(merc.SPC_PRINCE):
        handler_game.act("You make $N a Caitiff!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has made $N a Caitiff!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n has made you a Caitiff!", ch, None, victim, merc.TO_VICT)
        victim.clan = ""
    elif game_utils.str_cmp(arg2, "induct") and victim.powers[merc.UNI_GEN] > 2 and ch.powers[merc.UNI_GEN] == 2 and not victim.clan:
        if victim.special.is_set(merc.SPC_ANARCH):
            ch.send("You cannot induct an Anarch!\n")
            return

        handler_game.act("You induct $N into your clan!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n inducts $N into $s clan!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n inducts you into $s clan!", ch, None, victim, merc.TO_VICT)
        victim.clan = ch.clan
    elif game_utils.str_cmp(arg2, "induct") and victim.powers[merc.UNI_GEN] > 2 and not victim.special.is_set(merc.SPC_PRINCE) and \
            ch.special.is_set(merc.SPC_PRINCE) and not victim.clan:
        if victim.special.is_set(merc.SPC_ANARCH):
            ch.send("You cannot induct an Anarch!\n")
            return

        handler_game.act("You induct $N into your clan!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n inducts $N into $s clan!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n inducts you into $s clan!", ch, None, victim, merc.TO_VICT)
        victim.clan = ch.clan
    elif game_utils.str_cmp(arg2, "accept") and (ch.powers[merc.UNI_GEN] == 2 or ch.special.is_set(merc.SPC_PRINCE)):
        if victim.rank > merc.AGE_CHILDE:
            ch.send("But they are not a childe!\n")
            return

        handler_game.act("You accept $N into the clan!", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n has accepted $N into $s clan!", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n accepted you into $s clan!", ch, None, victim, merc.TO_VICT)
        victim.rank = merc.AGE_NEONATE
    else:
        ch.send("You are unable to grant that sort of favour.\n")


interp.register_command(
    interp.CmdType(
        name="favour",
        cmd_fun=cmd_favour,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
