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

import copy
import hashlib
import json
import os
import time

import bit
import comm
import const
import fight
import game_utils
import handler_game
import handler_log
import handler_room
import instance
import interp
import living
import merc
import settings
import state_checks
import sys_utils


class Pc(living.Living):
    template_count = 0
    instance_count = 0

    def __init__(self, template=None, **kwargs):
        import handler_item
        super().__init__()
        self.is_pc = True
        self.valid = False
        self.pnote = None

        self.act = bit.Bit(merc.PLR_BLANK | merc.PLR_COMBINE | merc.PLR_PROMPT, flagset_name="plr_flags")

        self.bamfin = ""
        self.bamfout = ""
        self.last_host = ""
        self.email = ""
        self._title = ""
        self.pload = ""
        self.prompt = ""
        self.cprompt = ""
        self.pwd = ""

        self.createtime = int(merc.current_time)
        self.home = merc.ROOM_VNUM_TEMPLE
        self.last_note = 0

        self.score = [0] * merc.MAX_SCORE
        self.learned = {}

        self._last_login = time.time()
        self._last_logout = None
        self._saved_room_vnum = merc.ROOM_VNUM_TEMPLE

        if template or kwargs:
            if template and not kwargs:
                self.name = template
                self.instancer()

            if kwargs:
                [setattr(self, k, copy.deepcopy(v)) for k, v in kwargs.items()]

                if self._fighting:
                    self._fighting = None
                    self.position = merc.POS_STANDING

                if self.environment:
                    if self._environment not in instance.global_instances.keys():
                        self.environment = None

                if self.inventory:
                    for instance_id in self.inventory[:]:
                        handler_item.Items.load(instance_id=instance_id, player_name=self.name)

                for item_id in self.equipped.values():
                    if item_id:
                        handler_item.Items.load(instance_id=item_id, player_name=self.name)

            self.instance_setup()

        if self.instance_id:
            Pc.instance_count += 1
        else:
            Pc.template_count += 1

        self._last_saved = None
        self._md5 = None

    def __del__(self):
        try:
            if self.instance_id:
                Pc.instance_count -= 1
                if instance.players.get(self.instance_id, None):
                    self.instance_destructor()
            else:
                Pc.template_count -= 1
        except:
            return

    def __repr__(self):
        return "<PC: {} ID {}>".format(self.name, self.instance_id)

    def instance_setup(self):
        instance.global_instances[self.instance_id] = self
        instance.characters[self.instance_id] = self
        instance.players[self.instance_id] = self

        if self.name not in instance.instances_by_player.keys():
            instance.instances_by_player[self.name] = [self.instance_id]
        else:
            instance.instances_by_player[self.name] += [self.instance_id]

    def instance_destructor(self):
        instance.instances_by_player[self.name].remove(self.instance_id)
        del instance.players[self.instance_id]
        del instance.characters[self.instance_id]
        del instance.global_instances[self.instance_id]

    def absorb(self, *args):
        pass

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if self.is_npc():
            return

        title = title[:50] if len(title) > 50 else title
        if title[0] in [".", ",", "!", "?"]:
            self._title = title
        else:
            self._title = " " + title

    @classmethod
    def add_color(cls, pstr, col):
        return "{col}{pstr}#n".format(col=col, pstr=pstr)

    @classmethod
    def col_scale(cls, pstr, curr, pmax):
        scale = ("#R", "#B", "#G", "#Y")

        if curr < 1:
            color = "#R"
        else:
            if curr < pmax:
                final = pmax if pmax > 0 else 1
                color = scale[int((4 * curr) // final)]
            else:
                color = "#C"

        return Pc.add_color(pstr, color)

    def update_skills(self):
        for sn in self.learned.copy():
            if sn not in const.skill_table:
                del self.learned[sn]

        for sn, skill in const.skill_table.items():
            if sn not in self.learned and self.level >= skill.skill_level:
                self.add_skill(sn)

        for sn, skill in const.skill_table.items():
            if sn in self.learned and self.level < skill.skill_level:
                self.del_skill(sn)

    # recursively adds a group given its number -- uses group_add
    def add_skill(self, name):
        if self.is_npc():
            return

        if name not in self.learned:  # i.e. not known
            self.learned[name] = 0

    # recursively removes a group given its number -- uses group_remove
    def del_skill(self, name):
        if self.is_npc():
            return

        if name in self.learned:
            del self.learned[name]
            return

    def check_social(self, command, argument):
        cmd = None
        for key, social in const.social_table.items():
            if command[0] == social.name[0] and game_utils.str_prefix(command, social.name):
                cmd = social
                break

        if not cmd:
            return False

        if not self.is_npc() and self.sentances.is_set(merc.SENT_NO_EMOTE):
            self.send("You are anti-social!\n")
            return True

        if self.position == merc.POS_DEAD:
            self.send("Lie still; you are DEAD.\n")
            return True
        if self.position in [merc.POS_INCAP, merc.POS_MORTAL]:
            self.send("You are hurt far too bad for that.\n")
            return True
        if self.position == merc.POS_STUNNED:
            self.send("You are too stunned to do that.\n")
            return True
        if self.position == merc.POS_SLEEPING:
            # I just know this is the path to a 12" 'if' statement.  :(
            # But two players asked for it already!  -- Furey
            if not game_utils.str_cmp(cmd.name, "snore"):
                self.send("In your dreams, or what?\n")
                return True

        holder, arg = game_utils.read_word(argument)
        victim = self.get_char_room(arg)
        if not arg:
            handler_game.act(cmd.others_no_arg, self, None, victim, merc.TO_ROOM)
            handler_game.act(cmd.char_no_arg, self, None, victim, merc.TO_CHAR)
        elif not victim:
            self.not_here(arg)
        elif victim == self:
            handler_game.act(cmd.others_auto, self, None, victim, merc.TO_ROOM)
            handler_game.act(cmd.char_auto, self, None, victim, merc.TO_CHAR)
        else:
            handler_game.act(cmd.others_found, self, None, victim, merc.TO_NOTVICT)
            handler_game.act(cmd.char_found, self, None, victim, merc.TO_CHAR)
            handler_game.act(cmd.vict_found, self, None, victim, merc.TO_VICT)

            if not self.is_npc() and victim.is_npc() and not victim.is_affected(merc.AFF_CHARM) and victim.is_awake():
                chance = game_utils.number_bits(4)
                if chance == 0:
                    fight.multi_hit(victim, self, merc.TYPE_UNDEFINED)
                elif chance in [1, 2, 3, 4, 5, 6, 7, 8]:
                    handler_game.act(cmd.others_found, victim, None, self, merc.TO_NOTVICT)
                    handler_game.act(cmd.char_found, victim, None, self, merc.TO_CHAR)
                    handler_game.act(cmd.vict_found, victim, None, self, merc.TO_VICT)
                elif chance in [9, 10, 11, 12]:
                    handler_game.act("$n slaps $N.", victim, None, self, merc.TO_NOTVICT)
                    handler_game.act("You slap $N.", victim, None, self, merc.TO_CHAR)
                    handler_game.act("$n slaps you.", victim, None, self, merc.TO_VICT)
        return True

    # TODO: RemoveDebug
    @handler_log.Logged("Interp")
    def interpret(self, argument):
        # Strip leading spaces.
        argument = argument.lstrip()
        if not argument:
            return

        # Implement freeze command.
        if not self.is_npc() and self.sentances.is_set(merc.SENT_FREEZE):
            self.send("You're totally frozen!\n")
            return

        # Grab the command word.
        # Special parsing so ' can be a command,
        #   also no spaces needed after punctuation.
        logline = argument
        if not argument[0].isalpha() and not argument[0].isdigit():
            command = argument[0]
            argument = argument[:1].lstrip()
        else:
            argument, command = game_utils.read_word(argument)

        # Look for command in command table.
        trust = self.trust
        cmd = state_checks.prefix_lookup(interp.cmd_table, command)
        if cmd:
            if command[0] == cmd.name[0] and game_utils.str_prefix(command, cmd.name) and cmd.level <= trust:
                if self.head.is_set(merc.LOST_HEAD) or self.extra.is_set(merc.EXTRA_OSWITCH):
                    cmd_list = ["say", "'", "immtalk", ":", "chat" ".", "look", "save", "exits", "emote", "tell", "order", "who",
                                "weather", "where", "relevel", "safe", "scan", "say", "spy", "score", "save", "inventory", "oreturn",
                                "roll", "leap", "lifespan", "nightsight", "truesight", "horns", "fangs", "cast"]
                    if game_utils.str_cmp(cmd.name, cmd_list) or (game_utils.str_cmp(cmd.name, ["quit", "humanform"]) and not self.is_npc() and
                                                                  self.obj_vnum != 0):
                        pass
                    else:
                        self.send("Not without a body!\n")
                        return
                elif self.extra.is_set(merc.EXTRA_TIED_UP):
                    cmd_list = ["say", "'", "chat", ".", "yell", "shout", "look", "save", "exits", "inventory", "tell", "order", "who",
                                "weather", "where", "introduce", "relevel", "safe", "scan", "spy", "wake", "fangs", "claws",
                                "nightsight", "shadowsight", "shadowplane", "regenerate", "shield", "vclan", "upkeep", "score",
                                "immune", "report", "goto", "flex", "change", "drink"]
                    if game_utils.str_cmp(cmd.name, cmd_list):
                        pass
                    else:
                        self.send("Not while tied up.\n")

                        if self.position > merc.POS_STUNNED:
                            handler_game.act("$n strains against $s bonds.", self, None, None, merc.TO_ROOM)
                        return
            else:
                cmd = None

        # Log and snoop.
        if cmd and cmd.log == merc.LOG_NEVER:
            logline = "XXXXXXXX XXXXXXXX XXXXXXXX"

        if (not self.is_npc() and self.sentances.is_set(merc.SENT_LOG)) or settings.LOGALL or (cmd and cmd.log == merc.LOG_ALWAYS):
            comm.notify("{}: {}".format(self.name, logline), merc.CONSOLE_INFO)

        if self.desc and self.desc.snoop_by:
            self.desc.snoop_by.send("% " + logline + "\n")

        if not cmd:
            # Look for command in socials table.
            if not Pc.check_social(self, command, argument):
                self.huh()
            return

        # Pc not in position for command?
        if self.position < cmd.position:
            if self.position == merc.POS_DEAD:
                self.send("Lie still; you are DEAD.\n")
            elif self.position in [merc.POS_MORTAL, merc.POS_INCAP]:
                self.send("You are hurt far too bad for that.\n")
            elif self.position == merc.POS_STUNNED:
                self.send("You are too stunned to do that.\n")
            elif self.position == merc.POS_SLEEPING:
                self.send("In your dreams, or what?\n")
            elif self.position in [merc.POS_MEDITATING, merc.POS_SITTING, merc.POS_RESTING]:
                self.send("Nah... You feel too relaxed...\n")
            elif self.position == merc.POS_FIGHTING:
                self.send("No way!  You are still fighting!\n")
            return

        # Dispatch the command.
        cmd.cmd_fun(self, cmd.default_arg if cmd.default_arg else argument.lstrip())

    # Serialization
    def to_json(self, outer_encoder=None):
        if outer_encoder is None:
            outer_encoder = json.JSONEncoder.default

        tmp_dict = {}
        for k, v in self.__dict__.items():
            if str(type(v)) in ("<class 'function'>", "<class 'method'>"):
                continue
            elif str(k) in ("desc", "send", "area", "available_light", "carry_weight", "carry_number", "chobj", "damcap", "familiar",
                            "is_area", "is_item", "is_living", "is_pc", "is_room", "leader", "logon", "master", "mount", "mounted",
                            "obj_vnum", "propose", "reply", "save_time", "timer", "valid", "wait", "was_in_room", "weight", "wizard",
                            "zone", "zone_template", "pnote", "followers"):
                continue
            elif str(k) in ("_last_saved", "_md5", "_fighting"):
                continue
            else:
                if str(k) == "position":
                    v = merc.POS_STANDING if v == merc.POS_FIGHTING else v
                tmp_dict[k] = v

        cls_name = "__class__/" + __name__ + "." + self.__class__.__name__
        return {cls_name: outer_encoder(tmp_dict)}

    @classmethod
    def from_json(cls, data, outer_decoder=None):
        if outer_decoder is None:
            outer_decoder = json.JSONDecoder.decode

        cls_name = "__class__/" + __name__ + "." + cls.__name__
        if cls_name in data:
            tmp_data = outer_decoder(data[cls_name])
            return cls(**tmp_data)
        return data

    # player get override to enforce saves, to avoid 'cheat' activities
    def get(self, instance_object, no_save=False):
        super().get(instance_object)
        # TODO: Fix dupeproofing code
        # if not no_save:
        #    self.save(force=True)
        return instance_object

    def save_stub(self, logout: bool = False):
        if logout:
            self._last_logout = time.time()

        pathname = os.path.join(settings.PLAYER_DIR, self.name[0].lower(), self.name.capitalize())
        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "login.json")

        stub = dict({})
        stub["name"] = self.name
        stub["createtime"] = self.createtime
        stub["title"] = self.title
        stub["pwd"] = self.pwd
        stub["email"] = self.email
        stub["is_immortal"] = self.is_immortal()
        stub["is_banned"] = self.sentances.is_set(merc.SENT_DENY)
        stub["instance_id"] = self.instance_id
        stub["last_login"] = self._last_login
        stub["last_logout"] = self._last_logout
        stub["last_host"] = self.last_host
        stub["last_time"] = int(self._last_saved) if self._last_saved else int(merc.current_time)
        stub["extra"] = self.extra.bits
        stub["sex"] = self.sex
        stub["level"] = self.level
        stub["race"] = self.race
        stub["played"] = self.played + (int(merc.current_time) + int(self.logon))
        stub["marriage"] = self.marriage
        stub["pkills"] = self.pkill
        stub["pdeaths"] = self.pdeath
        stub["mkills"] = self.mkill
        stub["mdeaths"] = self.mdeath
        stub["room"] = self._saved_room_vnum

        js = json.dumps(stub, default=instance.to_json, indent=2, sort_keys=True)
        with open(filename, "w") as fp:
            fp.write(js)

    @classmethod
    def load_stub(cls, player_name: str = None, silent=False):
        if not player_name:
            raise KeyError("Player name is required to load a player!")

        pathname = os.path.join(settings.PLAYER_DIR, player_name[0].lower(), player_name.capitalize())
        filename = os.path.join(pathname, "login.json")

        if os.path.isfile(filename):
            jso = ""
            with open(filename, "r+") as f:
                for line in f:
                    jso += line
            data = json.loads(jso, object_hook=instance.from_json)
            if isinstance(data, dict):
                return data
            else:
                if not silent:
                    comm.notify("Could not load player stub file for {}".format(player_name), merc.CONSOLE_ERROR)
                return None
        else:
            if not silent:
                comm.notify("Could not open player stub file for {}".format(player_name), merc.CONSOLE_ERROR)
            return None

    def save(self, logout: bool = False, force: bool = False):
        if not force and self.level < 2:
            return

        self._last_saved = time.time()
        self.last_host = self.desc.addr() if self.desc else self.last_host
        self.played_fake = self.played + int(merc.current_time - self.logon)
        self.save_stub(logout)

        pathname = os.path.join(settings.PLAYER_DIR, self.name[0].lower(), self.name.capitalize())
        os.makedirs(pathname, 0o755, True)
        filename = os.path.join(pathname, "player{}".format(settings.DATA_EXTN))

        js = json.dumps(self, default=instance.to_json, indent=2, sort_keys=True)
        md5 = hashlib.md5(js.encode("utf-8")).hexdigest()
        if self._md5 != md5:
            self._md5 = md5

            with open(filename, "w") as fp:
                fp.write(js)

        if self.inventory:
            for item_id in self.inventory[:]:
                if item_id not in instance.items:
                    comm.notify("Item {} is in Player {}'s inventory, but does not exist?".format(item_id, self.name), merc.CONSOLE_ERROR)
                    continue

                item = instance.items[item_id]
                item.save(in_inventory=True, player_name=self.name, force=force)
        for item_id in self.equipped.values():
            if item_id:
                if item_id not in instance.items:
                    comm.notify("Item {} is in Player {}'s inventory, but does not exist?".format(item_id, self.name), merc.CONSOLE_ERROR)
                    continue
                item = instance.items[item_id]
                item.save(is_equipped=True, player_name=self.name, force=force)

    @classmethod
    def load(cls, player_name: str = None, silent=False):
        if not player_name:
            raise KeyError("Player name is required to load a player!")

        pathname = os.path.join(settings.PLAYER_DIR, player_name[0].lower(), player_name.capitalize())
        filename = os.path.join(pathname, "player.json")

        if os.path.isfile(filename):
            jso = ""
            with open(filename, "r+") as f:
                for wline in f:
                    jso += wline

            obj = json.loads(jso, object_hook=instance.from_json)
            if isinstance(obj, Pc):
                obj._last_login = time.time()
                obj._last_logout = None
                obj.played = obj.played_fake
                return obj
            else:
                if not silent:
                    comm.notify("Could not load player file for {}".format(player_name), merc.CONSOLE_ERROR)
                return None
        else:
            if not silent:
                comm.notify("Could not open player file for {}".format(player_name), merc.CONSOLE_ERROR)
            return None

    # JINNOTE - 12/23/2020 @ 4:57 PM - Next two functions are hot messes, but less so than the original code.
    #                                  Could probably be simplified further with proper time/datetime functions.
    def other_age(self, is_self=False):
        total = 0
        yy = 17
        mm = 0
        dd = 0
        oday2 = 0
        omonth2 = 0
        oyear2 = 0
        argument = sys_utils.systimestamp(self.createtime)
        omonth = argument[4:7]
        oday0 = argument[8]
        oday1 = argument[9]
        ohour = argument[11:13]
        omin = argument[14:16]
        oyear = argument[20:24]

        if game_utils.str_cmp(omonth, ["Dec", "Oct", "Aug", "Jul", "May", "Mar", "Jan"]):
            omonth2 += 31
        elif game_utils.str_cmp(omonth, ["Nov", "Sep", "Jun", "Apr"]):
            omonth2 += 30
        elif game_utils.str_cmp(omonth, "Feb"):
            omonth2 += 28
        else:
            return "Error! Please inform an Immortal.\n"

        cday2 = 0
        cmonth2 = 0
        cyear2 = 0
        current = sys_utils.systimestamp(merc.current_time)
        cmonth = current[4:7]
        cday0 = current[8]
        cday1 = current[9]
        chour = current[11:13]
        cmin = current[14:16]
        cyear = current[20:24]

        if game_utils.str_cmp(cmonth, ["Dec", "Oct", "Aug", "Jul", "May", "Mar", "Jan"]):
            cmonth2 += 31
        elif game_utils.str_cmp(cmonth, ["Nov", "Sep", "Jun", "Apr"]):
            cmonth2 += 30
        elif game_utils.str_cmp(cmonth, "Feb"):
            cmonth2 += 28
        else:
            return "Error! Please inform an Immortal.\n"

        oyear2 += int(oyear) if oyear.isdigit() else 0
        cyear2 += int(cyear) if cyear.isdigit() else 0
        oday2 += (int(oday0) * 10) if oday0.isdigit() else 0
        oday2 += int(oday1) if oday1.isdigit() else 0
        cday2 += (int(cday0) * 10) if cday0.isdigit() else 0
        cday2 += int(cday1) if cday1.isdigit() else 0

        total += (cyear2 - oyear2) * 365
        total += cmonth2 - omonth2
        total += cday2 - oday2
        total *= 24  # Total playing time is now in hours

        if chour.isdigit() and ohour.isdigit():
            total += int(chour) - int(ohour)
        total *= 60  # Total now in minutes

        if cmin.isdigit() and omin.isdigit():
            total += int(cmin) - int(omin)

        if total < 1:
            total = 0
        else:
            total //= 12  # Time now in game days

        while True:
            if total >= 365:
                total -= 365
                yy += 1
            elif total >= 30:
                total -= 30
                mm += 1
            else:
                dd += total
                break

        if is_self:
            buf = "You are {} years, {} month{} and {} day{} old.\n".format(yy, mm, "" if mm == 1 else "s", dd, "" if dd == 1 else "s")
        else:
            buf = "Age: {} years, {} month{} and {} day{} old.\n".format(yy, mm, "" if mm == 1 else "s", dd, "" if dd == 1 else "s")
        return buf

    def years_old(self):
        total = 0
        yy = 17
        oday2 = 0
        omonth2 = 0
        oyear2 = 0
        argument = sys_utils.systimestamp(self.createtime)
        omonth = argument[4:7]
        oday0 = argument[8]
        oday1 = argument[9]
        ohour = argument[11:13]
        omin = argument[14:16]
        oyear = argument[20:24]

        if game_utils.str_cmp(omonth, ["Dec", "Oct", "Aug", "Jul", "May", "Mar", "Jan"]):
            omonth2 += 31
        elif game_utils.str_cmp(omonth, ["Nov", "Sep", "Jun", "Apr"]):
            omonth2 += 30
        elif game_utils.str_cmp(omonth, "Feb"):
            omonth2 += 28
        else:
            return yy

        cday2 = 0
        cmonth2 = 0
        cyear2 = 0
        current = sys_utils.systimestamp(merc.current_time)
        cmonth = current[4:7]
        cday0 = current[8]
        cday1 = current[9]
        chour = current[11:13]
        cmin = current[14:16]
        cyear = current[20:24]

        if game_utils.str_cmp(cmonth, ["Dec", "Oct", "Aug", "Jul", "May", "Mar", "Jan"]):
            cmonth2 += 31
        elif game_utils.str_cmp(cmonth, ["Nov", "Sep", "Jun", "Apr"]):
            cmonth2 += 30
        elif game_utils.str_cmp(cmonth, "Feb"):
            cmonth2 += 28
        else:
            return yy

        oyear2 += int(oyear) if oyear.isdigit() else 0
        cyear2 += int(cyear) if cyear.isdigit() else 0
        oday2 += (int(oday0) * 10) if oday0.isdigit() else 0
        oday2 += int(oday1) if oday1.isdigit() else 0
        cday2 += (int(cday0) * 10) if cday0.isdigit() else 0
        cday2 += int(cday1) if cday1.isdigit() else 0

        total += (cyear2 - oyear2) * 365
        total += cmonth2 - omonth2
        total += cday2 - oday2
        total *= 24  # Total playing time is now in hours

        if chour.isdigit() and ohour.isdigit():
            total += int(chour) - int(ohour)
        total *= 60  # Total now in minutes

        if cmin.isdigit() and omin.isdigit():
            total += int(cmin) - int(omin)

        if total < 1:
            total = 0
        else:
            total //= 12  # Time now in game days

        while total >= 365:
            total -= 365
            yy += 1
        return yy
