import sys
import xmlrpc.client

class BedrockServerConsole:

    SERVER_URL = 'http://localhost:11542'
    COMMAND = ' '.join(sys.argv[1:])

    def __init__(self, server_url=SERVER_URL) -> None:
        self.server = xmlrpc.client.ServerProxy(server_url)

    def send_command(self, command_str):
        print("Sending command: '%s' to RPC server: %s" % (command_str, self.server))
        self.server.send_command(command_str)

def run_console():
    BedrockServerConsole().send_command(' '.join(sys.argv[1:]))

