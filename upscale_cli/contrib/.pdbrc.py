from pdb import DefaultConfig


class Config(DefaultConfig):
    prompt = "pdb> "
    sticky_by_default = True
    editor = "vim"


# SOURCE: https://github.com/giampaolo/sysconf/blob/8e80194e59d643eae54f063d32a4feac8138a5f3/home/.pdbrc.py
# FIXME: Try this? 9/24/2018
# def main():
#     import atexit
#     import os
#     import readline
#     import sys
#     import termios
#     import textwrap

#     # =================================================================
#     # --- utils
#     # =================================================================

#     HISTORY_FILE = os.path.expanduser("~/.pyhistory")
#     HISTORY_LENGTH = 10000

#     def term_supports_colors():
#         file = sys.stdout
#         try:
#             import curses
#             assert file.isatty()
#             curses.setupterm()
#             assert curses.tigetnum("colors") > 0
#         except Exception:
#             return False
#         else:
#             return True

#     TERM_SUPPORTS_COLORS = term_supports_colors()

#     def hilite(s, ok=True, bold=False):
#         """Return an highlighted version of 'string'."""
#         if not TERM_SUPPORTS_COLORS:
#             return s
#         attr = []
#         if ok is None:  # no color
#             pass
#         elif ok:   # green
#             attr.append('32')
#         else:   # red
#             attr.append('31')
#         if bold:
#             attr.append('1')
#         return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), s)

#     def print_(s):
#         print(hilite(s))

#     # =================================================================
#     # --- ok, here we go
#     # =================================================================

#     # tab completion
#     if sys.platform.startswith("darwin"):
#         readline.parse_and_bind("bind ^I rl_complete")
#     else:
#         readline.parse_and_bind('tab: complete')

#     # load history
#     try:
#         readline.read_history_file(HISTORY_FILE)
#     except IOError:
#         pass

#     # save history on exit
#     def save_history(path):
#         import readline;
#         readline.set_history_length(HISTORY_LENGTH)
#         readline.write_history_file(path)

#     atexit.register(save_history, HISTORY_FILE)

#     # Taken from https://gist.github.com/1125049
#     # There are a couple of edge cases where you can lose terminal
#     # echo. This should restore it next time you open a pdb.
#     termios_fd = sys.stdin.fileno()
#     termios_echo = termios.tcgetattr(termios_fd)
#     termios_echo[3] = termios_echo[3] | termios.ECHO
#     termios_result = termios.tcsetattr(
#         termios_fd, termios.TCSADRAIN, termios_echo)

#     help_ = textwrap.dedent("""\
#         h(elp) [obj]  : same as help(obj)
#         w(here)       : print a stack trace
#         d(own)        : move the current frame one level down in the stack
#         u(p)          : move the current frame one level up in the stack trace
#         b(reak) [[filename:]lineno | function[, condition]]
#                       : sets breakpoint
#         tbreak [[filename:]lineno | function[, condition]]
#                       : sets a temporary breakpoint
#         cl(ear) [filename:lineno | bpnumber [bpnumber ...]]
#                       : clear breakpoints
#         s(tep)        : step into function
#         n(ext)        : next line
#         unt(il)       : continue execution until the line with the line number
#                         greater than the current one is reached
#         r(eturn)      : continue execution until the current function returns
#         c(ont(inue))  : continue execution
#         j(ump) lineno : set the next line that will be executed
#         l(ist) [first[, last]]
#                       : list source code for the current file;
#         a(rgs)        : print the argument list of the current function
#         p expression  : evaluate expr and print its value
#         pp <obj>      : pretty print obj
#         alias [name [command]]
#                       : creates an alias
#         [!]statement  : escape commands
#         run [args ...]: restart the debugged Python program;
#         q(uit)        : quit
#         """)
#     print_(help_)


# main()

# # Tab completion for pdb. Ths *NEEDS* to be done globally.
# # Also, at this
# import rlcompleter
# pdb.Pdb.complete = rlcompleter.Completer(locals()).complete

# # Cleanup namespace.
# del main, rlcompleter
