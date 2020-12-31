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

import const
import fight
import game_utils
import handler_game
import interp
import merc


# noinspection PyUnusedLocal
def cmd_kick(ch, argument):
    if not ch.is_npc() and ch.level < const.skill_table["kick"].skill_level:
        ch.send("First you should learn to kick.\n")
        return

    victim = ch.fighting
    if not victim:
        ch.send("You aren't fighting anyone.\n")
        return

    ch.wait_state(const.skill_table["kick"].beats)

    if ch.is_npc() or game_utils.number_percent() < ch.learned["kick"]:
        dam = game_utils.number_range(1, 4)
    elif not victim.is_npc() and victim.immune.is_set(merc.IMM_KICK):
        fight.damage(ch, victim, 0, "kick")
    else:
        fight.damage(ch, victim, 0, "kick")
        return

    dam = ch.damroll

    if dam == 0:
        dam = 1

    if not victim.is_awake():
        dam *= 2

    if not ch.is_npc() and ch.is_vampire() and ch.vampaff.is_set(merc.VAM_POTENCE):
        dam *= 1.5
    elif not ch.is_npc() and (ch.special.is_set(merc.SPC_CHAMPION) or ch.is_demon()) and ch.dempower.is_set(merc.DEM_MIGHT):
        dam *= 1.5

    if not victim.is_npc() and victim.is_werewolf():
        if victim.special.is_set(merc.SPC_WOLFMAN):
            dam *= 0.5

        if victim.powers[merc.WPOWER_BOAR] > 2:
            dam *= 0.5

        boots = ch.get_eq("feet")
        if boots and boots.flags.silver:
            dam *= 2

    # Vampires should be tougher at night and weaker during the day.
    if not ch.is_npc() and ch.is_vampire():
        if handler_game.weather_info.sunlight == merc.SUN_LIGHT and dam > 1:
            dam //= 1.5
        elif handler_game.weather_info.sunlight == merc.SUN_DARK:
            dam *= 1.5

    if not ch.is_npc():
        dam = dam + (dam * ((ch.wpn[merc.WPN_UNARMED] + 1) // 100))

        stance = ch.stance[0]
        if ch.stance[0] == merc.STANCE_NORMAL:
            dam *= 1.25
        else:
            dam = fight.dambonus(ch, victim, dam, stance)

    if dam <= 0:
        dam = 1

    fight.damage(ch, victim, dam, "kick")


interp.register_command(
    interp.CmdType(
        name="kick",
        cmd_fun=cmd_kick,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
