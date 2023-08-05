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

import comm
import fight
import game_utils
import handler_game
import interp
import merc


def cmd_decapitate(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    item = ch.get_eq("right_hand")
    if not item or item.item_type != merc.ITEM_WEAPON:
        item = ch.get_eq("left_hand")
        if not item or item.item_type != merc.ITEM_WEAPON:
            ch.send("But you are not wielding any weapons!\n")
            return

    if item.value[3] not in [1, 3]:
        ch.send("You need to wield a slashing or slicing weapon to decapitate.\n")
        return

    if not arg:
        ch.send("Decapitate whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if ch == victim:
        ch.not_self()
        return

    if victim.is_npc():
        ch.send("You can only decapitate other players.\n")
        return

    if not ch.can_pk():
        ch.send("You must be an avatar to decapitate someone.\n")
        return

    if not victim.can_pk():
        ch.send("You can only decapitate other avatars.\n")
        return

    if victim.position > merc.POS_MORTAL:
        ch.send("You can only do this to mortally wounded players.\n")
        return

    if fight.is_safe(ch, victim):
        return

    if ch.is_vampire() and ch.special.is_set(merc.SPC_INCONNU) and (victim.is_vampire() or victim.vampaff.is_set(merc.VAM_MORTAL)):
        ch.send("You cannot decapitate another vampire.\n")
        return

    if victim.is_vampire() and victim.special.is_set(merc.SPC_INCONNU) and (ch.is_vampire() or ch.vampaff.is_set(merc.VAM_MORTAL)):
        ch.send("You cannot decapitate an Inconnu vampire.\n")
        return

    if ch.is_vampire() and victim.is_vampire() and ch.clan and victim.clan:
        if game_utils.str_cmp(ch.clan, victim.clan):
            ch.send("You cannot decapitate someone of your own clan.\n")
            return

    handler_game.act("You bring your weapon down upon $N's neck!", ch, None, victim, merc.TO_CHAR)
    victim.send("Your head is sliced from your shoulders!\n")
    handler_game.act("$n swings $s weapon down towards $N's neck!", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n's head is sliced from $s shoulders!", victim, None, None, merc.TO_ROOM)

    if ch.is_demon() or ch.special.is_set(merc.SPC_CHAMPION) and not victim.is_demon() and not victim.special.is_set(merc.SPC_CHAMPION):
        if ch.race == 0 and victim.race == 0:
            ch.powers[merc.DEMON_CURRENT] += 1000
            ch.powers[merc.DEMON_TOTAL] += 1000
        else:
            ch.powers[merc.DEMON_CURRENT] += victim.race * 1000
            ch.powers[merc.DEMON_TOTAL] += victim.race * 1000

    if victim.race < 1 and ch.race > 0:
        comm.info(f"{victim.name} has been decapitated by {ch.name} for no status.")
        comm.notify(f"{victim.name} decapitated by {ch.name} at {victim.in_room.vnum} for no status.", merc.CONSOLE_INFO)

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
        ch.race += 1
    elif ch.race - ((ch.race // 100) * 100) < 25:
        ch.race += 1

    if ch.race - ((ch.race // 100) * 100) == 0:
        victim.race = victim.race
    elif victim.race - ((victim.race // 100) * 100) > 0:
        victim.race += 1

    handler_game.act("A misty white vapour pours from $N's corpse into your body.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("A misty white vapour pours from $N's corpse into $n's body.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("You double over in agony as raw energy pulses through your veins.", ch, None, None, merc.TO_CHAR)
    handler_game.act("$n doubles over in agony as sparks of energy crackle around $m.", ch, None, None, merc.TO_NOTVICT)

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
    victim.powers[merc.UNI_RAGE] = 0
    victim.level = 2
    comm.info(f"{victim.name} has been decapitated by {ch.name}.")
    comm.notify(f"{victim.name} decapitated by {ch.name} at {victim.in_room.vnum}.", merc.CONSOLE_INFO)


interp.register_command(
    interp.CmdType(
        name="decapitate",
        cmd_fun=cmd_decapitate,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_ALWAYS, show=True,
        default_arg=""
    )
)
