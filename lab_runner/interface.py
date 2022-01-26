import cmd
import pandas as pd

from interface_helper import Helper

# reference for aliases: https://stackoverflow.com/questions/12911327/aliases-for-commands-with-python-cmd-module

class MyCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.helper = Helper()
        self.aliases = { 'r'   : self.do_refresh,
                         'q'   : self.do_quit,
                         'h'   : self.do_help,
                         'c'   : self.do_custom }

    def do_refresh(self, line):
        'refresh: Refreshes the enchants based on the primary screen capture.'
        print(self.helper.refresh())
        pass

    def do_refresh_data(self, line):
        'refresh: Refreshed internal data then calls refresh.'
        self.helper = Helper()
        print(self.helper.refresh())
        pass

    def do_custom(self, line):
        'custom <enchant>: Prints notes for specific enchant. Supports tab completion.'
        return self.helper.to_table_str([line,])
    
    def complete_custom(self, line):
        if not line:
            return self.helper.get_enchant_list()
        else:
            completions = [ f
                            for f in self.helper.get_enchant_list()
                            if f.startswith(line)
                            ]
        return completions

    def do_quit(self, arg):
        'quit: Quits the app'
        return True
    
    def do_help(self, arg):
        if arg in self.aliases:
            arg = self.aliases[arg].__name__[3:]
        cmd.Cmd.do_help(self, arg)
    
    def default(self, line):
        cmd, arg, line = self.parseline(line)
        if cmd in self.aliases:
            self.aliases[cmd](arg)
        else:
            print("*** Unknown syntax: %s" % line)


if __name__ == '__main__':
    my_cmd = MyCmd()
    my_cmd.cmdloop('Type help for a list of available commands.')
