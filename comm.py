#  PythonWars copyright © 2020, 2021 by Paul Penner. All rights reserved.
#  In order to use this codebase you must comply with all licenses.
#
#  Original Diku Mud copyright © 1990, 1991 by Sebastian Hammer,
#  Michael Seifert, Hans Henrik Stærfeldt, Tom Madsen, and Katja Nyboe.
#
#  Merc Diku Mud improvements copyright © 1992, 1993 by Michael
#  Chastain, Michael Quan, and Mitchell Tse.
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

from collections import OrderedDict
import logging
import os
import platform
import random
import time
from types import MethodType

import db
import game_utils
import handler_ch
import handler_game
import handler_pc
import instance
import merc
import nanny
import settings


logger = logging.getLogger()
done = False
start_snapshot = None


def process_input():
    for d in instance.descriptor_list:
        if d.active and d.cmd_ready and d.connected:
            d.connected()

            if d.is_connected(nanny.con_playing):
                ch = handler_ch.ch_desc(d)
                if ch:
                    ch.timer = 0


def set_connected(self, state):
    self.connected = MethodType(state, self)


def is_connected(self, state):
    return self.connected == MethodType(state, self)


def process_output(self):
    ch = handler_ch.ch_desc(self)
    if ch and self.is_connected(nanny.con_playing) and self.send_buffer:
        if ch.act.is_set(merc.PLR_BLANK):
            ch.send("\n")

        if ch.act.is_set(merc.PLR_PROMPT) and ch.extra.is_set(merc.EXTRA_PROMPT):
            bust_a_prompt(ch)
        elif ch.act.is_set(merc.PLR_PROMPT):
            if ch.head.is_set(merc.LOST_HEAD) or ch.extra.is_set(merc.EXTRA_OSWITCH):
                exp_str = handler_pc.Pc.col_scale(ch.exp, ch.exp, 1000)
                buf = "<[{}X] [?H ?M ?V]> ".format(exp_str)
            elif ch.position == merc.POS_FIGHTING:
                victim = ch.fighting
                if victim.max_hit > 0:
                    percent = victim.hit * 100 // victim.max_hit
                else:
                    percent = -1

                if percent < 25:
                    cond = "#RAwful#n"
                elif percent < 50:
                    cond = "#BPoor#n"
                elif percent < 75:
                    cond = "#GFair#n"
                elif percent < 100:
                    cond = "#YGood#n"
                else:
                    cond = "#CPerfect#n"

                hit_str = handler_pc.Pc.col_scale(ch.hit, ch.hit, ch.max_hit)
                mana_str = handler_pc.Pc.col_scale(ch.mana, ch.mana, ch.max_mana)
                move_str = handler_pc.Pc.col_scale(ch.move, ch.move, ch.max_move)
                buf = "<[{}] [{}H {}M {}V]> ".format(cond, hit_str, mana_str, move_str)
            else:
                hit_str = handler_pc.Pc.col_scale(ch.hit, ch.hit, ch.max_hit)
                mana_str = handler_pc.Pc.col_scale(ch.mana, ch.mana, ch.max_mana)
                move_str = handler_pc.Pc.col_scale(ch.move, ch.move, ch.max_move)
                exp_str = handler_pc.Pc.col_scale(ch.exp, ch.exp, 1000)
                buf = "<[{}] [{}H {}M {}V]> ".format(exp_str, hit_str, mana_str, move_str)
            ch.send(buf)

    if self.snoop_by:
        self.send("% " + self.snoop_by)
    self.miniboa_send()


def init_descriptor(d):
    """ Gain control over process output without messing with miniboa.
    """
    notify("Sock.sinaddr: {}".format(d.address), merc.CONSOLE_INFO)

    d.set_connected = MethodType(set_connected, d)
    d.is_connected = MethodType(is_connected, d)
    d.set_connected(nanny.con_get_name)

    # Swiftest: I added the following to ban sites.  I don't
    # endorse banning of sites, but Copper has few descriptors now
    # and some people from certain sites keep abusing access by
    # using automated 'autodialers' and leaving connections hanging.
    #
    # Furey: added suffix check by request of Nickel of HiddenWorlds.
    for ban in instance.ban_list:
        if game_utils.str_suffix(ban.name, d.host):
            d.send("Your site has been banned from this Mud.\n")
            close_socket(d)
            return

    greeting = random.choice(instance.greeting_list)
    d.send(greeting.text)
    d.active = True
    d.character = None
    d.original = None
    d.snoop_by = None
    d.close = d.deactivate
    d.miniboa_send = d.socket_send
    d.socket_send = MethodType(process_output, d)
    instance.descriptor_list.append(d)
    d.request_terminal_type()
    d.request_naws()


# Check if already playing.
def check_playing(d, name):
    for dold in instance.descriptor_list:
        if dold != d and dold.character and dold.connected not in [nanny.con_get_name, nanny.con_get_old_password] and \
                game_utils.str_cmp(name, dold.original.name if dold.original else dold.character.name):
            if d.character:
                del d.character
                d.character = None

            dold.character.send("This body has been taken over!\n")
            d.set_connected(nanny.con_playing)
            d.character = dold.character
            d.character.desc = d
            d.active = True
            d.character.send = d.send
            d.character.send("You take over your body, which was already in use.\n")
            handler_game.act("$n doubles over in agony and $s eyes roll up into $s head.\n"
                             "..$n's body has been taken over by another spirit!", d.character, None, None, merc.TO_ROOM)
            dold.character = None
            notify("Kicking off old connection {}@{}".format(d.character.name, d.addrport()), merc.CONSOLE_INFO)
            close_socket(dold)  # Slam the old connection into the ether
            return True
    return False


# Look for link-dead player to reconnect.
# noinspection PyUnusedLocal
def check_reconnect(d, name, fconn):
    for ch in list(instance.players.values()):
        if not ch.is_npc() and not ch.extra.is_set(merc.EXTRA_OSWITCH) and (not fconn or not ch.desc) and game_utils.str_cmp(d.character.name, ch.name):
            if not fconn:
                d.character.pwd = ch.pwd
            else:
                del d.character
                d.character = ch
                ch.desc = d
                d.active = True
                ch.send = d.send
                ch.timer = 0
                ch.send("Reconnecting.\n")

                if ch.is_npc() or ch.obj_vnum == 0:
                    handler_game.act("$n has reconnected.", ch, None, None, merc.TO_ROOM)

                notify("{}@%{} reconnected.".format(ch.name, d.addrport()), merc.CONSOLE_INFO)
                d.set_connected(nanny.con_playing)
            return True
    return False


# Kick off old connection.  KaVir.
# noinspection PyUnusedLocal
def check_kickoff(d, name, fconn):
    for ch in list(instance.characters.values()):
        if not ch.is_npc() and (not fconn or not ch.desc) and game_utils.str_cmp(d.character.name, ch.name):
            if not fconn:
                d.character.pwd = ch.pwd
            else:
                del d.character
                d.character = ch
                ch.desc = d
                d.active = True
                ch.send = d.send
                ch.timer = 0
                ch.send("You take over your body, which was already in use.\n")
                handler_game.act("...$n's body has been taken over by another spirit!", ch, None, None, merc.TO_ROOM)
                notify("{}@{} kicking off old link.".format(ch.name, d.addrport()), merc.CONSOLE_INFO)
                d.set_connected(nanny.con_playing)
            return True
    return False


def close_socket(d):
    if not d:
        return

    d.socket_send()

    if d.snoop_by:
        d.snoop_by.send("Your victim has left the game.\n")

    ch = d.character
    if ch and d.is_connected(nanny.con_playing) and ch.is_npc():
        ch.cmd_return("")

    for sock in instance.descriptor_list:
        if sock.snoop_by == d:
            sock.snoop_by = None

    ch = d.character
    if ch:
        notify("Closing link to {}.".format(ch.name), merc.CONSOLE_INFO)

        if d.is_connected(nanny.con_playing):
            if ch.is_npc() or ch.obj_vnum == 0:
                handler_game.act("$n has lost $s link.", ch, None, None, merc.TO_ROOM)

            ch.save(force=True)
            ch.desc = None
        else:
            del d.character
            d.character = None

    if d in instance.descriptor_list:
        instance.descriptor_list.remove(d)
    d.active = False


def close_socket2(d, kickoff):
    if not d:
        return

    d.socket_send()

    if d.snoop_by:
        d.snoop_by.send("Your victim has left the game.\n")

    ch = d.character
    if ch and d.is_connected(nanny.con_playing) and ch.is_npc():
        ch.cmd_return("")

    for sock in instance.descriptor_list:
        if sock.snoop_by == d:
            sock.snoop_by = None

    ch = d.character
    if ch:
        if d.is_connected(nanny.con_playing):
            if kickoff:
                handler_game.act("$n doubles over in agony and $s eyes roll up into $s head.", ch, None, None, merc.TO_ROOM)

            ch.save(force=True)
            ch.desc = None
        else:
            del d.character
            d.character = None

    if d in instance.descriptor_list:
        instance.descriptor_list.remove(d)
    d.active = False


# Bust a prompt (player settable prompt)
# coded by Morgenes for Aldara Mud
def bust_a_prompt(ch):
    if not ch:
        ch.send("\n\n")
        return

    if ch.position == merc.POS_FIGHTING or ch.fighting:
        if not ch.cprompt:
            ch.send("\n\n")
            return
        else:
            prompt = ch.cprompt
    else:
        if not ch.prompt:
            ch.send("\n\n")
            return
        else:
            prompt = ch.prompt

    act_trans = OrderedDict()
    act_trans["%a"] = "#C{}#n".format("good" if ch.is_good() else "evil" if ch.is_evil() else "neutral")
    act_trans["%A"] = "#C{}#n".format(ch.alignment)
    act_trans["%b"] = "#C{}#n".format(ch.beast)
    act_trans["%B"] = "{}".format(ch.blood if (not ch.is_npc() and ch.is_vampire()) else "0")
    act_trans["%c"] = "{}".format(ch.armor)

    victim = ch.fighting
    if not victim:
        buf = "#CN/A#n"
    else:
        if victim.max_hit > 0:
            percent = victim.hit * 100 // victim.max_hit
        else:
            percent = -1
        if percent < 25:
            buf = "#RAwful#n"
        elif percent < 50:
            buf = "#BPoor#n"
        elif percent < 75:
            buf = "#GFair#n"
        elif percent < 100:
            buf = "#YGood#n"
        else:
            buf = "#CPerfect#n"
    act_trans["%f"] = buf

    victim = ch.fighting
    if not victim:
        buf = "#CN/A#n"
    else:
        tank = victim.fighting
        if not tank:
            buf = "#CN/A#n"
        else:
            if tank.max_hit > 0:
                percent = tank.hit * 100 // tank.max_hit
            else:
                percent = -1
            if percent < 25:
                buf = "#RAwful#n"
            elif percent < 50:
                buf = "#BPoor#n"
            elif percent < 75:
                buf = "#GFair#n"
            elif percent < 100:
                buf = "#YGood#n"
            else:
                buf = "#CPerfect#n"
    act_trans["%F"] = buf
    act_trans["%g"] = "#C{}#n".format(ch.gold)

    buf = "{:,}".format(ch.hit)
    act_trans["%h"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.hit, ch.max_hit))
    act_trans["%H"] = "#C{:,}#n".format(ch.max_hit)

    buf = "{:,}".format(ch.mana)
    act_trans["%m"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.mana, ch.max_mana))
    act_trans["%M"] = "#C{}#n".format(ch.max_mana)

    victim = ch.fighting
    if not victim:
        buf = "#CN/A#n"
    else:
        if not victim.is_npc() and victim.is_affected(merc.AFF_POLYMORPH):
            buf = victim.morph
        else:
            buf = victim.short_descr if victim.is_npc() else victim.name
        buf = buf[0].upper() + buf[1:]
    act_trans["%n"] = buf

    victim = ch.fighting
    if not victim:
        buf = "#CN/A#n"
    else:
        tank = victim.fighting
        if not tank:
            buf = "#CN/A#n"
        else:
            if ch == tank:
                buf = "You"
            elif not tank.is_npc() and tank.is_affected(merc.AFF_POLYMORPH):
                buf = tank.morph
            else:
                buf = tank.short_descr if tank.is_npc() else tank.name
            buf = buf[0].upper() + buf[1:]
    act_trans["%N"] = buf

    buf = "{}".format(ch.hitroll)
    act_trans["%p"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.hitroll, 200))
    buf = "{}".format(ch.damroll)
    act_trans["%P"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.damroll, 200))

    act_trans["%q"] = "#C{}#n".format(ch.quest)
    act_trans["%r"] = "#C{}#n".format(ch.in_room.name if ch.in_room else " ")
    act_trans["%R"] = "{}".format("#r{}#n".format(ch.powers[merc.UNI_RAGE]) if (not ch.is_npc() and (ch.is_werewolf() or ch.is_vampire())) else "0")

    buf_list = [(0, "Avatar"), (4, "Immortal"), (9, "Godling"), (14, "Demigod"), (19, "Lesser God"), (24, "Greater God")]
    for (aa, bb) in buf_list:
        if ch.race <= aa:
            buf = bb
            break
    else:
        buf = "Supreme God"
    act_trans["%s"] = buf
    act_trans["%S"] = "{}".format(ch.race)

    buf = "{:,}".format(ch.move)
    act_trans["%v"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.move, ch.max_move))
    act_trans["%V"] = "#C{}#n".format(ch.max_move)

    buf = "{:,}".format(ch.exp)
    act_trans["%x"] = "{}".format(handler_pc.Pc.col_scale(buf, ch.exp, 1000))
    act_trans["%%"] = "%"

    msg = game_utils.mass_replace(prompt, act_trans)
    ch.send(msg)
    ch.desc.send_ga()


# noinspection PyUnusedLocal
def is_reconnecting(d, name):
    for ch in instance.players.values():
        if not ch.desc and ch.name == name:
            return True
    return False


def game_loop(server):
    from update import update_handler
    import sys_utils
    global done
    global start_snapshot

    machine_type = platform.system()
    uid = 1 if machine_type == "Windows" else os.getuid()
    if uid == 0:
        print("Do not run the Mud as root user!  This is a security risk!")

        with open(settings.SHUTDOWN_FILE, "w") as fp:
            fp.write("Mud started as root ({}). Shutting down now.\n".format(uid))

        assert(uid != 0)

    start_snapshot = sys_utils.ResourceSnapshot()
    # notify(start_snapshot.log_data(), merc.CONSOLE_BOOT)

    db.boot_db()

    boot_snapshot = sys_utils.ResourceSnapshot()
    notify(boot_snapshot.log_data(start_snapshot), merc.CONSOLE_BOOT)

    # JINNOTE - 11/10/2020 @ 12:44p
    #           Disabled for now, clogs up PyCharm way too much and doesn't work how it should IMHO - Zones as instances
    #           is a nice idea, but this is a poor implementation of it IMHO.  Instances should be saved/reloaded as
    #           needed, not every time the Mud boots; shouldn't be every single zone instancing every npc, item, room, etc.
    #           .
    #           If the actual intention was to store zones in json it would be even better; maybe I'll get around to fixing
    #           the load routines someday.
    #           .
    #           instance.save()
    #           .
    #           ready_snapshot = sys_utils.ResourceSnapshot()
    #           notify(ready_snapshot.log_data(boot_snapshot), merc.CONSOLE_BOOT)
    #           notify("MOTU-Mud database written in %.3f seconds", (ready_snapshot.current_time(True) -
    #                                                                boot_snapshot.current_time(True)), merc.CONSOLE_BOOT)

    final = boot_snapshot.current_time(True) - start_snapshot.current_time(True)
    perf_list = [(0.51, "Spectacular"), (1.01, "Excellent"), (5.01, "Very good"), (8.01, "Good"),
                 (12.01, "Fair"), (20.01, "Poor"), (40.01, "Very poor"), (65.01, "Bad")]
    for (aa, bb) in perf_list:
        if final < aa:
            perf = bb
            break
    else:
        perf = "Bad, very bad"

    results = ("------------------------[ Statistic ]------------------------",
               " Port     : {:6}    Boot Time: {:.3f}    Perform  : {:6}".format(server.port, final, perf),
               "-------------------------------------------------------------"
               )
    spaces = "\n" + " " * 51
    notify(spaces.join(results), merc.CONSOLE_BOOT)

    done = False
    slice_time = 1.0 / merc.PULSE_PER_SECOND
    while not done:
        merc.current_time = int(time.time())
        loop_time = time.time()
        server.poll()
        process_input()
        update_handler()

        time_spent = time.time() - loop_time
        if time_spent < slice_time:
            nap_time = slice_time - time_spent
            if nap_time > 0.0:
                time.sleep(nap_time)
            else:
                notify("Exceeded pulse time by {:.3f} seconds!".format(abs(nap_time)), merc.CONSOLE_WARNING)


def log_string(string):
    t = time.localtime()
    t = time.mktime(t)
    buf = "{}/{}.log".format(settings.LOG_DIR, time.strftime("%b-%d-%Y", time.localtime(t)))

    with open(buf, "a") as fp:
        fp.write(string + "\n")


def notify(msg, console=merc.CONSOLE_INFO):
    if console == merc.CONSOLE_DEBUG:
        logger.debug(msg)
    elif console == merc.CONSOLE_INFO:
        logger.info(msg)
    elif console == merc.CONSOLE_WARNING:
        logger.warning(msg)
    elif console == merc.CONSOLE_ERROR:
        logger.error(msg)
    elif console == merc.CONSOLE_CRITICAL:
        logger.critical(msg)
    elif console == merc.CONSOLE_BOOT:
        # noinspection PyUnresolvedReferences
        logger.boot(msg)
    elif console == merc.CONSOLE_EXCEPTION:
        logger.exception(msg)
    else:
        pass

    if console == merc.CONSOLE_BOOT:
        if not msg or len(msg) < 1:
            buf = "[*****] -----------------------------------------------------------------------"
        else:
            buf = "[*****] {}".format(msg)

        log_string(buf)
        return
    else:
        log_list = [(merc.CONSOLE_INFO, "Info"), (merc.CONSOLE_DEBUG, "Debug"), (merc.CONSOLE_WARNING, "Warning"),
                    (merc.CONSOLE_ERROR, "Error"), (merc.CONSOLE_CRITICAL, "Critical"), (merc.CONSOLE_BOOT, "Boot"),
                    (merc.CONSOLE_EXCEPTION, "Exception")]
        for (console_type, name) in log_list:
            if console == console_type:
                pstr = name
                break
        else:
            pstr = "Unknown"

    t = time.strftime("%I:%M:%S%p", time.localtime())
    buf = "<: {} : {:^10} : {} :>".format(t, pstr, game_utils.colorstrip(msg))
    log_string(buf)

    for d in instance.descriptor_list:
        if d.is_connected(nanny.con_playing) and d.character:
            if d.character.is_immortal():
                d.send("#Y" + buf + "#n\n")


def info(pstr):
    buf = "-> Info: {}".format(pstr)

    for fpl in instance.players.values():
        if fpl.desc and not fpl.channels.is_set(merc.CHANNEL_INFO):
            fpl.send(buf)
