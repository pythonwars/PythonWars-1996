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
import handler_game
import interp
import merc


def cmd_claw(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if not ch.is_werewolf() or ch.powers[merc.UNI_GEN] < 1:
        ch.cmd_claws("")
        return

    can_sire = ch.powers[merc.UNI_GEN] <= 3
    if not can_sire:
        ch.send("You are unable to spread your gift.\n")
        return

    if ch.powers[merc.UNI_GEN] == 1 and ch.powers[merc.UNI_AFF] >= 4:
        ch.send("You have already created 4 tribal leaders.\n")
        return

    if not ch.clan and ch.powers[merc.UNI_GEN] != 1:
        ch.send("First you need to create a tribe.\n")
        return

    if not arg:
        ch.send("Claw whom?\n")
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
        ch.send("You cannot bite mages.\n")
        return

    if victim.level != merc.LEVEL_AVATAR and not victim.is_immortal():
        ch.send("You can only claw avatars.\n")
        return

    if victim.is_vampire() or victim.vampaff.is_set(merc.VAM_MORTAL):
        ch.send("You are unable to create werevamps!\n")
        return

    if victim.is_demon() or victim.special.is_set(merc.SPC_CHAMPION):
        ch.send("But they have no soul!\n")
        return

    if victim.is_highlander():
        ch.send("You cannot turn highlanders into werewolves.\n")
        return

    if victim.is_werewolf():
        ch.send("But they are already a werewolf!\n")
        return

    if not victim.immune.is_set(merc.IMM_VAMPIRE):
        ch.send("You cannot claw an unwilling person.\n")
        return

    if not victim.vampaff.is_set(merc.VAM_CLAWS):
        ch.send("First you better get your claws out!\n")
        return

    if ch.exp < 10000:
        ch.send("You cannot afford the 10000 exp to pass on the gift.\n")
        return

    ch.exp -= 10000

    if ch.powers[merc.UNI_CURRENT] < 1:
        ch.powers[merc.UNI_CURRENT] = 1
    else:
        ch.powers[merc.UNI_CURRENT] += 1

    ch.special.rem_bit(merc.SPC_SIRE)
    handler_game.act("You plunge your claws into $N.", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n plunges $s claws into $N.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act("$n plunges $s claws into your chest.", ch, None, victim, merc.TO_VICT)
    victim.ch_class = ch.ch_class
    victim.send("You are now a werewolf.\n")
    victim.powers[merc.UNI_GEN] = ch.powers[merc.UNI_GEN] + 1

    if ch.powers[merc.UNI_GEN] == 1:
        victim.lord = ch.name
    else:
        victim.lord = f"{ch.lord} {ch.name}"

    victim.clan = ch.clan
    victim.powers[merc.UNI_AFF] = 0
    victim.powers[merc.UNI_CURRENT] = 0
    ch.save(force=True)
    victim.save(force=True)


interp.register_command(
    interp.CmdType(
        name="claw",
        cmd_fun=cmd_claw,
        position=merc.POS_SITTING, level=3,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
