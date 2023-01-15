import cmd
import sys
import xmlrpc.client

class BedrockServerConsole(cmd.Cmd):
    intro = 'Type help or ? to list commands.\n'
    prompt = 'bds> '
    file = None

    SERVER_URL = 'http://localhost:11542'
    COMMAND = ' '.join(sys.argv[1:])

    def __init__(self, server_url=SERVER_URL) -> None:
        super().__init__()
        self.server = xmlrpc.client.ServerProxy(server_url)

    def do_cmd(self, command_str):
        'Send command to server: CMD <command string>'

        print("Sending command: '%s' to RPC server: %s" % (command_str, self.server))
        self.server.send_command(command_str)

    def do_exit(self, arg):
        'Exit the console'

        return True

def run_console():
    if len(sys.argv) > 1:
        BedrockServerConsole(' '.join(sys.argv[1:])).cmdloop()
    else:
        BedrockServerConsole().cmdloop()

