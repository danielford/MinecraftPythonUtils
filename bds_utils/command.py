import collections
import re

MinecraftCommand = collections.namedtuple(
    'MinecraftCommand', ['command', 'pattern'])

ListCommand = MinecraftCommand('list', re.compile(
    'There are (\d+)\/(\d+) players online:'))
ShutdownCommand = MinecraftCommand(
      'stop', re.compile('Server stop requested'))

class CommandExecution:
    def __init__(self, command, pattern, handler):
        self.command = command
        self.pattern = pattern
        self.handler = handler
        self.buffer = ''

    def send(self, pipe):
        pipe.write(self.command + '\n')
        pipe.flush()

    def check(self, new_output):
        if not self.handler:
            return True

        self.buffer += new_output

        match = self.pattern.match(self.buffer)

        if match:
            self.handler(*match.groups())
            return True
        else:
            return False
