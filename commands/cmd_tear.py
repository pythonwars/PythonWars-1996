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

import comm
import fight
import game_utils
import handler_game
import interp
import merc


def cmd_tear(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_werewolf():
        ch.huh()
        return

    if not ch.special.is_set(merc.SPC_WOLFMAN):
        ch.send("You can only tear heads off while in Crinos form.\n")
        return

    if not ch.vampaff.is_set(merc.VAM_CLAWS):
        ch.send("You better get your claws out first.\n")
        return

    if not arg:
        ch.send("Who's head do you wish to tear off?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_npc():
        ch.send("You can only tear the heads off other players.\n")
        return

    if not ch.can_pk():
        ch.send("You must be an avatar to tear someone's head off.\n")
        return

    if not victim.can_pk():
        ch.send("You can only tear the head off another avatar.\n")
        return

    if victim.position > merc.POS_MORTAL:
        ch.send("You can only do this to mortally wounded players.\n")
        return

    if fight.is_safe(ch, victim):
        return

    handler_game.act("You tear $N's head from $S shoulders!", ch, None, victim, merc.TO_CHAR)
    victim.send("Your head is torn from your shoulders!\n")
    handler_game.act("$n tears $N's head from $S shoulders!", ch, None, victim, merc.TO_NOTVICT)

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION):
        if ch.race == 0 and victim.race == 0:
            ch.powers[merc.DEMON_CURRENT] += 1000
            ch.powers[merc.DEMON_TOTAL] += 1000
        else:
            ch.powers[merc.DEMON_CURRENT] += victim.race * 1000
            ch.powers[merc.DEMON_TOTAL] += victim.race * 1000

    if victim.race < 1 and ch.race > 0:
        comm.info("{} has been decapitated by {}.".format(victim.name, ch.name))
        comm.notify("{} decapitated by {} at {} for no status.".format(victim.name, ch.name, victim.in_room.vnum), merc.CONSOLE_INFO)

        if victim.is_vampire():
            victim.mortalvamp()
        elif victim.special.is_set(merc.SPC_WOLFMAN):
            victim.unwerewolf()

        if victim.is_mage() and victim.is_affected(merc.AFF_POLYMORPH):
            victim.cmd_unpolymorph("")

        fight.behead(victim)
        ch.beastlike()
        ch.pkill += 1
        victim.pdeath += 1
        return

    ch.exp += 1000
    if ch.race - ((ch.race // 100) * 100) == 0:
        ch.race = ch.race + 1
    elif ch.race - ((ch.race // 100) * 100) < 25:
        ch.race = ch.race + 1

    if ch.race - ((ch.race // 100) * 100) == 0:
        victim.race = victim.race
    elif victim.race - ((victim.race // 100) * 100) > 0:
        victim.race = victim.race - 1

    handler_game.act("A misty white vapour pours from $N's corpse into your body.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("A misty white vapour pours from $N's corpse into $n's body.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("You double over in agony as raw energy pulses through your veins.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n doubles over in agony as sparks of energy crackle around $m.", ch, None, None, merc.TO_NOTVICT)

    if victim.is_vampire():
        victim.mortalvamp()
    elif victim.special.is_set(merc.SPC_WOLFMAN):
        victim.unwerewol()

    if victim.is_mage() and victim.is_affected(merc.AFF_POLYMORPH):
        victim.cmd_unpolymorph("")

    fight.behead(victim)
    ch.beastlike()
    ch.pkill += 1
    victim.pdeath += 1
    victim.powers[merc.UNI_RAGE] = 0
    victim.level = 2
    comm.info("{} has been decapitated by {}.".format(victim.name, ch.name))
    comm.notify("{} decapitated by {} at {}.".format(victim.name, ch.name, victim.in_room.vnum), merc.CONSOLE_INFO)


interp.register_command(
    interp.CmdType(
        name="tear",
        cmd_fun=cmd_tear,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
