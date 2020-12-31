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


def cmd_stance(ch, argument):
    argument, arg = game_utils.read_word(argument)

    if ch.is_npc():
        return

    if ch.mounted == merc.IS_RIDING:
        ch.send("Not while mounted.\n")
        return

    if ch.is_affected(merc.AFF_POLYMORPH) and not ch.vampaff.is_set(merc.VAM_DISGUISED):
        ch.send("Not while polymorphed.\n")
        return

    if not arg:
        if ch.stance[0] == -1:
            ch.stance[0] = 0
            ch.send("You drop into a fighting stance.\n")
            handler_game.act("$n drops into a fighting stance.", ch, None, None, merc.TO_ROOM)
        else:
            ch.stance[0] = -1
            ch.send("You relax from your fighting stance.\n")
            handler_game.act("$n relaxes from $s fighting stance.", ch, None, None, merc.TO_ROOM)
        return

    if ch.stance[0] > 0:
        ch.send("You cannot change stances until you come up from the one you are currently in.\n")
        return

    if game_utils.str_cmp(arg, "none"):
        selection = merc.STANCE_NONE
        ch.send("You drop into a general fighting stance.\n")
        handler_game.act("$n drops into a general fighting stance.", ch, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg, "viper"):
        selection = merc.STANCE_VIPER
        ch.send("You arch your body into the viper fighting stance.\n")
        handler_game.act("$n arches $s body into the viper fighting stance.", ch, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg, "crane"):
        selection = merc.STANCE_CRANE
        ch.send("You swing your body into the crane fighting stance.\n")
        handler_game.act("$n swings $s body into the crane fighting stance.", ch, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg, "crab"):
        selection = merc.STANCE_CRAB
        ch.send("You squat down into the crab fighting stance.\n")
        handler_game.act("$n squats down into the crab fighting stance.", ch, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg, "mongoose"):
        selection = merc.STANCE_MONGOOSE
        ch.send("You twist into the mongoose fighting stance.\n")
        handler_game.act("$n twists into the mongoose fighting stance.", ch, None, None, merc.TO_ROOM)
    elif game_utils.str_cmp(arg, "bull"):
        selection = merc.STANCE_BULL
        ch.send("You hunch down into the bull fighting stance.\n")
        handler_game.act("$n hunches down into the bull fighting stance.", ch, None, None, merc.TO_ROOM)
    else:
        if game_utils.str_cmp(arg, "mantis") and ch.stance[merc.STANCE_CRANE] >= 200 and ch.stance[merc.STANCE_VIPER] >= 200:
            selection = merc.STANCE_MANTIS
            ch.send("You spin your body into the mantis fighting stance.\n")
            handler_game.act("$n spins $s body into the mantis fighting stance.", ch, None, None, merc.TO_ROOM)
        elif game_utils.str_cmp(arg, "dragon") and ch.stance[merc.STANCE_BULL] >= 200 and ch.stance[merc.STANCE_CRAB] >= 200:
            selection = merc.STANCE_DRAGON
            ch.send("You coil your body into the dragon fighting stance.\n")
            handler_game.act("$n coils $s body into the dragon fighting stance.", ch, None, None, merc.TO_ROOM)
        elif game_utils.str_cmp(arg, "tiger") and ch.stance[merc.STANCE_BULL] >= 200 and ch.stance[merc.STANCE_VIPER] >= 200:
            selection = merc.STANCE_TIGER
            ch.send("You lunge into the tiger fighting stance.\n")
            handler_game.act("$n lunges into the tiger fighting stance.", ch, None, None, merc.TO_ROOM)
        elif game_utils.str_cmp(arg, "monkey") and ch.stance[merc.STANCE_CRANE] >= 200 and ch.stance[merc.STANCE_MONGOOSE] >= 200:
            selection = merc.STANCE_MONKEY
            ch.send("You rotate your body into the monkey fighting stance.\n")
            handler_game.act("$n rotates $s body into the monkey fighting stance.", ch, None, None, merc.TO_ROOM)
        elif game_utils.str_cmp(arg, "swallow") and ch.stance[merc.STANCE_CRAB] >= 200 and ch.stance[merc.STANCE_MONGOOSE] >= 200:
            selection = merc.STANCE_SWALLOW
            ch.send("You slide into the swallow fighting stance.\n")
            handler_game.act("$n slides into the swallow fighting stance.", ch, None, None, merc.TO_ROOM)
        else:
            ch.send("Syntax is: stance <style>.\n"
                    "Stance being one of: None, Viper, Crane, Crab, Mongoose, Bull.\n")
            return
    ch.stance[0] = selection
    ch.wait_state(merc.PULSE_VIOLENCE)


interp.register_command(
    interp.CmdType(
        name="stance",
        cmd_fun=cmd_stance,
        position=merc.POS_FIGHTING, level=0,
        log=merc.LOG_NORMAL, show=True,
        default_arg=""
    )
)
