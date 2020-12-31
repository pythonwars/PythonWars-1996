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

import fight
import game_utils
import handler_game
import interp
import merc


def cmd_bite(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_vampire() or ch.powers[merc.UNI_GEN] < 1:
        ch.huh()
        return

    if ch.powers[merc.UNI_CURRENT] == -1:
        ch.powers[merc.UNI_CURRENT] = ch.powers[merc.UNI_AFF]

    can_sire = ch.powers[merc.UNI_GEN] <= 6
    if not can_sire:
        ch.send("You are not able to create any childer.\n")
        return

    if not ch.clan and ch.powers[merc.UNI_GEN] == 2:
        ch.send("First you need to found a clan.\n")
        return

    clancount = 0
    clan_list = [merc.VAM_PROTEAN, merc.VAM_CELERITY, merc.VAM_FORTITUDE, merc.VAM_POTENCE, merc.VAM_OBFUSCATE, merc.VAM_OBTENEBRATION,
                 merc.VAM_SERPENTIS, merc.VAM_AUSPEX, merc.VAM_DOMINATE, merc.VAM_PRESENCE]
    for disc in clan_list:
        if ch.vampaff.is_set(disc):
            clancount += 1

    if clancount < 3:
        ch.send("First you need to master 3 disciplines.\n")
        return

    if not arg:
        ch.send("Bite whom?\n")
        return

    victim = ch.get_char_room(arg)
    if not victim:
        ch.not_here(arg)
        return

    if victim.is_npc():
        ch.not_npc()
        return

    if ch == victim:
        ch.not_self()
        return

    if not victim.is_immortal():
        ch.not_imm()
        return

    if not victim.is_mage():
        ch.send("You cannot bite mages.\n")
        return

    if victim.level != merc.LEVEL_AVATAR and not victim.is_immortal():
        ch.send("You can only bite avatars.\n")
        return

    if victim.is_werewolf():
        ch.send("You are unable to create werevamps!\n")
        return

    if victim.is_vampire() and ch.beast != 100:
        ch.send("But they are already a vampire!\n")
        return

    if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
        ch.send("But they have no soul!\n")
        return

    if victim.is_highlander():
        ch.send("You cannot turn highlanders into vampires.\n")
        return

    if not victim.immune.is_set(merc.IMM_VAMPIRE) and ch.beast != 100:
        ch.send("You cannot bite an unwilling person.\n")
        return

    if not ch.vampaff.is_set(merc.VAM_FANGS) and ch.beast != 100:
        ch.send("First you better get your fangs out!\n")
        return

    if ch.vampaff.is_set(merc.VAM_DISGUISED) and ch.beast != 100:
        ch.send("You must reveal your true nature to bite someone.\n")
        return

    if ch.exp < 1000 and ch.beast != 100:
        ch.send("You cannot afford the 1000 exp to create a childe.\n")
        return

    if ch.beast == 100 or ch.powers[merc.UNI_RAGE] > 0:
        if not ch.vampaff.is_set(merc.VAM_FANGS):
            ch.cmd_fangs("")

        handler_game.act("Your jaw opens wide and you leap hungrily at $N.", ch, None, victim, merc.TO_CHAR)
        handler_game.act("$n's jaw opens wide and $e leaps hungrily at $N.", ch, None, victim, merc.TO_NOTVICT)
        handler_game.act("$n's jaw opens wide and $e leaps hungrily at you.", ch, None, victim, merc.TO_VICT)
        fight.one_hit(ch, victim, -1, 0)
        return

    if ch.beast > 0:
        ch.beast += 1

    ch.exp -= 1000
    handler_game.act("You sink your teeth into $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n sinks $s teeth into $N.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n sinks $s teeth into your neck.", ch, None, victim, merc.TO_VICT)
    victim.ch_class = ch.ch_class

    if victim.powers[merc.UNI_GEN] != 0:
        ch.save(force=True)
        victim.save(force=True)
        victim.send("Your vampiric status has been restored.\n")
        return

    outcast = False
    if ch.special.is_set(merc.SPC_SIRE) or ch.powers[merc.UNI_GEN] < 3 or ch.special.is_set(merc.SPC_PRINCE):
        ch.special.rem_bit(merc.SPC_SIRE)

        if ch.special.is_set(merc.SPC_ANARCH) and not ch.clan:
            outcast = True
    else:
        outcast = True

    victim.send("You are now a vampire.\n")
    victim.powers[merc.UNI_GEN] += 1

    if ch.powers[merc.UNI_GEN] == 1:
        victim.lord = ch.name
    else:
        victim.lord = "{} {}".format(ch.lord, ch.name)

    if ch.powers[merc.UNI_GEN] != 1:
        if victim.powers[merc.UNI_CURRENT] == -1:
            victim.powers[merc.UNI_CURRENT] = victim.powers[merc.UNI_AFF]

        # Remove hp bonus from fortitude
        if victim.vamppass.is_set(merc.VAM_FORTITUDE) and not victim.vampaff.is_set(merc.VAM_FORTITUDE):
            victim.max_hit -= 50
            victim.hit -= 50
            if victim.hit < 1:
                victim.hit = 1

        # Remove any old powers they might have
        disc_list = [merc.VAM_PROTEAN, merc.VAM_CELERITY, merc.VAM_FORTITUDE, merc.VAM_POTENCE, merc.VAM_OBFUSCATE, merc.VAM_OBTENEBRATION,
                     merc.VAM_SERPENTIS, merc.VAM_AUSPEX, merc.VAM_DOMINATE, merc.VAM_PRESENCE]
        for disc in disc_list:
            if victim.vamppass.is_set(disc):
                victim.vamppass.rem_bit(disc)
                victim.vampaff.rem_bit(disc)

        if not outcast:
            victim.clan = ch.clan

        # Give the vampire the base powers of their sire
        if ch.vamppass.is_set(merc.VAM_FORTITUDE) and not victim.vampaff.is_set(merc.VAM_FORTITUDE):
            victim.max_hit += 50
            victim.hit += 50

        for disc in disc_list:
            if ch.vamppass.is_set(disc):
                victim.vamppass.set_bit(disc)
                victim.vampaff.set_bit(disc)

    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="bite",
        cmd_fun=cmd_bite,
        position=merc.POS_STANDING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
