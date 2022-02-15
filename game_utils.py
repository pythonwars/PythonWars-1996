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

import collections
import random
import re
import sys
import time
import uuid

import bit
import comm
import instance
import merc


def read_forward(pstr, jump=1):
    return pstr[jump:]


def read_letter(pstr):
    pstr = pstr.lstrip()
    return pstr[1:], pstr[:1]


def str_cmp(astr, bstr, lower: bool = True):
    if not astr or not bstr:
        return False

    if type(astr) != str:
        comm.notify(f"str_cmp: astr:{astr} must be a type(str), received {type(astr)}", merc.CONSOLE_WARNING)
        return False

    if type(bstr) == list:
        i = 0
        while i < len(bstr):
            if str_cmp(astr, bstr[i]):
                return True

            i += 1

        return False

    if len(astr) != len(bstr):
        return False

    if lower:
        astr = astr.lower()
        bstr = bstr.lower()

    index = 0
    while index < len(astr):
        if astr[index] != bstr[index]:
            return False

        index += 1

    return True


def read_word(pstr, to_lower=True):
    if not pstr:
        return "", ""

    pstr = pstr.strip()
    start = None
    end = None

    i = -1
    for c in pstr:
        i += 1
        if c == "'" and start is None:
            start = i + 1
            quote = pstr.find("'", i + 1)
            if quote > -1:
                end = quote
            else:
                end = len(pstr)
            return pstr[end + 1:], pstr[start:end]
        elif c == '"' and start is None:
            start = i + 1
            quote = pstr.find('"', i + 1)
            if quote > -1:
                end = quote
            else:
                end = len(pstr)
            return pstr[end + 1:], pstr[start:end]
        elif c.isspace():
            if start is not None:
                end = i
                break
        else:
            if start is None:
                start = i

    if not end:
        end = len(pstr)
    return pstr[end:].strip(), pstr[start:end].lower() if to_lower else pstr[start:end]


# JINNOTE - 11/10/2020 @ 8:41 PM (EST)
#           Probably overthinking how to do this. But maybe the function will
#           come in handy down the road beyond 'read_word()'; tried to allow it
#           have easy expansion.
def list_in_dict(pstr: str = None, orig_dict: dict = None, delimiter="|"):
    my_list = [str(s).strip() for s in pstr.split(delimiter)]
    my_dict = {k: orig_dict[k] for k in orig_dict.keys() & set(my_list)}
    fi_list = []

    if not my_dict:
        return "0"

    for k, v in my_dict.items():
        if k not in my_list:
            comm.notify(f"list_in_dict: bad format '{k}'", merc.CONSOLE_WARNING)
            fi_list.append("0")
            continue

        for bitvector in my_list:
            if str_cmp(bitvector, k):
                fi_list.append(str(v))

    return delimiter.join(fi_list)


# JINNOTE - 11/10/2020 @ 8:45 PM (EST)
#           Revamped read_int() function; seems to be working well from testing.
#           Can probably be refined more but is just a rehash of the stock Pyom version with "better"
#           functionality.  Supports additional -/+ functionality as well as adds | functionality.
#           read_int("1|+1|-1|100|-1|+1000 0 Mathmatically should be: 1 + 1 + -1 + 100 + -1 + 1000 = 1100")
#           (' 0 Mathmatically should be: 1 + 1 + -1 + 100 + -1 + 1000 = 1100', 1100)
#           read_int("100d20+100")
#           ('d20+100', 100)
#           read_int("20+100")
#           ('+100', 20)
def read_int(pstr):
    if not pstr:
        return None, None

    pstr = pstr.lstrip()
    nstr = ""

    if pstr.isalpha():
        pstr = list_in_dict(pstr, bit.bitvector_table)

    if not pstr[0].isdigit() and pstr[0] not in ["-", "+"]:
        comm.notify(f"read_int: bad format ({pstr})", merc.CONSOLE_CRITICAL)
        sys.exit(1)

    for index, c in enumerate(pstr):
        if c.isdigit() or c in ["-", "|"]:
            nstr += c
        elif c in ["+"]:
            if pstr[index - 1] and pstr[index - 1].isdigit():
                break

            nstr += c
        else:
            break

    pstr = pstr[len(nstr):]
    nstr = [int(s) for s in nstr.lstrip().split("|")]
    return pstr, sum(nstr)


def read_string(pstr):
    if not pstr:
        return None, None

    end = pstr.find("~")
    word = pstr[0:end]
    pstr = pstr[end + 1:]
    return pstr, word.strip()


# JINPOINT - Becareful when using with bit.Bit() types; if w.isdigit() it will change type(bit.Bit) to type(int).
#            Assuming that is why room.room_flags used both room_flags.is_set() and is_set(room_flags) and nobody tried/managed to fix.
#            Use the safer bit.read_bits().
def read_flags(pstr):
    if not pstr:
        return None, None

    pstr, w = read_word(pstr, False)
    if w in ["0", 0]:
        return pstr, 0

    if w.isdigit():
        return pstr, int(w)

    flags = 0

    for c in w:
        flag = 0
        if "A" <= c <= "Z":
            flag = merc.BV01
            while c != "A":
                flag *= 2
                c = chr(ord(c) - 1)

        elif "a" <= c <= "z":
            flag = merc.BV27
            while c != "a":
                flag *= 2
                c = chr(ord(c) - 1)

        flags += flag
    return pstr, flags


def item_bitvector_flag_str(bits: int, in_type="extra flags"):
    if not bits or not in_type:
        return None

    if bits == 0:
        return None

    if "wear flags" in in_type:
        bit_list = [(merc.ITEM_TAKE, "take"), (merc.ITEM_WEAR_FINGER, "left_finger, right_finger"), (merc.ITEM_WEAR_NECK, "neck_one, neck_two"),
                    (merc.ITEM_WEAR_BODY, "body"), (merc.ITEM_WEAR_HEAD, "head"), (merc.ITEM_WEAR_LEGS, "legs"), (merc.ITEM_WEAR_FEET, "feet"),
                    (merc.ITEM_WEAR_HANDS, "hands"), (merc.ITEM_WEAR_ARMS, "arms"), (merc.ITEM_WEAR_SHIELD, "right_hand, left_hand"),
                    (merc.ITEM_WEAR_ABOUT, "about_body"), (merc.ITEM_WEAR_WAIST, "waist"), (merc.ITEM_WEAR_WRIST, "left_wrist, right_wrist"),
                    (merc.ITEM_WIELD, "left_hand, right_hand"), (merc.ITEM_HOLD, "left_hand, right_hand"), (merc.ITEM_WEAR_FACE, "face")]
        for (aa, bb) in bit_list:
            if bits & aa:
                return bb
        else:
            return None

    if "extra flags" in in_type:
        bit_list = [(merc.ITEM_GLOW, "glow"), (merc.ITEM_HUM, "hum"), (merc.ITEM_THROWN, "thrown"), (merc.ITEM_KEEP, "keep"),
                    (merc.ITEM_VANISH, "vanish"), (merc.ITEM_INVIS, "invis"), (merc.ITEM_MAGIC, "magic"), (merc.ITEM_NODROP, "no_drop"),
                    (merc.ITEM_BLESS, "bless"), (merc.ITEM_ANTI_GOOD, "anti_good"), (merc.ITEM_ANTI_EVIL, "anti_evil"),
                    (merc.ITEM_ANTI_NEUTRAL, "anti_neutral"), (merc.ITEM_NOREMOVE, "no_remove"), (merc.ITEM_INVENTORY, "inventory"),
                    (merc.ITEM_LOYAL, "loyal"), (merc.ITEM_SHADOWPLANE, "shadowplane")]
        for (aa, bb) in bit_list:
            if bits & aa:
                return bb
        else:
            return None

    if "sitem flags" in in_type:
        bit_list = [(merc.SITEM_ACTIVATE, "activate"), (merc.SITEM_TWIST, "twist"), (merc.SITEM_PRESS, "press"), (merc.SITEM_PULL, "pull"),
                    (merc.SITEM_TARGET, "target"), (merc.SITEM_SPELL, "spell"), (merc.SITEM_TRANSPORTER, "transporter"),
                    (merc.SITEM_TELEPORTER, "teleporter"), (merc.SITEM_DELAY1, "delay1"), (merc.SITEM_DELAY2, "delay2"),
                    (merc.SITEM_OBJECT, "object"), (merc.SITEM_MOBILE, "mobile"), (merc.SITEM_ACTION, "action"), (merc.SITEM_MORPH, "morph"),
                    (merc.SITEM_SILVER, "silver"), (merc.SITEM_WOLFWEAPON, "wolfweapon"), (merc.SITEM_DROWWEAPON, "drowweapon"),
                    (merc.SITEM_CHAMPWEAPON, "champweapon"), (merc.SITEM_DEMONIC, "demonic"), (merc.SITEM_HIGHLANDER, "highlander")]
        for (aa, bb) in bit_list:
            if bits & aa:
                return bb
        else:
            return None


def item_flags_from_bits(bits: int, out_data: collections.namedtuple, in_type="wear flags"):
    if not out_data or not bits or not in_type:
        return None

    if bits == 0:
        return None

    if "wear flags" in in_type:
        bit_list = [(merc.ITEM_WEAR_FINGER, ["left_finger", "right_finger"]), (merc.ITEM_WEAR_NECK, ["neck_one", "neck_two"]),
                    (merc.ITEM_WEAR_BODY, "body"), (merc.ITEM_WEAR_HEAD, "head"), (merc.ITEM_WEAR_LEGS, "legs"), (merc.ITEM_WEAR_FEET, "feet"),
                    (merc.ITEM_WEAR_HANDS, "hands"), (merc.ITEM_WEAR_ARMS, "arms"), (merc.ITEM_WEAR_SHIELD, ["right_hand", "left_hand"]),
                    (merc.ITEM_WEAR_ABOUT, "about_body"), (merc.ITEM_WEAR_WAIST, "waist"), (merc.ITEM_WEAR_WRIST, ["left_wrist", "right_wrist"]),
                    (merc.ITEM_WIELD, ["right_hand", "left_hand"]), (merc.ITEM_HOLD, ["right_hand", "left_hand"]), (merc.ITEM_WEAR_FACE, "face")]
        for (aa, bb) in bit_list:
            if bits & aa:
                if type(bb) == list:
                    out_data.slots.update({str(s) for s in bb})
                else:
                    out_data.slots.update({bb})

        if bits & merc.ITEM_TAKE:
            out_data.attributes.update({"take"})

    if "extra flags" in in_type:
        bit_list = [(merc.ITEM_GLOW, "glow"), (merc.ITEM_HUM, "hum"), (merc.ITEM_THROWN, "thrown"), (merc.ITEM_VANISH, "vanish"),
                    (merc.ITEM_INVIS, "invis"), (merc.ITEM_MAGIC, "magic"), (merc.ITEM_BLESS, "bless"), (merc.ITEM_INVENTORY, "inventory"),
                    (merc.ITEM_LOYAL, "loyal"), (merc.ITEM_SHADOWPLANE, "shadowplane")]
        for (aa, bb) in bit_list:
            if bits & aa:
                out_data.attributes.update({bb})

        bit_list = [(merc.ITEM_KEEP, "keep"), (merc.ITEM_NODROP, "no_drop"), (merc.ITEM_ANTI_GOOD, "anti_good"), (merc.ITEM_ANTI_EVIL, "anti_evil"),
                    (merc.ITEM_ANTI_NEUTRAL, "anti_neutral"), (merc.ITEM_NOREMOVE, "no_remove")]
        for (aa, bb) in bit_list:
            if bits & aa:
                out_data.restrictions.update({bb})

    if "sitem flags" in in_type:
        bit_list = [(merc.SITEM_TRANSPORTER, "transporter"), (merc.SITEM_TELEPORTER, "teleporter"), (merc.SITEM_SILVER, "silver"),
                    (merc.SITEM_WOLFWEAPON, "wolfweapon"), (merc.SITEM_DROWWEAPON, "drowweapon"), (merc.SITEM_CHAMPWEAPON, "champweapon"),
                    (merc.SITEM_DEMONIC, "demonic"), (merc.SITEM_HIGHLANDER, "highlander")]
        for (aa, bb) in bit_list:
            if bits & aa:
                out_data.attributes.update({bb})


def find_location(ch, arg):
    if arg.isdigit():
        vnum = int(arg)

        if vnum in instance.room_templates.keys():
            if vnum != merc.ROOM_VNUM_IN_OBJECT:
                room_instance = instance.instances_by_room[vnum][0]
                return instance.rooms[room_instance]
        return None

    victim = ch.get_char_world(arg)
    if victim:
        return victim.in_room

    item = ch.get_item_world(arg)
    if item:
        if item.in_room:
            return item.in_room

        if item.in_living and item.in_living.in_room:
            return item.in_living.in_room

        if item.in_item and item.in_item.in_room:
            return item.in_item.in_room

        if item.in_item and item.in_item.in_living and item.in_item.in_living.in_room:
            return item.in_item.in_living.in_room
    return None


def append_file(ch, fp, pstr):
    pstr = f"[{ch.in_room.vnum:5}] {ch.name}: {pstr}"
    with open(fp, "a") as f:
        f.write(pstr + "\n")


def read_to_eol(pstr):
    locate = pstr.find("\n")
    if locate == -1:
        locate = len(pstr)
    return pstr[locate+1:], pstr[:locate]


_breakup = re.compile(r"(\".*?\"|\'.*?\'|[^\s]+)")


def is_name(arg, name):
    if not arg or not name:
        return False
    arg = arg.lower()
    name = name.lower()
    words = _breakup.findall(name)
    for word in words:
        if word[0] in ('"', "'"):
            if word[0] == word[-1]:
                word = word[1:-1]
            else:
                word = word[1:]
        if word.startswith(arg):
            return True
    return False


def dice(number, size):
    return sum([random.randint(1, int(size)) for _ in range(int(number))])


def number_fuzzy(number):
    return number_range(number - 1, number + 1)


# Handles ranges where b > a, prevents error being raised.
def number_range(a, b):
    if type(a) != int or type(b) != int:
        comm.notify(f"number_range: ({type(a)}, {type(b)})", merc.CONSOLE_WARNING)
        return -1

    if b < a:
        tmp = b
        b = a
        a = tmp

    return random.randint(a, b)


def number_bits(width):
    return number_range(0, 1 << width - 1)


def number_argument(argument):
    if not argument:
        return 1, ""

    if "." not in argument:
        return 1, argument

    dot = argument.find(".")
    number = argument[:dot]

    if number.isdigit():
        return int(number), argument[dot + 1:]
    else:
        return 1, argument[dot + 1:]


def number_percent(num_float=False):
    if not num_float:
        return int(random.randint(1, 100))
    else:
        return float(f"{random.randint(1, 100)}.{random.randint(0, 99):02}")


# Simple linear interpolation.
def interpolate(level, value_00, value_32):
    return value_00 + level * (value_32 - value_00) // 32


def mass_replace(pstr, pdict):
    for k, v in pdict.items():
        if v:
            pstr = pstr.replace(k, v)
    return pstr


def get_mob_id(npc=True):
    if npc:
        return f"{time.time()}"
    else:
        return str(uuid.uuid4())


# Get an extra description from a list.
def get_extra_descr(name, edd_list):
    if not edd_list:
        return None

    for edd in edd_list:
        if is_name(name, edd.keyword):
            return edd.description
    return None


def to_integer(s: str):
    try:
        return int(s)
    except ValueError:
        return int(float(s))


def colorstrip(msg):
    buf = []

    letter = 0
    while letter < len(msg):
        if msg[letter] in ["#", "^"]:
            letter += 1

            if letter not in range(len(msg)):
                buf += msg[letter - 1]
            elif msg[letter] not in merc.ANSI_STRING1:
                buf += msg[letter]
        else:
            buf += msg[letter]

        letter += 1
    return "".join(buf)


def str_between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)

    if pos_a == -1:
        return ""

    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1:
        return ""

    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b:
        return ""

    return value[adjusted_pos_a:pos_b]


def str_before(value, a):
    # Find first part and return slice before it.
    pos_a = value.find(a)
    if pos_a == -1:
        return ""

    return value[0:pos_a]


def str_after(value, a):
    # Find and validate first part.
    pos_a = value.rfind(a)

    if pos_a == -1:
        return ""

    # Returns chars after the found string.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= len(value):
        return ""

    return value[adjusted_pos_a:]


def str_infix(astr, bstr):
    if not astr:
        return False

    c0 = astr[0].lower()
    sstr1 = len(astr)
    sstr2 = len(bstr)

    for ichar in range(1 + (sstr2 - sstr1)):
        if c0 == bstr[ichar].lower() and astr.startswith(bstr[ichar:]):
            return True
    return False


def str_prefix(astr, bstr, lower=True):
    return len(astr) <= len(bstr) and str_cmp(astr, bstr[:len(astr)], lower)


def str_suffix(astr, bstr, lower=True):
    return len(astr) <= len(bstr) and str_cmp(astr, bstr[-len(astr):], lower)


def is_in(arg, ip):
    if not ip or ip[0] != "|":
        return False

    lo_arg = arg.lower()
    ip = ip[1:].split("*")
    fitted = [s for s in ip if s]

    for aa in fitted:
        if aa.lower() in lo_arg:
            return True
    return False


def all_in(arg, ip):
    if not ip or ip[0] != "&":
        return False

    lo_arg = arg.lower()
    ip = ip[1:].split("*")
    fitted = [s for s in ip if s]

    for aa in fitted:
        if aa.lower() not in lo_arg:
            return False
    return True
