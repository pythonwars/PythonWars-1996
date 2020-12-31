# -*- coding: utf-8 -*- line endings: unix -*-

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

#
# Report any bugs in this implementation to me (email above)
# ------------------------------------------------------------------------------
# Additional changes by Quixadhal on 2014.06.16
# -Re-split code into multiple files, for ease of maintenance
# -Rewrote terminal system
# ------------------------------------------------------------------------------

# Manage one Telnet client connected via a TCP/IP socket.

import sys
import socket
import time

import comm
import game_utils
import merc
from miniboa.terminal import color_convert
from miniboa.terminal import word_wrap
import settings


# ---[ Telnet Notes ]-----------------------------------------------------------
# (See RFC 854 for more information)
#
# Negotiating a Local Option
# --------------------------
#
# Side A begins with:
#
#    "IAC WILL/WONT XX" Meaning "I would like to [use|not use] option XX."
#
# Side B replies with either:
#
#    "IAC DO XX" Meaning "OK, you may use option XX."
#    "IAC DONT XX" Meaning "No, you cannot use option XX."
#
#
# Negotiating a Remote Option
# ----------------------------
#
# Side A begins with:
#
#    "IAC DO/DONT XX" Meaning "I would like YOU to [use|not use] option XX."
#
# Side B replies with either:
#
#    "IAC WILL XX" Meaning "I will begin using option XX"
#    "IAC WONT XX" Meaning "I will not begin using option XX"
#
#
# The syntax is designed so that if both parties receive simultaneous requests
# for the same option, each will see the other's request as a positive
# acknowledgement of its own.
#
# If a party receives a request to enter a mode that it is already in, the
# request should not be acknowledged.


# --[ Global Constants ]--------------------------------------------------------
UNKNOWN = -1
# Cap sockets to 500 on Windows because winsock can only process 512 at time
# Cap sockets to 1000 on Linux because you can only have 1024 file descriptors
MAX_CONNECTIONS = 500 if sys.platform == "win32" else 1000

# --[ Telnet Commands ]---------------------------------------------------------
SE = chr(240)  # End of subnegotiation parameters
NOP = chr(241)  # No operation
DATMK = chr(242)  # Data stream portion of a sync.
BREAK = chr(243)  # NVT Pc BRK
IP = chr(244)  # Interrupt Process
AO = chr(245)  # Abort Output
AYT = chr(246)  # Are you there
EC = chr(247)  # Erase Pc
EL = chr(248)  # Erase Line
GA = chr(249)  # The Go Ahead Signal
SB = chr(250)  # Sub-option to follow
WILL = chr(251)  # Will; request or confirm option begin
WONT = chr(252)  # Wont; deny option request
DO = chr(253)  # Do = Request or confirm remote option
DONT = chr(254)  # Don't = Demand or confirm option halt
IAC = chr(255)  # Interpret as Command
SEND = chr(1)  # Sub-process negotiation SEND command
IS = chr(0)  # Sub-process negotiation IS command

# --[ Telnet Options ]----------------------------------------------------------
BINARY = chr(0)  # Transmit Binary
ECHO = chr(1)  # Echo characters back to sender
RECON = chr(2)  # Reconnection
SGA = chr(3)  # Suppress Go-Ahead
TTYPE = chr(24)  # Terminal Type
NAWS = chr(31)  # Negotiate About Window Size
LINEMO = chr(34)  # Line Mode
MCCP = chr(86)  # MCCP compression
MXP = chr(91)  # MXP support


# --[ Connection Lost ]---------------------------------------------------------
class ConnectionLost(Exception):
    """
    Custom exception to signal a lost connection to the Telnet Server.
    """


# --[ Telnet Option ]-----------------------------------------------------------
class TelnetOption(object):
    """
    Simple class used to track the status of an extended Telnet option.
    """

    def __init__(self):
        self.local_option = UNKNOWN  # Local state of an option
        self.remote_option = UNKNOWN  # Remote state of an option
        self.reply_pending = False  # Are we expecting a reply?


# --[ Telnet Client ]-----------------------------------------------------------
class TelnetClient(object):
    """
    Represents a client connection via Telnet.

    First argument is the socket discovered by the Telnet Server.
    Second argument is the tuple (ip address, port number).
    """

    def __init__(self, sock, addr_tup):
        self.active = True  # Turns False when the connection is lost
        self.sock = sock  # The connection's socket
        self.fileno = sock.fileno()  # The socket's file descriptor
        self.address = addr_tup[0]  # The client's remote TCP/IP address
        self.port = addr_tup[1]  # The client's remote port
        hostname = socket.gethostbyaddr(addr_tup[0])[0]
        self.hostname = hostname if not game_utils.str_cmp(hostname, settings.LOCAL_NAME) else "localhost"
        self.terminal_type = "ANSI"  # set via request_terminal_type()
        self.columns = 80
        self.rows = 24
        self.send_pending = False
        self.send_buffer = ""
        self.recv_buffer = ""
        self.bytes_sent = 0
        self.bytes_received = 0
        self.cmd_ready = False
        self.command_list = []
        self.connect_time = time.time()
        self.last_input_time = time.time()
        self.snoop_by = None
        self.character = None
        self.original = None

        # State variables for interpreting incoming telnet commands
        self.telnet_got_iac = False  # Are we inside an IAC sequence?
        self.telnet_got_cmd = None  # Did we get a telnet command?
        self.telnet_got_sb = False  # Are we inside a subnegotiation?
        self.telnet_opt_dict = {}  # Mapping for up to 256 TelnetOptions
        self.telnet_echo = False  # Echo input back to the client?
        self.telnet_echo_password = False  # Echo back '*' for passwords?
        self.telnet_sb_buffer = ""  # Buffer for sub-negotiations

    def get_command(self):
        """
        Get a line of text that was received from the client. The class's
        cmd_ready attribute will be true if lines are available.
        """
        cmd = None
        count = len(self.command_list)
        if count > 0:
            cmd = self.command_list.pop(0)

        # If that was the last line, turn off lines_pending
        if count == 1:
            self.cmd_ready = False
        return cmd

    def show_terminal_type(self):
        return "Terminal Type set to {} ({} columns, {} rows)\n".format(self.terminal_type, self.columns, self.rows)

    def clear_screen(self, top):
        if top:
            self.send("\033[2J\033[H")
        else:
            self.send("\x1b[2J")

    def send(self, text: str, wrap: int = None, terminal: str = "ANSI"):
        if text and isinstance(text, str):
            text = text.replace("\n\r", "\n")  # DikuMUD got their line endings backwards
            text = text.replace("\r\n", "\n")  # This is correct for TELNET, but we need to ensure that "\r\n" doesn't become
            # \r\n\n" later.

            if wrap:
                text = "\n".join(word_wrap(text, wrap))  # Note self.columns is negotiated

            if terminal:
                text = color_convert(text, "ANSI")  # Note self.terminal_type is negotiated

            self.send_buffer += text.replace("\n", "\r\n")
            self.send_pending = True

    def deactivate(self):
        """
        Set the client to disconnect on the next server poll.
        """
        self.socket_send()  # Flush buffer
        self.active = False

    def addrport(self, ip=True):
        """
        Return the client's IP address and port number as string.
        """
        return "{}:{}".format(self.address if ip else self.hostname, self.port)

    def addr(self, ip=True):
        """
        Return the client's IP address as string.
        :return:
        """
        return "{}".format(self.address if ip else self.hostname)

    def idle(self, seconds=True):
        """
        Returns the number of seconds that have elasped since the client
        last sent us some input.
        :param seconds:
        """
        if seconds:
            return time.time() - self.last_input_time
        else:
            return (time.time() - self.last_input_time) // 60

    def duration(self, seconds=True):
        """
        Returns the number of seconds the client has been connected.
        :param seconds:
        """
        if seconds:
            return time.time() - self.connect_time
        else:
            return (time.time() - self.connect_time) // 60

    def request_do_sga(self):
        """
        Request client to Suppress Go-Ahead.  See RFC 858.
        """
        self._iac_do(SGA)
        self._note_reply_pending(SGA, True)

    def request_will_echo(self):
        """
        Tell the client that we would like to echo their text.  See RFC 857.
        """
        self._iac_will(ECHO)
        self._note_reply_pending(ECHO, True)
        self.telnet_echo = True

    def request_wont_echo(self):
        """
        Tell the client that we would like to stop echoing their text.
        See RFC 857.
        """
        self._iac_wont(ECHO)
        self._note_reply_pending(ECHO, True)
        self.telnet_echo = False

    def password_mode_on(self):
        """
        Tell client we will echo (but don't) so typed passwords don't show.
        """
        self._iac_will(ECHO)
        self._note_reply_pending(ECHO, True)

    def password_mode_off(self):
        """
        Tell client we are done echoing (we lied) and show typing again.
        """
        self._iac_wont(ECHO)
        self._note_reply_pending(ECHO, True)

    def request_naws(self):
        """
        Request to Negotiate About Window Size.  See RFC 1073.
        """
        self._iac_do(NAWS)
        self._note_reply_pending(NAWS, True)

    def request_terminal_type(self):
        """
        Begins the Telnet negotiations to request the terminal type from
        the client.  See RFC 779.
        """
        self._iac_do(TTYPE)
        self._note_reply_pending(TTYPE, True)

    def socket_send(self):
        """
        Called by TelnetServer when send data is ready.
        """
        if len(self.send_buffer):
            try:
                # convert to ansi before sending
                sent = self.sock.send(bytes(self.send_buffer, "latin1"))
            except socket.error as err:
                comm.notify("SEND error '{}' from {}".format(err, self.addrport()), merc.CONSOLE_INFO)
                self.active = False
                return

            self.bytes_sent += sent
            self.send_buffer = self.send_buffer[sent:]
        else:
            self.send_pending = False

    def socket_recv(self):
        """
        Called by TelnetServer when recv data is ready.
        """
        try:
            # Encode recieved bytes in ansi
            data = str(self.sock.recv(2048), "latin1")
        except socket.error as err:
            comm.notify("RECIEVE socket error '{}' from {}".format(err, self.addrport()), merc.CONSOLE_ERROR)
            raise ConnectionLost()

        # Did they close the connection?
        size = len(data)
        if size == 0:
            comm.notify("No data recieved, client closed connection", merc.CONSOLE_ERROR)
            raise ConnectionLost()

        # Update some trackers
        self.last_input_time = time.time()
        self.bytes_received += size

        # Test for telnet commands
        for byte in data:
            self._iac_sniffer(byte)

        # Look for newline characters to get whole lines from the buffer
        while True:
            mark = self.recv_buffer.find("\n")
            if mark == -1:
                break

            cmd = self.recv_buffer[:mark].strip()
            self.command_list.append(cmd)
            self.cmd_ready = True
            self.recv_buffer = self.recv_buffer[mark + 1:]

    def _recv_byte(self, byte):
        """
        Non-printable filtering currently disabled because it did not play
        well with extended character sets.
        """
        # Filter out non-printing characters
        # if (byte >= ' ' and byte <= '~') or byte == '\n':
        if self.telnet_echo:
            self._echo_byte(byte)
        self.recv_buffer += byte

    def _echo_byte(self, byte):
        """
        Echo a character back to the client and convert LF into CR/LF.
        """
        if byte == "\n":
            self.send_buffer += "\r"
        if self.telnet_echo_password:
            self.send_buffer += "*"
        else:
            self.send_buffer += byte

    def _iac_sniffer(self, byte):
        """
        Watches incomming data for Telnet IAC sequences.
        Passes the data, if any, with the IAC commands stripped to
        _recv_byte().
        """
        # Are we not currently in an IAC sequence coming from the client?
        if self.telnet_got_iac is False:

            if byte == IAC:
                # Well, we are now
                self.telnet_got_iac = True
                return
            # Are we currenty in a sub-negotion?
            elif self.telnet_got_sb is True:
                # Sanity check on length
                if len(self.telnet_sb_buffer) < 64:
                    self.telnet_sb_buffer += byte
                else:
                    self.telnet_got_sb = False
                    self.telnet_sb_buffer = ""
                return

            else:
                # Just a normal NVT character
                self._recv_byte(byte)
                return

        # Byte handling when already in an IAC sequence sent from the client
        else:
            # Did we get sent a second IAC?
            if byte == IAC and self.telnet_got_sb is True:
                # Must be an escaped 255 (IAC + IAC)
                self.telnet_sb_buffer += byte
                self.telnet_got_iac = False
                return

            # Do we already have an IAC + CMD?
            elif self.telnet_got_cmd:
                # Yes, so handle the option
                self._three_byte_cmd(byte)
                return

            # We have IAC but no CMD
            else:
                # Is this the middle byte of a three-byte command?
                if byte == DO:
                    self.telnet_got_cmd = DO
                    return
                elif byte == DONT:
                    self.telnet_got_cmd = DONT
                    return
                elif byte == WILL:
                    self.telnet_got_cmd = WILL
                    return
                elif byte == WONT:
                    self.telnet_got_cmd = WONT
                    return
                else:
                    # Nope, must be a two-byte command
                    self._two_byte_cmd(byte)

    def _two_byte_cmd(self, cmd):
        """
        Handle incoming Telnet commands that are two bytes long.
        """
        if cmd == SB:
            # Begin capturing a sub-negotiation string
            self.telnet_got_sb = True
            self.telnet_sb_buffer = ""
        elif cmd == SE:
            # Stop capturing a sub-negotiation string
            self.telnet_got_sb = False
            self._sb_decoder()
        elif cmd in [NOP, DATMK, IP, AO, AYT, EC, EL, GA]:
            pass
        else:
            comm.notify("Send an invalid 2 byte command", merc.CONSOLE_ERROR)

        self.telnet_got_iac = False
        self.telnet_got_cmd = None

    def _three_byte_cmd(self, option):
        """
        Handle incoming Telnet commmands that are three bytes long.
        """
        cmd = self.telnet_got_cmd
        # comm.notify("_three_byte_cmd: {}:{}".format(ord(cmd), ord(option)), merc.CONSOLE_INFO)

        # Incoming DO's and DONT's refer to the status of this end
        if cmd == DO:
            if option in [BINARY, SGA, ECHO]:
                if self._check_reply_pending(option):
                    self._note_reply_pending(option, False)
                    self._note_local_option(option, True)
                elif self._check_local_option(option) is False or self._check_local_option(option) is UNKNOWN:
                    self._note_local_option(option, True)
                    self._iac_will(option)

                    if option == ECHO:
                        self.telnet_echo = True
            else:
                # All other options = Default to refusing once
                if self._check_local_option(option) is UNKNOWN:
                    self._note_local_option(option, False)
                    self._iac_wont(option)
        elif cmd == DONT:
            if option in [BINARY, SGA]:
                if self._check_reply_pending(option):
                    self._note_reply_pending(option, False)
                    self._note_local_option(option, False)
                elif self._check_local_option(option) is True or self._check_local_option(option) is UNKNOWN:
                    self._note_local_option(option, False)
                    self._iac_wont(option)
            elif option == ECHO:
                if self._check_reply_pending(option):
                    self._note_reply_pending(option, False)
                    self._note_local_option(option, False)
                elif self._check_local_option(option) is True or self._check_local_option(option) is UNKNOWN:
                    self._note_local_option(option, False)
                    self._iac_wont(option)
                    self.telnet_ehco = False
            else:
                # All other options = Default to ignoring
                pass
        # Incoming WILL's and WONT's refer to the status of the client
        elif cmd == WILL:
            if option == ECHO:
                # Nutjob client offering to echo the server...
                if self._check_remote_option(ECHO) is UNKNOWN:
                    self._note_remote_option(ECHO, False)
                    # No no, bad client!
                    self._iac_dont(ECHO)
            elif option in [NAWS, SGA]:
                if self._check_reply_pending(option):
                    self._note_reply_pending(option, False)
                    self._note_remote_option(option, True)
                elif self._check_remote_option(option) is False or self._check_remote_option(option) is UNKNOWN:
                    self._note_remote_option(option, True)
                    self._iac_do(option)
                    # Client should respond with SB (for NAWS)
            elif option == TTYPE:
                if self._check_reply_pending(TTYPE):
                    self._note_reply_pending(TTYPE, False)
                    self._note_remote_option(TTYPE, True)
                    # Tell them to send their terminal type
                    self.send("{}{}{}{}{}{}".format(IAC, SB, TTYPE, SEND, IAC, SE))
                elif self._check_remote_option(TTYPE) is False or self._check_remote_option(TTYPE) is UNKNOWN:
                    self._note_remote_option(TTYPE, True)
                    self._iac_do(TTYPE)
        elif cmd == WONT:
            if option == ECHO:
                # Client states it wont echo us -- good, they're not supposes
                # to.
                if self._check_remote_option(ECHO) is UNKNOWN:
                    self._note_remote_option(ECHO, False)
                    self._iac_dont(ECHO)
            elif option in [SGA, TTYPE, MXP]:
                if self._check_reply_pending(option):
                    self._note_reply_pending(option, False)
                    self._note_remote_option(option, False)
                elif self._check_remote_option(option) is True or self._check_remote_option(option) is UNKNOWN:
                    self._note_remote_option(option, False)
                    self._iac_dont(option)
                    # Should TTYPE be below this?
            else:
                # All other options = Default to ignoring
                pass
        else:
            comm.notify("Send an invalid 3 byte command", merc.CONSOLE_ERROR)

        self.telnet_got_iac = False
        self.telnet_got_cmd = None

    def _sb_decoder(self):
        """
        Figures out what to do with a received sub-negotiation block.
        """
        bloc = self.telnet_sb_buffer
        if len(bloc) > 2:
            if bloc[0] == TTYPE and bloc[1] == IS:
                self.terminal_type = bloc[2:].lower()
                # comm.notify("Terminal type = '{}'".format(self.terminal_type), merc.CONSOLE_INFO)

            if bloc[0] == NAWS:
                if len(bloc) != 5:
                    comm.notify("Bad length on NAWS SB: {}".format(str(len(bloc))), merc.CONSOLE_INFO)
                else:
                    self.columns = (256 * ord(bloc[1])) + ord(bloc[2])
                    self.rows = (256 * ord(bloc[3])) + ord(bloc[4])
                # comm.notify("Screen is {} x {}".format(self.columns, self.rows), merc.CONSOLE_INFO)

        self.telnet_sb_buffer = ""

    # ---[ State Juggling for Telnet Options ]----------------------------------
    # Sometimes verbiage is tricky.  I use 'note' rather than 'set' here
    # because (to me) set infers something happened.
    def _check_local_option(self, option):
        # Test the status of local negotiated Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()

        return self.telnet_opt_dict[option].local_option

    def _note_local_option(self, option, state):
        # Record the status of local negotiated Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()

        self.telnet_opt_dict[option].local_option = state

    def _check_remote_option(self, option):
        # Test the status of remote negotiated Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()
        return self.telnet_opt_dict[option].remote_option

    def _note_remote_option(self, option, state):
        # Record the status of local negotiated Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()
        self.telnet_opt_dict[option].remote_option = state

    def _check_reply_pending(self, option):
        # Test the status of requested Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()
        return self.telnet_opt_dict[option].reply_pending

    def _note_reply_pending(self, option, state):
        # Record the status of requested Telnet options.
        if option not in self.telnet_opt_dict:
            self.telnet_opt_dict[option] = TelnetOption()

        self.telnet_opt_dict[option].reply_pending = state

    # ---[ Telnet Command Shortcuts ]-------------------------------------------

    def _iac_do(self, option):
        # Send a Telnet IAC "DO" sequence.
        self.send("{}{}{}".format(IAC, DO, option))

    def _iac_dont(self, option):
        # Send a Telnet IAC "DONT" sequence.
        self.send("{}{}{}".format(IAC, DONT, option))

    def _iac_will(self, option):
        # Send a Telnet IAC "WILL" sequence.
        self.send("{}{}{}".format(IAC, WILL, option))

    def _iac_wont(self, option):
        # Send a Telnet IAC "WONT" sequence.
        self.send("{}{}{}".format(IAC, WONT, option))

    def send_ga(self):
        self.send("{}{}".format(IAC, GA))
